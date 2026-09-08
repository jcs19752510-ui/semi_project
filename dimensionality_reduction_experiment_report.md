# Opinosis 군집화 — 차원 축소 효과 검증 실험 결과

`dimensionality_reduction_comparison.md`의 설계를 `03_Opiniosis_Opinion_Review.ipynb`에 실제로 구현·실행한 결과를 정리한다.

## 1. 목적

TF-IDF 벡터에 TruncatedSVD를 적용하는 것이 K-means 군집화 품질을 실제로 개선하는지 검증한다.

- **파이프라인 A (baseline)**: TF-IDF → KMeans
- **파이프라인 B (SVD)**: TF-IDF → TruncatedSVD → Normalizer → KMeans

## 2. 실험 흐름

### 2-1. 함정 회피

서로 다른 차원의 공간에서 계산한 실루엣 점수는 직접 비교하지 않았다. 고차원(TF-IDF, 4610차원)에서는 거리 집중 현상으로 실루엣이 구조적으로 낮게 나와, 저차원(SVD)이 이기는 것이 당연해지기 때문이다. 대신 **대리 정답 기반 외부 평가(ARI/NMI)** 를 주력 지표로, **군집 안정성**과 **군집 키워드 육안 확인**을 보조 지표로 사용했다.

### 2-2. 대리 정답(proxy label) 정의

먼저 `data/topics/*.data` 51개 파일명을 직접 확인했다. 파일명은 `{주제}_{대상}` 구조였고, 대상 식별자를 접미사로 매칭해 두 가지 기준의 대리 정답을 만들었다.

- **대상 종류 기준** (`target_category`, 3클래스): electronics 25 / hotel 16 / car 10
- **주제 기준** (`aspect_label`, 35클래스): battery-life, mileage, rooms, service 등

파싱 과정에서 원본 데이터의 표기 불일치를 확인하고 정규화했다.

- `netbook_1005ha` ↔ `asus_netbook_1005ha` → 동일 기기
- `swissotel_chicago` ↔ `swissotel_hotel_chicago` → 동일 호텔
- `room` ↔ `rooms` → 동일 주제

### 2-3. 파이프라인 실행 및 통제 조건

- `n_clusters=3`으로 두 파이프라인 동일하게 고정 (기존 메인 분석과 동일)
- SVD의 `n_components`를 `[2, 5, 10, 20, 30, 40]`로 바꿔가며 비교 (문서 51개이므로 유의미한 축은 최대 50개 근처)
- KMeans 초기화 편차를 줄이기 위해 `random_state` 30개 시드로 반복 후 평균
- 같은 30회 반복 결과로 쌍별 ARI 평균(군집 안정성)도 함께 계산 — 별도 실험 없이 재사용
- TruncatedSVD 뒤에는 `Normalizer`를 붙여 코사인 기반 군집화에 가깝게 구성 (scikit-learn 공식 예제 구성과 동일)
- 전처리(토크나이저, stop words, `min_df`, `max_df`, `ngram_range`)는 두 파이프라인에서 완전히 동일

### 2-4. 군집 키워드 육안 확인

ARI(대상 종류)가 가장 높았던 SVD 설정(`n_components=5`)에 대해 `TruncatedSVD.inverse_transform`으로 군집 중심을 단어 공간에 되돌려 상위 10개 단어를 확인하고, baseline과 비교했다.

## 3. 결과

| 파이프라인 | n_components | ARI (대상종류) | NMI (대상종류) | ARI (주제) | NMI (주제) | 안정성 |
|---|---|---|---|---|---|---|
| A (TF-IDF) | — | 0.9966 | 0.9954 | 0.0456 | 0.4362 | 0.9932 |
| B (SVD) | 2 | 0.7419 | 0.7550 | 0.0518 | 0.4505 | 1.0000 |
| B (SVD) | **5** | **1.0000** | **1.0000** | 0.0455 | 0.4359 | **1.0000** |
| B (SVD) | 10 | 0.9219 | 0.9494 | 0.0445 | 0.4336 | 0.8609 |
| B (SVD) | 20 | 0.9682 | 0.9716 | 0.0463 | 0.4378 | 0.9379 |
| B (SVD) | 30 | 0.9737 | 0.9763 | 0.0462 | 0.4375 | 0.9484 |
| B (SVD) | 40 | 0.9913 | 0.9892 | 0.0455 | 0.4360 | 0.9827 |

누적 설명분산비: n_components=10 → 0.452, 20 → 0.718, 40 → 0.977

**군집 키워드** (baseline과 SVD n_components=5 모두 동일한 양상):

- Cluster A(전자기기): `battery, screen, keyboard, video, direction, voice, map`
- Cluster B(자동차): `mileage, gas mileage, interior, seat, comfort, performance`
- Cluster C(호텔): `room, hotel, service, staff, location, food`

## 4. 결론

- **대상 종류(전자기기/자동차/호텔) 기준**: baseline이 이미 ARI 0.997로 거의 완벽하게 분리한다. TF-IDF 벡터 자체가 도메인별로 어휘가 뚜렷이 갈리는 데이터라 개선 여지가 크지 않다. `n_components=5`인 SVD가 ARI 1.000·안정성 1.000으로 baseline보다 소폭 더 낫고 완전히 안정적인 반면, `n_components=10~40`은 오히려 baseline보다 낮은 ARI를 보였다. **SVD는 성분 수를 작게(5 근처) 잡을 때만 미세한 개선 효과가 있고, 성분 수를 늘릴수록 이득이 사라지거나 역전된다.**
- **주제(aspect, 35개 세부 클래스) 기준**: baseline과 SVD 모두 ARI가 0.05 미만으로 낮다. `n_clusters=3`으로는 애초에 35개 세부 주제를 구분할 수 없기 때문이며, 두 파이프라인의 우열을 가리는 근거로는 쓸 수 없다. 즉 **대리 정답의 정의(대상 기준 vs 주제 기준)에 따라 결론이 갈리지는 않았지만, 주제 기준 지표는 애초에 판단력이 없는 지표였다.**
- **군집 키워드 육안 확인**: baseline과 SVD(n_components=5) 모두 군집 내용이 도메인별로 깨끗하게 갈려 성공 예에 해당한다.
- **종합 판단**: 이 데이터셋(문서 51개, 도메인별 어휘가 뚜렷함)에서는 TruncatedSVD 도입이 필수가 아니다. baseline이 이미 충분히 좋고, SVD는 성분 수를 잘 고르면 아주 소폭의 정확도·안정성 이득을 줄 뿐 극적인 개선은 아니다. 문서 수가 많고 어휘 중첩이 큰 데이터셋일수록 SVD의 효과가 더 크게 나타날 가능성이 높다.

## 5. 구현 위치

`염윤호/03 Opiniosis Opinion Review/03_Opiniosis_Opinion_Review.ipynb` — "차원 축소(TruncatedSVD) 효과 검증" 절 (선행 작업 → 파이프라인 A/B 실행 → 시각화 → 키워드 확인 → 결과표/결론 순서로 14개 셀).
