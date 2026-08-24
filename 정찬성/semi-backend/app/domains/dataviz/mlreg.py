"""마켓 가격 예측(업무명=04. 마켓 가격 예측) 도메인 — 회귀 모델 학습/평가.

근거 노트북: 정찬성/ipynb/src/10 캐글 mercari price_정제후.ipynb (Kaggle Mercari Price
Suggestion Challenge)
원본 흐름:
  1) name(상품명)은 CountVectorizer, item_description(상품설명)은 TfidfVectorizer로 벡터화
  2) brand_name/item_condition_id/shipping/cat_dae/cat_jung/cat_so(대/중/소분류)는
     LabelBinarizer로 원-핫 인코딩 후 전부 hstack으로 결합한 sparse 피처 행렬 구성
  3) price는 log1p로 정규화해 학습하고, 평가할 때는 expm1로 원복해 RMSLE(Root Mean
     Squared Logarithmic Error)로 채점
  4) Ridge(선형회귀)와 LightGBM 두 모델을 비교

이 모듈은 위 흐름을 그대로 따르되, Ridge/LightGBM 두 종류가 아니라 registry의 5종
회귀기 카탈로그(선형회귀(Ridge)/LightGBM/XGBoost/랜덤포레스트/GradientBoost) 전부를
평가할 수 있게 일반화했다.

santander/credit_card(이진 분류)·doc_clustering(다중클래스 분류)과 달리 이 업무는
회귀(연속값)라 ROC/AUC 개념 자체가 없다 — 모델 수행결과는 "실제값 vs 예측값 산점도" +
RMSLE로 표현한다(§schemas.RegressionCurve).

주요 설계 결정:
- 원본 노트북은 TfidfVectorizer(max_features=50000)·전체 1,482,535행을 오프라인
  노트북에서 한 번만 학습했지만, 이 화면은 요청마다 5종 모델 중 선택된 것을 실시간
  학습해야 한다. 응답 지연을 감당할 수 있는 수준으로 (a) 배포용 표본을 80,000행으로
  줄이고(§config.mercari_tsv_path), (b) 그중에서도 실제 학습에는 MAX_TRAIN_ROWS(20,000)행만
  사용하며, (c) TF-IDF/CountVectorizer의 max_features를 50,000→5,000으로 낮췄다.
  (검증 스크립트 실측: 20,000행·11,719차원 기준 모델당 0.2~14.5초, 전체 5종 합산 약 51초 —
  신용카드 업무의 model=all 5종 학습(§작업이력 §8-7, 약 60초)과 같은 수준으로 맞춘 절충이다.)
- 원본 노트북의 `zip(*apply(split_cat))`는 category_name의 계층 깊이가 데이터셋 전체에서
  전부 3단계일 때만 안전하다(zip은 가장 짧은 행 기준으로 전체를 잘라낸다 — 단 한 행이라도
  2단계 이하면 전체 행의 중/소분류가 밀려서 오염된다). 실측 결과 실제 표본에 4~5단계
  category_name이 존재해(§내부테스트 결과서), 행 단위로 독립적으로 앞 3단계만 취하고
  모자란 단계는 'Other_Null'로 채우는 방식으로 더 안전하게 재구현했다.
"""

from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from xgboost import XGBRegressor

try:
    from lightgbm import LGBMRegressor
except ImportError:  # pragma: no cover — ml.py도 동일 전제(lightgbm은 필수 의존성)
    LGBMRegressor = None

MODEL_LABELS = {
    "logistic_regression": "선형회귀(Ridge)",
    "lightgbm": "LightGBM",
    "xgboost": "XGBoost",
    "random_forest": "랜덤포레스트",
    "gradient_boost": "GradientBoost",
}

# 텍스트 피처 차원 상한(원본 노트북 50,000 → 응답속도 우선으로 축소, 모듈 docstring 참고).
TEXT_MAX_FEATURES = 5_000

# 실시간 학습 상한. mercari_sample.tsv(80,000행) 중 이 행수만큼만 추려 피처를 만든다.
MAX_TRAIN_ROWS = 20_000

# 프론트 산점도 렌더링 부담을 줄이기 위한 다운샘플링 포인트 수(ml.CURVE_POINTS와 별개 상수 —
# 산점도는 ROC 곡선보다 점이 많아도 부담이 적어 넉넉히 잡았다).
SCATTER_POINTS = 300


def _split_category(category_name) -> tuple[str, str, str]:
    if not isinstance(category_name, str):
        return "Other_Null", "Other_Null", "Other_Null"
    parts = category_name.split("/")
    parts = (parts + ["Other_Null"] * 3)[:3]
    return parts[0], parts[1], parts[2]


def _build_features(df: pd.DataFrame) -> tuple[csr_matrix, np.ndarray, np.ndarray]:
    """반환: (X 희소행렬, y_log(log1p(price)), y_original(price 원본 — RMSLE/R² 계산용))"""
    sample = df.sample(n=min(MAX_TRAIN_ROWS, len(df)), random_state=42).reset_index(drop=True)

    sample["brand_name"] = sample["brand_name"].fillna("Other_Null")
    sample["item_description"] = sample["item_description"].fillna("Other_Null")
    cat_parts = sample["category_name"].apply(_split_category)
    sample["cat_dae"] = cat_parts.apply(lambda t: t[0])
    sample["cat_jung"] = cat_parts.apply(lambda t: t[1])
    sample["cat_so"] = cat_parts.apply(lambda t: t[2])

    cnt_vec = CountVectorizer(max_features=TEXT_MAX_FEATURES)
    X_name = cnt_vec.fit_transform(sample["name"])

    tfidf_descp = TfidfVectorizer(max_features=TEXT_MAX_FEATURES, ngram_range=(1, 2), stop_words="english")
    X_descp = tfidf_descp.fit_transform(sample["item_description"])

    lb_brand = LabelBinarizer(sparse_output=True)
    X_brand = lb_brand.fit_transform(sample["brand_name"])
    lb_cond = LabelBinarizer(sparse_output=True)
    X_cond = lb_cond.fit_transform(sample["item_condition_id"])
    lb_ship = LabelBinarizer(sparse_output=True)
    X_ship = lb_ship.fit_transform(sample["shipping"])
    lb_dae = LabelBinarizer(sparse_output=True)
    X_dae = lb_dae.fit_transform(sample["cat_dae"])
    lb_jung = LabelBinarizer(sparse_output=True)
    X_jung = lb_jung.fit_transform(sample["cat_jung"])
    lb_so = LabelBinarizer(sparse_output=True)
    X_so = lb_so.fit_transform(sample["cat_so"])

    X = hstack((X_name, X_descp, X_brand, X_cond, X_ship, X_dae, X_jung, X_so)).tocsr()
    y_original = sample["price"].to_numpy(dtype=float)
    y_log = np.log1p(y_original)
    return X, y_log, y_original


# _build_features는 DataFrame(unhashable)을 받아 lru_cache를 직접 못 쓴다 — ml.py/docclustering.py와
# 동일하게 (데이터 객체 id) 키의 수동 캐시를 쓴다.
_feature_cache: dict[int, tuple[csr_matrix, np.ndarray, np.ndarray]] = {}


def _get_features(df: pd.DataFrame) -> tuple[csr_matrix, np.ndarray, np.ndarray]:
    key = id(df)
    if key not in _feature_cache:
        _feature_cache[key] = _build_features(df)
    return _feature_cache[key]


def _build_regressor(model: str):
    if model == "logistic_regression":
        # 원본 노트북과 동일 설정(Ridge, solver="lsqr", fit_intercept=False).
        return Ridge(solver="lsqr", fit_intercept=False, random_state=42)
    if model == "lightgbm":
        if LGBMRegressor is None:  # pragma: no cover
            raise RuntimeError("lightgbm이 설치되어 있지 않습니다")
        return LGBMRegressor(n_estimators=200, learning_rate=0.1, num_leaves=63, random_state=42, verbosity=-1)
    if model == "xgboost":
        return XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1)
    if model == "random_forest":
        return RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    if model == "gradient_boost":
        return GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
    raise ValueError(f"지원하지 않는 모델입니다: {model}")


def _rmsle(y_true_original: np.ndarray, y_pred_original: np.ndarray) -> float:
    # underflow/overflow 방지를 위해 log가 아닌 log1p로 RMSLE 계산(원본 노트북과 동일 정의).
    y_pred_clipped = np.clip(y_pred_original, a_min=0.0, a_max=None)
    return float(np.sqrt(np.mean((np.log1p(y_true_original) - np.log1p(y_pred_clipped)) ** 2)))


def _train_and_evaluate(df: pd.DataFrame, model: str) -> dict:
    X, y_log, y_original = _get_features(df)
    X_train, X_test, y_log_train, y_log_test, _y_orig_train, y_orig_test = train_test_split(
        X, y_log, y_original, test_size=0.2, random_state=42
    )

    reg = _build_regressor(model)
    reg.fit(X_train, y_log_train)
    pred_log = reg.predict(X_test)
    pred_original = np.clip(np.expm1(pred_log), a_min=0.0, a_max=None)

    rmsle = _rmsle(y_orig_test, pred_original)
    r2 = float(r2_score(y_orig_test, pred_original))

    actual_ds, predicted_ds = _downsample_scatter(y_orig_test, pred_original, SCATTER_POINTS)
    return {
        "model": model,
        "label": MODEL_LABELS.get(model, model),
        "rmsle": round(rmsle, 4),
        "r2": round(r2, 4),
        "actual": [round(v, 2) for v in actual_ds],
        "predicted": [round(v, 2) for v in predicted_ds],
    }


def _downsample_scatter(actual: np.ndarray, predicted: np.ndarray, points: int) -> tuple[list[float], list[float]]:
    if len(actual) <= points:
        return actual.tolist(), predicted.tolist()
    idx = np.linspace(0, len(actual) - 1, points).astype(int)
    return actual[idx].tolist(), predicted[idx].tolist()


# ml.compute_roc_curve/docclustering.compute_model_result와 동일한 수동 캐시 패턴.
_result_cache: dict[tuple[int, str], dict] = {}


def compute_regression_result(df: pd.DataFrame, model: str) -> dict:
    key = (id(df), model)
    if key not in _result_cache:
        _result_cache[key] = _train_and_evaluate(df, model)
    return _result_cache[key]
