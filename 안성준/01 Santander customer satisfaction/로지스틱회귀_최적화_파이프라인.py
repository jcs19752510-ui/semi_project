"""
Santander Customer Satisfaction - 로지스틱 회귀 성능 최적화 파이프라인

데이터 로드부터 전처리, StandardScaler, PCA 차원축소, L1/L2 정규화,
class_weight 조정, Hyperopt 기반 하이퍼파라미터 튜닝까지 전체 과정을
노트북이 아닌 스크립트로 재구성했다. (노트북에서 셀을 순서 없이 재실행하며
X_features를 inplace로 계속 덮어써 상태가 꼬였던 문제를 피하기 위해,
매 실행마다 원본 CSV부터 새로 읽어 동일한 전처리 함수만 통과시킨다.)

실행: python "로지스틱회귀_최적화_파이프라인.py" [--max-evals 30]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from hyperopt import STATUS_OK, Trials, fmin, hp, space_eval, tpe
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "santander-customer-satisfaction" / "train.csv"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    # var3의 -999999는 결측 표기로 알려져 있음 -> 최빈값(2)으로 대체
    df["var3"] = df["var3"].replace(-999999, 2)
    return df


def remove_duplicate_columns(X: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    dup_mask = X.T.duplicated()
    dup_cols = X.columns[dup_mask].tolist()
    return X.drop(columns=dup_cols), dup_cols


def remove_zero_variance_columns(X: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    stds = X.std()
    zero_var_cols = stds[stds == 0].index.tolist()
    return X.drop(columns=zero_var_cols), zero_var_cols


def remove_sparse_columns(X: pd.DataFrame, threshold: float = 0.99) -> tuple[pd.DataFrame, list[str]]:
    num_rows = X.shape[0]
    sparse_cols = [c for c in X.columns if (X[c] == 0).sum() / num_rows >= threshold]
    return X.drop(columns=sparse_cols), sparse_cols


def engineer_features(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    # 대출금액(var38) 우편향 완화
    X["var38"] = np.log1p(X["var38"])
    # 나이 관련 변수(var15) 피처 엔지니어링
    X["var15_below_23"] = (X["var15"] < 23).astype(int)
    X["var15_bin"] = pd.cut(X["var15"], bins=5, labels=False).astype(int)
    return X


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    y = df["TARGET"]
    X = df.drop(columns=["ID", "TARGET"])

    X, dup_removed = remove_duplicate_columns(X)
    X, zero_var_removed = remove_zero_variance_columns(X)
    X, sparse_removed = remove_sparse_columns(X)
    X = engineer_features(X)

    print(f"[전처리] 중복 컬럼 제거: {len(dup_removed)}개")
    print(f"[전처리] 분산 0 컬럼 제거: {len(zero_var_removed)}개")
    print(f"[전처리] 희소(>=99% 0) 컬럼 제거: {len(sparse_removed)}개")
    print(f"[전처리] 최종 피처 수: {X.shape[1]}")

    return X, y


def resolve_class_weight(params: dict):
    mode = params["class_weight_mode"]
    if mode == "none":
        return None
    if mode == "balanced":
        return "balanced"
    return {0: 1.0, 1: params["class_weight_1"]}


def build_pipeline(params: dict) -> Pipeline:
    steps = [("scaler", StandardScaler())]

    if params["use_pca"]:
        steps.append(("pca", PCA(n_components=params["pca_n_components"], random_state=RANDOM_STATE)))

    steps.append(
        (
            "clf",
            LogisticRegression(
                penalty=params["penalty"],
                C=params["C"],
                class_weight=resolve_class_weight(params),
                solver="liblinear",  # l1/l2 둘 다 지원, 이진분류에 적합
                max_iter=3000,
                random_state=RANDOM_STATE,
            ),
        )
    )
    return Pipeline(steps)


def objective(params: dict, X_train: pd.DataFrame, y_train: pd.Series, cv: StratifiedKFold) -> dict:
    pipe = build_pipeline(params)
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
    return {"loss": -scores.mean(), "status": STATUS_OK}


def run_hyperopt(X_train: pd.DataFrame, y_train: pd.Series, max_evals: int):
    space = {
        "penalty": hp.choice("penalty", ["l1", "l2"]),
        "C": hp.loguniform("C", np.log(1e-3), np.log(10)),
        "class_weight_mode": hp.choice("class_weight_mode", ["none", "balanced", "custom"]),
        "class_weight_1": hp.uniform("class_weight_1", 1.0, 30.0),
        "use_pca": hp.choice("use_pca", [False, True]),
        "pca_n_components": hp.uniform("pca_n_components", 0.80, 0.99),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    trials = Trials()

    best = fmin(
        fn=lambda params: objective(params, X_train, y_train, cv),
        space=space,
        algo=tpe.suggest,
        max_evals=max_evals,
        trials=trials,
        rstate=np.random.default_rng(RANDOM_STATE),
    )
    best_params = space_eval(space, best)
    best_cv_auc = -min(trials.losses())
    return best_params, best_cv_auc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-evals", type=int, default=30, help="Hyperopt 탐색 횟수 (기본 30)")
    parser.add_argument("--test-size", type=float, default=0.2, help="테스트 비율 (기본 0.2)")
    args = parser.parse_args()

    print("=" * 70)
    print("1. 데이터 로드")
    df = load_data()
    print(f"원본 shape: {df.shape}")
    print(f"TARGET 분포:\n{df['TARGET'].value_counts(normalize=True)}")

    print("=" * 70)
    print("2. 전처리")
    X, y = preprocess(df)

    print("=" * 70)
    print("3. Train/Test Split (stratify)")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=RANDOM_STATE, stratify=y
    )
    print(f"train: {X_train.shape}, test: {X_test.shape}")

    print("=" * 70)
    print(f"4. Hyperopt 하이퍼파라미터 튜닝 (5-fold CV roc_auc, max_evals={args.max_evals})")
    print("   탐색 대상: penalty(l1/l2), C, class_weight, PCA 사용여부/설명분산비")
    best_params, best_cv_auc, _trials = run_hyperopt(X_train, y_train, args.max_evals)
    print(f"최적 CV roc_auc: {best_cv_auc:.4f}")
    print(f"최적 파라미터:")
    for k, v in best_params.items():
        print(f"  - {k}: {v}")

    print("=" * 70)
    print("5. 최적 파라미터로 최종 모델 학습 및 홀드아웃 평가")
    final_pipe = build_pipeline(best_params)
    final_pipe.fit(X_train, y_train)

    y_pred = final_pipe.predict(X_test)
    y_proba = final_pipe.predict_proba(X_test)[:, 1]

    print(f"accuracy      : {accuracy_score(y_test, y_pred):.4f}")
    print(f"roc_auc       : {roc_auc_score(y_test, y_proba):.4f}")
    print(f"recall(class1): {recall_score(y_test, y_pred):.4f}")
    print()
    print(classification_report(y_test, y_pred, digits=4))


if __name__ == "__main__":
    main()
