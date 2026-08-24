# v2(업무/모델 선택형) 화면의 업무·모델 매핑.
# §0-1-4 [기본값]: 최초 구현은 코드 상수로 관리한다. 모델이 3개 이상으로 늘어나면 DB 전환을 검토한다.
#
# 2026-08-24 업무종류.png/모델종류.png 반영: 업무명 4종(산탄데르/신용카드/문서 군집화/마켓 가격 예측),
# 모델명 5종(로지스틱 회귀/LightGBM/XGBoost/랜덤포레스트/GradientBoost)을 드롭다운에 "표시"한다.
# 다만 문서 군집화·마켓 가격 예측은 이 리포지토리에 데이터셋 자체가 없어(팀 미착수) enabled=False로
# 표시만 하고 선택은 막는다 — 사용자 확정: "표시만, 전부 준비중 처리".
#
# 2026-08-24(2차) 문서 군집화 실연동: 07_문서군집화_실습_RandomForest추가.ipynb(Opinosis 리뷰
# 51건 TF-IDF+KMeans 군집화 + RandomForest 보조검증) 데이터셋을 semi-backend/data/에 확보해
# enabled=True로 전환. 신용카드 추가 때와 동일하게 §8 "다음에 할 일" 계획을 그대로 따랐다.
TASKS: list[dict] = [
    {"id": "santander", "label": "01 산탄데르", "enabled": True},
    {"id": "credit_card", "label": "02 신용카드", "enabled": True},
    {"id": "doc_clustering", "label": "03 문서 군집화", "enabled": True},
    {"id": "market_price", "label": "04 마켓 가격 예측", "enabled": False},
]

# 팀 진행상황 표(요청항목.png §4)의 모델 드롭다운과 동일한 5종 카탈로그.
# ml.py의 분류기 팩토리가 이 5개 id를 모두 지원하며, 실제 업무(santander/credit_card)에는
# 동일 카탈로그를 그대로 연결해 온다 — id별 실제 학습 로직 차이는 ml.py에 있다.
MODEL_CATALOG: list[dict[str, str]] = [
    {"id": "logistic_regression", "label": "로지스틱 회귀"},
    {"id": "lightgbm", "label": "LightGBM"},
    {"id": "xgboost", "label": "XGBoost"},
    {"id": "random_forest", "label": "랜덤포레스트"},
    {"id": "gradient_boost", "label": "GradientBoost"},
]

MODELS: dict[str, list[dict[str, str]]] = {
    "santander": MODEL_CATALOG,
    "credit_card": MODEL_CATALOG,
    # 문서 군집화는 (KMeans 군집 결과와 별개로) TF-IDF 피처→카테고리(다중클래스) 분류기
    # 학습 검증에도 동일 5종 분류기 카탈로그를 재사용한다(§docclustering.py).
    "doc_clustering": MODEL_CATALOG,
    "market_price": [],
}


def get_tasks() -> list[dict]:
    return TASKS


def get_models(task: str | None) -> list[dict[str, str]]:
    # §0-1-1 [기본값]: 업무명이 미지정("전체")이면 모델명도 "전체" 고정 + 비활성화 상태로 취급한다.
    if task is None or task == "all":
        return []
    return MODELS.get(task, [])


def task_exists(task: str) -> bool:
    return task == "all" or any(t["id"] == task for t in TASKS)


def task_enabled(task: str) -> bool:
    return any(t["id"] == task and t["enabled"] for t in TASKS)


def model_exists(task: str, model: str) -> bool:
    if model == "all":
        return True
    return any(m["id"] == model for m in MODELS.get(task, []))
