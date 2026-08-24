import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score, 
    f1_score, roc_auc_score, average_precision_score, precision_recall_curve
)

def evaluate_model(model, X_test, y_test, threshold=0.5):
    """12단계: 주요 평가 지표 산출"""
    # 확률 예측값 추출 가능 여부에 따른 분기
    if hasattr(model, "predict_proba"):
        y_probs = model.predict_proba(X_test)[:, 1]
        y_pred = (y_probs >= threshold).astype(int)
    else:
        y_pred = model.predict(X_test)
        y_probs = None

    metrics = {
        "Confusion Matrix": confusion_matrix(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1-score": f1_score(y_test, y_pred, zero_division=0),
    }
    
    if y_probs is not None:
        metrics["ROC-AUC"] = roc_auc_score(y_test, y_probs)
        metrics["PR-AUC"] = average_precision_score(y_test, y_probs)
        
    return metrics, y_probs

def optimize_threshold(y_true, y_probs):
    """13단계: F1-score 기준 최적 Threshold 탐색"""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    best_f1 = f1_scores[best_idx]
    
    return best_threshold, best_f1