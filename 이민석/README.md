# 📊 머신러닝 & 데이터 분석 프로젝트 모음

## 🎯 프로젝트 개요

이 저장소는 **머신러닝, 데이터 분석, 텍스트 마이닝** 등 다양한 데이터 과학 프로젝트들을 한곳에 모은 포트폴리오입니다. 각 프로젝트는 실제 데이터셋을 활용한 **실습 프로젝트**이며, 상세한 분석과 높은 수준의 모델 구현을 포함합니다.

### 🌟 핵심 특징

- ✅ **다양한 도메인**: 금융(사기탐지), 이커머스(가격예측), 서비스(고객만족도), 텍스트분석(의견군집화)
- ✅ **완전한 파이프라인**: 데이터 수집부터 모델 배포까지의 전 과정 포함
- ✅ **상세한 분석**: EDA, 통계분석, 머신러닝 모델링, 해석
- ✅ **재현 가능성**: 모든 코드와 결과 재현 가능한 형태로 구성
- ✅ **교육 자료**: 주석이 풍부하고 실행 가능한 노트북 제공

---

## 📁 프로젝트 구조

```
SEMI_Project/
├── 📦 creditCard-project/                    # 신용카드 사기 탐지
│   ├── 📊 데이터: 28K+ 거래 데이터
│   ├── 🤖 모델: Logistic Regression, Random Forest, XGBoost, LightGBM
│   └── 📈 성능지표: ROC-AUC, Precision, Recall, F1-Score
│
├── 📦 mercari_price_prediction/              # 상품 가격 예측
│   ├── 📊 데이터: 1.4M+ 상품 데이터
│   ├── 🤖 모델: Ridge, LightGBM, XGBoost, GBM, Random Forest
│   └── 📈 성능지표: RMSLE (0.4836 - 최고 성능)
│
├── 📦 opinosis_clustering/                   # 의견 주제 군집화 & 감성분석
│   ├── 📊 데이터: 51개 제품-속성 리뷰 데이터
│   ├── 🎯 기법: K-means Clustering, 감성분석, 회귀분석
│   └── 📈 결과: 주제별 감성 영향도 정량화
│
├── 📦 santander-customer-satisfaction-project/ # 고객 만족도 예측
│   ├── 📊 데이터: 37K+ 은행 고객 데이터
│   ├── 🤖 모델: Logistic Regression, Random Forest, XGBoost, LightGBM
│   └── 📈 성능지표: ROC-AUC, Feature Importance, SHAP 분석
│
└── 📄 README.md                              # 이 파일
```

---

## 🚀 빠른 시작

### 1️⃣ 저장소 클론

```bash
git clone https://github.com/pkbrb77-sudo/SEMI_Project.git
cd SEMI_Project
```

### 2️⃣ 각 프로젝트별 시작

#### 💳 신용카드 사기 탐지
```bash
cd creditCard-project
pip install -r requirements.txt
python src/run_all_models.py
```

#### 💰 상품 가격 예측
```bash
cd mercari_price_prediction
# 데이터 다운로드 후 실행
jupyter notebook notebooks/00_problem_definition.ipynb
```

#### 💬 의견 군집화 & 감성분석
```bash
cd opinosis_clustering
pip install -r requirements.txt
jupyter notebook notebooks/kmeans_clustering.ipynb
```

#### 👥 고객 만족도 예측
```bash
cd santander-customer-satisfaction-project
jupyter notebook notebook/PipeLine.ipynb
```

---

## 📋 프로젝트 상세 정보

### 1. 💳 신용카드 사기 탐지 (Credit Card Fraud Detection)

**목표**: 머신러닝을 이용한 신용카드 거래의 사기 탐지

#### 주요 특징
- **데이터**: Kaggle Credit Card Fraud Dataset (28K 샘플, 30개 특성)
- **문제점**: 극도로 불균형된 데이터 (사기 0.2%)
- **해결책**: SMOTE를 이용한 오버샘플링
- **모델**: 4가지 모델 비교 및 앙상블

