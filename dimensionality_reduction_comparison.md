# Opinosis 군집화 — 차원 축소 효과 비교 실험

## 1. 목적

TF-IDF 벡터에 TruncatedSVD를 적용하는 것이 KMeans 군집화 품질을 실제로 개선하는지 검증한다.

비교 대상은 두 파이프라인이다.

- **파이프라인 A (baseline)**: TF-IDF → KMeans
- **파이프라인 B (SVD)**: TF-IDF → TruncatedSVD → Normalizer → KMeans

두 결과 중 어느 쪽이 나은지 근거를 가지고 판단하는 것이 목표다.

## 2. 배경

### 왜 검증이 필요한가

차원 축소는 군집화의 필수 단계가 아니다. 선택지다.

기대하는 효과는 두 가지다.

1. 동의어 통합 — 함께 등장하는 단어들이 같은 잠재 축으로 묶여 문서 간 유사도가 살아난다
2. 노이즈 제거 — 특이값이 작은 축(희귀 단어, 오타)이 버려진다

두 효과 모두 **가정**이다. 데이터에서 실제로 나타나는지 확인해야 한다.

Opinosis는 문서가 51개뿐이다. 계산 속도 이득은 사실상 없다. 따라서 속도는 평가 항목에서 제외한다.

### 반드시 피해야 할 함정

서로 다른 공간에서 계산한 내부 지표를 직접 비교하면 안 된다.

```python
# 잘못된 비교 — 절대 이렇게 하지 말 것
score_a = silhouette_score(X_tfidf, labels_a)   # 수천 차원
score_b = silhouette_score(X_svd,   labels_b)   # 수십 차원
```

실루엣 계수는 거리를 계산한 공간에 종속된다.

고차원에서는 거리 집중 현상(distance concentration) 때문에 실루엣이 구조적으로 낮게 나온다. SVD 쪽이 이기는 것이 당연하다. 군집이 좋아서가 아니라 차원이 낮아서 이긴다.

이 비교는 결론을 낼 수 없다.

## 3. 평가 전략

| 순위 | 방법 | 지표 | 정답 필요 | 공간 종속 |
|---|---|---|---|---|
| **주력** | 대리 정답 기반 외부 평가 | ARI, NMI | 대리 정답 | 없음 |
| 보조 1 | 군집 안정성 | 반복 간 평균 ARI | 없음 | 없음 |
| 보조 2 | 군집 키워드 육안 확인 | 정성 판단 | 없음 | 없음 |

내부 지표(실루엣)를 주력으로 쓰지 않는 이유는 두 가지다.

- 공간 종속 문제를 회피하려면 평가 공간을 고정해야 하는데, 그러면 SVD 쪽에 불리한 조건이 된다
- 실루엣은 뭉쳐 있고 둥근 군집을 선호한다. KMeans의 형태 가정과 취향이 같다. "좋은 군집"이 아니라 "KMeans스러운 군집"을 높게 평가하는 편향이 있다

---

## 4. 주력 — 대리 정답 기반 외부 평가 (ARI / NMI)

### 근거

Opinosis 데이터의 파일명에는 주제(aspect)와 대상(product/hotel)이 들어 있다.

이 정보로 레이블을 만들 수 있다.

- 대상 종류 기준 — 전자기기 / 자동차 / 호텔
- 주제 기준 — battery, mileage, rooms, service 등

ARI와 NMI는 군집 번호가 달라도 상관없다. 어떤 문서들이 함께 묶였는지만 본다. 공간에도 종속되지 않는다.

따라서 3절의 함정을 완전히 피한다.

### 선행 작업

**먼저 실제 파일명 형식을 직접 확인할 것.** 형식을 확인한 뒤 파싱 규칙을 정한다.

```python
import os
files = sorted(os.listdir(DATA_DIR))
print(files[:10])
```

### 절차

1. 파일명에서 대리 정답 레이블을 추출한다
2. 파이프라인 A, B로 각각 군집 레이블을 만든다
3. 두 결과에 대해 ARI와 NMI를 계산한다

```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

for name, labels in [("A_tfidf", labels_a), ("B_svd", labels_b)]:
    ari = adjusted_rand_score(true_labels, labels)
    nmi = normalized_mutual_info_score(true_labels, labels)
    print(f"{name}: ARI={ari:.3f}, NMI={nmi:.3f}")
```

### 통제 조건

- `n_clusters`는 두 파이프라인에서 동일하게 맞춘다
- `random_state`를 고정한다
- KMeans 초기화 편차를 줄이기 위해 여러 시드로 반복하고 평균을 낸다

### 한계

이것은 진짜 정답이 아니다. 사람이 붙인 파일명에서 유도한 **대리 정답(proxy label)** 이다.

결과를 기록할 때 이 점을 명시한다.

---

