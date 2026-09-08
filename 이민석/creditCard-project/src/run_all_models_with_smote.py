"""
모든 모델(LightGBM, RandomForest, XGBoost, LogisticRegression)을 SMOTE 적용 후 학습하고 성능 지표 비교
"""
import sys
import pandas as pd
import numpy as np
sys.path.insert(0, 'src')

from loader import load_data, validate_data_quality
from preprocessing import preprocess_data
from models import (
    train_logistic_regression,
    train_random_forest,
    train_xgboost,
    apply_smote
)
from lightgbm import LGBMClassifier
from evaluation import evaluate_model
from sklearn.metrics import accuracy_score

# 1. 데이터 로드
print("="*60)
print("1단계: 데이터 로드")
print("="*60)
df = load_data('data/raw/creditcard.csv')
print(f"데이터 로드 완료: {df.shape}")

# 2. 데이터 품질 검증
print("\n" + "="*60)
print("2단계: 데이터 품질 검증")
print("="*60)
quality_report = validate_data_quality(df)
print(f"데이터 형태: {quality_report['shape']}")
print(f"결측치: {quality_report['missing_values']}")
print(f"중복값: {quality_report['duplicates']}")
print(f"클래스 분포: {quality_report['class_distribution']}")

# 3. 데이터 전처리
print("\n" + "="*60)
print("3단계: 데이터 전처리 (Train/Test 분리)")
print("="*60)
X_train, X_test, y_train, y_test, scaler = preprocess_data(df, test_size=0.2, random_state=42)
print(f"Train 데이터 (원본): {X_train.shape}")
print(f"Test 데이터: {X_test.shape}")
print(f"Train 클래스 분포 (원본): {pd.Series(y_train).value_counts().to_dict()}")

# 4. SMOTE 적용
print("\n" + "="*60)
print("4단계: SMOTE 적용 (불균형 데이터 해결)")
print("="*60)
X_train_smote, y_train_smote = apply_smote(X_train, y_train)
print(f"Train 데이터 (SMOTE 적용): {X_train_smote.shape}")
print(f"Train 클래스 분포 (SMOTE 후): {pd.Series(y_train_smote).value_counts().to_dict()}")
print(f"✓ SMOTE 적용 완료 - 소수 클래스 오버샘플링됨")

# 5. 모델 학습 및 평가
print("\n" + "="*60)
print("5단계: 모든 모델 학습 및 평가 (SMOTE 적용 데이터)")
print("="*60)

models = {}
results = {}

# 5-1. 로지스틱 회귀
print("\n[1/4] 로지스틱 회귀 학습 중...")
models['Logistic Regression'] = train_logistic_regression(X_train_smote, y_train_smote)
metrics_lr, probs_lr = evaluate_model(models['Logistic Regression'], X_test, y_test)
results['Logistic Regression'] = metrics_lr
print("✓ 로지스틱 회귀 학습 완료")

# 5-2. 랜덤 포레스트
print("[2/4] 랜덤 포레스트 학습 중...")
models['Random Forest'] = train_random_forest(X_train_smote, y_train_smote)
metrics_rf, probs_rf = evaluate_model(models['Random Forest'], X_test, y_test)
results['Random Forest'] = metrics_rf
print("✓ 랜덤 포레스트 학습 완료")

# 5-3. XGBoost
print("[3/4] XGBoost 학습 중...")
models['XGBoost'] = train_xgboost(X_train_smote, y_train_smote)
metrics_xgb, probs_xgb = evaluate_model(models['XGBoost'], X_test, y_test)
results['XGBoost'] = metrics_xgb
print("✓ XGBoost 학습 완료")

# 5-4. LightGBM
print("[4/4] LightGBM 학습 중...")
models['LightGBM'] = LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
models['LightGBM'].fit(X_train_smote, y_train_smote)
metrics_lgb, probs_lgb = evaluate_model(models['LightGBM'], X_test, y_test)
results['LightGBM'] = metrics_lgb
print("✓ LightGBM 학습 완료")

