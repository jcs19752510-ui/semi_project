"""
SMOTE 적용 전후 성능 비교 시각화
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")

# 데이터 로드
original_df = pd.read_csv('model_performance_comparison.csv')
smote_df = pd.read_csv('model_performance_comparison_with_smote.csv')

print("="*60)
print("SMOTE 적용 전후 비교")
print("="*60)

# 1. F1-Score 비교
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('F1-Score Comparison: Before vs After SMOTE', fontsize=16, fontweight='bold')

x = np.arange(len(original_df))
width = 0.35

ax1 = axes[0]
bars1 = ax1.bar(x - width/2, original_df['F1-Score'], width, label='Before SMOTE', alpha=0.8, color='#1f77b4', edgecolor='black')
bars2 = ax1.bar(x + width/2, smote_df['F1-Score'], width, label='After SMOTE', alpha=0.8, color='#ff7f0e', edgecolor='black')

ax1.set_ylabel('F1-Score', fontsize=11, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(original_df['Model'], rotation=45, ha='right')
ax1.set_ylim(0, 1)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 값 표시
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.4f}', ha='center', va='bottom', fontsize=8)

# 2. 성능 변화도
ax2 = axes[1]
improvements = []
for orig_row, smote_row in zip(original_df.iterrows(), smote_df.iterrows()):
    orig_f1 = orig_row[1]['F1-Score']
    smote_f1 = smote_row[1]['F1-Score']
    improvement = ((smote_f1 - orig_f1) / orig_f1 * 100) if orig_f1 > 0 else 0
    improvements.append(improvement)

colors = ['#2ca02c' if x > 0 else '#d62728' for x in improvements]
bars = ax2.bar(original_df['Model'], improvements, alpha=0.8, color=colors, edgecolor='black')

ax2.set_ylabel('Improvement %', fontsize=11, fontweight='bold')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.set_xticklabels(original_df['Model'], rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)

# 값 표시
for bar, val in zip(bars, improvements):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + (2 if height > 0 else -5),
            f'{val:+.2f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('smote_f1score_comparison.png', dpi=300, bbox_inches='tight')
print("\n✓ F1-Score 비교 그래프 저장: smote_f1score_comparison.png")

# 3. ROC-AUC 비교
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle('ROC-AUC Comparison: Before vs After SMOTE', fontsize=16, fontweight='bold')

x = np.arange(len(original_df))
width = 0.35

bars1 = ax.bar(x - width/2, original_df['ROC-AUC'], width, label='Before SMOTE', alpha=0.8, color='#1f77b4', edgecolor='black')
bars2 = ax.bar(x + width/2, smote_df['ROC-AUC'], width, label='After SMOTE', alpha=0.8, color='#ff7f0e', edgecolor='black')

ax.set_ylabel('ROC-AUC', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(original_df['Model'], rotation=45, ha='right')
ax.set_ylim(0.7, 1)
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 값 표시
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{height:.4f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('smote_roc_auc_comparison.png', dpi=300, bbox_inches='tight')
print("✓ ROC-AUC 비교 그래프 저장: smote_roc_auc_comparison.png")

# 4. Recall 비교
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle('Recall Comparison: Before vs After SMOTE', fontsize=16, fontweight='bold')

x = np.arange(len(original_df))
width = 0.35

bars1 = ax.bar(x - width/2, original_df['Recall'], width, label='Before SMOTE', alpha=0.8, color='#1f77b4', edgecolor='black')
bars2 = ax.bar(x + width/2, smote_df['Recall'], width, label='After SMOTE', alpha=0.8, color='#ff7f0e', edgecolor='black')

ax.set_ylabel('Recall', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(original_df['Model'], rotation=45, ha='right')
ax.set_ylim(0, 1)
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 값 표시
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.4f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('smote_recall_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Recall 비교 그래프 저장: smote_recall_comparison.png")

# 5. 다중 지표 비교 (Precision, Recall, F1-Score)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Detailed Metrics Comparison: Before vs After SMOTE', fontsize=16, fontweight='bold')

metrics_to_compare = ['Precision', 'Recall', 'F1-Score', 'ROC-AUC']
x = np.arange(len(original_df))
width = 0.35

for idx, (ax, metric) in enumerate(zip(axes.flat, metrics_to_compare)):
    bars1 = ax.bar(x - width/2, original_df[metric], width, label='Before SMOTE', alpha=0.8, color='#1f77b4', edgecolor='black')
    bars2 = ax.bar(x + width/2, smote_df[metric], width, label='After SMOTE', alpha=0.8, color='#ff7f0e', edgecolor='black')

    ax.set_ylabel(metric, fontsize=10, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(original_df['Model'], rotation=45, ha='right')
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('smote_detailed_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 상세 지표 비교 그래프 저장: smote_detailed_comparison.png")

# 6. 최종 요약 테이블
print("\n" + "="*60)
print("📊 최종 비교 요약")
print("="*60)

summary_data = []
for orig_row, smote_row in zip(original_df.iterrows(), smote_df.iterrows()):
    orig_f1 = orig_row[1]['F1-Score']
    smote_f1 = smote_row[1]['F1-Score']
    improvement = ((smote_f1 - orig_f1) / orig_f1 * 100) if orig_f1 > 0 else 0

    summary_data.append({
        'Model': orig_row[1]['Model'],
        'Before F1': f"{orig_f1:.4f}",
        'After F1': f"{smote_f1:.4f}",
        'Improvement': f"{improvement:+.2f}%",
        'Before Recall': f"{orig_row[1]['Recall']:.4f}",
        'After Recall': f"{smote_row[1]['Recall']:.4f}",
    })

summary_table = pd.DataFrame(summary_data)
print("\n" + summary_table.to_string(index=False))

# 7. 권장 모델
print("\n" + "="*60)
print("🏆 권장 모델")
print("="*60)

best_f1_original = original_df.loc[original_df['F1-Score'].idxmax()]
best_f1_smote = smote_df.loc[smote_df['F1-Score'].idxmax()]

print(f"\n📌 원본 데이터에서 최고: {best_f1_original['Model']}")
print(f"   F1-Score: {best_f1_original['F1-Score']:.4f} | ROC-AUC: {best_f1_original['ROC-AUC']:.4f} | Recall: {best_f1_original['Recall']:.4f}")

print(f"\n📌 SMOTE 적용 후 최고: {best_f1_smote['Model']}")
print(f"   F1-Score: {best_f1_smote['F1-Score']:.4f} | ROC-AUC: {best_f1_smote['ROC-AUC']:.4f} | Recall: {best_f1_smote['Recall']:.4f}")

# 8. 의견
print("\n" + "="*60)
print("💡 분석 의견")
print("="*60)
print("""
✅ SMOTE의 효과:
  - LightGBM: F1-Score 95.22% 대폭 개선 (0.3631 → 0.7089)
  - 이진 분류에서 불균형이 심할 때 SMOTE는 효과적

⚠️  주의사항:
  - Random Forest, XGBoost: 원본이 이미 잘 작동하여 SMOTE로 약간 하락
  - Logistic Regression: 정밀도 저하 (여러 거짓 양성 증가)

🎯 최종 추천:
  - 원본 데이터: Random Forest (F1: 0.8743)
  - SMOTE 적용: Random Forest 또는 XGBoost (F1: ~0.826)
  - 사기 탐지 특성상 Recall이 중요하면 SMOTE 적용 추천
""")

print("\n✅ 모든 시각화 완료!")
