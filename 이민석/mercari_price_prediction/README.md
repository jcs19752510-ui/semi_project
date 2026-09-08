# Mercari 상품 가격 예측 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 온라인 중고거래 플랫폼 **Mercari**의 상품 데이터를 분석하여 상품의 특성을 기반으로 판매 가격을 예측하는 머신러닝 모델을 구축합니다.

단순한 가격 예측에 그치지 않고, 통계적 분석과 머신러닝을 함께 활용하여 **가격 결정 요인을 해석**하고 **예측 모델의 성능을 비교**하는 것을 목표로 합니다.

## 🎯 핵심 분석 질문

1. **상품의 어떤 특성이 가격에 유의한 영향을 미치는가?**
2. **상품의 특성을 이용하여 가격을 얼마나 정확하게 예측할 수 있는가?**
3. **통계적으로 확인된 가격 결정 요인과 머신러닝 모델이 중요하게 판단한 변수는 어떻게 다른가?**

## 📁 프로젝트 구조

```
mercari_price_prediction/
├── data/
│   ├── raw/
│   │   └── mercari_train.tsv          # 원본 데이터 (약 1.4M 행)
│   └── processed/
│       ├── mercari_preprocessed.pkl   # 전처리된 데이터
│       ├── X_final.pkl                # 최종 특성 데이터
│       ├── y.pkl                      # 가격 데이터
│       ├── y_log.pkl                  # 로그 변환된 가격
│       ├── tfidf_lemmatized_fixed.npz # TF-IDF 벡터 (텍스트)
│       └── model_summary_fixed.txt    # 모델 성능 요약
├── notebooks/
│   ├── 00_problem_definition.ipynb    # 문제 정의
│   ├── 01_data_understanding.ipynb    # 데이터 이해
│   ├── 03_eda.ipynb                   # 탐색적 데이터 분석
│   ├── 04_preprocessing.ipynb         # 데이터 전처리
│   ├── 05_statistical_analysis.ipynb  # 통계적 분석 (다중회귀)
│   ├── 06_Machine_Learning.ipynb      # 머신러닝 기본 모델
│   ├── 07_Ridge.ipynb                 # Ridge 회귀
│   ├── 08_LightGBM.ipynb              # LightGBM 모델
│   ├── 09_Lemmatization.ipynb         # 텍스트 어근추출 및 TF-IDF
│   └── 10_GBM_RandomForest_Fixed.ipynb # GBM & Random Forest 모델
├── models/
│   ├── ridge_lemmatized_model_fixed.pkl              # Ridge 모델 (최고 성능)
│   ├── lightgbm_lemmatized_model_fixed.pkl           # LightGBM 모델
│   ├── gbm_lemmatized_model_fixed.pkl                # GBM 모델
│   ├── randomforest_lemmatized_model_fixed.pkl       # Random Forest 모델
│   └── all_models_results_fixed.csv                  # 모델 성능 비교
└── outputs/
    └── figures/
        ├── price_distribution.png                     # 가격 분포
        ├── 02_log_price_distribution.png              # 로그 가격 분포
        ├── 03_high_price_outliers.png                 # 이상치
        ├── 04_item_condition_distribution.png         # 상품 상태별 분포
        ├── 05_shipping_distribution.png               # 배송 관련 분포
        ├── 06_top20_category_distribution.png         # 카테고리 분석
        ├── 07_top20_brand_distribution.png            # 브랜드 분석
        ├── 08_condition_price_median.png              # 상태별 중앙값
        ├── model_comparison_fixed.png                 # 모델 성능 비교
        └── 05_residual_distribution.png               # 잔차 분석
```

## 📊 데이터 정보

- **데이터셋**: Mercari 상품 판매 데이터
- **크기**: 약 1.4M 행
- **주요 변수**:
  - 범주형: category_name, brand_name, item_condition_id, shipping
  - 수치형: price (목표변수)
  - 텍스트: name, item_description
- **타겟**: 상품 가격 (log 스케일로 변환)

## 🔍 분석 단계