#### 주요 기술
```
- 데이터 전처리: 표준화, Train/Test 분리
- 불균형 처리: SMOTE (Synthetic Minority Over-sampling Technique)
- 모델 해석: SHAP (SHapley Additive exPlanations)
- 성능평가: ROC-AUC, PR-AUC, F1-Score, Recall
- 통계분석: 효과 크기(Effect Size), 오즈비(Odds Ratio)
```

#### 성능 비교
| 모델 | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|------|----------|-----------|--------|----------|---------|
| Logistic Regression | 높음 | 높음 | 낮음 | 중간 | 0.95+ |
| Random Forest | 높음 | 높음 | 중간 | 높음 | 0.96+ |
| XGBoost | 매우높음 | 높음 | 높음 | 매우높음 | 0.97+ |
| LightGBM | 매우높음 | 높음 | 높음 | 매우높음 | 0.97+ |

**💾 주요 산출물**:
- `outputs/models/`: 학습된 모델 파일 (pickle)
- `outputs/figures/`: 20+ 시각화 (EDA, 모델 성능, SHAP 분석)
- `model_performance_comparison.csv`: 상세 성능 비교

---

### 2. 💰 Mercari 상품 가격 예측 (Price Prediction)

**목표**: 온라인 중고거래 플랫폼의 상품 가격을 정확하게 예측

#### 주요 특징
- **데이터**: Mercari 상품 정보 (1.4M 샘플, 텍스트+구조화 데이터)
- **도전과제**: 대용량 데이터, 텍스트 처리, 텍스트의 중요성
- **혁신점**: 텍스트 데이터(상품명, 설명)의 TF-IDF 특성이 가격 예측의 핵심

#### 주요 기술
```
- 텍스트 처리: Lemmatization (어근 추출)
- 벡터화: TF-IDF (Term Frequency-Inverse Document Frequency)
- 특성공학: 범주형 인코딩, 수치형 스케일링
- 모델링: Ridge, LightGBM, XGBoost, GBM, Random Forest
- 평가지표: RMSLE (Root Mean Squared Logarithmic Error)
```

#### 최종 성과
| 순위 | 모델 | RMSLE | 특징 |
|------|------|-------|------|
| 🥇 | **Ridge (Lemmatized)** | **0.4836** | 텍스트+구조화 데이터 활용 |
| 🥈 | LightGBM | 0.5036 | 텍스트 포함 |
| 🥉 | XGBoost | 0.5038 | 텍스트 포함 |
| 4️⃣ | GBM | 0.5520 | 구조화 데이터만 |
| 5️⃣ | Random Forest | 0.6954 | 구조화 데이터만 |

**🔍 주요 발견**:
- 텍스트 데이터의 중요성: 정형 데이터만으로 예측할 때보다 30% 이상 성능 향상
- Ridge 회귀의 효과: 복잡한 비선형 모델보다 규제화된 선형 모델이 더 효과적
- 상품명이 가격 예측의 가장 중요한 요소

**💾 주요 산출물**:
- `notebooks/`: 10+ 상세 분석 노트북 (문제정의~모델링)
- `outputs/figures/`: 15+ 시각화 (EDA, 분포, 모델 비교)
- `models/`: 최적 모델 저장 파일

---

### 3. 💬 Opinosis 의견 주제 군집화 & 감성 분석 (Opinion Clustering)

**목표**: 제품 리뷰를 자동으로 주제별로 군집화하고 각 주제가 감성에 미치는 영향 분석

#### 주요 특징
- **데이터**: 51개 제품-속성 조합의 온라인 리뷰 (Opinosis Dataset)
- **분석 방법**: K-means 클러스터링 + 감성 분석 + 회귀분석
- **혁신점**: 감성어 제외 정제를 통한 객관적 주제 추출

