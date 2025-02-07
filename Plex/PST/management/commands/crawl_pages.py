import asyncio
import aiohttp
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from PST.models import WebPage, VisitedURL
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db import transaction
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langdetect import detect
from urllib.robotparser import RobotFileParser
import logging

# ça j'ai pas compris à quoi ça servait encore
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

crawl_schedule = {
    # 'https://news.google.com/home?hl=fr&gl=FR&ceid=FR:fr': {'query': 'youtube search', 'last_crawl': datetime(2025, 1, 20, 12, 0)},
    'https://www.domainedeboischampt.fr/produit/julienas-beauvernay-bio/': {'query': 'scholar search', 'last_crawl': datetime(2025, 1, 21, 15, 30)},
    # 'https://fr.wiktionary.org/wiki/Wiktionnaire:Page_d%E2%80%99accueil/': {'query': 'google search', 'last_crawl': datetime(2025, 1, 20, 12, 0)},
    # 'https://fr.wikibooks.org/wiki/Accueil': {'query': 'google search', 'last_crawl': datetime(2025, 1, 20, 12, 0)},
    # 'https://fr.wikiversity.org/wiki/Wikiversit%C3%A9:Accueil': {'query': 'google search', 'last_crawl': datetime(2025, 1, 20, 12, 0)},
}

minimum_crawl_interval = timedelta(seconds=1)

import nltk
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')


class Command(BaseCommand):
    help = 'Crawl les pages avec des crawlers parallèles'

    def handle(self, *args, **options):
        asyncio.run(self.crawl())

    async def crawl(self):
        visited_urls = set()
        queue = asyncio.Queue()

        for url in crawl_schedule.keys():
            await queue.put(url)

        semaphore = asyncio.Semaphore(5) #ptn ça marche pas cette histoire
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.crawler_task(queue, visited_urls, semaphore, session)
                for _ in range(5)
            ]
            await asyncio.gather(*tasks)

    async def crawler_task(self, queue, visited_urls, semaphore, session):
        while not queue.empty():
            url = await queue.get()  # recup URL de la queue

            async with semaphore:
                await self.crawl_page(url, visited_urls, queue, session)

            queue.task_done()

    async def crawl_page(self, url, visited_urls, queue, session):
        if url in visited_urls:
            return

        if not await self.is_crawl_allowed(url):
            logger.warning(f"Crawling interdit par robots.txt : {url}")
            return

        logger.info(f"Visiting: {url}")
        visited_urls.add(url)
        await self.mark_url_as_visited(url)

        content = await self.get_page_content(url, session)
        if not content:
            return

        title, keywords = self.extract_title_and_keywords(content)
        meta_description = self.extract_meta_description(content)
        text_content = self.extract_content(content)
        language = self.detect_language(text_content)
        generated_keywords = self.extract_keywords_from_text(text_content)
        keywords = keywords or generated_keywords
        content_length, last_modified = await self.get_page_metadata(url, session)

        await self.save_page(url, title, text_content, keywords, meta_description, language, content_length, last_modified)

        links = self.extract_links(content, url)
        for link in links:
            if self.is_valid_url(link) and link not in visited_urls:
                await queue.put(link)  # rajoute les nouveaux liens (hyper utile)

    @database_sync_to_async
    def is_url_visited(self, url):
        return VisitedURL.objects.filter(url=url).exists()

    @database_sync_to_async
    @transaction.atomic
    def mark_url_as_visited(self, url):
        VisitedURL.objects.get_or_create(url=url)

    @database_sync_to_async
    @transaction.atomic
    def save_page(self, url, title, content, keywords, meta_description, language, content_length, last_modified):
        WebPage.objects.update_or_create(
            url=url,
            defaults={
                'title': title,
                'content': content,
                'keywords': keywords,
                'meta_description': meta_description,
                'language': language,
                'content_length': content_length,
                'last_modified': last_modified
            }
        )
        logger.info(f"Page enregistrée: {url}")

    async def get_page_content(self, url, session):
        """Récupère le contenu de la page avec une gestion de l'encodage."""
        try:
            async with session.get(url) as response:
                # Utiliser le charset du serveur s'il est spécifié, sinon fallback à 'utf-8'
                content_type = response.headers.get('Content-Type', '')
                encoding = response.charset or 'utf-8'  # Détecte ou utilise UTF-8 par défaut
                return await response.text(encoding=encoding)
        except UnicodeDecodeError:
            # Si une erreur se produit, utiliser 'ignore' ou un encodage différent
            async with session.get(url) as response:
                raw_content = await response.read()  # Récupérer les octets bruts
                return raw_content.decode('utf-8', errors='ignore')  # Ignore les erreurs


    async def is_crawl_allowed(self, base_url, user_agent='*'):
        parsed_url = urlparse(base_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        robot_parser = RobotFileParser()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=10) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        robot_parser.parse(robots_content.splitlines())
                    else:
                        return True
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification de {robots_url}: {e}")
            return True

        return robot_parser.can_fetch(user_agent, base_url)

    async def get_page_metadata(self, url, session):
        try:
            async with session.head(url, timeout=10) as response:
                content_length = response.headers.get('Content-Length', '0')
                last_modified = response.headers.get('Last-Modified', None)
                return int(content_length), last_modified
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métadonnées: {e}")
            return 0, None

    def extract_title_and_keywords(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Extraction du titre
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else None

        # Extraction des meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = meta_keywords['content'].strip() if meta_keywords and 'content' in meta_keywords.attrs else None

        return title, keywords


    def extract_meta_description(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        meta_description = soup.find('meta', attrs={'name': 'description'})

        if meta_description and 'content' in meta_description.attrs:
            return meta_description['content']
        else:
            return 'No description found'


    def extract_content(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text

    def extract_links(self, content, base_url):
        soup = BeautifulSoup(content, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = self.resolve_url(href, base_url)
            if full_url:
                links.add(full_url)

        logger.info(f"Liens extraits de {base_url}: {len(links)}")
        return links

    def resolve_url(self, href, base_url):
        return urljoin(base_url, href) if href else None

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.scheme in ['http', 'https']

    def detect_language(self, text):
        try:
            return detect(text)
        except Exception:
            return 'unknown'

    def extract_keywords_from_text(self, text):
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
        return ', '.join([word for word, count in Counter(filtered_words).most_common(10)])