# 6. 결과 요약
print("\n" + "="*60)
print("📊 모델 성능 지표 비교 (SMOTE 적용)")
print("="*60)

# 결과를 DataFrame으로 변환
summary_data = []
accuracies = []
for model_name, model in models.items():
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracies.append(acc)

    metrics = results[model_name]
    summary_data.append({
        'Model': model_name,
        'Accuracy': acc,
        'Precision': metrics.get('Precision', 0),
        'Recall': metrics.get('Recall', 0),
        'F1-Score': metrics.get('F1-score', 0),
        'ROC-AUC': metrics.get('ROC-AUC', 0),
        'PR-AUC': metrics.get('PR-AUC', 0)
    })

summary_df = pd.DataFrame(summary_data)

print("\n" + summary_df.to_string(index=False))

# 7. 가장 좋은 모델 선정
print("\n" + "="*60)
print("🏆 모델 성능 순위 (F1-Score 기준)")
print("="*60)
rank_df = summary_df.sort_values('F1-Score', ascending=False)
for idx, (_, row) in enumerate(rank_df.iterrows(), 1):
    print(f"{idx}. {row['Model']:<20} - F1-Score: {row['F1-Score']:.4f}")

print("\n" + "="*60)
print("🏆 모델 성능 순위 (ROC-AUC 기준)")
print("="*60)
rank_df_auc = summary_df.sort_values('ROC-AUC', ascending=False)
for idx, (_, row) in enumerate(rank_df_auc.iterrows(), 1):
    print(f"{idx}. {row['Model']:<20} - ROC-AUC: {row['ROC-AUC']:.4f}")

# 8. 상세 혼동 행렬
print("\n" + "="*60)
print("📈 상세 성능 지표 (혼동 행렬)")
print("="*60)
for model_name, metrics in results.items():
    print(f"\n[{model_name}]")
    cm = metrics['Confusion Matrix']
    print(f"혼동 행렬:\n{cm}")
    print(f"  - True Negatives (TN):  {cm[0,0]}")
    print(f"  - False Positives (FP): {cm[0,1]}")
    print(f"  - False Negatives (FN): {cm[1,0]}")
    print(f"  - True Positives (TP):  {cm[1,1]}")

# 9. 결과 저장
print("\n" + "="*60)
print("💾 결과 저장 중...")
print("="*60)
summary_df.to_csv('model_performance_comparison_with_smote.csv', index=False)
print("✓ SMOTE 적용 결과를 'model_performance_comparison_with_smote.csv'에 저장했습니다.")

# 10. SMOTE 적용 전후 비교
print("\n" + "="*60)
print("📊 SMOTE 적용 전후 비교")
print("="*60)

# 원본 결과 로드
original_df = pd.read_csv('model_performance_comparison.csv')
smote_df = summary_df

print("\n[SMOTE 적용 전 (원본 데이터)]")
print(original_df[['Model', 'F1-Score', 'ROC-AUC', 'Recall']].to_string(index=False))

print("\n[SMOTE 적용 후]")
print(smote_df[['Model', 'F1-Score', 'ROC-AUC', 'Recall']].to_string(index=False))

print("\n[성능 개선도 (F1-Score 기준)]")
comparison_data = []
for orig_row, smote_row in zip(original_df.iterrows(), smote_df.iterrows()):
    orig_f1 = orig_row[1]['F1-Score']
    smote_f1 = smote_row[1]['F1-Score']
    improvement = ((smote_f1 - orig_f1) / orig_f1 * 100) if orig_f1 > 0 else 0

    comparison_data.append({
        'Model': orig_row[1]['Model'],
        'Before SMOTE': f"{orig_f1:.4f}",
        'After SMOTE': f"{smote_f1:.4f}",
        'Improvement %': f"{improvement:+.2f}%"
    })

comparison_df = pd.DataFrame(comparison_data)
print("\n" + comparison_df.to_string(index=False))

print("\n" + "="*60)
print("✅ SMOTE 적용 모든 모델 학습 및 평가 완료!")
print("="*60)