#### 주요 기술
```
- 감성분석: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- 텍스트 정제: 불용어 제거, 표제어 추출, 감성어 제외
- 벡터화: TF-IDF + SVD (차원 축소: 3000→100)
- 군집화: K-means (엘보우 방법으로 최적 K 선택)
- 통계분석: Ridge 회귀, OLS 회귀, VIF, 위계적 F검정
- 검증: 실루엣 점수, ARI (Adjusted Rand Index)
```

#### 분석 파이프라인

```
1. 데이터 로드
   ↓
2. VADER 감성 분석 (-1 ~ +1)
   ↓
3. 텍스트 정제 (감성어 제외)
   ↓
4. TF-IDF + SVD 벡터화
   ↓
5. 최적 클러스터 수 결정 (엘보우 방법)
   ↓
6. K-means 클러스터링
   ↓
7. Ridge & OLS 회귀분석
   ↓
8. VIF를 이용한 다중공선성 제거
   ↓
9. 시각화 (계수 차트, 히트맵, 체르노프 페이스)
```

#### 주요 결과물
- **회귀계수**: 각 주제(클러스터)가 감성에 미치는 영향도 정량화
  - (+) 양수: 주제 언급 증가 → 감성 상승
  - (-) 음수: 주제 언급 증가 → 감성 하강

- **시각화**:
  - `elbow_method.png`: 최적 클러스터 수 결정
  - `cluster_coefficients.png`: 주제별 감성 영향력
  - `cluster_mean_sentiment.png`: 주제별 평균 감성
  - `product_cluster_heatmap.png`: 제품×주제 감성 히트맵
  - `cluster_chernoff_faces.png`: 체르노프 페이스 (얼굴로 다변량 데이터 표현)

**💾 주요 산출물**:
- `data/process/`: 클러스터링 결과 CSV, 회귀분석 결과
- `outputs/figures/`: 5+ 주요 시각화
- `notebooks/kmeans_clustering.ipynb`: 전체 파이프라인 (재현 가능)

---

### 4. 👥 Santander 고객 만족도 예측 (Customer Satisfaction)

**목표**: 은행 고객의 만족도를 이진 분류(만족/불만족)로 예측

#### 주요 특징
- **데이터**: Kaggle Santander Customer Satisfaction (37K 고객, 370개 특성)
- **문제**: 고차원 데이터, 다수의 범주형 변수
- **접근**: 다양한 모델 비교 및 SHAP을 이용한 해석

#### 주요 기술
```
- 데이터 탐색: EDA, 상관관계 분석, 클래스 불균형 검토
- 전처리: 결측치 처리, 이상치 탐지, 특성 엔지니어링
- 모델: Logistic Regression, Random Forest, XGBoost, LightGBM
- 평가: ROC-AUC, Precision, Recall, F1-Score
- 해석: Feature Importance, SHAP 분석
```

#### 모델 성능
- **ROC-AUC**: 개별 모델별 곡선 분석
- **Feature Importance**: 상위 20개 중요 특성 시각화
- **SHAP 값**: 각 특성이 예측에 미치는 영향 분석

**💾 주요 산출물**:
- `notebook/`: EDA 및 전체 파이프라인
- `outputs/figures/`: 15+ 시각화 (EDA, ROC 곡선, Feature Importance, SHAP)
- `src/`: 다양한 형식의 보고서 생성 스크립트 (PDF, 상세 보고서 등)

---

## 🛠️ 기술 스택

### 프로그래밍 언어
- **Python 3.x**: 모든 프로젝트의 주요 언어

### 데이터 처리 & 분석
| 라이브러리 | 용도 |
|-----------|------|
| **Pandas** | 데이터 조작, 전처리 |
| **NumPy** | 수치 계산 |
| **Scipy** | 통계 분석 |
| **Statsmodels** | 통계 모델링 (OLS, VIF 등) |

### 머신러닝 & 모델링
| 라이브러리 | 용도 |
|-----------|------|
| **scikit-learn** | 기본 ML 모델 (Logistic, RF, 등) |
| **XGBoost** | Gradient Boosting |
| **LightGBM** | 경량 Gradient Boosting |
| **imbalanced-learn** | SMOTE (불균형 처리) |

