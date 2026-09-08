# Opinosis Clustering Project

이 프로젝트는 제품 및 속성별 온라인 리뷰 데이터에 대해 **K-means 클러스터링**과 **감성 분석**을 결합하여 의견의 주요 주제(topic)를 자동으로 발견하고, 각 주제가 전체 감성에 미치는 영향을 정량적으로 분석하는 프로젝트입니다.

## 📋 프로젝트 개요

### 목표
- 리뷰 텍스트를 **주제별로 군집화**
- 각 군집이 **감성에 미치는 영향**을 회귀분석으로 정량화
- 제품/속성별 **감성 패턴** 파악 및 시각화

### 주요 특징
- **VADER 감성 분석**: 원본 텍스트의 감성 점수 계산 (-1 ~ +1)
- **감성어 제외 정제**: 군집화 시 객관적인 주제만 추출
- **TF-IDF + SVD**: 고차원 텍스트 데이터 벡터화 및 차원축소
- **엘보우 방법**: 최적 클러스터 수(K) 자동 결정
- **통계적 유의성 검정**: OLS 회귀, VIF, 위계적 F검정 등
- **클러스터 안정성 검증**: 실루엣 점수, ARI 재현성 지표
- **다양한 시각화**: 회귀계수 차트, 히트맵, 체르노프 페이스

---

## 📁 폴더 구조

```
opinosis_clustering/
├── data/
│   ├── topics/              # 원본 데이터 (.data 파일들, 51개 aspect_product 조합)
│   └── process/             # 처리된 결과 (CSV, PNG 등)
├── notebooks/
│   └── kmeans_clustering.ipynb   # 전체 분석 과정 (main notebook)
├── outputs/
│   └── figures/             # 생성된 시각화 이미지
├── src/                     # 재사용 가능한 함수 모듈 (필요시)
├── README.md                # 이 파일
└── .gitignore              # git 추적 제외 설정
```

---

## 🔄 분석 파이프라인

### 1️⃣ 데이터 로드 및 기본 정제
- `data/topics/` 에서 51개 `.data` 파일 읽기
- aspect, product, raw_text로 DataFrame 구성
- 공백, 개행 문자 등 기본 노이즈 제거

### 2️⃣ VADER 감성 분석
```python
sentiment = SentimentIntensityAnalyzer().polarity_scores(raw_text)["compound"]
```
- 범위: -1 (매우 부정) ~ +1 (매우 긍정)
- 각 문장마다 감성 점수 할당

### 3️⃣ 텍스트 정제 (클러스터링용)
- 소문자 변환, 특수문자 제거
- 불용어(stopwords) 제거
- **감성어 제외**: VADER 어휘에서 강도가 높은 단어 제거
  - 이유: 군집이 객관적 주제만 담도록 하기 위함
- 표제어 추출(Lemmatization)
- 2글자 이하 단어 제거

### 4️⃣ 벡터화 및 차원축소
```python
TfidfVectorizer(max_features=3000, min_df=3, max_df=0.9, ngram_range=(1,2))
TruncatedSVD(n_components=100)
```
- TF-IDF: 문서-단어 행렬로 변환
- SVD: 3000차원 → 100차원 축소 (차원의 저주 방지, 속도 개선)

### 5️⃣ 최적 클러스터 수 결정
- **엘보우 방법**: inertia 곡선에서 첫점-끝점 직선으로부터 가장 먼 지점(K)을 선택
- 그래프: `elbow_method.png`

### 6️⃣ K-means 클러스터링
```python
KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
```
- 각 문장을 `cluster_0`, `cluster_1`, ... 로 할당

### 7️⃣ 회귀 분석 (감성에 미치는 영향)

#### 7-1. Ridge 회귀 (해석용)
- 입력: 클러스터 원-핫 인코딩, 제품/속성 더미변수
- 출력: 각 클러스터의 회귀계수 (감성에 미치는 영향도)

#### 7-2. OLS 회귀 (통계적 유의성)
```
sentiment ~ cluster_i + product_j + aspect_k + ε
```
- 강건표준오차(HC3) 적용 (이분산성 대비)
- p-value, 신뢰구간 계산
- 결과: `cluster_ols_regression_table.csv`

#### 7-3. 다중공선성 점검 (VIF)
```python
VIF = 1 / (1 - R²_i)
```
- VIF < 5: 양호
- 5 ≤ VIF < 10: 주의 필요
- VIF ≥ 10: 심각
- 문제 변수 단계적 제거 후 재적합
- 결과: `cluster_vif_table.csv` → `cluster_vif_table_refined.csv`

