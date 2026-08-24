import pandas as pd

from app.domains.dataviz import crud


def run_preprocess_check(df: pd.DataFrame) -> dict:
    """전처리조회 버튼 클릭 한 번에 필요한 검증 차트 4종을 한 번에 묶어 반환한다.
    (가이드요청서 99-02_A1 §2 run_preprocess_check 명세)"""
    return {
        "target_distribution": crud.compute_target_distribution(df),
        "age_unsatisfied_ratio": crud.compute_age_unsatisfied_ratio(df),
        "balance_unsatisfied_ratio": crud.compute_balance_unsatisfied_ratio(df),
        "balance_boxplot": crud.compute_balance_boxplot(df),
    }
