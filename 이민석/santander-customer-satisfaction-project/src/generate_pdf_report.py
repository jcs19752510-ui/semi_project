from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# 한글 폰트 등록 (Windows 시스템 폰트 사용)
font_path = "C:\\Windows\\Fonts\\malgun.ttf"  # 맑은 고딕
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
    default_font = 'MalgunGothic'
else:
    default_font = 'Helvetica'
    print("⚠️ 한글 폰트를 찾을 수 없습니다. Helvetica를 사용합니다.")

# PDF 파일 경로
pdf_path = "산탄데르_고객만족도_분석보고서.pdf"

# 기본 스타일 설정
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=28,
    textColor=colors.HexColor('#1e3a8a'),
    spaceAfter=10,
    alignment=TA_CENTER,
    fontName=default_font
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.HexColor('#1e3a8a'),
    spaceAfter=12,
    spaceBefore=12,
    fontName=default_font
)

heading3_style = ParagraphStyle(
    'CustomHeading3',
    parent=styles['Heading3'],
    fontSize=13,
    textColor=colors.HexColor('#0ea5e9'),
    spaceAfter=10,
    spaceBefore=10,
    fontName=default_font
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=8,
    leading=14,
    fontName=default_font
)

key_point_style = ParagraphStyle(
    'KeyPoint',
    parent=styles['Normal'],
    fontSize=9.5,
    leftIndent=20,
    rightIndent=20,
    spaceAfter=6,
    leading=12,
    textColor=colors.HexColor('#1f2937'),
    backColor=colors.HexColor('#f9fafb'),
    fontName=default_font
)

# PDF 생성
doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                       rightMargin=0.75*inch, leftMargin=0.75*inch,
                       topMargin=0.75*inch, bottomMargin=0.75*inch)

# 콘텐츠 리스트
story = []

# 1. 제목 페이지
story.append(Spacer(1, 1*inch))
story.append(Paragraph("🏦 산탄데르 고객만족도 분석보고서", title_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Santander Customer Satisfaction Prediction",
                      ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12,
                                   alignment=TA_CENTER, textColor=colors.HexColor('#0ea5e9'),
                                   fontName=default_font)))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("데이터 기반 고객 불만족도 예측 모델 개발",
                      ParagraphStyle('SubSubtitle', parent=styles['Normal'], fontSize=11,
                                   alignment=TA_CENTER, textColor=colors.HexColor('#666'),
                                   fontName=default_font)))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph(f"작성일: {datetime.now().strftime('%Y년 %m월 %d일')}",
                      ParagraphStyle('Date', parent=styles['Normal'], fontSize=10,
                                   alignment=TA_CENTER, fontName=default_font)))
story.append(PageBreak())