## 5. 보조 1 — 군집 안정성

### 근거

정답이 없어도 쓸 수 있다.

데이터를 조금씩 흔들어 여러 번 군집화한다. 결과가 매번 비슷하면 그 구조는 우연이 아닐 가능성이 높다.

노이즈 제거 효과가 실제로 있다면 SVD 쪽이 더 안정적으로 나와야 한다. 이 방법은 2절에서 세운 가정 2를 직접 검증한다.

문서가 51개뿐이라 반복 실행 비용이 낮다.

### 절차

1. 부트스트랩 샘플 또는 서로 다른 시드로 N회(예: 30회) 군집화한다
2. 실행 결과 쌍끼리 ARI를 계산한다
3. 쌍별 ARI의 평균을 그 파이프라인의 안정성 점수로 삼는다
4. 파이프라인 A와 B의 안정성 점수를 비교한다

```python
# 개념 코드 — 실제 구현 시 인덱스 정합성 처리 필요
runs = []
for seed in range(30):
    labels = KMeans(n_clusters=k, random_state=seed).fit_predict(X)
    runs.append(labels)

scores = [adjusted_rand_score(runs[i], runs[j])
          for i in range(len(runs)) for j in range(i + 1, len(runs))]
stability = sum(scores) / len(scores)
```

부트스트랩을 쓸 경우 두 실행에 공통으로 포함된 문서에 대해서만 ARI를 계산해야 한다.

---

## 6. 보조 2 — 군집 키워드 육안 확인

### 근거

지표가 아니다. 하지만 실제 판단 근거가 된다.

수치가 좋아도 군집 내용이 뒤섞여 있으면 그 결과는 쓸 수 없다.

### 절차

각 군집의 중심에서 상위 단어를 뽑는다.

SVD를 쓴 경우 잠재 축은 사람이 읽을 수 없다. 원래 단어 공간으로 되돌려야 한다.

```python
# 파이프라인 B — 단어 공간으로 역투영
centroids = svd.inverse_transform(kmeans.cluster_centers_)

# 파이프라인 A — 역투영 불필요
# centroids = kmeans.cluster_centers_

terms = vectorizer.get_feature_names_out()
for i, c in enumerate(centroids):
    top = c.argsort()[::-1][:10]
    print(f"Cluster {i}: {[terms[j] for j in top]}")
```

### 판정 기준

- 성공 예 — `battery, charge, hours, life, power`
- 실패 예 — `battery, hotel, mileage, room, seat`

한 군집 안에 서로 무관한 도메인의 단어가 섞여 있으면 실패로 본다.

---

## 7. 구현 시 주의사항

### TruncatedSVD 뒤에는 Normalizer를 붙인다

TruncatedSVD 출력은 L2 정규화가 되어 있지 않다.

정규화된 벡터에 KMeans를 쓰면 코사인 기반 군집화에 가까워진다. scikit-learn 공식 텍스트 군집화 예제도 이 구성을 쓴다.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

lsa = make_pipeline(TruncatedSVD(n_components=k), Normalizer(copy=False))
```

### n_components 상한

행렬의 랭크는 `min(문서 수, 단어 수)`를 넘지 못한다.

문서가 51개이므로 의미 있는 성분은 최대 50개 근처다. 그 이상을 요청해도 뒤쪽은 사실상 빈 축이다.

`explained_variance_ratio_`를 확인해서 실제로 몇 개 축이 의미 있는지 판단한다.

### PCA가 아니라 TruncatedSVD를 쓴다

TruncatedSVD는 데이터를 중심화(centering)하지 않는다. sparse 행렬에 바로 적용할 수 있다.

PCA는 중심화 과정에서 sparse 구조를 깨뜨린다.

### 전처리는 두 파이프라인에서 동일하게

토크나이저, stop words, `min_df`, `max_df`, `ngram_range`를 모두 같게 맞춘다.

TF-IDF 단계가 다르면 비교가 성립하지 않는다.

---

## 8. 결과 기록 형식

| 파이프라인 | n_components | ARI | NMI | 안정성 | 키워드 판정 |
|---|---|---|---|---|---|
| A (TF-IDF) | — | | | | |
| B (SVD) | | | | | |

`n_components`를 여러 값으로 바꿔가며 표를 채운다. 그 결과 SVD의 효과가 성분 수에 어떻게 반응하는지 함께 확인한다.

## 9. 결론 도출 기준

- ARI/NMI에서 B가 A보다 뚜렷하게 높고, 안정성도 높고, 키워드도 깨끗하면 → 차원 축소 채택
- 지표가 엇갈리면 → 어떤 지표가 어떤 이유로 엇갈렸는지 기록하고 판단을 보류한다
- 대리 정답의 정의(대상 기준 / 주제 기준)에 따라 결론이 뒤집히는지도 확인한다
