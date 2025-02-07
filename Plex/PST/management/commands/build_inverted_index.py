import json
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.core.management.base import BaseCommand
from PST.models import WebPage
import nltk

try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

class Command(BaseCommand):
    help = 'Construit un index inversé à partir des contenus de la base de données'

    def handle(self, *args, **options):
        self.stdout.write("Construction de l'index inversé...")

        inverted_index = self.build_inverted_index()

        self.stdout.write("Index inversé construit.")

        self.save_index_to_file(inverted_index)

        self.stdout.write("Index inversé sauvegardé dans inverted_index.json.")

    def build_inverted_index(self):

        from collections import defaultdict
        inverted_index = defaultdict(set)
        stop_words = set(stopwords.words('english'))

        for page in WebPage.objects.all():
            if page.content:
                words = word_tokenize(page.content.lower())
                filtered_words = [
                    word for word in words if word.isalnum() and word not in stop_words
                ]

                for word in filtered_words:
                    inverted_index[word].add(page.url)

        return {word: list(urls) for word, urls in inverted_index.items()}

        inverted_index = defaultdict(list)
        stop_words = set(stopwords.words('english'))

        for page in WebPage.objects.all():
            if page.content:
                words = word_tokenize(page.content.lower())
                filtered_words = [
                    word for word in words if word.isalnum() and word not in stop_words
                ]

                for word in filtered_words:
                    inverted_index[word].append(page.url)

        return inverted_index

    def save_index_to_file(self, inverted_index):

        with open('inverted_index.json', 'w') as file:
            json.dump(inverted_index, file, indent=4)
