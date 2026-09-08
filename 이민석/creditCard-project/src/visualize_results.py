"""
모델 성능 비교를 시각화합니다
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")

# 결과 로드
results_df = pd.read_csv('model_performance_comparison.csv')

print("모델 성능 데이터:")
print(results_df.to_string(index=False))

# 1. 성능 지표 비교 (막대 그래프)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for idx, (ax, metric) in enumerate(zip(axes.flat, metrics)):
    data = results_df[['Model', metric]].sort_values(metric, ascending=False)
    ax.bar(data['Model'], data[metric], color=colors[idx], alpha=0.7, edgecolor='black')
    ax.set_ylabel(metric, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3)

    # 값 표시
    for i, (model, value) in enumerate(zip(data['Model'], data[metric])):
        ax.text(i, value + 0.02, f'{value:.4f}', ha='center', fontsize=9)

    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('model_performance_comparison.png', dpi=300, bbox_inches='tight')
print("\n✓ 성능 지표 비교 그래프 저장: model_performance_comparison.png")

# 2. ROC-AUC 및 PR-AUC 비교
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('ROC-AUC and PR-AUC Comparison', fontsize=16, fontweight='bold')

# ROC-AUC
data_roc = results_df[['Model', 'ROC-AUC']].sort_values('ROC-AUC', ascending=False)
ax1.bar(data_roc['Model'], data_roc['ROC-AUC'], color='#1f77b4', alpha=0.7, edgecolor='black')
ax1.set_ylabel('ROC-AUC Score', fontsize=11, fontweight='bold')
ax1.set_ylim(0, 1)
ax1.grid(axis='y', alpha=0.3)
for i, (model, value) in enumerate(zip(data_roc['Model'], data_roc['ROC-AUC'])):
    ax1.text(i, value + 0.02, f'{value:.4f}', ha='center', fontsize=9)
ax1.tick_params(axis='x', rotation=45)

# PR-AUC
data_pr = results_df[['Model', 'PR-AUC']].sort_values('PR-AUC', ascending=False)
ax2.bar(data_pr['Model'], data_pr['PR-AUC'], color='#ff7f0e', alpha=0.7, edgecolor='black')
ax2.set_ylabel('PR-AUC Score', fontsize=11, fontweight='bold')
ax2.set_ylim(0, 1)
ax2.grid(axis='y', alpha=0.3)
for i, (model, value) in enumerate(zip(data_pr['Model'], data_pr['PR-AUC'])):
    ax2.text(i, value + 0.02, f'{value:.4f}', ha='center', fontsize=9)
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('auc_comparison.png', dpi=300, bbox_inches='tight')
print("✓ AUC 비교 그래프 저장: auc_comparison.png")

# 3. 레이더 차트 (각 모델의 다차원 성능)
from math import pi

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

categories = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'PR-AUC']
N = len(categories)

angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

colors_radar = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for idx, row in results_df.iterrows():
    values = [
        row['Accuracy'],
        row['Precision'],
        row['Recall'],
        row['F1-Score'],
        row['ROC-AUC'],
        row['PR-AUC']
    ]
    values += values[:1]

    ax.plot(angles, values, 'o-', linewidth=2, label=row['Model'], color=colors_radar[idx])
    ax.fill(angles, values, alpha=0.15, color=colors_radar[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=10)
ax.set_ylim(0, 1)
ax.set_title('Model Performance Radar Chart', size=16, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.grid(True)

plt.tight_layout()
plt.savefig('radar_chart.png', dpi=300, bbox_inches='tight')
print("✓ 레이더 차트 저장: radar_chart.png")

# 4. 히트맵
fig, ax = plt.subplots(figsize=(10, 5))

# 정규화 (0-1 범위로)
normalized_df = results_df.copy()
for col in ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'PR-AUC']:
    normalized_df[col] = (normalized_df[col] - normalized_df[col].min()) / (normalized_df[col].max() - normalized_df[col].min())

# 히트맵 데이터
heatmap_data = normalized_df.set_index('Model')[['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'PR-AUC']]

sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='YlGn', cbar_kws={'label': 'Normalized Score'},
            linewidths=0.5, ax=ax, vmin=0, vmax=1)
ax.set_title('Model Performance Heatmap (Normalized)', fontsize=16, fontweight='bold')
ax.set_ylabel('Model', fontsize=11, fontweight='bold')
ax.set_xlabel('Metrics', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('performance_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ 성능 히트맵 저장: performance_heatmap.png")

# 5. 종합 순위 (F1-Score 기준)
print("\n" + "="*60)
print("🏆 최종 모델 순위 (F1-Score 기준)")
print("="*60)

rank_df = results_df[['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']].sort_values('F1-Score', ascending=False)
rank_df['Rank'] = range(1, len(rank_df) + 1)
rank_df = rank_df[['Rank', 'Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']]

print("\n" + rank_df.to_string(index=False))

# 최고의 모델
best_model = results_df.loc[results_df['F1-Score'].idxmax()]
print(f"\n{'='*60}")
print(f"🥇 최고의 모델: {best_model['Model']}")
print(f"{'='*60}")
print(f"  Accuracy:     {best_model['Accuracy']:.4f}")
print(f"  Precision:    {best_model['Precision']:.4f}")
print(f"  Recall:       {best_model['Recall']:.4f}")
print(f"  F1-Score:     {best_model['F1-Score']:.4f}")
print(f"  ROC-AUC:      {best_model['ROC-AUC']:.4f}")
print(f"  PR-AUC:       {best_model['PR-AUC']:.4f}")

print(f"\n✅ 모든 시각화 완료!")