### 1️⃣ 탐색적 데이터 분석 (EDA)
- 가격 분포 및 이상치 분석
- 카테고리, 브랜드, 상품 상태별 가격 비교
- 배송비 부담 여부와 가격의 관계 파악

### 2️⃣ 통계적 분석
- 다중회귀분석을 통한 가격 결정 요인 검증
- 회귀계수, 유의확률, 신뢰구간 분석
- 다중공선성(VIF) 확인

### 3️⃣ 특성 공학 (Feature Engineering)
- 범주형 변수 인코딩
- 텍스트 데이터 어근추출(Lemmatization)
- TF-IDF를 이용한 텍스트 벡터화

### 4️⃣ 머신러닝 모델링
- **Ridge 회귀** (선형 정규화)
- **LightGBM** (부스팅)
- **XGBoost** (부스팅)
- **Gradient Boosting** (부스팅)
- **Random Forest** (앙상블)

### 5️⃣ 모델 평가
- RMSLE (Root Mean Squared Logarithmic Error) 기준
- 잔차 분석
- Feature Importance 분석

## 🏆 최종 결과

| 순위 | 모델명 | RMSLE | 설명 |
|:----:|:-----:|:-----:|:----:|
| 1 | **Ridge (Ch.9)** | **0.4836** | ✅ 최고 성능 (텍스트 포함) |
| 2 | LightGBM (Ch.9) | 0.5036 | 텍스트 포함 |
| 3 | XGBoost (Ch.9) | 0.5038 | 텍스트 포함 |
| 4 | GBM (Ch.10) | 0.5520 | 정형 특성만 |
| 5 | Random Forest (Ch.10) | 0.6954 | 정형 특성만 |

### 🌟 주요 발견

- **텍스트 데이터의 중요성**: 상품명과 상품 설명의 TF-IDF 특성이 가격 예측에 큰 영향을 미침
- **Ridge 회귀의 효과성**: 복잡한 비선형 모델보다 규제화된 선형 모델이 더 우수한 성능 달성
- **특성 개수의 영향**: 정형 특성(297개)만 사용할 때보다 텍스트 특성을 추가했을 때 성능 향상

## 🛠 주요 기술 스택

- **데이터 처리**: Python, Pandas, NumPy
- **시각화**: Matplotlib, Seaborn
- **텍스트 처리**: NLTK (Lemmatization), scikit-learn (TF-IDF)
- **머신러닝**: scikit-learn, LightGBM, XGBoost
- **분석**: Jupyter Notebook, scipy (통계분석)

## 📝 사용 방법

### 1. 데이터 로드
```python
import pickle

# 전처리된 데이터 로드
with open('data/processed/X_final.pkl', 'rb') as f:
    X = pickle.load(f)
    
with open('data/processed/y_log.pkl', 'rb') as f:
    y = pickle.load(f)
```

### 2. 모델 로드 및 예측
```python
# Ridge 모델 로드
with open('models/ridge_lemmatized_model_fixed.pkl', 'rb') as f:
    model = pickle.load(f)

# 예측
predictions = model.predict(X_new)
```

### 3. 노트북 실행
각 단계별 분석은 `notebooks/` 폴더의 노트북들을 순서대로 실행하면 됩니다.
- 01_data_understanding → 03_eda → 04_preprocessing → 05_statistical_analysis → 06_Machine_Learning 등

## 📌 주의사항

- `data/raw/mercari_train.tsv` 파일은 크기가 크므로 `.gitignore`에 등록되어 있습니다
- 모델 재학습이 필요한 경우 해당 노트북을 실행하면 됩니다
- 특성 공학 재적용이 필요한 경우 09_Lemmatization.ipynb를 먼저 실행하세요

## 👨‍💻 프로젝트 작성자

이민석

## 📅 프로젝트 기간

2024-2025

## 📚 참고 자료

- Problem Definition: notebooks/00_problem_definition.ipynb
- 모델 성능 요약: data/processed/model_summary_fixed.txt
- 모든 분석 결과: notebooks/ 폴더의 각 Jupyter 노트북

---

**마지막 업데이트**: 2026년 9월
