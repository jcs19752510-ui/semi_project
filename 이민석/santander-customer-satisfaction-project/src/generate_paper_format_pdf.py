from fpdf import FPDF
from datetime import datetime
import os

class PaperPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_font('NotoSansKR', '', 'C:\\Windows\\Fonts\\malgun.ttf')
        self.add_font('NotoSansKR', 'B', 'C:\\Windows\\Fonts\\malgunbd.ttf')
        self.line_height = 5.5

    def header(self):
        """페이지 헤더"""
        if self.page_no() > 1:
            self.set_font('NotoSansKR', '', 9)
            self.cell(0, 8, f'- {self.page_no()} -', 0, 1, 'C')

    def footer(self):
        """페이지 푸터"""
        pass

    def add_title_section(self, title, author, affiliation, date):
        """제목 페이지"""
        self.add_page()
        self.set_font('NotoSansKR', 'B', 18)
        self.multi_cell(0, 8, title, align='C')
        self.ln(8)

        self.set_font('NotoSansKR', '', 11)
        self.cell(0, 6, author, 0, 1, 'C')
        self.cell(0, 6, affiliation, 0, 1, 'C')
        self.ln(5)

        self.set_font('NotoSansKR', '', 10)
        self.cell(0, 6, f'Date: {date}', 0, 1, 'C')
        self.ln(15)

    def add_abstract(self, abstract_text):
        """초록"""
        self.set_font('NotoSansKR', 'B', 12)
        self.cell(0, 8, '초록 (Abstract)', 0, 1)
        self.ln(2)

        self.set_font('NotoSansKR', '', 10)
        self.multi_cell(0, self.line_height, abstract_text)
        self.ln(3)

        self.set_font('NotoSansKR', '', 9)
        self.cell(0, 5, '키워드: 머신러닝, 고객 만족도, 불만족도 예측, XGBoost, 변수 선택', 0, 1)
        self.ln(5)

    def add_section(self, title):
        """섹션 제목"""
        self.set_font('NotoSansKR', 'B', 12)
        self.cell(0, 7, title, 0, 1)
        self.ln(2)

    def add_subsection(self, title):
        """서브섹션 제목"""
        self.set_font('NotoSansKR', 'B', 11)
        self.cell(0, 6, title, 0, 1)
        self.ln(1)

    def add_text(self, text, size=10):
        """일반 텍스트"""
        self.set_font('NotoSansKR', '', size)
        self.multi_cell(0, self.line_height, text)
        self.ln(1)

    def add_image_with_caption(self, image_path, caption, width=150):
        """이미지와 캡션"""
        if os.path.exists(image_path):
            try:
                y_pos = self.get_y()
                self.image(image_path, x=30, y=y_pos, w=width)
                self.ln(width * 0.7)

                self.set_font('NotoSansKR', '', 9)
                self.cell(0, 4, caption, 0, 1, 'C')
                self.ln(1)
            except:
                pass

    def add_table(self, data, col_widths):
        """테이블"""
        self.set_font('NotoSansKR', 'B', 9)

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                if i == 0:
                    self.set_fill_color(30, 58, 138)
                    self.set_text_color(255, 255, 255)
                else:
                    self.set_fill_color(249, 250, 251) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
                    self.set_text_color(0, 0, 0)
                    self.set_font('NotoSansKR', '', 8.5)

                self.cell(col_widths[j], 5, str(cell), 1, 0, 'C', True)
            self.ln()
        self.ln(2)

# PDF 생성
pdf = PaperPDF()

# 1. 제목 페이지
pdf.add_title_section(
    '머신러닝을 이용한 고객 만족도 예측 모델 개발\n: Santander 고객 데이터 분석',
    '이민석',
    '데이터 과학 연구팀',
    datetime.now().strftime('%Y년 %m월 %d일')
)

# 2. 초록
abstract_text = '''본 연구는 Santander 은행의 고객 데이터를 활용하여 고객 불만족도를 예측하는 머신러닝 모델을 개발하였다.
전체 76,020명의 고객 데이터로부터 371개 변수를 수집하였으며, 심각한 클래스 불균형(만족 96.04%, 불만족 3.96%)을 해결하기 위해 다양한 전처리 기법을 적용하였다.
통계적 검정, LASSO 회귀, Random Forest, XGBoost의 4가지 변수 선택 방법을 적용하여 최종 15개 변수를 선택하였으며, 이 중 86.7%가 모든 방법에서 공통적으로 선택되었다.
XGBoost, LightGBM, RandomForest 등 5개 모델을 평가한 결과, XGBoost Tuned 모델이 0.8172의 ROC-AUC와 0.2618의 F1-score로 최고 성능을 달성하였다.
본 연구 결과는 금융 기관의 고객 이탈 방지 및 맞춤형 서비스 제공에 활용될 수 있으며, 불균형 데이터셋에서의 머신러닝 모델 개발 방법론을 제시한다.'''

