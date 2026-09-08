# 신용카드 사기 탐지 프로젝트 (Credit Card Fraud Detection)

## 📋 프로젝트 개요

본 프로젝트는 머신러닝 기법을 활용하여 신용카드 거래에서 사기를 탐지하는 분류(Classification) 문제를 다룹니다. 
불균형 데이터셋 처리, 다양한 머신러닝 모델의 비교 및 성능 평가, 모델 해석을 포함합니다.

### 주요 특징
- ✅ **다중 모델 비교**: Logistic Regression, Random Forest, XGBoost, LightGBM
- ✅ **불균형 데이터 처리**: SMOTE를 이용한 오버샘플링
- ✅ **상세한 성능 평가**: Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC
- ✅ **모델 해석**: SHAP을 이용한 특성 중요도 분석
- ✅ **통계 분석**: 효과 크기(Effect Size), 상관관계 분석

---

## 📁 프로젝트 구조

```
creditCard-project/
├── data/
│   └── raw/
│       └── creditcard.csv          # 원본 신용카드 거래 데이터
├── notebooks/
│   └── 01_main_analysis.ipynb      # 종합 분석 노트북
├── src/
│   ├── __init__.py
│   ├── config.py                   # 프로젝트 설정 및 경로 정의
│   ├── loader.py                   # 데이터 로드 및 검증
│   ├── preprocessing.py            # 데이터 전처리 및 스케일링
│   ├── models.py                   # 머신러닝 모델 정의
│   ├── evaluation.py               # 모델 성능 평가
│   ├── stats.py                    # 통계 분석 (효과 크기 등)
│   ├── interpret.py                # SHAP을 이용한 모델 해석
│   ├── run_all_models.py           # 모든 모델 학습 및 평가 실행 스크립트
│   ├── run_all_models_with_smote.py # SMOTE 적용 후 모델 학습 및 평가 스크립트
│   ├── visualize_results.py        # 결과 시각화
│   └── visualize_smote_comparison.py # SMOTE 적용 전후 비교 시각화
├── outputs/
│   ├── figures/                    # 시각화 결과 (PNG 이미지)
│   │   ├── EDA (탐색적 데이터 분석)
│   │   ├── 상관관계 히트맵
│   │   ├── 모델 성능 비교
│   │   ├── SMOTE 비교
│   │   ├── SHAP 분석 결과
│   │   └── ...
│   └── models/                     # 학습된 모델 저장 (pickle)
│       ├── credit_fraud_*_model.pkl
│       ├── model_performance_comparison.csv
│       └── model_performance_comparison_with_smote.csv
├── requirements.txt                # 필요 라이브러리
└── README.md                       # 본 문서
```

---

## 🛠️ 필요한 라이브러리

```
pandas              # 데이터 조작 및 분석
numpy              # 수치 계산
scikit-learn       # 머신러닝 모델 및 평가 도구
xgboost            # XGBoost 모델
lightgbm           # LightGBM 모델
imbalanced-learn   # SMOTE 및 불균형 데이터 처리
shap               # SHAP을 이용한 모델 해석
statsmodels        # 통계 분석
```

### 설치 방법

```bash
pip install -r requirements.txt
```

---

## 📊 데이터셋

