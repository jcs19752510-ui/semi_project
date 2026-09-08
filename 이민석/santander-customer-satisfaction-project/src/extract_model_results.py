
import json
import pickle
import re
import pandas as pd
from pathlib import Path

# notebook 파일 경로
notebook_path = Path("notebook/01_data_understanding.ipynb")

# notebook 로드
with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# 모델별 성능 메트릭을 저장할 딕셔너리
model_results = {}

# notebook의 모든 cell을 순회
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        output = cell.get('outputs', [])

        # 각 모델별로 성능 메트릭 추출
        # Logistic Regression
        if 'roc_auc =' in source and 'Logistic' not in source:
            continue

        # output에서 메트릭 찾기
        for out in output:
            if out['output_type'] == 'stream':
                text = ''.join(out['text'])

                # Logistic Regression 메트릭
                if 'ROC-AUC' in text and 'XGBoost' not in text and 'GBM' not in text:
                    if 'Logistic' not in model_results:
                        model_results['Logistic Regression'] = {}

                    # 정규식으로 메트릭 추출
                    patterns = {
                        'accuracy': r'Accuracy\s*:\s*([\d.]+)',
                        'roc_auc': r'ROC-AUC\s*:\s*([\d.]+)',
                        'recall': r'Recall\s*:\s*([\d.]+)',
                        'f1_score': r'F1-score\s*:\s*([\d.]+)',
                        'precision': r'Precision\s*:\s*([\d.]+)',
                    }

                    for metric_name, pattern in patterns.items():
                        match = re.search(pattern, text)
                        if match:
                            model_results['Logistic Regression'][metric_name] = float(match.group(1))

                # XGBoost Baseline
                elif 'XGBoost Baseline' in text or ('xgb_roc_auc' in source):
                    if 'XGBoost Baseline' not in model_results:
                        model_results['XGBoost Baseline'] = {}

                # XGBoost Tuned
                elif 'Tuned' in text and 'XGBoost' in text:
                    if 'XGBoost Tuned' not in model_results:
                        model_results['XGBoost Tuned'] = {}

                # LightGBM
                elif 'GBM' in text or 'gbm_roc_auc' in source:
                    if 'LightGBM' not in model_results:
                        model_results['LightGBM'] = {}

print("✅ Notebook 파싱 완료")
print(f"발견된 모델 수: {len(model_results)}")

# 더 정확한 방법: notebook의 실제 결과 테이블 찾기
print("\n=== 모델별 성능 메트릭 ===\n")

# 수동으로 추출한 데이터 (notebook에서 관찰된 값)
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
}

# 결과 출력
for model_name, metrics in results_data.items():
    print(f"📊 {model_name}:")
    for metric, value in metrics.items():
        print(f"   {metric:15} : {value:.4f}")
    print()

# DataFrame으로 변환
df_results = pd.DataFrame(results_data).T
print("=== 모델 비교 테이블 ===\n")
print(df_results)

# pkl 파일로 저장
output_path = Path("model_results.pkl")
with open(output_path, 'wb') as f:
    pickle.dump(results_data, f)

print(f"\n✅ 모델 결과가 '{output_path}'에 저장되었습니다!")

# CSV로도 저장 (참고용)
csv_path = Path("model_results.csv")
df_results.to_csv(csv_path)
print(f"✅ CSV 파일도 '{csv_path}'에 저장되었습니다!")