#### 7-4. 위계적 회귀 (F검정)
- 축소모형: 제품/속성만
- 완전모형: 제품/속성 + 클러스터
- 부분 F검정으로 클러스터 블록의 유의성 검증

### 8️⃣ 클러스터 안정성 검증
- **실루엣 점수**: -1 ~ 1 (0.5 이상이면 뚜렷한 구조)
- **ARI (Adjusted Rand Index)**: 서로 다른 seed로 재현성 검증

### 9️⃣ 시각화

| 파일명 | 설명 |
|--------|------|
| `elbow_method.png` | 엘보우 곡선으로 최적 K 시각화 |
| `cluster_coefficients.png` | 클러스터별 회귀계수 (감성 영향력) |
| `cluster_mean_sentiment.png` | 클러스터별 평균 감성 점수 |
| `product_cluster_heatmap.png` | 제품 × 클러스터 평균 감성 히트맵 |
| `cluster_chernoff_faces.png` | 클러스터별 체르노프 페이스 |

#### 체르노프 페이스 해석
- 얼굴 크기: 클러스터의 문장 수
- 눈 크기: 감성 편차(표준편차)
- 눈썹: 회귀계수 (위로=양수, 아래=음수)
- 입: 평균 감성 (웃음=긍정, 찡그림=부정)
- 색깔: 초록=감성 상승, 빨강=감성 하강

---

## 📊 주요 출력 파일

### CSV 결과물 (`data/process/`)
- **`cluster_sentiment_result.csv`**: 모든 문장 + 클러스터 + 감성 점수
- **`cluster_ols_regression_table.csv`**: OLS 회귀계수 (1차)
- **`cluster_ols_regression_table_refined.csv`**: OLS 회귀계수 (VIF 정제 후)
- **`cluster_vif_table.csv`**: VIF 값 (1차)
- **`cluster_vif_table_refined.csv`**: VIF 값 (정제 후)

### PNG 시각화 (`data/process/` 및 `outputs/figures/`)
- `elbow_method.png`
- `cluster_coefficients.png`
- `cluster_mean_sentiment.png`
- `product_cluster_heatmap.png`
- `cluster_chernoff_faces.png`

---

## 🛠️ 사용 방법

### 필수 라이브러리
```bash
pip install numpy pandas matplotlib seaborn scikit-learn nltk statsmodels
```

### 데이터 준비
- `data/topics/` 폴더에 `*.data` 파일 배치 (51개 aspect_product 조합)

### 실행
```bash
cd notebooks/
jupyter notebook kmeans_clustering.ipynb
```

### 주요 설정값 (수정 가능)
```python
N_CLUSTERS_RANGE = range(2, 31)        # 엘보우 탐색 범위
MAX_FEATURES = 3000                    # TF-IDF 어휘 크기
SVD_COMPONENTS = 100                   # 차원축소 후 차원 수
RANDOM_STATE = 42                      # 재현성 보장
```

---

## 📈 결과 해석 예시

### 클러스터별 상위 단어
```
cluster_0: battery, life, product
cluster_1: screen, display, quality
cluster_2: price, cost, expensive
...
```

### 회귀계수 해석
- **양수(+)**: 이 주제가 많이 언급될수록 전체 감성이 상승
  - 예: `cluster_0 = +0.15` → 배터리 주제가 높을수록 긍정 감정 증가
  
- **음수(-)**: 이 주제가 많이 언급될수록 전체 감성이 하강
  - 예: `cluster_2 = -0.12` → 가격 주제가 높을수록 부정 감정 증가

---

## ⚠️ 주의사항

1. **데이터 크기**: 51개 `.data` 파일 전체 처리 시 수 분 소요 가능
2. **NLTK 데이터**: 첫 실행 시 VADER 어휘 및 stopwords 자동 다운로드
3. **한글 폰트**: Windows/Mac/Linux별 자동 설정 (필요시 조정)
4. **다중공선성**: VIF 기반 변수 제거 후 해석값(계수)이 변할 수 있음

---

## 📝 라이선스 & 저작권

- 프로젝트: Opinosis Sentiment Clustering Analysis
- 작성자: 이민석
- 데이터: Opinosis Dataset (온라인 리뷰)

---

## 🔗 관련 자료

- VADER Sentiment Analysis: https://github.com/cjhutto/vaderSentiment
- K-means Clustering: https://scikit-learn.org/stable/modules/clustering.html#k-means
- Chernoff Face Plot: https://en.wikipedia.org/wiki/Chernoff_face

---

**Last Updated**: 2026-09-02  
**Status**: Production Ready
