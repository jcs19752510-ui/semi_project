from functools import lru_cache

import numpy as np
import pandas as pd

from app.core.config import get_settings

# 캐글산탄데르.ipynb 원본 EDA에서 실제로 다룬 컬럼만 로드한다.
# (전체 371개 컬럼을 다 읽으면 대시보드 응답이 느려지고, 나머지 컬럼은
# 원본 노트북에서도 탐색하지 않았다 — var3=지역, var15=나이, var38=대출액수)
# saldo_var30(계좌잔고)은 v2(업무/모델 선택형, TRD 99-02) 전처리검증 boxplot에 필요해 추가했다.
USE_COLUMNS = ["ID", "var3", "var15", "var38", "saldo_var30", "TARGET"]

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


@lru_cache
def load_creditcard_dataframe() -> pd.DataFrame:
    """캐글 신용카드 사기검출 원본 CSV(284,807행). V1~V28은 이미 PCA로 익명화된 값이라
    산탄데르처럼 usecols로 컬럼을 추릴 이유가 없어(전 컬럼이 ML 피처거나 차트에 쓰임) 그대로 읽는다."""
    settings = get_settings()
    return pd.read_csv(settings.creditcard_csv_path)


def get_creditcard_dataframe() -> pd.DataFrame:
    """FastAPI Depends용 진입점. 테스트에서는 이 함수를 override해 작은 표본으로 대체한다."""
    return load_creditcard_dataframe()


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


# ── v2(업무/모델 선택형, TRD 99-02) — 전처리 데이터 검증결과 4종 ────────────────
#
# 2026-08-24: 업무가 산탄데르 1종뿐일 때는 "연령"/"계좌잔고"/TARGET 컬럼명을 함수에
# 그대로 박아둬도 됐지만, 신용카드(타깃 컬럼 Class, 비교 축 Time/Amount) 업무가 추가되며
# 컬럼명을 파라미터로 받는 범용 함수로 바꿨다. 업무별 실제 컬럼/문구 매핑은 DOMAIN_CHARTS.
DOMAIN_CHARTS: dict[str, dict] = {
    "santander": {
        "target_col": "TARGET",
        "negative_label": "만족(0)",
        "positive_label": "불만족(1)",
        "bin1_col": "var15",
        "bin1_title": "연령 구간별 불만족 고객 비율",
        "bin2_col": "saldo_var30",
        "bin2_title": "계좌잔고 구간별 불만족 고객 비율",
        "box_col": "saldo_var30",
        "box_title": "계좌잔고(saldo_var30) 만족여부별 비교",
    },
    "credit_card": {
        "target_col": "Class",
        "negative_label": "정상(0)",
        "positive_label": "사기(1)",
        "bin1_col": "Time",
        "bin1_title": "거래시각 구간별 사기 비율",
        "bin2_col": "Amount",
        "bin2_title": "거래금액 구간별 사기 비율",
        "box_col": "Amount",
        "box_title": "거래금액(Amount) 사기여부별 비교",
    },
}


def compute_target_distribution(df: pd.DataFrame, target_col: str = "TARGET") -> dict:
    """타깃 클래스(0/1) 불균형 분포. v1의 get_target_distribution과 달리
    {labels, counts} 배열이 아니라 v2 스키마({satisfied, unsatisfied})로 반환한다.
    필드명은 "만족/불만족" 전용이 아니라 "음성(0)/양성(1)" 클래스를 뜻하는 고정 스키마다
    — 업무별 실제 표시 문구는 DOMAIN_CHARTS의 negative_label/positive_label을 쓴다."""
    counts = df[target_col].value_counts()
    return {
        "satisfied": int(counts.get(0, 0)),
        "unsatisfied": int(counts.get(1, 0)),
    }


def compute_ratio_bins(df: pd.DataFrame, column: str, bins: int = 5, target_col: str = "TARGET") -> list[dict]:
    """column을 bins개 분위(quantile) 구간으로 나눠 구간별 양성 클래스(target_col=1) 비율(%)을 계산한다.
    §0-1-6 [기본값]: 비율은 소수점 1자리로 반올림."""
    if len(df) == 0:
        return []
    try:
        binned = pd.qcut(df[column], q=bins, duplicates="drop")
    except ValueError:
        # 표본이 작아 분위 개수만큼 값이 나뉘지 않는 경우(단위 테스트 등) 단일 구간으로 대체한다.
        binned = pd.cut(df[column], bins=1)

    result: list[dict] = []
    for interval, group in df.groupby(binned, observed=True)[target_col]:
        total = len(group)
        if total == 0:
            continue
        ratio = round(float((group == 1).sum()) / total * 100, 1)
        result.append({"range": str(interval), "ratio": ratio})
    return result


def _five_number_summary(series: pd.Series) -> dict:
    """min/q1/median/q3/max는 원본 통계값(클리핑 없음, §0-1-3 기본값 유지).
    whisker_low/high는 박스플롯 렌더링용으로 별도 제공하는 Tukey 1.5×IQR 수염 —
    saldo_var30처럼 꼬리가 매우 긴 컬럼은 whisker를 진짜 min/max로 그리면
    박스가 화면에 실선처럼 눌려버려서, 렌더링 표준 관례(1.5×IQR)를 따로 계산해둔다."""
    if len(series) == 0:
        return {
            "min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0,
            "whisker_low": 0.0, "whisker_high": 0.0, "outlier_count": 0,
        }
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    within_fence = series[(series >= lower_fence) & (series <= upper_fence)]
    return {
        "min": float(series.min()),
        "q1": q1,
        "median": float(series.quantile(0.5)),
        "q3": q3,
        "max": float(series.max()),
        "whisker_low": float(within_fence.min()) if len(within_fence) else q1,
        "whisker_high": float(within_fence.max()) if len(within_fence) else q3,
        "outlier_count": int(len(series) - len(within_fence)),
    }


def five_number_summary(series: pd.Series) -> dict:
    """_five_number_summary의 공개 래퍼. docclustering.py처럼 이진 target_col 그룹화
    없이(클러스터 등 N개 그룹) 동일한 1.5×IQR whisker 규칙을 재사용하고 싶을 때 쓴다."""
    return _five_number_summary(series)


def compute_value_boxplot(df: pd.DataFrame, column: str, target_col: str = "TARGET") -> dict:
    """column의 클래스(0/1)별 5수치요약(min/q1/median/q3/max) +
    렌더링용 whisker_low/high, outlier_count.
    §0-1-3 [기본값, 사용자 확정]: 통계치는 클리핑 없이 원본 그대로 계산하고,
    화면 표시(whisker)만 1.5×IQR 표준 방식으로 그린다."""
    return {
        "satisfied": _five_number_summary(df[df[target_col] == 0][column]),
        "unsatisfied": _five_number_summary(df[df[target_col] == 1][column]),
    }
