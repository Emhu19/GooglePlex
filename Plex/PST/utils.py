from sklearn.feature_extraction.text import TfidfVectorizer
import functools

# Cache des résultats pour éviter de recalculer plusieurs fois les mêmes choses
@functools.lru_cache(maxsize=1024)
def get_tfidf_matrix(documents):
    vectorizer = TfidfVectorizer(stop_words='english')
    return vectorizer.fit_transform(documents)

def calculate_tfidf_score(page_content, query):
    """Calcul du score TF-IDF optimisé pour une requête par rapport à un contenu."""
    # Prétraitement de la requête et du contenu
    documents = [page_content, query]

    # Calcul du score en utilisant un cache pour éviter des recalculs
    tfidf_matrix = get_tfidf_matrix(tuple(documents))

    # Le score TF-IDF est la similarité entre la requête et le contenu de la page
    score = tfidf_matrix[1, :].dot(tfidf_matrix[0, :].T).toarray()[0][0]
    return score
