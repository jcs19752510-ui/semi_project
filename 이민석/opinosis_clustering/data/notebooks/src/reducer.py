from sklearn.decomposition import PCA

def apply_pca(X, variance_ratio=0.90, random_state=42):
    """누적 분산 비율을 만족하는 PCA 차원 축소 수행"""
    pca = PCA(n_components=variance_ratio, random_state=random_state)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca