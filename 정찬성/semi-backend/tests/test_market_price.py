import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.domains.dataviz import crud, mlreg
from app.main import app

MODEL_IDS = {"logistic_regression", "lightgbm", "xgboost", "random_forest", "gradient_boost"}


def _build_sample_dataframe(rows: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    names = [f"item name {i} great deal" for i in range(rows)]
    descriptions = [f"this is a description for product {i} in good condition" for i in range(rows)]
    categories = [
        "Men/Tops/T-shirts",
        "Electronics/Computers & Tablets/Laptops",
        "Women/Dresses/Above Knee",
    ]
    brands = ["Nike", "Apple", None, "Zara"]
    return pd.DataFrame(
        {
            "train_id": range(rows),
            "name": names,
            "item_condition_id": rng.integers(1, 6, size=rows),
            "category_name": [categories[i % len(categories)] for i in range(rows)],
            "brand_name": [brands[i % len(brands)] for i in range(rows)],
            "price": rng.uniform(5, 200, size=rows).round(2),
            "shipping": rng.integers(0, 2, size=rows),
            "item_description": descriptions,
        }
    )


@pytest.fixture(autouse=True)
def sample_mercari_dataframe(monkeypatch: pytest.MonkeyPatch):
    df = _build_sample_dataframe()
    monkeypatch.setattr(crud, "get_mercari_dataframe", lambda: df)
    mlreg._feature_cache.clear()
    mlreg._result_cache.clear()
    yield df


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_models_market_price_regression_catalog(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "market_price"})
    assert res.status_code == 200
    body = res.json()
    assert {m["id"] for m in body} == MODEL_IDS
    assert {"id": "logistic_regression", "label": "선형회귀(Ridge)"} in body


# TC-MP-01 — market_price는 shipping(0/1)이 실제 이진 컬럼이라 기존 이진 전처리검증
# 파이프라인(PreprocessCheckResponse)을 그대로 재사용한다(§crud.DOMAIN_CHARTS).
def test_preprocess_check_reuses_binary_schema(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "market_price", "model": "all"})
    assert res.status_code == 200
    body = res.json()

    dist = body["target_distribution"]
    assert dist["satisfied"] + dist["unsatisfied"] == 60
    assert body["labels"] == {
        "negative": "배송비 구매자부담(0)",
        "positive": "무료배송·판매자부담(1)",
        "bin1_title": "가격 구간별 무료배송 비율",
        "bin2_title": "상품상태 구간별 무료배송 비율",
        "box_title": "가격(원본, $) 배송비 부담별 비교",
    }


def test_preprocess_check_value_boxplot_five_number_summary(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "market_price", "model": "all"})
    assert res.status_code == 200
    box = res.json()["value_boxplot"]
    for group in ("satisfied", "unsatisfied"):
        summary = box[group]
        assert summary["min"] <= summary["q1"] <= summary["median"] <= summary["q3"] <= summary["max"]


# TC-MP-02 — AC-MP-01: 회귀 모델 수행결과는 ROC가 아니라 RMSLE + 실제/예측 산점도.
def test_model_result_single_model_regression_curve_and_cache(client: TestClient) -> None:
    res1 = client.get("/dataviz/model-result", params={"task": "market_price", "model": "random_forest"})
    assert res1.status_code == 200
    curves1 = res1.json()["curves"]
    assert len(curves1) == 1
    curve = curves1[0]
    assert curve["model"] == "random_forest"
    assert curve["rmsle"] >= 0.0
    assert len(curve["actual"]) == len(curve["predicted"])
    assert len(curve["actual"]) > 0

    res2 = client.get("/dataviz/model-result", params={"task": "market_price", "model": "random_forest"})
    assert res2.json()["curves"][0]["rmsle"] == curve["rmsle"]  # 캐시로 동일 값 재사용


def test_model_result_all_models_returns_5_regression_curves(client: TestClient) -> None:
    res = client.get("/dataviz/model-result", params={"task": "market_price", "model": "all"})
    assert res.status_code == 200
    curves = res.json()["curves"]
    assert len(curves) == 5
    assert {c["model"] for c in curves} == MODEL_IDS
    labels = {c["model"]: c["label"] for c in curves}
    assert labels["logistic_regression"] == "선형회귀(Ridge)"
    for c in curves:
        assert c["rmsle"] >= 0.0


def test_model_result_predicted_prices_are_non_negative(client: TestClient) -> None:
    # 로그공간 예측을 expm1로 복원할 때 음수 가격이 나오지 않도록 클리핑되어야 한다.
    res = client.get("/dataviz/model-result", params={"task": "market_price", "model": "logistic_regression"})
    assert res.status_code == 200
    curve = res.json()["curves"][0]
    assert all(v >= 0.0 for v in curve["predicted"])
