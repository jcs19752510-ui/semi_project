from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.domains.dataviz import crud, docclustering, ml, registry, service
from app.domains.dataviz.schemas import (
    AgeDistributionResponse,
    DocClusteringPreprocessResponse,
    HistogramResponse,
    ModelOption,
    ModelResultResponse,
    PreprocessCheckResponse,
    RecordsResponse,
    RegionOption,
    SummaryResponse,
    TargetDistributionResponse,
    TaskOption,
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


# ── v2(업무/모델 선택형, TRD 99-02) ──────────────────────────────────────


def _validate_task_model(task: str, model: str) -> None:
    if not registry.task_exists(task):
        raise HTTPException(status_code=404, detail="존재하지 않는 업무입니다")
    if task == "all" and model != "all":
        # §0-1-1 / 가이드요청서 §4: 업무가 '전체'인데 모델을 구체적으로 지정하는 조합은 모순.
        raise HTTPException(status_code=422, detail="업무가 '전체'일 때는 모델을 특정할 수 없습니다")
    if task != "all" and not registry.task_enabled(task):
        # 업무명 드롭다운에는 표시되지만(§업무종류.png) 데이터 파이프라인이 아직 없는 업무
        # (문서 군집화/마켓 가격 예측) — 선택 자체는 유효하니 404가 아니라 409(준비중)로 구분한다.
        raise HTTPException(status_code=409, detail="아직 준비 중인 업무입니다")
    if task != "all" and not registry.model_exists(task, model):
        raise HTTPException(status_code=404, detail="존재하지 않는 모델입니다")


@router.get("/dataviz/tasks", response_model=list[TaskOption])
def tasks() -> list[dict]:
    return registry.get_tasks()


@router.get("/dataviz/models", response_model=list[ModelOption])
def models(task: str | None = Query(default=None)) -> list[dict]:
    return registry.get_models(task)


def _dataframe_for_task(task: str) -> pd.DataFrame:
    # 2026-08-24 수정: task별로 필요한 CSV만 그때그때 로드한다. 이전에는 santander_df/
    # creditcard_df를 둘 다 Depends로 항상 주입받았는데, 그러면 task=santander 요청에서도
    # creditcard.csv를 매번 로드 시도하게 된다 — 운영(Render)에는 creditcard.csv가 아예
    # 배포돼 있지 않아(§ .gitignore로 제외, 144MB로 GitHub 100MB 제한 초과) 산탄데르
    # 요청까지 전부 500으로 죽는 실장애가 있었다(운영오류1.png). task를 먼저 보고 실제로
    # 필요한 로더 하나만 호출해 업무 간 장애가 전파되지 않도록 격리한다.
    if task == "credit_card":
        return crud.get_creditcard_dataframe()
    return crud.get_dataframe()


@router.get(
    "/dataviz/preprocess-check",
    response_model=PreprocessCheckResponse | DocClusteringPreprocessResponse,
)
def preprocess_check(
    task: str = Query(...),
    model: str = Query(default="all"),
) -> dict:
    _validate_task_model(task, model)
    if task == "doc_clustering":
        # 문서 군집화는 지도학습 이진 타깃이 없는 비지도 업무라(§docclustering.py 모듈
        # docstring) santander/credit_card와 응답 스키마 자체가 다르다 — service.py의
        # DOMAIN_CHARTS 이진 파이프라인 대신 이 업무 전용 경로를 탄다.
        document_df, _ = docclustering.get_document_corpus()
        return docclustering.run_preprocess_check(document_df)
    df = _dataframe_for_task(task)
    return service.run_preprocess_check(task, df)


@router.get("/dataviz/model-result", response_model=ModelResultResponse)
def model_result(
    task: str = Query(...),
    model: str = Query(default="all"),
) -> dict:
    _validate_task_model(task, model)
    if model == "all":
        # §0-1-2 [기본값]: 백엔드는 다중 곡선을 반환할 수 있어야 하지만, 프론트 오버레이는
        # 후속 이터레이션이다(app.js는 curves[0]만 그린다).
        target_models = [m["id"] for m in registry.get_models(task)]
    else:
        target_models = [model]

    if task == "doc_clustering":
        # 타깃이 다중클래스(카테고리)라 ROC/AUC는 macro One-vs-Rest 평균으로 계산하되
        # (§docclustering.py), 응답 스키마(ROCCurve)는 santander/credit_card와 동일하게
        # 재사용해 프론트 ROC 차트를 그대로 쓸 수 있게 한다.
        document_df, feature_matrix = docclustering.get_document_corpus()
        curves = [docclustering.compute_model_result(document_df, feature_matrix, m) for m in target_models]
        return {"curves": curves}

    df = _dataframe_for_task(task)
    curves = [ml.compute_roc_curve(df, task, m) for m in target_models]
    return {"curves": curves}