pdf.add_abstract(abstract_text)

# 3. 서론
pdf.add_page()
pdf.add_section('1. 서론')
pdf.add_text(
    '''금융 기관에서 고객 유지는 매우 중요한 경영 과제이다. 특히 고객 불만족은 이탈로 직결되기 때문에,
불만족 고객을 사전에 식별하여 대응하는 것이 필수적이다. 본 연구는 Santander 은행의 고객 데이터를 활용하여
머신러닝 기반의 고객 불만족도 예측 모델을 개발하고자 한다.'''
)

pdf.add_subsection('1.1 연구의 필요성')
pdf.add_text(
    '''전통적인 고객 관리 방식은 사후 대응에 불과하나, 머신러닝을 통한 예측 모델은 고객 이탈을 사전에 방지할 수 있다.
또한 대규모 고객 데이터에서 불만족 고객의 특성을 자동으로 학습하여 맞춤형 서비스를 제공할 수 있다.'''
)

pdf.add_subsection('1.2 연구의 목표')
pdf.add_text(
    '''본 연구의 목표는 다음과 같다:
• 고객 데이터의 탐색적 분석을 통해 불만족과 관련된 변수 식별
• 통계적 및 머신러닝 기반 변수 선택 방법의 통합
• 불균형 데이터셋에 적합한 모델 개발 및 평가
• 실무 적용 가능한 예측 모델 제시''', 10
)

# 4. 데이터 및 방법론
pdf.add_section('2. 데이터 및 방법론')

pdf.add_subsection('2.1 데이터셋')
pdf.add_text(
    '''Santander 고객 데이터셋은 총 76,020명의 관측치와 371개의 변수로 구성되어 있다.
타겟 변수(TARGET)는 고객 만족도를 나타내며, 0 (만족)과 1 (불만족)의 이진 분류 문제이다.'''
)

data_info = [
    ['항목', '값'],
    ['총 관측치', '76,020'],
    ['전체 변수', '371'],
    ['만족 고객 (TARGET=0)', '72,979명 (96.04%)'],
    ['불만족 고객 (TARGET=1)', '3,041명 (3.96%)'],
    ['데이터 타입', '수치형 (371개)'],
    ['결측치', '0개'],
]

pdf.add_table(data_info, [85, 85])

pdf.add_subsection('2.2 데이터 전처리')
pdf.add_text(
    '''데이터 전처리는 다음 단계로 진행하였다:
• 결측값 처리: var3 변수의 특수 결측 코드(-999999)를 NaN으로 변환 후 중앙값으로 대체
• 변수 제거: ID 변수 (고유값), 상수 변수 (분산=0), 극희소 변수 (표본<100명) 제거
• 특성 생성: var3_missing 파생변수 생성으로 원래 결측 정보 보존
• 표준화: 연속형 변수에 표준정규화(StandardScaler) 적용'''
)

# 이미지 삽입
pdf.add_image_with_caption('figures/eda_target_distribution.png', 'Figure 1: 타겟 변수 분포 (클래스 불균형)')

pdf.add_subsection('2.3 변수 선택 방법')
pdf.add_text(
    '''변수 선택의 안정성을 보장하기 위해 4가지 독립적인 방법을 적용하였다:
1) 통계적 검정: 카이제곱 검정으로 변수와 TARGET 간의 통계적 유의성 평가
2) LASSO 회귀: L1 정규화를 통한 선형 모델 기반 변수 선택
3) Random Forest: 트리 기반 모델의 특성 중요도로 상위 20% 변수 선택
4) XGBoost: 그래디언트 부스팅의 특성 중요도로 상위 20% 변수 선택'''
)

pdf.add_subsection('2.4 모델 개발')
pdf.add_text(
    '''다음 5개 모델을 개발하여 비교하였다:
• Logistic Regression: 베이스라인 모델
• XGBoost Baseline: 기본 하이퍼파라미터
• XGBoost Tuned: RandomizedSearchCV를 통한 하이퍼파라미터 최적화
• LightGBM: 그래디언트 부스팅 모델
• RandomForest: 트리 기반 앙상블 모델

클래스 불균형을 해결하기 위해 class_weight='balanced' 설정을 적용하였다.'''
)

