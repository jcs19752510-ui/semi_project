import pandas as pd

from app.domains.dataviz import crud


def run_preprocess_check(task: str, df: pd.DataFrame) -> dict:
    """전처리조회 버튼 클릭 한 번에 필요한 검증 차트 4종 + 업무별 표시 라벨을 묶어 반환한다.
    (가이드요청서 99-02_A1 §2 run_preprocess_check 명세)
    2026-08-24: 업무가 2종(산탄데르/신용카드) 이상이 되며, 컬럼명·문구가 업무마다 달라
    crud.DOMAIN_CHARTS에서 업무별 설정을 읽어와 범용 crud 함수에 넘기는 방식으로 바꿨다."""
    cfg = crud.DOMAIN_CHARTS[task]
    return {
        "target_distribution": crud.compute_target_distribution(df, cfg["target_col"]),
        "bin1_ratio": crud.compute_ratio_bins(df, cfg["bin1_col"], target_col=cfg["target_col"]),
        "bin2_ratio": crud.compute_ratio_bins(df, cfg["bin2_col"], target_col=cfg["target_col"]),
        "value_boxplot": crud.compute_value_boxplot(df, cfg["box_col"], target_col=cfg["target_col"]),
        "labels": {
            "negative": cfg["negative_label"],
            "positive": cfg["positive_label"],
            "bin1_title": cfg["bin1_title"],
            "bin2_title": cfg["bin2_title"],
            "box_title": cfg["box_title"],
        },
    }
