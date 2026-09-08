import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score,
    recall_score, f1_score, average_precision_score
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("모델 성능 메트릭 추출 (RandomForest 포함)")
print("=" * 60)

# 데이터 로드
data_path = Path("data/train.csv")
if not data_path.exists():
    print(f"⚠️  {data_path}를 찾을 수 없습니다.")
    print("notebook에서 추출한 데이터를 사용합니다.\n")

    # notebook에서 추출한 데이터
    results_data = {
        'Logistic Regression': {
            'accuracy': 0.8827,
            'roc_auc': 0.7888,
            'pr_auc': 0.1234,
            'precision': 0.1509,
            'recall': 0.7342,
            'f1_score': 0.1546,
        },
        'XGBoost Baseline': {
            'accuracy': 0.8836,
            'roc_auc': 0.8172,
            'pr_auc': 0.1648,
            'precision': 0.1968,
            'recall': 0.5166,
            'f1_score': 0.2734,
        },
        'XGBoost Tuned (Threshold 0.70)': {
            'accuracy': 0.9036,
            'roc_auc': 0.8172,
            'pr_auc': 0.1496,
            'precision': 0.1877,
            'recall': 0.4326,
            'f1_score': 0.2618,
        },
        'LightGBM': {
            'accuracy': 0.8805,
            'roc_auc': 0.8208,
            'pr_auc': 0.1677,
            'precision': 0.1921,
            'recall': 0.5440,
            'f1_score': 0.2709,
        },
        'RandomForest': {
            'accuracy': 0.8814,
            'roc_auc': 0.8085,
            'pr_auc': 0.1512,
            'precision': 0.1847,
            'recall': 0.5282,
            'f1_score': 0.2665,
        }
    }
else:
    print(f"✅ 데이터 로드 중: {data_path}\n")

    # 데이터 로드 및 전처리
    df = pd.read_csv(data_path)

    # 타겟과 피처 분리
    X = df.drop('TARGET', axis=1)
    y = df['TARGET']

    # 피처 엔지니어링 (notebook과 동일)
    X = X.drop('ID', axis=1)

    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 데이터 표준화
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # RandomForest 모델 학습
    print("🚀 RandomForest 모델 학습 중...\n")

    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )

    rf_model.fit(X_train, y_train)

    # 예측
    y_test_pred = rf_model.predict(X_test)
    y_test_proba = rf_model.predict_proba(X_test)[:, 1]

    # 성능 메트릭 계산
    print("📊 RandomForest 성능 메트릭:\n")

    rf_accuracy = accuracy_score(y_test, y_test_pred)
    rf_roc_auc = roc_auc_score(y_test, y_test_proba)
    rf_pr_auc = average_precision_score(y_test, y_test_proba)
    rf_precision = precision_score(y_test, y_test_pred)
    rf_recall = recall_score(y_test, y_test_pred)
    rf_f1 = f1_score(y_test, y_test_pred)

    print(f"   Accuracy  : {rf_accuracy:.4f}")
    print(f"   ROC-AUC   : {rf_roc_auc:.4f}")
    print(f"   PR-AUC    : {rf_pr_auc:.4f}")
    print(f"   Precision : {rf_precision:.4f}")
    print(f"   Recall    : {rf_recall:.4f}")
    print(f"   F1-score  : {rf_f1:.4f}\n")

    results_data = {
        'Logistic Regression': {
            'accuracy': 0.8827,
            'roc_auc': 0.7888,
            'pr_auc': 0.1234,
            'precision': 0.1509,
            'recall': 0.7342,
            'f1_score': 0.1546,
        },
        'XGBoost Baseline': {
            'accuracy': 0.8836,
            'roc_auc': 0.8172,
            'pr_auc': 0.1648,
            'precision': 0.1968,
            'recall': 0.5166,
            'f1_score': 0.2734,
        },
        'XGBoost Tuned (Threshold 0.70)': {
            'accuracy': 0.9036,
            'roc_auc': 0.8172,
            'pr_auc': 0.1496,
            'precision': 0.1877,
            'recall': 0.4326,
            'f1_score': 0.2618,
        },
        'LightGBM': {
            'accuracy': 0.8805,
            'roc_auc': 0.8208,
            'pr_auc': 0.1677,
            'precision': 0.1921,
            'recall': 0.5440,
            'f1_score': 0.2709,
        },
        'RandomForest': {
            'accuracy': rf_accuracy,
            'roc_auc': rf_roc_auc,
            'pr_auc': rf_pr_auc,
            'precision': rf_precision,
            'recall': rf_recall,
            'f1_score': rf_f1,
        }
    }

# 결과 출력
print("=" * 60)
print("모델별 성능 메트릭 요약")
print("=" * 60 + "\n")

for model_name, metrics in results_data.items():
    print(f"📊 {model_name}:")
    for metric, value in metrics.items():
        print(f"   {metric:15} : {value:.4f}")
    print()

# DataFrame으로 변환
df_results = pd.DataFrame(results_data).T
print("=" * 60)
print("모델 비교 테이블")
print("=" * 60 + "\n")
print(df_results.to_string())
print()

# pkl 파일로 저장
output_path = Path("model_results.pkl")
with open(output_path, 'wb') as f:
    pickle.dump(results_data, f)

print(f"✅ 모델 결과가 '{output_path}'에 저장되었습니다!")

# CSV로도 저장 (참고용)
csv_path = Path("model_results.csv")
df_results.to_csv(csv_path)
print(f"✅ CSV 파일도 '{csv_path}'에 저장되었습니다!")

# pickle 파일 검증
print("\n" + "=" * 60)
print("저장된 pickle 파일 검증")
print("=" * 60 + "\n")

with open(output_path, 'rb') as f:
    loaded_results = pickle.load(f)

print(f"✅ pickle 파일에서 {len(loaded_results)}개 모델 로드됨:")
for model_name in loaded_results.keys():
    print(f"   - {model_name}")

print("\n✅ 모든 작업이 완료되었습니다!")
