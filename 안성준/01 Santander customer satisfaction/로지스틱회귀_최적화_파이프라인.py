"""
Santander Customer Satisfaction - 로지스틱 회귀 최종 파이프라인 (2026-08-20 재작업)

목표: recall(class 1) >= 0.80, roc_auc >= 0.83.

이전 버전(PCA + Hyperopt로 penalty/C/class_weight 탐색)은 병렬로 다시 검증한 결과
불필요한 것으로 확인되어 제거했다:
  - PCA 차원축소: 채택된 적 없음 (탐색에서 매번 기각됨)
  - Hyperopt(L1/L2, C, class_weight) 탐색: 홀드아웃 성능이 단순
    class_weight='balanced' 기본값보다 오히려 낮았음(auc 0.8107 vs 0.8116).
    트라이얼당 최대 30분씩 걸릴 정도로 비용도 컸음.
  - 추가 피처 엔지니어링(num_var4 구간화, var15*var38 상호작용,
    var38 분위수변환, PCA 성분 추가), 행 단위 집계 피처(n_zeros 등),
    상관관계 가지치기: 전부 roc_auc 변화가 ±0.0002 이내로 노이즈 수준.

대신 이번에 새로 들어간 것: recall 목표를 맞추기 위한 분류 임계값(threshold) 튜닝.
roc_auc는 threshold와 무관하지만 recall은 threshold에 크게 좌우되므로,
학습 데이터 내부에서 val split을 따로 떼어 recall>=0.80을 만족하는 가장 높은
threshold를 고르고, 그 값을 테스트셋에 적용한다(테스트셋 누수 방지).

실행: python "로지스틱회귀_최적화_파이프라인.py"

2026-08-20 실행 결과(145개 피처):
  - threshold 0.50: accuracy 0.7459, roc_auc 0.8116, recall 0.7359, precision 0.1068
  - threshold 0.40: accuracy 0.6190, roc_auc 0.8116, recall 0.8239, precision 0.0802
  -> recall 목표(>=0.80) 달성, roc_auc 목표(>=0.83)는 미달성(약 0.018 부족 -
     선형 모델의 사실상 성능 한계로 보임, 넘기려면 비선형 모델 필요).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "santander-customer-satisfaction" / "train.csv"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    df["var3"] = df["var3"].replace(-999999, 2)
    return df


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """검증된 1~5단계 전처리만 적용 (369 -> 145개 피처)."""
    y = df["TARGET"]
    X = df.drop(columns=["ID", "TARGET"])

    dup_cols = X.columns[X.T.duplicated()].tolist()
    X = X.drop(columns=dup_cols)

    stds = X.std()
    X = X.drop(columns=stds[stds == 0].index.tolist())

    num_rows = X.shape[0]
    sparse_cols = [c for c in X.columns if (X[c] == 0).sum() / num_rows >= 0.99]
    X = X.drop(columns=sparse_cols)

    X["var38"] = np.log1p(X["var38"])
    X["var15_below_23"] = (X["var15"] < 23).astype(int)
    X["var15_bin"] = pd.cut(X["var15"], bins=5, labels=False).astype(int)

    return X, y


def build_model() -> LogisticRegression:
    return LogisticRegression(
        class_weight="balanced", C=1.0, penalty="l2",
        solver="liblinear", max_iter=3000, random_state=RANDOM_STATE,
    )


def evaluate(y_true, y_pred, y_proba, label: str) -> dict:
    metrics = {
        "label": label,
        "accuracy": accuracy_score(y_true, y_pred),
        "roc_auc": roc_auc_score(y_true, y_proba),
        "recall": recall_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
    }
    print(f"[{label}] accuracy={metrics['accuracy']:.4f}  roc_auc={metrics['roc_auc']:.4f}  "
          f"recall={metrics['recall']:.4f}  precision={metrics['precision']:.4f}")
    return metrics


def find_threshold(y_val, val_proba, target_recall: float = 0.80) -> float:
    for t in np.arange(0.50, 0.03, -0.01):
        pred = (val_proba >= t).astype(int)
        if recall_score(y_val, pred) >= target_recall:
            return round(float(t), 2)
    return 0.03


def main():
    print("=" * 70)
    print("1. 데이터 로드 및 전처리")
    df = load_data()
    X, y = preprocess(df)
    print(f"최종 피처 수: {X.shape[1]}")

    print("=" * 70)
    print("2. Train/Test 분리 (stratify)")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_s = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    print("=" * 70)
    print("3. 모델 학습 (class_weight='balanced', C=1.0, l2)")
    clf = build_model()
    clf.fit(X_train_s, y_train)
    test_proba = clf.predict_proba(X_test_s)[:, 1]
    test_pred_05 = clf.predict(X_test_s)
    evaluate(y_test, test_pred_05, test_proba, "threshold=0.50 (before)")

    print("=" * 70)
    print("4. 임계값(threshold) 튜닝 - 내부 검증셋에서 recall>=0.80 만족하는 threshold 탐색")
    X_tr2, X_val, y_tr2, y_val = train_test_split(
        X_train, y_train, test_size=0.25, random_state=RANDOM_STATE, stratify=y_train
    )
    scaler_val = StandardScaler()
    X_tr2_s = pd.DataFrame(scaler_val.fit_transform(X_tr2), columns=X_tr2.columns)
    X_val_s = pd.DataFrame(scaler_val.transform(X_val), columns=X_val.columns)

    clf_val = build_model()
    clf_val.fit(X_tr2_s, y_tr2)
    val_proba = clf_val.predict_proba(X_val_s)[:, 1]

    threshold = find_threshold(y_val, val_proba, target_recall=0.80)
    print(f"선택된 threshold: {threshold:.2f}")

    test_pred_tuned = (test_proba >= threshold).astype(int)
    evaluate(y_test, test_pred_tuned, test_proba, f"threshold={threshold:.2f} (after)")


if __name__ == "__main__":
    main()
