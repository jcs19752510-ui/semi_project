import pandas as pd
import numpy as np
from scipy import stats

def get_cluster_keywords(X_dense, labels, vectorizer, top_n=5):
    df_temp = pd.DataFrame(X_dense)
    df_temp['cluster'] = labels
    cluster_means = df_temp.groupby('cluster').mean()
    feature_names = np.array(vectorizer.get_feature_names_out())
    
    keywords = {}
    for cluster_id, row in cluster_means.iterrows():
        top_indices = row.argsort()[::-1][:top_n]
        keywords[cluster_id] = feature_names[top_indices].tolist()
    return keywords

def perform_statistical_validation(df: pd.DataFrame, target_col='review_len'):
    clusters = df['cluster'].unique()
    group_data = [df[df['cluster'] == c][target_col].values for c in sorted(clusters)]
    
    # 정규성 검정
    _, p_shapiro = stats.shapiro(df[target_col].sample(min(len(df), 1000), random_state=42))
    
    print(f"\n[통계적 검증: 군집별 {target_col} 분포 비교]")
    if p_shapiro > 0.05:
        stat_val, p_val = stats.f_oneway(*group_data)
        print(" - 적용 검정법: One-way ANOVA")
    else:
        stat_val, p_val = stats.kruskal(*group_data)
        print(" - 적용 검정법: Kruskal-Wallis H-test")
        
    print(f" - 검정 통계량: {stat_val:.4f} | P-value: {p_val:.4e}")
    if p_val < 0.05:
        print(" => 결론: 군집 간 특성에 통계적으로 유의미한 차이가 존재합니다.")
    else:
        print(" => 결론: 군집 간 특성 차이가 통계적으로 유의미하지 않습니다.")