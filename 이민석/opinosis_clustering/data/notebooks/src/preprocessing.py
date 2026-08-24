import re
import pandas as pd

def clean_text(text: str) -> str:
    """특수문자 제거 및 소문자 변환 등 기초 정제"""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.lower().strip()

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임에 전처리 및 통계량용 컬럼 추가"""
    df = df.copy()
    df['cleaned_review'] = df['review'].apply(clean_text)
    # 빈 리뷰 제거
    df = df[df['cleaned_review'].str.len() > 0].reset_index(drop=True)
    
    # 통계 분석용 리뷰 길이(단어 수 기준) 컬럼 추가
    df['review_len'] = df['cleaned_review'].apply(lambda x: len(x.split()))
    return df