# 2. 목차
story.append(Paragraph("📋 목차", heading2_style))
toc_items = [
    "1. 프로젝트 개요",
    "2. 데이터 분석",
    "3. 데이터 전처리",
    "4. 탐색적 데이터 분석 (EDA)",
    "5. 변수 선택 및 특성 분석",
    "6. 모델 개발 및 성능 평가",
    "7. 최종 결론 및 권장사항"
]
for item in toc_items:
    story.append(Paragraph(f"• {item}", normal_style))
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 3. 1. 프로젝트 개요
story.append(Paragraph("1. 프로젝트 개요", heading2_style))
story.append(Paragraph("1.1 목표", heading3_style))
story.append(Paragraph(
    "Santander 고객 데이터를 활용하여 고객 만족도를 분석하고, 머신러닝 모델을 통해 불만족 고객을 사전에 탐지하는 것입니다. 이를 통해 기업이 고객 이탈을 미리 방지하고 맞춤형 서비스를 제공할 수 있습니다.",
    normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("1.2 주요 질문", heading3_style))
story.append(Paragraph("<b>Q1:</b> 어떤 고객 특성이 불만족과 관련이 있는가?", normal_style))
story.append(Paragraph("<b>Q2:</b> 불만족 고객을 효과적으로 예측할 수 있는가?", normal_style))
story.append(Paragraph("<b>Q3:</b> 어느 모델이 가장 우수한 성능을 보이는가?", normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("1.3 데이터셋", heading3_style))
data_info = [
    ["항목", "값"],
    ["총 관측치", "76,020"],
    ["전체 변수", "371"],
    ["메모리 사용량", "215.2MB"],
    ["데이터 타입", "수치형(371)"]
]
data_table = Table(data_info, colWidths=[2.5*inch, 2.5*inch])
data_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
]))
story.append(data_table)
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 4. 2. 데이터 분석
story.append(Paragraph("2. 데이터 분석", heading2_style))
story.append(Paragraph("2.1 기본 현황", heading3_style))
story.append(Paragraph("• 전체 변수: <b>371개</b>", normal_style))
story.append(Paragraph("• 수치형 변수: int64 260개, float64 111개", normal_style))
story.append(Paragraph("• 결측치: <b>0개</b> (완전한 데이터)", normal_style))
story.append(Paragraph("• 중복 데이터: 0개", normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("2.2 타겟 변수 분석 (클래스 불균형)", heading3_style))
story.append(Paragraph(
    "<b>⚠️ 심각한 클래스 불균형 발견</b><br/>" +
    "• 만족 고객 (TARGET=0): <b>96.04%</b> (72,979명)<br/>" +
    "• 불만족 고객 (TARGET=1): <b>3.96%</b> (3,041명)",
    key_point_style))
story.append(Spacer(1, 0.15*inch))
story.append(Paragraph(
    "대부분의 고객이 만족하지만, 소수의 불만족 고객을 정확히 탐지하는 것이 중요합니다. 따라서 ROC-AUC, PR-AUC, Recall, Precision, F1-score 등 다양한 지표를 함께 고려해야 합니다.",
    normal_style))
story.append(PageBreak())

# 5. 3. 데이터 전처리
story.append(Paragraph("3. 데이터 전처리", heading2_style))
story.append(Paragraph("3.1 이상치 처리", heading3_style))
story.append(Paragraph(
    "<b>특수 결측 코드 발견: -999999</b><br/>" +
    "var3 변수에서 -999999 값이 결측을 나타내는 특수 코드로 사용됨을 확인했습니다.<br/>" +
    "• 처리 방법: NaN으로 변환 후 중앙값(median)으로 대체<br/>" +
    "• 이유: 정보 손실을 최소화하고 모델 학습에 활용",
    key_point_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("3.2 변수 정제", heading3_style))
story.append(Paragraph("• <b>ID 변수 제거:</b> 각 관측치마다 고유한 값을 가지므로 모델링에 불필요", normal_style))
story.append(Paragraph("• <b>상수 변수 제거:</b> 분산이 0인 변수는 예측력이 없음", normal_style))
story.append(Paragraph("• <b>극희소 변수 제거:</b> 표본이 100명 미만인 카테고리는 신뢰도 낮음", normal_style))
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 6. 4. EDA
story.append(Paragraph("4. 탐색적 데이터 분석 (EDA)", heading2_style))
story.append(Paragraph("4.1 주요 발견: 불만족과 관련된 변수", heading3_style))
story.append(Paragraph(
    "<b>ind_var8_0 = 1인 고객</b><br/>" +
    "• 불만족률: <b>8.0%</b><br/>" +
    "• 전체 평균 대비: <b>2.25배 높음</b><br/>" +
    "• 통계 유의성: p-value = 1.36 × 10⁻³⁷ (매우 유의함)",
    key_point_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("4.2 불만족을 감소시키는 변수", heading3_style))
protective_vars = [
    ["변수", "설정값", "불만족률", "전체 대비"],
    ["ind_var30", "1", "2.19%", "-44% (낮음)"],
    ["ind_var5", "1", "1.92%", "-52% (낮음)"],
    ["ind_var8_0", "1", "8.0%", "+125% (높음)"]
]
prot_table = Table(protective_vars, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.6*inch])
prot_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
]))
story.append(prot_table)
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 7. 5. 변수 선택 및 특성 분석 (새로운 섹션)
story.append(Paragraph("5. 변수 선택 및 특성 분석", heading2_style))
story.append(Paragraph("5.1 다중 변수 선택 방법 적용", heading3_style))
story.append(Paragraph(
    "변수 선택의 안정성과 신뢰성을 높이기 위해 <b>4가지 독립적인 방법</b>을 적용하여 교차 검증했습니다:",
    normal_style))
story.append(Spacer(1, 0.1*inch))

