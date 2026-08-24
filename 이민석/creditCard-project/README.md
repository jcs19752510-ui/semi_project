# 💳 Credit Card Fraud Detection & Prevention Pipeline

> **극심한 클래스 불균형(Class Imbalance) 환경 극복을 위한 16단계 엔드투엔드(End-to-End) 머신러닝 파이프라인**  
> 사기 탐지율(Recall) 극대화, 오탐지(False Positive) 최소화, 그리고 임계값 최적화 및 모델 해석(SHAP)을 아우르는 프로덕션급 금융 AI 파이프라인 프로젝트입니다.

---

## 🎯 1. Problem Definition (문제 정의 및 배경)

### 📌 비즈니스 배경
* **극단적인 클래스 불균형**: 신용카드 거래 데이터는 전체 거래량 중 사기(Fraud) 거래가 **1% 미만**을 차지하는 심각한 불균형 구조를 지닙니다.
* **Accuracy의 함정**: 단순 정확도(Accuracy) 지표에 의존할 경우, 모든 거래를 '정상'으로 예측하기만 해도 99% 이상의 Accuracy가 나오는 치명적인 한계가 존재합니다.

### 💡 핵심 해결 과제
1. **사기 누락 최소화 (Maximize Recall)**: 실제 사기 거래를 놓치는 경우(False Negative) 발생하는 직접적인 금전적 손실을 방어합니다.
2. **오탐지 제어 (Minimize False Positive)**: 정상 거래를 사기로 오인하여 차단할 때 발생하는 고객 불편(Customer Friction)과 브랜드 신뢰도 하락을 방지합니다.
3. **커스텀 임계값 최적화 (Threshold Tuning)**: 기본 분류 기준인 $0.5$를 탈피하여, 비즈니스 비용 함수에 부합하는 최적의 결정 임계값을 도출합니다.
4. **블랙박스 모델의 투명성 확보 (Explainability)**: 복잡한 앙상블 모델의 판정 근거를 SHAP을 통해 규명하여 현업의 수용성을 높입니다.

---

## 🛠 2. Tech Stack & Environment
* **Language**: Python 3.11.15
* **Core Machine Learning**: `Scikit-Learn`, `XGBoost`, `LightGBM`, `Gradient Boosting`
* **Imbalanced Learning**: `Imbalanced-Learn` (SMOTE)
* **Model Explainability**: `SHAP` (SHapley Additive exPlanations)
* **Serialization & Management**: `Joblib`, `Pandas`, `NumPy`, `Matplotlib`
* **Environment**: Jupyter Notebook (Incremental 16-Step Modular Pipeline)

---

## 🚀 3. 16-Step Pipeline Architecture
본 프로젝트는 데이터 수집부터 최종 배포 준비까지 총 16단계의 체계적인 모듈형 구조로 설계되었습니다.

```text
[Data & Prep] ──> [Imbalance Handling] ──> [Multi-Model Training] ──> [Optimization & Explain] ──> [Deployment]
  1. EDA           5. Imbalance Analysis   9. Model Diversification   13. Threshold Tuning      15. Serialization
  2. Cleansing     6. Baseline Modeling   10. Hyperparameter Tuning   14. SHAP Explainability   16. Documentation
  3. Feat. Eng.    7. Class Weight         11. Cross-Experimentation
  4. Train/Test    8. SMOTE Oversampling   12. Comprehensive Eval
```
## 📊 4. Key Results & Performance Insights

| Evaluation Metric / Feature | Baseline Model | Best Tuned Model (XGBoost + SMOTE) | Optimized Threshold Model |
| :--- | :---: | :---: | :---: |
| **ROC-AUC** | 0.9446 | **0.9844** | **0.9844** |
| **PR-AUC** | 0.8373 | **0.8445** | **0.8411** |
| **Recall (사기 탐지율)** | 0.7755 | **0.8878** | **0.7143** |
| **Precision (정밀도)** | 0.9157 | 0.2444 | **0.9859** |
| **False Positives (오탐지)** | ~10건 미만 | 수백 건 (오탐 증가) | **1건 (극소화)** |

> **💡 핵심 인사이트 요약**
> * **클래스 불균형 보정의 효과**: `SMOTE` 및 `Scale Weight`를 적용했을 때 사기 포착률(`Recall`)이 최대 **88.78%**까지 대폭 향상되었습니다.
> * **임계값 최적화 (`Threshold = 0.9979`)**: 기본값($0.5$)을 탈피하여 F1-Score를 극대화한 결과, 정상 거래 오탐지(False Positive)를 **단 1건**(`[[56863, 1]]`)으로 철저히 통제하는 데 성공했습니다.
> * **SHAP 모델 해석**: `V14`, `V4`, `V12` 등의 PCA 성분이 사기 판별에 가장 지대한 영향을 미치며, 특정 임계값 하락 시 사기 확률이 비선형적으로 급증함을 입증했습니다.

---

## 📁 5. Project Directory Structure

프로젝트의 모든 소스 코드와 산출물은 깃허브 표준 구조에 맞춰 `outputs/` 디렉토리 아래 체계적으로 관리됩니다.

```text
├── outputs/
│   ├── data/
│   │   └── credit_card_processed.csv    # 전처리 및 SMOTE 증강 완료된 데이터셋
│   ├── figure/
│   │   ├── feature_importance.png       # XGBoost Feature Importance 시각화
│   │   ├── shap_summary_bar.png         # SHAP Summary Bar Plot
│   │   └── shap_beeswarm.png            # SHAP Beeswarm Plot (방향성 해석)
│   ├── table/
│   │   └── model_performance_summary.csv # 5개 모델 다각도 성능 비교 표
│   └── model/
│       ├── credit_fraud_xgboost_model.pkl          # 최종 직렬화된 XGBoost 객체
│       ├── credit_fraud_random_forest_model.pkl    # 직렬화된 Random Forest 객체
│       ├── credit_fraud_lightgbm_model.pkl         # 직렬화된 LightGBM 객체
│       ├── credit_fraud_logistic_regression_model.pkl # 직렬화된 Logistic Regression 객체
│       └── credit_fraud_gradient_boosting_model.pkl # 직렬화된 GBM 객체
├── 01_credit_card_fraud_pipeline.ipynb      # 메인 16단계 일체형 주피터 노트북
└── README.md                                # 프로젝트 공식 소개서
```