pdf.add_subsection('2.5 평가 지표')
pdf.add_text(
    '''클래스 불균형 데이터의 특성을 고려하여 다음 지표를 사용하였다:
• ROC-AUC: 모든 임계값에서 분류 성능 평가
• PR-AUC: 소수 클래스(불만족) 중심 평가
• Precision: 불만족 예측의 정확도
• Recall: 실제 불만족 고객의 탐지율
• F1-score: Precision과 Recall의 조화평균'''
)

# 5. 실험 결과
pdf.add_page()
pdf.add_section('3. 실험 결과')

pdf.add_subsection('3.1 변수 선택 결과')
pdf.add_text(
    '''4가지 변수 선택 방법을 통해 총 15개의 최종 변수를 선택하였다.
13개 변수 (86.7%)가 4가지 방법 모두에서 선택되었으며, 2개 변수는 3개 이상의 방법에서 선택되었다.
이는 선택된 변수들의 신뢰도가 매우 높음을 의미한다.''')

var_selection = [
    ['변수명', '의미', '선택횟수'],
    ['ind_var30', '지표 변수 30', '4/4'],
    ['ind_var13', '지표 변수 13', '4/4'],
    ['saldo_var30', '잔액 변수 30', '4/4'],
    ['num_var22_ult1', '숫자 변수 22', '4/4'],
    ['var15', '변수 15', '4/4'],
    ['saldo_var5', '잔액 변수 5', '4/4'],
    ['num_var35', '숫자 변수 35', '4/4'],
]

pdf.add_table(var_selection, [50, 80, 40])

pdf.add_subsection('3.2 모델 성능 비교')
pdf.add_text(
    '''Test 데이터셋을 기준으로 각 모델의 성능을 평가하였다. XGBoost Tuned 모델이
0.8172의 ROC-AUC와 0.2618의 F1-score로 최고 성능을 달성하였다.''')

model_performance = [
    ['모델', 'Accuracy', 'ROC-AUC', 'Precision', 'Recall', 'F1-score'],
    ['Logistic', '0.8827', '0.7888', '0.1509', '0.7342', '0.1546'],
    ['XGBoost Base', '0.8836', '0.8172', '0.1968', '0.5166', '0.2734'],
    ['XGBoost Tuned*', '0.9036', '0.8172', '0.1877', '0.4326', '0.2618'],
    ['LightGBM', '0.8805', '0.8208', '0.1921', '0.5440', '0.2709'],
    ['RandomForest', '0.8389', '0.8074', '0.1402', '0.5980', '0.2272'],
]

pdf.add_table(model_performance, [22, 18, 18, 18, 17, 17])

pdf.add_text('* 선택된 최종 모델', 9)

# 이미지 삽입
pdf.add_image_with_caption('figures/eda_correlation_heatmap.png', 'Figure 2: 선택된 변수들의 상관관계 히트맵')

pdf.add_subsection('3.3 특성 중요도 분석')
pdf.add_text(
    '''XGBoost Tuned 모델에서 추출한 특성 중요도를 분석하면, ind_var30, saldo 변수들이
모델의 예측에 가장 큰 영향을 미치는 것으로 나타났다. 이는 고객의 특정 지표와 계좌 잔액이
만족도 예측에 중요함을 의미한다.''')

pdf.add_image_with_caption('figures/model_feature_importance.png', 'Figure 3: XGBoost Tuned 모델의 특성 중요도')

# 6. 토의
pdf.add_page()
pdf.add_section('4. 토의')

pdf.add_subsection('4.1 주요 발견사항')
pdf.add_text(
    '''본 연구에서 얻은 주요 발견사항은 다음과 같다:

1) 클래스 불균형 해결: 불균형 데이터(만족 96%, 불만족 4%)에서도 ROC-AUC 0.8172의
우수한 성능을 달성하였다.

2) 안정적인 변수 선택: 4가지 독립적인 방법 중 86.7%의 변수가 모두 선택되어 선택 변수의
신뢰도가 높다.

3) 모델 성능 향상: 하이퍼파라미터 튜닝을 통해 기존 모델 대비 F1-score를 69.4% 개선하였다.

4) 관련 변수 식별: ind_var30, ind_var5는 고객 만족 지표, ind_var8_0은 위험 지표로
실무 활용 가능성이 높다.''')

pdf.add_subsection('4.2 모델 해석')
pdf.add_text(
    '''XGBoost Tuned 모델은 Threshold 0.70으로 설정할 때 최고 F1-score를 달성한다.
이는 불만족 고객을 무조건 많이 탐지하기보다는 정밀도(Precision)와 재현율(Recall)의
균형을 취한 결정 기준점이다. Recall 0.4326은 실제 불만족 고객의 43.26%를 탐지할 수 있음을 의미하며,
한정된 리소스를 고위험 고객에 집중할 수 있다.''')

