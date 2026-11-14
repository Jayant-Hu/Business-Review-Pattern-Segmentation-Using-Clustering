"""
PCA Dimensionality Reduction and Visualization Module
Reduces scaled feature space to 2 Principal Components for 2D visualization,
evaluates explained variance, and plots annotated cluster projections.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from config import OUTPUT_GRAPHS_DIR, OUTPUT_RESULTS_DIR

def run_pca_visualization(X_scaled, biz_df):
    """
    Computes PCA (2 components) and plots 2D scatter plots of the clusters.
    Clustering is strictly performed on the original 10-dimensional scaled matrix;
    PCA is strictly employed for visual projection and interpretability.
    """
    print("=" * 60)
    print("RUNNING PRINCIPAL COMPONENT ANALYSIS (PCA)")
    print("=" * 60)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    var_ratio = pca.explained_variance_ratio_
    print(f"Explained Variance: PC1 = {var_ratio[0]*100:.2f}%, PC2 = {var_ratio[1]*100:.2f}% (Total = {sum(var_ratio)*100:.2f}%)")

    biz_df['PCA1'] = X_pca[:, 0]
    biz_df['PCA2'] = X_pca[:, 1]

    # Save PCA coordinates
    pca_file = os.path.join(OUTPUT_RESULTS_DIR, "pca_projections.csv")
    biz_df[['business_id', 'place', 'cluster', 'PCA1', 'PCA2']].to_csv(pca_file, index=False)

    # 1. Plot 2D PCA Clusters
    plt.figure(figsize=(9, 6))
    palette = sns.color_palette("deep", n_colors=biz_df['cluster'].nunique())
    sns.scatterplot(
        x='PCA1',
        y='PCA2',
        hue='cluster',
        palette=palette,
        data=biz_df,
        alpha=0.7,
        s=35,
        edgecolor='k',
        linewidth=0.3
    )
    plt.title(f"2D PCA Projection of Discovered Business Clusters\n(PC1: {var_ratio[0]*100:.1f}%, PC2: {var_ratio[1]*100:.1f}%)", 
              fontsize=13, fontweight='bold')
    plt.xlabel(f"Principal Component 1 ({var_ratio[0]*100:.1f}% Variance)")
    plt.ylabel(f"Principal Component 2 ({var_ratio[1]*100:.1f}% Variance)")
    plt.legend(title="Cluster", loc="best")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "pca_clusters.png"), dpi=300)
    plt.close()

    print(f"PCA scatter plot saved to {os.path.join(OUTPUT_GRAPHS_DIR, 'pca_clusters.png')}")
    return pca, X_pca

if __name__ == "__main__":
    from feature_engineering import get_clustering_matrix
    from config import CLUSTERED_BUSINESSES_CSV
    biz_df = pd.read_csv(CLUSTERED_BUSINESSES_CSV)
    X_scaled, _, _ = get_clustering_matrix(biz_df)
    run_pca_visualization(X_scaled, biz_df)
