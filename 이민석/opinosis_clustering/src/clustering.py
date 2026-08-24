import numpy as np
from sklearn.mixture import GaussianMixture

def find_optimal_gmm_bic(X, min_k=2, max_k=10, random_state=42):
    """BIC(Bayesian Information Criterion)를 이용한 최적 컴포넌트 수 탐색"""
    n_components_range = range(min_k, max_k + 1)
    bics = []

    for n in n_components_range:
        gmm = GaussianMixture(n_components=n, random_state=random_state)
        gmm.fit(X)
        bics.append(gmm.bic(X))

    best_n = n_components_range[np.argmin(bics)]
    print(f"[GMM] BIC 기준 최적 군집 수(K): {best_n}")
    return best_n, bics

def fit_gmm(X, n_components, random_state=42):
    """최적 컴포넌트 수로 GMM 학습 및 소프트 클러스터링 확률 반환"""
    gmm = GaussianMixture(n_components=n_components, random_state=random_state)
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)
    return gmm, labels, probs