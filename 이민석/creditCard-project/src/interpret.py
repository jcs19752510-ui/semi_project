import pandas as pd
import shap

def get_feature_importance(model, feature_names):
    """14단계: 트리 기반 모델의 Feature Importance 추출"""
    if hasattr(model, "feature_importances_"):
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=False)
        return importance_df
    return None

def compute_shap_values(model, X_sample):
    """14단계: SHAP Value 계산"""
    explainer = shap.Explainer(model, X_sample)
    shap_values = explainer(X_sample)
    return explainer, shap_values