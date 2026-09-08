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


# ── 마켓 가격 예측(04. 마켓 가격 예측, market_price) 전용 모델 수행결과 응답 ───────────
#
# 회귀(연속값 가격 예측) 과제라 ROC/AUC 개념 자체가 없다. 대신 회귀 진단의 표준 방식인
# "실제값 vs 예측값 산점도" + RMSLE(원본 노트북이 채택한 평가지표)를 반환한다.
# 전처리검증 4종은 shipping(0/1)이 실제 이진 컬럼이라 기존 PreprocessCheckResponse를
# 그대로 재사용하지만(§crud.DOMAIN_CHARTS), 모델 수행결과만큼은 ROCCurve로 표현할 수
# 없어 이 전용 스키마를 별도로 둔다.
class RegressionCurve(BaseModel):
    model: str
    label: str
    rmsle: float
    r2: float
    actual: list[float]
    predicted: list[float]


class RegressionResultResponse(BaseModel):
    curves: list[RegressionCurve]


# ── 문서 군집화(03. 문서 군집화, doc_clustering) 전용 응답 ─────────────────────
#
# 산탄데르/신용카드는 "이진 타깃(0/1) 불균형 분포"가 자연스럽지만, 문서 군집화는
# 지도학습 타깃 자체가 없다(비지도 KMeans 군집화 + 파일명에서 뽑은 카테고리 다중클래스
# 보조검증). PreprocessCheckResponse의 satisfied/unsatisfied 이진 스키마를 억지로
# 재사용하면 의미가 왜곡되므로, 이 업무 전용 응답 스키마를 별도로 둔다.
# (모델 수행결과는 다중클래스 macro One-vs-Rest ROC로 계산해 기존 ModelResultResponse를
#  그대로 재사용한다 — §docclustering.py compute_model_result.)


class CountBin(BaseModel):
    range: str
    count: int


class LabeledCounts(BaseModel):
    labels: list[str]
    counts: list[int]


class GroupFiveNumberSummary(BaseModel):
    group: str
    summary: FiveNumberSummary


class DocClusteringLabels(BaseModel):
    category_title: str
    length_title: str
    cluster_title: str
    boxplot_title: str


class DocClusteringPreprocessResponse(BaseModel):
    category_distribution: LabeledCounts
    length_bins: list[CountBin]
    cluster_distribution: LabeledCounts
    length_boxplot: list[GroupFiveNumberSummary]
    labels: DocClusteringLabels
