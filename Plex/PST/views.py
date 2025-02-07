from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .forms import SearchForm
from PST.models import WebPage
from django.shortcuts import render
from PST.models import Page  # Modèle où vous avez stocké les pages
from .utils import calculate_tfidf_score  # Fonction pour calculer le score TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer

def home(request):
    return render(request, 'index.html')
import gzip
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict

# Charger l'index inversé depuis le fichier JSON
with gzip.open('inverted_index.json.gz', 'rt', encoding='utf-8') as f:
    inverted_index = json.load(f)
# Fonction de recherche
def search(request):
    query = request.GET.get('q', '')
    if query:
        stop_words = set(stopwords.words('english'))

        # Tokeniser et filtrer les termes de la requête
        query_terms = [word.lower() for word in word_tokenize(query) if word.isalnum() and word.lower() not in stop_words]

        # Trouver les documents correspondants à la requête à l'aide de l'index inversé
        relevant_documents = defaultdict(list)
        for term in query_terms:
            if term in inverted_index:
                for url in inverted_index[term]:
                    relevant_documents[url].append(term)

        # Récupérer les contenus des documents correspondants depuis la base de données
        web_pages = WebPage.objects.filter(url__in=relevant_documents.keys())

        # Construire une liste de contenu pour le calcul TF-IDF
        documents = [page.content for page in web_pages]
        documents.append(query)  # Ajouter la requête

        # Calculer le TF-IDF pour les documents pertinents
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Le dernier vecteur est celui de la requête
        query_vector = tfidf_matrix[-1]
        scores = []

        for i, page in enumerate(web_pages):
            # Calculer la similarité cosinus entre la requête et le document
            score = (query_vector * tfidf_matrix[i].T).toarray()[0][0]
            scores.append((page, score))

        # Trier les résultats par score décroissant
        sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)

        # Passer les résultats au template
        return render(request, 'index.html', {'results': sorted_results, 'query': query})
    else:
        return render(request, 'index.html', {'results': [], 'query': query})

