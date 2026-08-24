import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preprocess_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """07단계: Time 변환, Amount 스케일링 및 Train/Test 분리"""
    df_processed = df.copy()
    
    # Time 변환 예시: 초 단위를 시간(0~23)으로 변환 (필요시 활용)
    # df_processed['Hour'] = (df_processed['Time'] // 3600) % 24
    
    # Amount 스케일링 (RobustScaler 또는 StandardScaler)
    scaler = StandardScaler()
    df_processed['Amount_Scaled'] = scaler.fit_transform(df_processed[['Amount']])
    
    # 원본 Amount 및 Time 처리 (필요에 따라 드롭하거나 유지)
    # 여기서는 기존 Amount 대신 스케일된 Amount를 쓰거나 함께 유지 가능
    X = df_processed.drop(columns=['Class', 'Amount']) # 필요시 Time도 드롭 가능
    y = df_processed['Class']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    return X_train, X_test, y_train, y_test, scaler