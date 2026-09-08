## Opinion Review 머신러닝 계획서
### 목적
- 군집화 실시에 따른 결과 확인
- 벡터화 기법과 군집화 알고리즘을 비교

### 파일 대상
1. 코드 파일
- 03_Opiniosis_Opinion_Review.ipynb
2. 데이터 파일
- data/topics/*

### 실시 방법
- 벡터화 방법 2가지 * 군집화 방법 2가지. 총 4가지 경우의 수로 결과를 비교.
- 벡터화 방법
    - CountVectorizer
    - TfIdfVectorizer
- 군집화 방법
    - K-means
    - DBSCAN
- 산출물
    - 경우의 수에 따른 결과 비교
    (CountVectorizer&K-means, CountVectorizer&DBSCAN, TfIdfVectorizer&K-means, TfIdfVectorizer&DBSCAN)
    - 군집화 결과 바탕으로 감성 분석을 통한 긍정 / 부정 확인.