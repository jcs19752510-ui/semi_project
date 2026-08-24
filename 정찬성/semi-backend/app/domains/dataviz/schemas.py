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
    enabled: bool = True


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


class ValueBoxplot(BaseModel):
    satisfied: FiveNumberSummary
    unsatisfied: FiveNumberSummary


class ChartLabels(BaseModel):
    """업무별로 의미가 달라지는 차트 문구(예: 산탄데르 '만족/불만족' vs 신용카드 '정상/사기').
    satisfied/unsatisfied 같은 JSON 필드명 자체는 업무 불문 고정 스키마로 유지하고,
    화면에 실제로 보여줄 한글 라벨만 이 객체로 전달한다."""

    negative: str
    positive: str
    bin1_title: str
    bin2_title: str
    box_title: str


class PreprocessCheckResponse(BaseModel):
    target_distribution: TargetDistributionV2
    bin1_ratio: list[RatioBin]
    bin2_ratio: list[RatioBin]
    value_boxplot: ValueBoxplot
    labels: ChartLabels


class ROCCurve(BaseModel):
    model: str
    label: str
    auc: float
    fpr: list[float]
    tpr: list[float]


class ModelResultResponse(BaseModel):
    curves: list[ROCCurve]