### 데이터 출처
[Kaggle Credit Card Fraud Detection Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

### 📥 데이터 다운로드 방법

#### **방법 1: Kaggle 웹사이트에서 직접 다운로드** (권장)

1. **Kaggle 계정 생성** (없을 경우)
   - https://www.kaggle.com 방문
   - 회원가입 완료

2. **데이터셋 페이지 방문**
   - https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud 접속

3. **데이터 다운로드**
   - "Download" 버튼 클릭
   - `creditcard.csv` 파일 다운로드

4. **프로젝트에 저장**
   ```bash
   # 다운로드 받은 파일을 다음 위치에 저장
   data/raw/creditcard.csv
   ```

#### **방법 2: Kaggle API를 이용한 자동 다운로드**

```bash
# 1. Kaggle API 설치
pip install kaggle

# 2. Kaggle API 토큰 설정
# https://www.kaggle.com/account에서 "Create New API Token" 클릭
# 다운로드된 kaggle.json을 ~/.kaggle/ 폴더에 이동
# (Windows: C:\Users\[사용자명]\.kaggle\)

# 3. 데이터셋 다운로드
kaggle datasets download -d mlg-ulb/creditcardfraud

# 4. 압축 해제 및 이동
unzip creditcardfraud.zip
mv creditcard.csv data/raw/
```

### 📋 데이터 특징
- **샘플 수**: 약 28,000개
- **특성(Features)**: 30개 (V1~V28, Amount, Time)
- **목표 변수**: Class (0: 정상, 1: 사기)
- **클래스 불균형**: 약 99.8% 정상, 0.2% 사기 (심각한 불균형)
- **파일 크기**: 약 69.2 MB

### 🔧 전처리 작업
1. Amount 컬럼 표준화 (Standard Scaling)
2. Time 컬럼 표준화
3. Train/Test 분리 (80/20)

---

## 🤖 머신러닝 모델

### 1. 로지스틱 회귀 (Logistic Regression)
- **설명**: 선형 분류 모델
- **장점**: 해석 가능성이 높음, 계산 속도 빠름
- **단점**: 비선형 관계 포착 어려움

### 2. 랜덤 포레스트 (Random Forest)
- **설명**: 앙상블 기반 트리 모델
- **장점**: 비선형 관계 잘 포착, 특성 중요도 제공
- **단점**: 모델 크기가 큼, 해석이 어려울 수 있음

### 3. XGBoost
- **설명**: Gradient Boosting 기반 모델
- **장점**: 높은 성능, 불균형 데이터 처리 용이, 빠른 학습
- **단점**: 하이퍼파라미터 튜닝 필요

### 4. LightGBM
- **설명**: 경량 Gradient Boosting 모델
- **장점**: 메모리 효율적, 빠른 학습 속도
- **단점**: 작은 데이터셋에서 과적합 가능성

---

## 🔧 주요 기법

### SMOTE (Synthetic Minority Over-sampling Technique)
불균형 데이터셋에서 소수 클래스(사기)를 인위적으로 생성하여 클래스 균형을 맞추는 기법입니다.

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

### SHAP (SHapley Additive exPlanations)
각 특성이 모델의 예측에 어느 정도 영향을 미치는지 분석하는 모델 해석 기법입니다.

---

## 📈 성능 평가 지표

| 지표 | 설명 |
|------|------|
| **Accuracy** | 전체 샘플 중 올바르게 분류된 비율 |
| **Precision** | 사기로 예측한 것 중 실제 사기의 비율 |
| **Recall** | 실제 사기 중 올바르게 탐지한 비율 |
| **F1-Score** | Precision과 Recall의 조화평균 |
| **ROC-AUC** | 거짓양성률 대 진정양성률의 곡선 아래 면적 |
| **PR-AUC** | Precision-Recall 곡선 아래 면적 |

### 불균형 데이터셋에서의 지표 선택
- ✅ **추천**: Recall, F1-Score, ROC-AUC, PR-AUC
- ⚠️ **주의**: Accuracy (대다수 클래스에 편향됨)

---

## ⚡ 빠른 시작

```bash
# 1. 저장소 클론
git clone <repository-url>
cd creditCard-project

# 2. 필요한 라이브러리 설치
pip install -r requirements.txt

# 3. Kaggle에서 데이터 다운로드
# (위의 "데이터 다운로드 방법" 섹션 참고)
# data/raw/creditcard.csv 경로에 저장

# 4. 모든 모델 학습 및 평가 실행
python src/run_all_models.py

# 5. 결과 시각화
python src/visualize_results.py

# 6. Jupyter 노트북으로 분석 보기
jupyter notebook notebooks/01_main_analysis.ipynb
```

---

## 🚀 사용 방법

### 1. 모든 모델 학습 및 평가 (SMOTE 미적용)

```bash
python src/run_all_models.py
```

**출력 결과**:
- 모델별 성능 지표 비교표
- 혼동 행렬 (Confusion Matrix)
- 결과 CSV 저장: `model_performance_comparison.csv`

### 2. SMOTE 적용 후 모델 학습 및 평가

```bash
python src/run_all_models_with_smote.py
```

**출력 결과**:
- SMOTE 적용 후 모델별 성능 지표 비교표
- 결과 CSV 저장: `model_performance_comparison_with_smote.csv`

### 3. 결과 시각화

```bash
python src/visualize_results.py
python src/visualize_smote_comparison.py
```

**생성되는 시각화**:
- EDA 시각화 (분포, 상관관계)
- 모델 성능 비교 차트
- ROC 곡선, PR 곡선
- SHAP 분석 결과
- SMOTE 적용 전후 비교

### 4. Jupyter 노트북 분석

```bash
jupyter notebook notebooks/01_main_analysis.ipynb
```

---

## 📊 출력 결과

### 모델 성능 비교 (SMOTE 미적용)
`outputs/models/model_performance_comparison.csv`

### 모델 성능 비교 (SMOTE 적용)
`outputs/models/model_performance_comparison_with_smote.csv`

### 학습된 모델 파일
```
outputs/models/
├── credit_fraud_logistic_regression_model.pkl
├── credit_fraud_random_forest_model.pkl
├── credit_fraud_xgboost_model.pkl
└── credit_fraud_lightgbm_model.pkl
```

### 시각화 결과
```
outputs/figures/
├── 04_eda_correlation_heatmap.png
├── 04_eda_distributions.png
├── 05_eda_v_distributions_sample.png
├── 06_correlation_heatmap_all.png
├── 07_eda_effect_size.png
├── 08_logistic_odds_ratio.png
├── 09_confusion_matrix.png
├── 09_odds_ratio_forest_plot.png
├── 10_pr_curve.png
├── auc_comparison.png
├── feature_importance.png
├── model_performance_comparison.png
├── performance_heatmap.png
├── radar_chart.png
├── shap_beeswarm.png
├── shap_summary_bar.png
├── smote_detailed_comparison.png
├── smote_f1score_comparison.png
├── smote_recall_comparison.png
└── smote_roc_auc_comparison.png
```

---

## 📋 파일별 설명

### `src/config.py`
프로젝트 전체에서 사용할 설정값과 경로를 정의합니다.
```python
BASE_DIR: 프로젝트 루트 디렉토리
DATA_DIR: 데이터 디렉토리
OUTPUT_DIR: 출력 디렉토리
RANDOM_STATE: 재현성을 위한 난수 시드
TEST_SIZE: Train/Test 분리 비율
TARGET_COL: 목표 변수 이름
```

### `src/loader.py`
- `load_data()`: CSV 파일에서 데이터 로드
- `validate_data_quality()`: 데이터 품질 검증 (결측치, 중복값, 클래스 분포)

### `src/preprocessing.py`
- `preprocess_data()`: 데이터 정규화 및 Train/Test 분리
- StandardScaler를 사용하여 특성 표준화

### `src/models.py`
- `train_logistic_regression()`: 로지스틱 회귀 모델 학습
- `train_random_forest()`: 랜덤 포레스트 모델 학습
- `train_xgboost()`: XGBoost 모델 학습
- `apply_smote()`: SMOTE 오버샘플링 적용

### `src/evaluation.py`
- `evaluate_model()`: 모델 성능 평가
- 계산 지표: Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC, 혼동 행렬

### `src/stats.py`
- `calculate_effect_size()`: 효과 크기(Effect Size, Cohen's d) 계산
- 통계적 유의성 분석

### `src/interpret.py`
- SHAP을 이용한 모델 해석
- 특성 중요도 시각화

### `src/run_all_models.py`
통합 실행 스크립트:
1. 데이터 로드
2. 데이터 품질 검증
3. 데이터 전처리
4. 모든 모델 학습 및 평가
5. 성능 비교 및 순위 매김
6. 결과 저장

### `src/run_all_models_with_smote.py`
SMOTE 적용 후 모델 학습 및 평가

### `src/visualize_results.py`
결과 시각화:
- EDA 시각화
- 모델 성능 비교
- ROC/PR 곡선
- SHAP 분석

### `src/visualize_smote_comparison.py`
SMOTE 적용 전후 성능 비교 시각화

---

## 🔍 주요 분석 항목

### 1. 탐색적 데이터 분석 (EDA)
- 특성 분포 분석
- 상관관계 분석
- 클래스별 특성 비교

### 2. 모델 성능 비교
- SMOTE 미적용 vs 적용
- 모델별 성능 순위
- 지표별 비교 (F1-Score, ROC-AUC)

### 3. 통계 분석
- 효과 크기 (Cohen's d)
- 로지스틱 회귀의 오즈비 (Odds Ratio)

### 4. 모델 해석
- SHAP을 이용한 특성 기여도
- 개별 예측 해석

---

## 💡 주요 발견사항

### SMOTE의 효과
- **Recall 향상**: SMOTE 적용으로 사기 탐지율(Recall)이 대폭 향상
- **Precision 조정 필요**: SMOTE 적용 시 거짓양성(False Positive)이 증가할 수 있으므로 Precision 모니터링 필요

### 모델 성능
- **LightGBM/XGBoost**: 부스팅 기반 모델들이 일반적으로 높은 성능 발휘
- **로지스틱 회귀**: 해석 가능성이 높으며, 간단한 모델로도 양호한 성능 달성 가능

---

## 🎯 개선 사항

1. **하이퍼파라미터 튜닝**: GridSearchCV/RandomizedSearchCV를 통한 최적 파라미터 찾기
2. **교차검증**: K-Fold 교차검증으로 모델 성능의 안정성 검증
3. **앙상블 기법**: 여러 모델을 결합한 앙상블 방식 시도
4. **비용 민감 학습**: 사기 탐지의 비용을 고려한 맞춤형 가중치 적용
5. **특성 엔지니어링**: 새로운 특성 생성 및 선택

---

## 📝 참고사항

### 데이터 불균형 문제
신용카드 사기 데이터는 극도로 불균형된 데이터셋입니다. 따라서:
- Accuracy만으로는 모델 성능을 판단하기 어려움
- Recall, F1-Score, ROC-AUC 등 여러 지표를 종합적으로 평가해야 함
- SMOTE 같은 오버샘플링 기법의 신중한 적용 필요

### 모델 선택 기준
- **실제 운영 환경**: 사기 탐지 비용 vs 놓친 사기 손실을 고려하여 Recall/Precision 트레이드오프 결정
- **해석 필요성**: 모델의 결정 이유를 설명해야 한다면 로지스틱 회귀나 SHAP 활용
- **성능**: 최고의 성능이 필요하면 부스팅 기반 모델 (XGBoost, LightGBM)

---

## 👨‍💼 프로젝트 관리자

**이민석**

---

## 📄 라이선스

본 프로젝트는 교육 목적으로 제작되었습니다.

---

## 📞 문의

프로젝트에 대한 질문이나 개선 사항이 있으시면 연락주시기 바랍니다.

---

**마지막 업데이트**: 2026-09-02
