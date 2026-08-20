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
