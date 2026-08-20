from functools import lru_cache

import numpy as np
import pandas as pd

from app.core.config import get_settings

# 캐글산탄데르.ipynb 원본 EDA에서 실제로 다룬 5개 컬럼만 로드한다.
# (전체 371개 컬럼을 다 읽으면 대시보드 응답이 느려지고, 나머지 컬럼은
# 원본 노트북에서도 탐색하지 않았다 — var3=지역, var15=나이, var38=대출액수)
USE_COLUMNS = ["ID", "var3", "var15", "var38", "TARGET"]

# 원본 데이터셋의 전체 컬럼 수(피처 370개 + TARGET). usecols로 5개만 읽으므로
# 로드된 DataFrame에서는 알 수 없어 노트북 1번 셀 기준으로 상수화했다.
TOTAL_COLUMNS = 371


@lru_cache
def load_dataframe() -> pd.DataFrame:
    settings = get_settings()
    return pd.read_csv(settings.santander_csv_path, encoding="latin-1", usecols=USE_COLUMNS)


def get_dataframe() -> pd.DataFrame:
    """FastAPI Depends용 진입점. 테스트에서는 이 함수를 override해 작은 표본으로 대체한다."""
    return load_dataframe()


def apply_filters(
    df: pd.DataFrame,
    target: int | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    region: int | None = None,
) -> pd.DataFrame:
    filtered = df
    if target is not None:
        filtered = filtered[filtered["TARGET"] == target]
    if age_min is not None:
        filtered = filtered[filtered["var15"] >= age_min]
    if age_max is not None:
        filtered = filtered[filtered["var15"] <= age_max]
    if region is not None:
        filtered = filtered[filtered["var3"] == region]
    return filtered


def get_summary(df: pd.DataFrame) -> dict:
    total = int(len(df))
    unsatisfied = int((df["TARGET"] == 1).sum())
    satisfied = total - unsatisfied
    return {
        "total_rows": total,
        "total_columns": TOTAL_COLUMNS,
        "satisfied_count": satisfied,
        "unsatisfied_count": unsatisfied,
        "unsatisfied_ratio": round(unsatisfied / total, 4) if total else 0.0,
        "var15_min": int(df["var15"].min()) if total else 0,
        "var15_max": int(df["var15"].max()) if total else 0,
        "var38_min": float(df["var38"].min()) if total else 0.0,
        "var38_max": float(df["var38"].max()) if total else 0.0,
        "var38_mean": float(df["var38"].mean()) if total else 0.0,
    }


def get_top_regions(df: pd.DataFrame, limit: int = 20) -> list[dict]:
    counts = df["var3"].value_counts().head(limit)
    return [{"var3": int(var3), "count": int(count)} for var3, count in counts.items()]


def get_records(df: pd.DataFrame, page: int, size: int) -> dict:
    total = len(df)
    start = (page - 1) * size
    page_df = df.iloc[start : start + size]
    rows = [
        {
            "id": int(row.ID),
            "var3": int(row.var3),
            "var15": int(row.var15),
            "var38": float(row.var38),
            "target": int(row.TARGET),
        }
        for row in page_df.itertuples(index=False)
    ]
    return {"page": page, "size": size, "total": total, "rows": rows}


def get_target_distribution(df: pd.DataFrame) -> dict:
    counts = df["TARGET"].value_counts()
    return {
        "labels": ["만족(0)", "불만족(1)"],
        "counts": [int(counts.get(0, 0)), int(counts.get(1, 0))],
    }


def get_var38_histogram(df: pd.DataFrame, bins: int, log_scale: bool) -> dict:
    values = df["var38"].to_numpy()
    if log_scale:
        values = np.log1p(values)
    if len(values) == 0:
        return {"bin_edges": [], "counts": []}
    counts, edges = np.histogram(values, bins=bins)
    return {"bin_edges": [round(float(e), 4) for e in edges], "counts": [int(c) for c in counts]}


def get_age_distribution(df: pd.DataFrame, bins: int) -> dict:
    satisfied = df[df["TARGET"] == 0]["var15"].to_numpy()
    unsatisfied = df[df["TARGET"] == 1]["var15"].to_numpy()
    if len(df) == 0:
        return {"bin_edges": [], "satisfied_counts": [], "unsatisfied_counts": []}
    edges = np.histogram_bin_edges(df["var15"].to_numpy(), bins=bins)
    satisfied_counts, _ = np.histogram(satisfied, bins=edges)
    unsatisfied_counts, _ = np.histogram(unsatisfied, bins=edges)
    return {
        "bin_edges": [round(float(e), 2) for e in edges],
        "satisfied_counts": [int(c) for c in satisfied_counts],
        "unsatisfied_counts": [int(c) for c in unsatisfied_counts],
    }
