from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_rows: int
    total_columns: int
    satisfied_count: int
    unsatisfied_count: int
    unsatisfied_ratio: float
    var15_min: int
    var15_max: int
    var38_min: float
    var38_max: float
    var38_mean: float


class RecordRow(BaseModel):
    id: int
    var3: int
    var15: int
    var38: float
    target: int


class RecordsResponse(BaseModel):
    page: int
    size: int
    total: int
    rows: list[RecordRow]


class RegionOption(BaseModel):
    var3: int
    count: int


class TargetDistributionResponse(BaseModel):
    labels: list[str]
    counts: list[int]


class HistogramResponse(BaseModel):
    bin_edges: list[float]
    counts: list[int]


class AgeDistributionResponse(BaseModel):
    bin_edges: list[float]
    satisfied_counts: list[int]
    unsatisfied_counts: list[int]


# ── v2(업무/모델 선택형, TRD 99-02) ──────────────────────────────────────


class TaskOption(BaseModel):
    id: str
    label: str


class ModelOption(BaseModel):
    id: str
    label: str


class TargetDistributionV2(BaseModel):
    satisfied: int
    unsatisfied: int


class RatioBin(BaseModel):
    range: str
    ratio: float


class FiveNumberSummary(BaseModel):
    min: float
    q1: float
    median: float
    q3: float
    max: float
    whisker_low: float
    whisker_high: float
    outlier_count: int


class BalanceBoxplot(BaseModel):
    satisfied: FiveNumberSummary
    unsatisfied: FiveNumberSummary


class PreprocessCheckResponse(BaseModel):
    target_distribution: TargetDistributionV2
    age_unsatisfied_ratio: list[RatioBin]
    balance_unsatisfied_ratio: list[RatioBin]
    balance_boxplot: BalanceBoxplot


class ROCCurve(BaseModel):
    model: str
    label: str
    auc: float
    fpr: list[float]
    tpr: list[float]


class ModelResultResponse(BaseModel):
    curves: list[ROCCurve]