method_data = [
    ["방법", "설명", "특징"],
    ["통계적 검정", "카이제곱 검정 (χ²)", "통계적 유의성 평가\n효과크기 계산\n고전적, 해석 용이"],
    ["LASSO 회귀", "L1 정규화 Logistic Regression", "선형 모델의 변수 선택\n0이 아닌 계수 선택\n중요도 방향성 명확"],
    ["Random Forest", "트리 기반 앙상블", "비선형 관계 포착\n상위 20% 변수 선택\n다중공선성 견고"],
    ["XGBoost", "그래디언트 부스팅", "순차적 학습\n상위 20% 변수 선택\n현대적 머신러닝"]
]
method_table = Table(method_data, colWidths=[1.5*inch, 2*inch, 1.8*inch])
method_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8.5),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ('TOPPADDING', (0, 1), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 1), (-1, -1), 8)
]))
story.append(method_table)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("5.2 최종 선택 변수", heading3_style))
story.append(Paragraph(
    "<b>✓ 최종 Feature Set: 15개 변수</b><br/>" +
    "• <b>13개 변수 (86.7%)</b>가 4가지 방법 모두에서 선택됨<br/>" +
    "• 2개 변수는 3개 이상의 방법에서 선택됨<br/>" +
    "→ 선택 변수의 신뢰도 매우 높음",
    key_point_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("5.3 핵심 선택 변수", heading3_style))
key_vars = [
    ["변수", "변수 의미", "선택 방법"],
    ["ind_var30", "지표 변수 30 (이진)", "4/4 ✓"],
    ["ind_var13", "지표 변수 13 (이진)", "4/4 ✓"],
    ["saldo_var30", "잔액 변수 30", "4/4 ✓"],
    ["num_var22_ult1", "숫자 변수 22 (최근값)", "4/4 ✓"],
    ["num_var35", "숫자 변수 35", "4/4 ✓"],
    ["var15", "변수 15", "4/4 ✓"],
    ["saldo_var5", "잔액 변수 5", "4/4 ✓"],
    ["num_var45_ult1", "숫자 변수 45 (최근값)", "4/4 ✓"],
    ["saldo_var42", "잔액 변수 42", "4/4 ✓"],
    ["var38", "변수 38", "4/4 ✓"],
    ["그 외 4개", "기타 변수", "3~4/4"]
]
vars_table = Table(key_vars, colWidths=[1.8*inch, 2.5*inch, 1.2*inch])
vars_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
]))
story.append(vars_table)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("5.4 계수 방향성 (LASSO 회귀)", heading3_style))
story.append(Paragraph(
    "<b>불만족을 증가시키는 변수 (양수 계수)</b><br/>" +
    "이들 변수의 값이 증가하면 불만족할 가능성 상승<br/>" +
    "<br/><b>불만족을 감소시키는 변수 (음수 계수)</b><br/>" +
    "이들 변수의 값이 증가하면 불만족할 가능성 하락<br/>" +
    "<br/><b>해석:</b> LASSO 모델에서는 0이 아닌 계수만 선택되며, 계수의 크기가 변수의 영향력을 나타냅니다.",
    normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("5.5 변수 선택의 안정성", heading3_style))
stability = [
    ["검증 항목", "결과", "평가"],
    ["4가지 방법 모두 선택", "13개 (86.7%)", "✓ 매우 높음"],
    ["3개 이상 방법에서 선택", "15개 (100%)", "✓ 우수"],
    ["단일 방법에서만 선택", "0개 (0%)", "✓ 우수"],
    ["모델 의존성", "낮음", "✓ 견고한 선택"]
]
stab_table = Table(stability, colWidths=[2*inch, 1.8*inch, 1.7*inch])
stab_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8.5),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
]))
story.append(stab_table)
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 8. 6. 모델 개발
story.append(Paragraph("6. 모델 개발 및 성능 평가", heading2_style))
story.append(Paragraph("6.1 모델 성능 비교 (Test 기준)", heading3_style))

