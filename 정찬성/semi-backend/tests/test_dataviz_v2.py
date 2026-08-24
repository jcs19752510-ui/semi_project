import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.domains.dataviz import crud
from app.main import app

MODEL_IDS = {"logistic_regression", "lightgbm", "xgboost", "random_forest", "gradient_boost"}


@pytest.fixture(autouse=True)
def sample_dataframe(monkeypatch: pytest.MonkeyPatch):
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
    # v1 엔드포인트(summary/regions/records/chart/*)는 여전히 Depends(crud.get_dataframe)라
    # dependency_overrides로도 잡히지만, v2 엔드포인트(preprocess-check/model-result)는
    # router._dataframe_for_task가 crud.get_dataframe()을 직접 호출하므로(§ 운영 장애 수정 —
    # santander 요청이 creditcard.csv 로딩 실패에 발목 잡히지 않도록 task별 지연 로딩으로
    # 바꿨다) monkeypatch로 모듈 속성 자체를 바꿔야 두 경로 모두 잡힌다.
    app.dependency_overrides[crud.get_dataframe] = lambda: df
    monkeypatch.setattr(crud, "get_dataframe", lambda: df)
    yield df
    app.dependency_overrides.pop(crud.get_dataframe, None)


@pytest.fixture(autouse=True)
def sample_creditcard_dataframe(monkeypatch: pytest.MonkeyPatch):
    # V1 하나만 있어도 되는 소표본이 아니라, ml.FEATURE_COLUMNS["credit_card"](V1~V28+Amount)를
    # 전부 채워야 model-result 엔드포인트가 실제로 학습·평가를 수행할 수 있다.
    rows = 6
    data = {"Time": [0, 1, 2, 3, 4, 5]}
    for i in range(1, 29):
        data[f"V{i}"] = [float(i + r) for r in range(rows)]
    data["Amount"] = [10.0, 20.0, 5000.0, 15.0, 30.0, 4000.0]
    data["Class"] = [0, 0, 1, 0, 0, 1]
    df = pd.DataFrame(data)
    monkeypatch.setattr(crud, "get_creditcard_dataframe", lambda: df)
    yield df


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# TC-DV2-01 (TC-DV1/TC-50)
# 2026-08-24(2차): 문서 군집화 데이터셋을 확보해 enabled=True로 전환(§docclustering.py).
# 문서 군집화 전용 케이스는 tests/test_doc_clustering.py로 분리했다.
def test_tasks(client: TestClient) -> None:
    res = client.get("/dataviz/tasks")
    assert res.status_code == 200
    body = res.json()
    assert body == [
        {"id": "santander", "label": "01 산탄데르", "enabled": True},
        {"id": "credit_card", "label": "02 신용카드", "enabled": True},
        {"id": "doc_clustering", "label": "03 문서 군집화", "enabled": True},
        {"id": "market_price", "label": "04 마켓 가격 예측", "enabled": False},
    ]


# TC-DV2-02 (TC-DV2/TC-51)
def test_models_with_task(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "santander"})
    assert res.status_code == 200
    body = res.json()
    assert {m["id"] for m in body} == MODEL_IDS
    assert {"id": "lightgbm", "label": "LightGBM"} in body
    assert {"id": "logistic_regression", "label": "로지스틱 회귀"} in body


def test_models_for_credit_card_task_same_catalog(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "credit_card"})
    assert res.status_code == 200
    assert {m["id"] for m in res.json()} == MODEL_IDS


def test_models_for_doc_clustering_task_same_catalog(client: TestClient) -> None:
    # 2026-08-24(2차): 문서 군집화도 5종 분류기 카탈로그를 그대로 재사용한다(§registry.MODELS).
    res = client.get("/dataviz/models", params={"task": "doc_clustering"})
    assert res.status_code == 200
    assert {m["id"] for m in res.json()} == MODEL_IDS


def test_models_for_disabled_task_is_empty(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "market_price"})
    assert res.status_code == 200
    assert res.json() == []


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
    assert body["labels"] == {
        "negative": "만족(0)",
        "positive": "불만족(1)",
        "bin1_title": "연령 구간별 불만족 고객 비율",
        "bin2_title": "계좌잔고 구간별 불만족 고객 비율",
        "box_title": "계좌잔고(saldo_var30) 만족여부별 비교",
    }


# TC-DV2-05 (TC-DV4)
def test_preprocess_check_bin1_ratio(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res.status_code == 200
    bins = res.json()["bin1_ratio"]
    assert len(bins) >= 1
    for b in bins:
        assert 0.0 <= b["ratio"] <= 100.0


# TC-DV2-06 (TC-DV5)
def test_preprocess_check_value_boxplot_five_number_summary(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res.status_code == 200
    box = res.json()["value_boxplot"]
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
    assert len(curves) == 5  # registry MODEL_CATALOG 5종 전부
    assert {c["model"] for c in curves} == MODEL_IDS


# 2026-08-24 추가: 업무명이 신용카드일 때도 동일한 5종 모델 카탈로그로 실제 학습이 수행된다
# (타깃 컬럼 Class, 피처 V1~V28+Amount — ml.FEATURE_COLUMNS["credit_card"] 참고).
def test_credit_card_preprocess_check_labels(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "credit_card", "model": "xgboost"})
    assert res.status_code == 200
    body = res.json()
    assert body["target_distribution"] == {"satisfied": 4, "unsatisfied": 2}
    assert body["labels"]["negative"] == "정상(0)"
    assert body["labels"]["positive"] == "사기(1)"


def test_credit_card_model_result_all_models(client: TestClient) -> None:
    res = client.get("/dataviz/model-result", params={"task": "credit_card", "model": "all"})
    assert res.status_code == 200
    curves = res.json()["curves"]
    assert len(curves) == 5
    assert {c["model"] for c in curves} == MODEL_IDS
    for c in curves:
        assert 0.0 <= c["auc"] <= 1.0


# 2026-08-24 회귀 테스트 — 운영 장애 재현/수정 검증: creditcard.csv가 없는 환경(Render처럼
# 해당 CSV가 배포되지 않은 경우, §운영오류1.png)에서도 task=santander 요청은 영향받지
# 않아야 한다. router가 santander_df/creditcard_df를 항상 함께 Depends로 주입받던 예전
# 구조에서는 이 테스트가 실패했다(creditcard 로더 예외가 santander 요청까지 500으로 만듦).
def test_santander_unaffected_when_creditcard_csv_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom():
        raise FileNotFoundError("[Errno 2] No such file or directory: '../ipynb/data/creditcard.csv'")

    monkeypatch.setattr(crud, "get_creditcard_dataframe", _boom)

    res1 = client.get("/dataviz/preprocess-check", params={"task": "santander", "model": "lightgbm"})
    assert res1.status_code == 200

    res2 = client.get("/dataviz/model-result", params={"task": "santander", "model": "lightgbm"})
    assert res2.status_code == 200


# 2026-08-24 추가: 마켓 가격 예측은 드롭다운에는 보이지만(§업무종류.png) 데이터 파이프라인이
# 없어 선택 시 409(준비중)로 명확히 구분된다(404=존재하지 않음과 다름). 문서 군집화는
# 2026-08-24(2차)에 데이터셋을 확보해 이 카테고리에서 빠졌다(§test_doc_clustering.py).
def test_preprocess_check_disabled_task_is_409(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "market_price", "model": "all"})
    assert res.status_code == 409


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
