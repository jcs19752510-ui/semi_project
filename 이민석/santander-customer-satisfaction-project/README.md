# Santander Customer Satisfaction Project

고객 만족도 예측 모델링 프로젝트입니다. Kaggle의 Santander Customer Satisfaction 데이터셋을 활용하여 머신러닝 모델을 통해 고객 만족도를 예측합니다.

## 📋 프로젝트 개요

- **목표**: Santander 은행 고객의 만족도 이진 분류 (만족/불만족)
- **데이터셋**: Kaggle Santander Customer Satisfaction Dataset
- **주요 기술**: Python, Pandas, Scikit-learn, XGBoost, LightGBM, SHAP

## 📁 디렉토리 구조

```
santander-customer-satisfaction-project/
├── data/                          # 데이터 파일 (gitignore됨)
│   ├── train.csv                  # 훈련 데이터
│   ├── test.csv                   # 테스트 데이터
│   └── sample_submission.csv      # 제출 샘플
│
├── notebook/                      # Jupyter 노트북
│   ├── 01_data_understanding.ipynb    # EDA 및 데이터 이해
│   └── PipeLine.ipynb                 # 전체 파이프라인
│
├── src/                           # 소스 코드
│   ├── extract_model_results.py       # 모델 결과 추출
│   ├── extract_model_results_with_rf.py
│   ├── generate_detailed_paper.py     # 상세 보고서 생성
│   ├── generate_extended_paper.py     # 확장 보고서 생성
│   ├── generate_full_paper.py         # 전체 보고서 생성
│   ├── generate_pdf_report.py         # PDF 리포트 생성
│   ├── generate_pdf_report_v2.py
│   ├── generate_pdf_report_v3_with_figures.py
│   └── ...
│
├── outputs/                       # 모델 결과 및 시각화
│   ├── figures/                   # 생성된 그래프 및 이미지
│   └── models/                    # 모델 결과 및 메트릭
│
├── .gitignore                     # Git 무시 파일 설정
└── README.md                      # 프로젝트 문서

```

## 🔧 주요 파일 설명

### 데이터 파일 (data/)
- **train.csv**: 훈련 데이터 (37,888 rows × 371 columns)
- **test.csv**: 테스트 데이터 (9,472 rows × 370 columns)
- **sample_submission.csv**: Kaggle 제출 형식 샘플

### 노트북 (notebook/)
- **01_data_understanding.ipynb**: 데이터 탐색, EDA, 시각화
- **PipeLine.ipynb**: 전체 모델링 파이프라인

### 스크립트 (src/)
- **extract_model_results*.py**: 훈련된 모델의 결과 추출 및 분석
- **generate_*_paper.py**: 다양한 형식의 분석 리포트 생성 (PDF, 상세 보고서 등)

### 결과 (outputs/)
- **figures/**: EDA 및 모델 성능 관련 시각화 이미지
- **models/**: 모델 성능 메트릭 및 비교 결과

## 📊 프로젝트 단계

1. **데이터 이해 (EDA)**
   - 데이터 형태 분석
   - 결측치 확인
   - 타겟 변수 분포 분석
   - 특성 간 상관관계 분석

2. **데이터 전처리**
   - 결측치 처리
   - 이상치 탐지
   - 특성 엔지니어링
   - 데이터 스케일링

3. **모델 개발**
   - 베이스라인 모델: Logistic Regression
   - 트리 기반 모델: Random Forest, XGBoost, LightGBM
   - 모델 비교 및 평가

4. **해석 및 분석**
   - Feature Importance 분석
   - SHAP값을 이용한 모델 해석
   - 모델 성능 비교 시각화

5. **보고서 생성**
   - 상세 분석 리포트
   - PDF 형식 최종 보고서

## 🚀 사용 방법

### 환경 설정
```bash
# 필요한 패키지 설치
pip install pandas numpy scikit-learn xgboost lightgbm matplotlib seaborn shap

# 또는 requirements.txt가 있으면
pip install -r requirements.txt
```

### 노트북 실행
```bash
jupyter notebook notebook/01_data_understanding.ipynb
```

### 보고서 생성
```bash
python src/generate_full_paper.py
python src/generate_pdf_report_v3_with_figures.py
```

## 📈 모델 성능

주요 성능 지표 (outputs/models/ 참고):
- **ROC-AUC**: 각 모델별 곡선 분석
- **분류 성능**: Precision, Recall, F1-Score
- **모델 비교**: 여러 알고리즘의 성능 비교

## 📝 주요 발견사항

- 데이터에서 클래스 불균형 존재
- 특정 특성들이 고객 만족도 예측에 중요한 영향
- 앙상블 모델 (XGBoost, LightGBM)의 우수한 성능

## 🔍 분석 리소스

- **시각화**: `outputs/figures/` 폴더의 EDA 및 모델 분석 그래프
- **상세 분석**: `src/` 폴더의 보고서 생성 스크립트로 생성 가능
- **모델 결과**: `outputs/models/` 폴더의 성능 메트릭

## 🛠 기술 스택

- **언어**: Python 3.x
- **데이터 처리**: Pandas, NumPy
- **머신러닝**: Scikit-learn, XGBoost, LightGBM
- **시각화**: Matplotlib, Seaborn
- **모델 해석**: SHAP
- **보고서**: ReportLab (PDF 생성)

## 📄 라이선스

이 프로젝트는 교육 및 분석 목적으로 작성되었습니다.

## 👤 작성자

이민석

---


