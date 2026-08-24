import os
from src.data_loader import load_opinosis_data
from src.preprocessing import preprocess_dataframe
from src.vectorizer import get_tfidf_matrix
from src.reducer import apply_pca
from src.clustering import find_optimal_gmm_bic, fit_gmm
from src.evaluator import get_cluster_keywords, perform_statistical_validation
from src.visualizer import plot_gmm_clusters

def main():
    # 본인의 데이터 raw 폴더 경로로 설정
    data_path = r'C:\big21\ml-dev\opinosis_clustering\data\raw'
    
    if not os.path.exists(data_path):
        # 만약 data/raw에 없다면 이전 경로 예시로 대체 체크
        data_path = r'C:\big21\ml-dev\data\topics'
        if not os.path.exists(data_path):
            print(f"데이터 경로를 찾을 수 없습니다. data/raw 폴더에 .data 파일들을 넣어주세요.")
            return

    print("=== [1/6] 데이터 로드 중 ===")
    raw_df = load_opinosis_data(data_path)
    print(f"로드된 전체 리뷰 수: {len(raw_df)}")

    print("=== [2/6] 데이터 전처리 중 ===")
    processed_df = preprocess_dataframe(raw_df)
    
    print("=== [3/6] TF-IDF 벡터화 중 ===")
    tfidf_matrix, vectorizer = get_tfidf_matrix(processed_df['cleaned_review'], max_features=1000)
    
    print("=== [4/6] PCA 차원 축소 중 (누적 분산 90%) ===")
    X_dense = tfidf_matrix.toarray()
    X_reduced, pca_model = apply_pca(X_dense, variance_ratio=0.90)
    print(f"축소 전 차원: {X_dense.shape[1]} -> 축소 후 차원: {X_reduced.shape[1]}")

    print("=== [5/6] GMM 클러스터링 및 BIC 최적화 ===")
    best_k, _ = find_optimal_gmm_bic(X_reduced, min_k=2, max_k=8)
    gmm_model, labels, probs = fit_gmm(X_reduced, n_components=best_k)
    processed_df['cluster'] = labels
    
    print("=== [6/6] 군집 프로파일링, 통계 검정 및 시각화 ===")
    keywords = get_cluster_keywords(X_dense, labels, vectorizer, top_n=5)
    for cid, kw in keywords.items():
        print(f"  - Cluster {cid} Keywords: {kw}")

    perform_statistical_validation(processed_df, target_col='review_len')
    plot_gmm_clusters(X_reduced, labels, gmm_model, save_path="outputs/figures/gmm_clusters.png")

    print("\n🎉 파이프라인 분석이 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    main()