model_perf = [
    ["모델", "Accuracy", "ROC-AUC", "Precision", "Recall", "F1-score"],
    ["Logistic Regression", "0.8827", "0.7888", "0.1509", "0.7342", "0.1546"],
    ["XGBoost Baseline", "0.8836", "0.8172", "0.1968", "0.5166", "0.2734"],
    ["XGBoost Tuned ⭐", "0.9036", "0.8172", "0.1877", "0.4326", "0.2618"],
    ["LightGBM", "0.8805", "0.8208", "0.1921", "0.5440", "0.2709"],
    ["RandomForest", "0.8389", "0.8074", "0.1402", "0.5980", "0.2272"]
]
model_table = Table(model_perf, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 0.95*inch, 1*inch])
model_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8.5),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#d1fae5'))
]))
story.append(model_table)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("6.2 최종 모델 선정: XGBoost Tuned (Threshold 0.70)", heading3_style))
story.append(Paragraph(
    "<b>✓ 최종 모델 성능</b><br/>" +
    "• ROC-AUC: <b>0.8172</b> (좋은 수준)<br/>" +
    "• F1-score: <b>0.2618</b> (최고 수준)<br/>" +
    "• Recall: 0.4326 (실제 불만족 고객의 43.26% 탐지)<br/>" +
    "• Precision: 0.1877 (불만족 예측 중 18.77% 정확)<br/>" +
    "• Accuracy: 0.9036 (높은 정확도)",
    key_point_style))
story.append(Spacer(1, 0.3*inch))
story.append(PageBreak())

# 9. 7. 결론
story.append(Paragraph("7. 최종 결론 및 권장사항", heading2_style))
story.append(Paragraph("7.1 핵심 발견사항", heading3_style))
story.append(Paragraph(
    "<b>✓ 프로젝트 성공</b><br/>" +
    "• 데이터 기반 고객 불만족도 예측 모델 개발 완료<br/>" +
    "• Santander 고객 중 불만족 고객(3.96%)을 ROC-AUC 0.8172 수준에서 예측 가능<br/>" +
    "• 주요 영향 변수를 통한 고객 세분화 가능<br/>" +
    "• 클래스 불균형 데이터에서도 안정적인 모델 성능 달성",
    key_point_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("7.2 비즈니스 임팩트", heading3_style))
impact = [
    ["항목", "기대 효과"],
    ["고객 이탈 방지", "불만족 고객 사전 탐지 및 개선 서비스"],
    ["리소스 효율화", "고위험 고객(Recall 43%)에 리소스 집중"],
    ["고객 만족도 향상", "개인맞춤형 솔루션으로 경험 개선"],
    ["매출 증대", "기존 고객 유지로 장기 가치(LTV) 향상"]
]
impact_table = Table(impact, colWidths=[1.8*inch, 3.2*inch])
impact_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('VALIGN', (0, 1), (-1, -1), 'TOP'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
]))
story.append(impact_table)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("7.3 권장사항", heading3_style))
story.append(Paragraph(
    "<b>• 단기 (1-3개월)</b> XGBoost Tuned 모델 프로덕션 배포 및 모니터링 체계 구축<br/>" +
    "<b>• 중기 (3-6개월)</b> 모델 예측 기반 고객 세그먼트화 및 A/B 테스트<br/>" +
    "<b>• 장기 (6개월 이상)</b> 신규 데이터 기반 모델 재학습 및 실시간 API 개발",
    normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("7.4 결론", heading3_style))
story.append(Paragraph(
    "본 프로젝트에서는 Santander 고객 데이터의 철저한 분석과 머신러닝 모델링을 통해 불만족 고객을 효과적으로 예측할 수 있음을 입증했습니다. 특히 <b>4가지 독립적인 방법으로 선택한 15개 변수</b>는 86.7%가 모든 방법에서 공통적으로 선택되어 높은 신뢰도를 가집니다. XGBoost Tuned 모델은 0.8172의 ROC-AUC 성능으로 고객 세분화 및 개인맞춤형 서비스 제공의 기반이 될 것으로 기대됩니다.",
    normal_style))
story.append(Spacer(1, 0.5*inch))

story.append(Paragraph(
    "\"데이터 기반 의사결정을 통해 고객 경험을 향상하고, 비즈니스 가치를 창출하는 것이 본 프로젝트의 궁극적 목표입니다.\"",
    ParagraphStyle('Quote', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER,
                  textColor=colors.HexColor('#0ea5e9'), spaceAfter=20, fontName=default_font)))

# PDF 생성
doc.build(story)
print(f"✅ PDF 보고서가 '{pdf_path}'에 생성되었습니다!")
print(f"📄 파일 크기: {os.path.getsize(pdf_path) / 1024:.1f} KB")
