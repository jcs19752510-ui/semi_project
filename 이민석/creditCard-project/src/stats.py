import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from statsmodels.stats.outliers_influence import variance_inflation_factor

def perform_mann_whitney_u(df: pd.DataFrame, feature_cols: list, target_col: str = 'Class'):
    """05단계: 사기 거래 여부에 따른 변수 간 Mann-Whitney U 검정 수행"""
    results = []
    class_0 = df[df[target_col] == 0]
    class_1 = df[df[target_col] == 1]
    
    for col in feature_cols:
        stat, p_val = mannwhitneyu(class_0[col], class_1[col], alternative='two-sided')
        results.append({
            'Feature': col,
            'Statistic': stat,
            'p_value': p_val
        })
    
    return pd.DataFrame(results)

def calculate_vif(X: pd.DataFrame) -> pd.DataFrame:
    """06단계: 다중공선성 측정을 위한 VIF 계산"""
    vif_data = pd.DataFrame()
    vif_data["Feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    return vif_data.sort_values(by="VIF", ascending=False)