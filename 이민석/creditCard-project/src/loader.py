import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """CSV 파일로부터 데이터를 로드합니다."""
    df = pd.read_csv(file_path)
    return df

def validate_data_quality(df: pd.DataFrame) -> dict:
    """03단계: 데이터 품질 검증 (결측치, 중복값, 기본 통계 확인)"""
    quality_report = {
        "shape": df.shape,
        "missing_values": df.isnull().sum().sum(),
        "duplicates": df.duplicated().sum(),
        "class_distribution": df['Class'].value_counts(normalize=True).to_dict()
    }
    return quality_report