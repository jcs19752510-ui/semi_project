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
            "TARGET": [0, 0, 1, 0, 1],
        }
    )
    app.dependency_overrides[crud.get_dataframe] = lambda: df
    yield df
    app.dependency_overrides.pop(crud.get_dataframe, None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_summary(client: TestClient) -> None:
    res = client.get("/dataviz/summary")
    assert res.status_code == 200
    body = res.json()
    assert body["total_rows"] == 5
    assert body["satisfied_count"] == 3
    assert body["unsatisfied_count"] == 2
    assert body["unsatisfied_ratio"] == pytest.approx(0.4)


def test_regions(client: TestClient) -> None:
    res = client.get("/dataviz/regions")
    assert res.status_code == 200
    body = res.json()
    assert {"var3": 2, "count": 3} in body
    assert {"var3": 8, "count": 2} in body


def test_records_filtering_by_target(client: TestClient) -> None:
    res = client.get("/dataviz/records", params={"target": 1})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert all(row["target"] == 1 for row in body["rows"])


def test_records_filtering_by_age_range(client: TestClient) -> None:
    res = client.get("/dataviz/records", params={"age_min": 30, "age_max": 60})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert all(30 <= row["var15"] <= 60 for row in body["rows"])


def test_records_pagination(client: TestClient) -> None:
    res = client.get("/dataviz/records", params={"page": 2, "size": 2})
    assert res.status_code == 200
    body = res.json()
    assert body["page"] == 2
    assert body["size"] == 2
    assert len(body["rows"]) == 2


def test_target_distribution_ignores_target_filter(client: TestClient) -> None:
    res = client.get("/dataviz/chart/target-distribution")
    assert res.status_code == 200
    body = res.json()
    assert body["counts"] == [3, 2]


def test_var38_histogram_bin_count(client: TestClient) -> None:
    res = client.get("/dataviz/chart/var38-histogram", params={"bins": 5, "log_scale": False})
    assert res.status_code == 200
    body = res.json()
    assert len(body["bin_edges"]) == 6
    assert sum(body["counts"]) == 5


def test_age_distribution_splits_by_target(client: TestClient) -> None:
    res = client.get("/dataviz/chart/age-distribution", params={"bins": 5})
    assert res.status_code == 200
    body = res.json()
    assert sum(body["satisfied_counts"]) == 3
    assert sum(body["unsatisfied_counts"]) == 2


def test_dataviz_page_serves_html(client: TestClient) -> None:
    res = client.get("/dataviz")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