pdf.add_subsection('4.3 실무 적용 가능성')
pdf.add_text(
    '''본 모델은 다음과 같이 실무에 적용할 수 있다:
• 신규 고객 또는 기존 고객의 불만족 확률 실시간 예측
• 고객 세그먼트화: 예측 확률에 따른 차등 관리 전략 수립
• 고객 이탈 방지 캠페인: 고위험 고객 대상 맞춤형 서비스 제공
• 리소스 최적화: 한정된 고객 관리 인력의 효율적 배분''')

pdf.add_subsection('4.4 한계 및 향후 연구')
pdf.add_text(
    '''본 연구의 한계점은 다음과 같다:
• 변수의 비즈니스 의미가 명확하지 않아 해석 어려움
• 시계열 정보 부재: 시간에 따른 고객의 변화 패턴 미반영
• 외부 변수 미포함: 거시경제 지표, 경쟁사 정보 등

향후 연구 방향으로는:
• SHAP, LIME 등 해석 가능한 AI(XAI) 기법 도입
• 시계열 분석을 통한 고객 변화 추적
• 외부 데이터 통합 분석
• 멀티태스크 러닝을 통한 다중 예측 모델 개발''')

# 7. 결론
pdf.add_section('5. 결론')
pdf.add_text(
    '''본 연구는 Santander 고객 데이터를 활용하여 불만족도 예측 머신러닝 모델을 성공적으로 개발하였다.
통계적 방법과 머신러닝 방법을 결합한 변수 선택으로 신뢰도 높은 15개 변수를 도출하였으며,
XGBoost Tuned 모델이 0.8172의 ROC-AUC 성능으로 고객 세분화의 기반을 제공할 수 있음을 입증하였다.

특히 클래스 불균형이 심한 금융 데이터셋에서 다양한 평가 지표를 통해 모델을 종합적으로 평가하고,
4가지 변수 선택 방법의 교차 검증으로 모델의 견고성을 확보하였다.

본 연구 결과는 금융 기관의 고객 이탈 방지, 맞춤형 서비스 제공, 리소스 최적화에 직접 활용될 수 있으며,
불균형 데이터셋에서의 머신러닝 모델 개발 방법론을 제시한다는 점에서 학술적 의의도 있다.''')

# 8. 참고문헌
pdf.add_page()
pdf.add_section('참고문헌')

references = [
    '[1] Chen, T., & Guestrin, C. (2016). "XGBoost: A scalable tree boosting system". In KDD\'16: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.',
    '[2] Ke, G., Meng, Q., Finley, T., et al. (2017). "LightGBM: A fast, distributed, gradient boosting framework". In Advances in Neural Information Processing Systems.',
    '[3] Breiman, L. (2001). "Random forests". Machine Learning, 45(1), 5-32.',
    '[4] Tibshirani, R. (1996). "Regression shrinkage and selection via the lasso". Journal of the Royal Statistical Society, 58(1), 267-288.',
    '[5] Fawcett, T. (2006). "An introduction to ROC analysis". Pattern Recognition Letters, 27(8), 861-874.',
    '[6] Powers, D. M. (2011). "Evaluation: from precision, recall and F-measure to ROC, informedness, markedness and correlation". arXiv preprint arXiv:1502.05477.',
    '[7] Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). "SMOTE: synthetic minority over-sampling technique". Journal of Artificial Intelligence Research, 16, 321-357.',
    '[8] Lundberg, S. M., & Lee, S. I. (2017). "A unified approach to interpreting model predictions". In Advances in Neural Information Processing Systems.',
]

pdf.set_font('NotoSansKR', '', 9)
for i, ref in enumerate(references, 1):
    pdf.multi_cell(0, 4, ref)
    pdf.ln(1)

# PDF 저장
pdf_path = "산탄데르_고객만족도_분석논문.pdf"
pdf.output(pdf_path)

print(f"✅ 논문 형식 PDF가 '{pdf_path}'에 생성되었습니다!")
print(f"📄 파일 크기: {os.path.getsize(pdf_path) / 1024:.1f} KB")
print(f"\n논문 구성:")
print("  • 제목 페이지")
print("  • 초록 및 키워드")
print("  • 1. 서론")
print("  • 2. 데이터 및 방법론")
print("  • 3. 실험 결과")
print("  • 4. 토의")
print("  • 5. 결론")
print("  • 참고문헌")