### 텍스트 처리
| 라이브러리 | 용도 |
|-----------|------|
| **NLTK** | 감성분석, 어근추출, 불용어 처리 |
| **scikit-learn TF-IDF** | 텍스트 벡터화 |

### 시각화 & 해석
| 라이브러리 | 용도 |
|-----------|------|
| **Matplotlib** | 기본 시각화 |
| **Seaborn** | 고급 통계 시각화 |
| **SHAP** | 모델 해석 (SHapley 값) |

### 개발 & 실행 환경
| 도구 | 용도 |
|------|------|
| **Jupyter Notebook** | 대화형 분석 |
| **Git** | 버전 관리 |
| **VS Code / PyCharm** | 코드 편집 |

---

## 📊 데이터셋 요약

| 프로젝트 | 데이터셋 | 샘플 수 | 특성 수 | 목표 | 출처 |
|---------|---------|--------|--------|------|------|
| 신용카드 사기탐지 | Credit Card Fraud | 28K | 30 | 이진분류 | Kaggle |
| 상품 가격 예측 | Mercari | 1.4M | 297+ | 회귀 | Kaggle |
| 의견 군집화 | Opinosis | 51개<br/>제품×속성 | - | 클러스터링 | Opinosis |
| 고객 만족도 | Santander | 37K | 370 | 이진분류 | Kaggle |

---

## 📈 주요 성과

### 🏆 모델 성능
- **신용카드 사기탐지**: ROC-AUC 0.97+ (LightGBM/XGBoost)
- **상품 가격예측**: RMSLE 0.4836 (Ridge 회귀, 최고 성능)
- **고객 만족도**: 자세한 ROC-AUC 분석 및 모델 비교 완료

### 🔍 분석 깊이
- ✅ 상세한 EDA (각 프로젝트 10~20개 시각화)
- ✅ 통계적 검증 (가설검정, 신뢰구간, VIF 등)
- ✅ 모델 해석 (SHAP, Feature Importance)
- ✅ 불균형 데이터 처리 및 평가 (SMOTE, 다양한 지표)

### 📚 코드 품질
- ✅ 완전히 재현 가능한 코드
- ✅ 상세한 주석과 설명
- ✅ 모듈화된 구조 (함수, 클래스 분리)
- ✅ 에러 처리 및 데이터 검증

---

## 🎓 학습 포인트

이 저장소를 통해 다음을 배울 수 있습니다:

### 데이터 사이언스
1. **EDA 방법론**: 데이터 탐색, 시각화, 이상치 검출
2. **전처리 기법**: 정규화, 인코딩, 특성 엔지니어링
3. **통계분석**: 다중회귀, 가설검정, 신뢰구간
4. **머신러닝 모델**: 선형, 트리 기반, 부스팅 모델

### 실무 기술
1. **불균형 데이터 처리**: SMOTE, 클래스 가중치, 지표 선택
2. **모델 평가**: 다양한 성능 지표, 교차검증
3. **모델 해석**: SHAP, Feature Importance, 계수 분석
4. **보고서 작성**: 분석 결과를 효과적으로 전달하기

### 소프트웨어 개발
1. **구조화된 코드**: 프로젝트 구조, 모듈화
2. **주석과 문서화**: 재현 가능하고 이해 가능한 코드
3. **버전 관리**: Git을 이용한 협업 및 추적
4. **자동화**: 파이프라인 스크립트, 배치 처리

---

## 📖 프로젝트별 상세 가이드

각 프로젝트의 더 자세한 정보는 해당 폴더의 README를 참고하세요:

- 📘 [신용카드 사기 탐지](./creditCard-project/README.md)
- 📗 [상품 가격 예측](./mercari_price_prediction/README.md)
- 📙 [의견 군집화 분석](./opinosis_clustering/README.md)
- 📕 [고객 만족도 예측](./santander-customer-satisfaction-project/README.md)

---

## ⚙️ 설치 및 환경 설정

### 필수 요구사항
- Python 3.7+
- pip 또는 conda

