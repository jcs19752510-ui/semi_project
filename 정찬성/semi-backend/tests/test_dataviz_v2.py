import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.domains.dataviz import crud
from app.main import app


@pytest.fixture(autouse=True)
def sample_dataframe():
    df = pd.DataFrame(
        {
            "ID": [1, 2, 3, 4, 5],
            "var3": [2, 2, 8, 8, 2],
            "var15": [23, 45, 30, 60, 25],
            "var38": [1000.0, 2000.0, 3000.0, 4000.0, 5000.0],
            "saldo_var30": [100.0, 200.0, -50.0, 300.0, 400.0],
            "TARGET": [0, 0, 1, 0, 1],
        }
    )
    app.dependency_overrides[crud.get_dataframe] = lambda: df
    yield df
    app.dependency_overrides.pop(crud.get_dataframe, None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# TC-DV2-01 (TC-DV1/TC-50)
def test_tasks(client: TestClient) -> None:
    res = client.get("/dataviz/tasks")
    assert res.status_code == 200
    assert res.json() == [{"id": "santander", "label": "1.산탄데르"}]


# TC-DV2-02 (TC-DV2/TC-51)
def test_models_with_task(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "santander"})
    assert res.status_code == 200
    body = res.json()
    assert {"id": "lightgbm", "label": "1.lightGBM"} in body


# TC-DV2-03 (TC-52) — AC-DV2-01
def test_models_without_task_returns_empty(client: TestClient) -> None:
    res = client.get("/dataviz/models")
    assert res.status_code == 200
    assert res.json() == []


# TC-DV2-04 (TC-DV3/TC-53) — AC-DV2-04
def test_preprocess_check_target_distribution(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res.status_code == 200
    body = res.json()
    dist = body["target_distribution"]
    assert dist["satisfied"] + dist["unsatisfied"] == 5
    assert dist["satisfied"] == 3
    assert dist["unsatisfied"] == 2


# TC-DV2-05 (TC-DV4)
def test_preprocess_check_age_ratio_bins(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res.status_code == 200
    bins = res.json()["age_unsatisfied_ratio"]
    assert len(bins) >= 1
    for b in bins:
        assert 0.0 <= b["ratio"] <= 100.0


# TC-DV2-06 (TC-DV5)
def test_preprocess_check_balance_boxplot_five_number_summary(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res.status_code == 200
    box = res.json()["balance_boxplot"]
    for group in ("satisfied", "unsatisfied"):
        summary = box[group]
        assert set(summary.keys()) == {
            "min", "q1", "median", "q3", "max", "whisker_low", "whisker_high", "outlier_count",
        }
        assert summary["min"] <= summary["q1"] <= summary["median"] <= summary["q3"] <= summary["max"]
        # whisker(1.5×IQR)는 항상 실제 min/max 범위 안쪽(또는 같은 지점)에 있어야 한다.
        assert summary["min"] <= summary["whisker_low"] <= summary["q1"]
        assert summary["q3"] <= summary["whisker_high"] <= summary["max"]
        assert summary["outlier_count"] >= 0


# TC-DV2-07 (TC-DV6/TC-54) — AC-DV2-05
def test_model_result_single_model_auc_range_and_cache(client: TestClient) -> None:
    res1 = client.get("/dataviz/model-result", params={"task": "santander", "model": "lightgbm"})
    assert res1.status_code == 200
    curves1 = res1.json()["curves"]
    assert len(curves1) == 1
    auc1 = curves1[0]["auc"]
    assert 0.0 <= auc1 <= 1.0
    assert len(curves1[0]["fpr"]) == len(curves1[0]["tpr"])

    res2 = client.get("/dataviz/model-result", params={"task": "santander", "model": "lightgbm"})
    auc2 = res2.json()["curves"][0]["auc"]
    assert auc1 == auc2  # 동일 (task, model) 재조회 시 캐시된 동일 값


# TC-DV2-08 (TC-DV7) — model=all 다중 곡선(현재 등록 모델 수만큼)
def test_model_result_all_models(client: TestClient) -> None:
    res = client.get("/dataviz/model-result", params={"task": "santander", "model": "all"})
    assert res.status_code == 200
    curves = res.json()["curves"]
    assert len(curves) == 2  # registry에 등록된 모델(lightgbm, random_forest) 수만큼
    assert {c["model"] for c in curves} == {"lightgbm", "random_forest"}


# TC-DV2-09 (TC-55) — AC-DV2-06
def test_preprocess_check_task_all_with_specific_model_is_422(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "all", "model": "lightgbm"})
    assert res.status_code == 422


# TC-DV2-10 (TC-56)
def test_preprocess_check_unknown_task_is_404(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "unknown", "model": "lightgbm"})
    assert res.status_code == 404


def test_model_result_unknown_model_is_404(client: TestClient) -> None:
    res = client.get("/dataviz/model-result", params={"task": "santander", "model": "unknown"})
    assert res.status_code == 404
