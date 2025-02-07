from django.db import models
from PST.forms import SearchForm

class WebPage(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)  # Nouvelle colonne
    language = models.CharField(max_length=20, null=True, blank=True)  # Langue détectée
    content_length = models.IntegerField(null=True, blank=True)  # Taille du contenu en octets
    last_modified = models.CharField(max_length=100, null=True, blank=True)  # Date ou ETag
    tfidf_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url

class VisitedURL(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class WebCrawler:
    def __init__(self):
        self.page_contents = []  # Définir l'attribut ici
        self.page_urls = []

    async def get_page_content(self, url, session):
        """ Récupère le contenu de la page via une requête asynchrone """
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()

                if 'text' in content_type or 'html' in content_type:
                    try:
                        content = await response.text()
                    except UnicodeDecodeError:
                        content = await response.text(encoding='ISO-8859-1')  # Autre encodage
                    self.page_contents.append(content)  # Ajout à l'attribut
                    self.page_urls.append(url)
                    return content
                else:
                    print(f"Le contenu de {url} n'est pas du texte.")
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Erreur lors de la récupération de {url}: {e}")
            return None


def search_web_pages(query):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM webpage_fts WHERE webpage_fts MATCH ?
    ''', [query])
    results = cursor.fetchall()

    return results

class Page(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # Le contenu de la page (peut être HTML ou texte brut)
    url = models.URLField()

    def __str__(self):
        return self.title
