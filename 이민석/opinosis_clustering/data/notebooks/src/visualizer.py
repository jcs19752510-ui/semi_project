import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

def draw_ellipse(position, covariance, ax=None, **kwargs):
    ax = ax or plt.gca()
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        width, height = 2 * np.sqrt(covariance)
        angle = 0
    for n_sig in range(1, 4):
        ax.add_patch(Ellipse(position, n_sig * width, n_sig * height, angle, **kwargs))

def plot_gmm_clusters(X_reduced, labels, gmm_model, save_path="outputs/figures/gmm_clusters.png"):
    X_2d = X_reduced[:, :2]
    fig, ax = plt.subplots(figsize=(10, 7))
    
    scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, s=40, cmap='viridis', alpha=0.6, zorder=2)
    
    w_factor = 0.2 / gmm_model.weights_.max()
    for pos, covar, w in zip(gmm_model.means_[:, :2], gmm_model.covariances_, gmm_model.weights_):
        sub_covar = covar[:2, :2] if covar.ndim == 2 else np.diag(covar[:2])
        draw_ellipse(pos, sub_covar, alpha=w * w_factor, color='crimson', zorder=1)

    ax.set_title("GMM Clustering & Confidence Ellipses", fontsize=14, fontweight='bold')
    ax.set_xlabel("PC 1", fontsize=12)
    ax.set_ylabel("PC 2", fontsize=12)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.colorbar(scatter, label='Cluster ID')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[시각화 완료] 저장 경로: {save_path}")