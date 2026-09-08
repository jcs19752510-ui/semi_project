import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.domains.dataviz import docclustering
from app.main import app

MODEL_IDS = {"logistic_regression", "lightgbm", "xgboost", "random_forest", "gradient_boost"}


def _build_corpus() -> pd.DataFrame:
    # 카테고리 3종(battery/screen/sound)은 문서 2건씩 — 원본 노트북과 동일하게
    # "카테고리당 2건 이상"만 모델 평가 대상이 된다. price는 1건뿐이라 평가에서 제외되는
    # 가드(§docclustering._train_and_evaluate)를 검증하는 표본이다.
    return pd.DataFrame(
        {
            "filename": [
                "battery_deviceA",
                "battery_deviceB",
                "screen_deviceA",
                "screen_deviceB",
                "sound_deviceA",
                "sound_deviceB",
                "price_deviceA",
            ],
            "category": ["battery", "battery", "screen", "screen", "sound", "sound", "price"],
            "opinion_text": [
                "battery life is good and long lasting all day",
                "battery lasts long and charges fast every day",
                "screen is bright and clear with vivid colors",
                "screen display is sharp and clear in sunlight",
                "sound quality is great and very clear",
                "sound is loud and clear with deep bass",
                "price is high and expensive for this model",
            ],
        }
    )


@pytest.fixture(autouse=True)
def sample_document_corpus(monkeypatch: pytest.MonkeyPatch):
    document_df, feature_matrix = docclustering._vectorize_and_cluster(_build_corpus())
    monkeypatch.setattr(docclustering, "get_document_corpus", lambda: (document_df, feature_matrix))
    docclustering._cache.clear()
    yield document_df, feature_matrix


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_models_doc_clustering_reuses_5_model_catalog(client: TestClient) -> None:
    res = client.get("/dataviz/models", params={"task": "doc_clustering"})
    assert res.status_code == 200
    assert {m["id"] for m in res.json()} == MODEL_IDS


def test_preprocess_check_category_distribution(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "doc_clustering", "model": "all"})
    assert res.status_code == 200
    body = res.json()

    dist = body["category_distribution"]
    assert sum(dist["counts"]) == 7  # 표본 전체 문서 수(카테고리 1건짜리 price 포함)
    assert set(dist["labels"]) == {"battery", "price", "screen", "sound"}


def test_preprocess_check_length_bins_cover_all_documents(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "doc_clustering", "model": "all"})
    assert res.status_code == 200
    bins = res.json()["length_bins"]
    assert len(bins) >= 1
    assert sum(b["count"] for b in bins) == 7


def test_preprocess_check_cluster_distribution_and_boxplot(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "doc_clustering", "model": "all"})
    assert res.status_code == 200
    body = res.json()

    cluster_dist = body["cluster_distribution"]
    assert sum(cluster_dist["counts"]) == 7
    assert len(cluster_dist["labels"]) <= 3  # N_CLUSTERS=3

    boxplot = body["length_boxplot"]
    assert len(boxplot) == len(cluster_dist["labels"])
    for group in boxplot:
        summary = group["summary"]
        assert summary["min"] <= summary["q1"] <= summary["median"] <= summary["q3"] <= summary["max"]


def test_preprocess_check_labels_titles(client: TestClient) -> None:
    res = client.get("/dataviz/preprocess-check", params={"task": "doc_clustering", "model": "all"})
    assert res.status_code == 200
    labels = res.json()["labels"]
    assert set(labels.keys()) == {"category_title", "length_title", "cluster_title", "boxplot_title"}


# TC-DC-01 — AC-DC-01: 카테고리 2건 이상인 유효 표본만으로 다중클래스 macro OvR AUC를 계산한다.
def test_model_result_single_model_macro_auc_range_and_cache(client: TestClient) -> None:
    res1 = client.get("/dataviz/model-result", params={"task": "doc_clustering", "model": "random_forest"})
    assert res1.status_code == 200
    curves1 = res1.json()["curves"]
    assert len(curves1) == 1
    curve = curves1[0]
    assert curve["model"] == "random_forest"
    assert 0.0 <= curve["auc"] <= 1.0
    assert len(curve["fpr"]) == len(curve["tpr"])

    res2 = client.get("/dataviz/model-result", params={"task": "doc_clustering", "model": "random_forest"})
    assert res2.json()["curves"][0]["auc"] == curve["auc"]  # 동일 (task, model) 재조회 시 캐시 재사용


def test_model_result_all_models_returns_5_curves(client: TestClient) -> None:
    res = client.get("/dataviz/model-result", params={"task": "doc_clustering", "model": "all"})
    assert res.status_code == 200
    curves = res.json()["curves"]
    assert len(curves) == 5
    assert {c["model"] for c in curves} == MODEL_IDS
    for c in curves:
        assert 0.0 <= c["auc"] <= 1.0


# TC-DC-02 — AC-DC-02: 카테고리가 전부 1건뿐(계층화 불가)이면 임의확률(0.5) 평평한 곡선으로 대체한다.
def test_model_result_degrades_gracefully_when_no_valid_category(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # TF-IDF min_df=2(§docclustering.TFIDF_MIN_DF)를 만족시키려면 "정확히 2개" 문서에
    # 걸치는 공통 단어가 있어야 한다 — 3개 문서 전부에 넣으면 이번엔 max_df=0.85(3건 중
    # 2.55건 상한)에 걸려 똑같이 잘려나가므로 "device"는 두 문서에만 넣는다.
    singleton_df = pd.DataFrame(
        {
            "filename": ["a_x", "b_y", "c_z"],
            "category": ["a", "b", "c"],
            "opinion_text": ["alpha bravo device", "delta echo device", "golf hotel india"],
        }
    )
    document_df, feature_matrix = docclustering._vectorize_and_cluster(singleton_df)
    monkeypatch.setattr(docclustering, "get_document_corpus", lambda: (document_df, feature_matrix))
    docclustering._cache.clear()

    res = client.get("/dataviz/model-result", params={"task": "doc_clustering", "model": "logistic_regression"})
    assert res.status_code == 200
    curve = res.json()["curves"][0]
    assert curve["auc"] == 0.5
    assert curve["fpr"] == [0.0, 1.0]
    assert curve["tpr"] == [0.0, 1.0]
