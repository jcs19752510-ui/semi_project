import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# v2(업무/모델 선택형, TRD 99-02) 대시보드는 업무별로 이미 좁혀둔 피처만 사용한다
# (대시보드 화면이 로드하는 컬럼 스코프와 모델 입력 스코프를 일치시켜, 대시보드에 없는
# 컬럼을 모델만 몰래 참조하는 불일치를 방지한다).
# - santander: crud.USE_COLUMNS 4개 피처(캐글산탄데르.ipynb 원본 EDA에서 실제로 다룬 컬럼)
# - credit_card: V1~V28(PCA 익명화 피처) + Amount. Time은 거래 순번일 뿐 사기 여부와
#   직접적 인과가 없어 원본 노트북(10 신용카드 사기검출_XGBoost_정제후.ipynb 1단계)과
#   동일하게 피처에서 제외하고 전처리조회 차트(bin1)에서만 참고용으로 쓴다.
FEATURE_COLUMNS: dict[str, list[str]] = {
    "santander": ["var3", "var15", "var38", "saldo_var30"],
    "credit_card": [f"V{i}" for i in range(1, 29)] + ["Amount"],
}

TARGET_COLUMNS: dict[str, str] = {
    "santander": "TARGET",
    "credit_card": "Class",
}

MODEL_LABELS = {
    "logistic_regression": "로지스틱 회귀",
    "lightgbm": "LightGBM",
    "xgboost": "XGBoost",
    "random_forest": "랜덤포레스트",
    "gradient_boost": "GradientBoost",
}

# ROC 곡선 프론트 렌더링 부담을 줄이기 위한 다운샘플링 포인트 수.
CURVE_POINTS = 100

# 신용카드 업무는 284,807행으로 산탄데르(76,020행)보다 훨씬 커서, 학습이 느린
# GradientBoostingClassifier(sklearn, 트리 단위 순차 학습이라 n_jobs 병렬화가 안 됨) 기준으로
# 요청당 학습 시간이 과도해질 수 있다. 산탄데르 76,020행은 이 상한보다 작아 영향이 없고
# (기존에 실측·문서화된 AUC 0.8264 등 산탄데르 결과값은 그대로 유지된다), 상한을 넘는
# 업무만 계층화(stratify) 표본추출로 학습 시간을 통제한다.
MAX_TRAIN_ROWS = 80_000


def _build_classifier(model: str):
    if model == "logistic_regression":
        return LogisticRegression(max_iter=1000, random_state=42)
    if model == "lightgbm":
        return LGBMClassifier(
            n_estimators=200,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbosity=-1,
        )
    if model == "xgboost":
        return XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        )
    if model == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            random_state=42,
            n_jobs=-1,
        )
    if model == "gradient_boost":
        # sklearn GradientBoostingClassifier는 병렬화가 안 돼 다른 4종보다 느리므로
        # n_estimators를 100으로 낮춰(다른 모델의 1/2~1/3) 응답 시간을 다른 모델과 비슷하게 맞춘다.
        return GradientBoostingClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
        )
    raise ValueError(f"지원하지 않는 모델입니다: {model}")


def _downsample(fpr: np.ndarray, tpr: np.ndarray, points: int) -> tuple[list[float], list[float]]:
    if len(fpr) <= points:
        return fpr.tolist(), tpr.tolist()
    idx = np.linspace(0, len(fpr) - 1, points).astype(int)
    return fpr[idx].tolist(), tpr[idx].tolist()


def _maybe_downsample_for_training(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    if len(X) <= MAX_TRAIN_ROWS or y.value_counts().min() < 2:
        return X, y
    X_sampled, _, y_sampled, _ = train_test_split(
        X, y, train_size=MAX_TRAIN_ROWS, random_state=42, stratify=y
    )
    return X_sampled, y_sampled


def _train_and_evaluate(df: pd.DataFrame, task: str, model: str) -> dict:
    feature_columns = FEATURE_COLUMNS[task]
    target_col = TARGET_COLUMNS[task]

    X = df[feature_columns].fillna(df[feature_columns].median(numeric_only=True))
    y = df[target_col]
    X, y = _maybe_downsample_for_training(X, y)

    # 실제 데이터는 정상적으로 홀드아웃 검증한다. 단위테스트의 소표본처럼
    # 클래스별 최소 표본 수를 못 채우면 stratify가 불가능하므로 전량을 학습/평가에
    # 함께 써서 "실행은 되지만 신뢰도는 낮은" AUC를 낸다 — §0-1-8 스코프상
    # 소표본 자체 계층화 샘플링 로직 도입은 하지 않는다.
    can_holdout = len(X) >= 20 and y.nunique() > 1 and y.value_counts().min() >= 2
    if can_holdout:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    if y_train.nunique() < 2:
        # 학습 데이터에 클래스가 하나뿐이면 학습 자체가 불가능하므로 임의 확률(0.5)로 대체한다.
        proba = np.full(len(X_test), 0.5)
    else:
        clf = _build_classifier(model)
        clf.fit(X_train, y_train)
        proba = clf.predict_proba(X_test)[:, 1]

    if y_test.nunique() < 2:
        auc = 0.5
        fpr, tpr = np.array([0.0, 1.0]), np.array([0.0, 1.0])
    else:
        auc = float(roc_auc_score(y_test, proba))
        fpr, tpr, _ = roc_curve(y_test, proba)

    fpr_list, tpr_list = _downsample(fpr, tpr, CURVE_POINTS)
    return {
        "model": model,
        "label": MODEL_LABELS.get(model, model),
        "auc": round(auc, 4),
        "fpr": [round(v, 4) for v in fpr_list],
        "tpr": [round(v, 4) for v in tpr_list],
    }


# §0-1-8 [기본값]: 사전 계산된 결과를 캐싱해서 반환하고, 요청마다 재학습하지 않는다.
# functools.lru_cache는 DataFrame(unhashable)을 키로 못 쓰므로, (데이터 객체 id, task, model)
# 조합을 키로 하는 수동 캐시를 쓴다 — crud.load_dataframe()이 이미 lru_cache로 프로세스
# 생애주기 동안 동일 DataFrame 객체를 반환하므로 운영에서는 (task, model)당 1회만 계산된다.
# (테스트에서는 매 테스트마다 새 표본 DataFrame 객체를 주입하므로 id()가 달라져
#  테스트 간 캐시 오염도 함께 방지된다.)
_cache: dict[tuple[int, str, str], dict] = {}


def compute_roc_curve(df: pd.DataFrame, task: str, model: str) -> dict:
    key = (id(df), task, model)
    if key not in _cache:
        _cache[key] = _train_and_evaluate(df, task, model)
    return _cache[key]
