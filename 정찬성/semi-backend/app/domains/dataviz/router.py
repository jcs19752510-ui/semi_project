from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from app.domains.dataviz import crud
from app.domains.dataviz.schemas import (
    AgeDistributionResponse,
    HistogramResponse,
    RecordsResponse,
    RegionOption,
    SummaryResponse,
    TargetDistributionResponse,
)

router = APIRouter(tags=["dataviz"])

STATIC_DIR = Path(__file__).resolve().parents[2] / "static" / "dataviz"


@router.get("/dataviz", include_in_schema=False)
def dataviz_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/dataviz/summary", response_model=SummaryResponse)
def summary(df: pd.DataFrame = Depends(crud.get_dataframe)) -> dict:
    return crud.get_summary(df)


@router.get("/dataviz/regions", response_model=list[RegionOption])
def regions(df: pd.DataFrame = Depends(crud.get_dataframe)) -> list[dict]:
    return crud.get_top_regions(df)


@router.get("/dataviz/records", response_model=RecordsResponse)
def records(
    target: int | None = Query(default=None, ge=0, le=1, description="0=만족, 1=불만족, 미지정 시 전체"),
    age_min: int | None = Query(default=None, ge=0, le=120),
    age_max: int | None = Query(default=None, ge=0, le=120),
    region: int | None = Query(default=None, description="var3 코드값"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    df: pd.DataFrame = Depends(crud.get_dataframe),
) -> dict:
    filtered = crud.apply_filters(df, target=target, age_min=age_min, age_max=age_max, region=region)
    return crud.get_records(filtered, page=page, size=size)


@router.get("/dataviz/chart/target-distribution", response_model=TargetDistributionResponse)
def target_distribution(
    age_min: int | None = Query(default=None, ge=0, le=120),
    age_max: int | None = Query(default=None, ge=0, le=120),
    region: int | None = Query(default=None, description="var3 코드값"),
    df: pd.DataFrame = Depends(crud.get_dataframe),
) -> dict:
    # target 필터는 이 차트의 목적(만족/불만족 비교)과 배치되므로 일부러 받지 않는다.
    filtered = crud.apply_filters(df, age_min=age_min, age_max=age_max, region=region)
    return crud.get_target_distribution(filtered)


@router.get("/dataviz/chart/var38-histogram", response_model=HistogramResponse)
def var38_histogram(
    target: int | None = Query(default=None, ge=0, le=1, description="0=만족, 1=불만족, 미지정 시 전체"),
    age_min: int | None = Query(default=None, ge=0, le=120),
    age_max: int | None = Query(default=None, ge=0, le=120),
    region: int | None = Query(default=None, description="var3 코드값"),
    bins: int = Query(default=50, ge=5, le=200),
    log_scale: bool = Query(default=True, description="var38은 꼬리가 매우 길어 기본값은 log1p 변환"),
    df: pd.DataFrame = Depends(crud.get_dataframe),
) -> dict:
    filtered = crud.apply_filters(df, target=target, age_min=age_min, age_max=age_max, region=region)
    return crud.get_var38_histogram(filtered, bins=bins, log_scale=log_scale)


@router.get("/dataviz/chart/age-distribution", response_model=AgeDistributionResponse)
def age_distribution(
    region: int | None = Query(default=None, description="var3 코드값"),
    bins: int = Query(default=20, ge=5, le=100),
    df: pd.DataFrame = Depends(crud.get_dataframe),
) -> dict:
    # target 필터는 받지 않는다 — 만족/불만족 두 분포를 겹쳐서 비교하는 게 이 차트의 목적.
    filtered = crud.apply_filters(df, region=region)
    return crud.get_age_distribution(filtered, bins=bins)