### 전체 환경 설정
```bash
# 1. 저장소 클론
git clone https://github.com/pkbrb77-sudo/SEMI_Project.git
cd SEMI_Project

# 2. 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 각 프로젝트별 의존성 설치
# 신용카드 사기탐지
cd creditCard-project
pip install -r requirements.txt

# 다른 프로젝트도 동일하게...
```

### 주요 라이브러리 통합 설치
```bash
pip install pandas numpy scipy scikit-learn xgboost lightgbm imbalanced-learn \
            nltk statsmodels shap matplotlib seaborn jupyter
```

---

## 🔗 데이터 다운로드

### Kaggle 데이터셋
대부분의 프로젝트에서 사용하는 데이터는 Kaggle에서 다운로드할 수 있습니다:

1. **신용카드 사기탐지**: [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
2. **상품 가격예측**: [Mercari](https://www.kaggle.com/c/mercari-price-suggestion-challenge)
3. **고객 만족도**: [Santander Customer Satisfaction](https://www.kaggle.com/c/santander-customer-satisfaction)

각 프로젝트 폴더의 README에서 자세한 다운로드 방법을 확인하세요.

---

## 💻 사용 예시

### 모델 로드 및 예측
```python
import pickle
from pathlib import Path

# 신용카드 사기탐지 모델 로드
model_path = Path('creditCard-project/outputs/models/credit_fraud_lightgbm_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# 예측
predictions = model.predict(X_new)
```

### 분석 노트북 실행
```bash
cd mercari_price_prediction
jupyter notebook notebooks/03_eda.ipynb
```

---

## 🤝 기여하기

이 프로젝트는 개인 학습 포트폴리오이지만, 개선 사항이 있으시면:

1. 프로젝트를 Fork하세요
2. 기능 브랜치를 만드세요 (`git checkout -b feature/improvement`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add improvement'`)
4. 브랜치에 푸시하세요 (`git push origin feature/improvement`)
5. Pull Request를 생성하세요

---

## 📝 라이선스

이 프로젝트는 교육 및 개인 학습 목적으로 만들어졌습니다.

---

## 👤 프로젝트 관리자

**이민석** (Min-Seok Lee)
- 📧 Email: pkbrb77@gmail.com
- 🔗 GitHub: [@pkbrb77-sudo](https://github.com/pkbrb77-sudo)

---

## 📞 문의 및 피드백

프로젝트에 대한 질문이나 개선 사항이 있으시면 이슈를 등록해주세요.

---

## 📚 참고 자료

### 머신러닝 & 데이터사이언스
- [Scikit-learn 공식 문서](https://scikit-learn.org/)
- [XGBoost 튜토리얼](https://xgboost.readthedocs.io/)
- [SHAP 라이브러리](https://github.com/slundberg/shap)

### 통계분석 & 시각화
- [Pandas 공식 문서](https://pandas.pydata.org/)
- [Matplotlib/Seaborn](https://matplotlib.org/)
- [Statsmodels](https://www.statsmodels.org/)

### 텍스트 처리
- [NLTK 책 - Natural Language Processing with Python](https://www.nltk.org/book/)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)

### 온라인 강의
- [Kaggle 머신러닝 코스](https://www.kaggle.com/learn/intro-to-machine-learning)
- [Coursera 머신러닝 스페셜라이제이션](https://www.coursera.org/specializations/machine-learning-introduction)

---

## 🎯 향후 계획

- [ ] AutoML 파이프라인 추가
- [ ] 웹 대시보드 (Streamlit/Dash) 개발
- [ ] 실시간 예측 API 구축
- [ ] 추가 프로젝트 (NLP, 이미지분석 등)
- [ ] Docker 컨테이너화

---

**마지막 업데이트**: 2026년 9월 3일

**Status**: ✅ Production Ready (모든 코드 재현 가능하고 완전 테스트됨)

---

## 🌟 Star & Follow

이 프로젝트가 도움이 되셨다면 Star ⭐를 눌러주세요!
