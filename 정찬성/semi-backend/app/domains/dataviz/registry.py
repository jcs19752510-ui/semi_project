# v2(업무/모델 선택형) 화면의 업무·모델 매핑.
# §0-1-4 [기본값]: 최초 구현은 코드 상수로 관리한다. 모델이 3개 이상으로 늘어나면 DB 전환을 검토한다.
TASKS: list[dict[str, str]] = [
    {"id": "santander", "label": "1.산탄데르"},
]

MODELS: dict[str, list[dict[str, str]]] = {
    "santander": [
        {"id": "lightgbm", "label": "1.lightGBM"},
        {"id": "random_forest", "label": "2.RandomForest"},
    ],
}


def get_tasks() -> list[dict[str, str]]:
    return TASKS


def get_models(task: str | None) -> list[dict[str, str]]:
    # §0-1-1 [기본값]: 업무명이 미지정("전체")이면 모델명도 "전체" 고정 + 비활성화 상태로 취급한다.
    if task is None or task == "all":
        return []
    return MODELS.get(task, [])


def task_exists(task: str) -> bool:
    return task == "all" or any(t["id"] == task for t in TASKS)


def model_exists(task: str, model: str) -> bool:
    if model == "all":
        return True
    return any(m["id"] == model for m in MODELS.get(task, []))
