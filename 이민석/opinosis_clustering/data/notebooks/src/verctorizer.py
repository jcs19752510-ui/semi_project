from sklearn.feature_extraction.text import TfidfVectorizer

def get_tfidf_matrix(corpus, max_features=1000):
    """TF-IDF 벡터라이저를 통한 밀집/희소 행렬 생성"""
    vectorizer = TfidfVectorizer(
        max_features=max_features, 
        stop_words='english', 
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return tfidf_matrix, vectorizer