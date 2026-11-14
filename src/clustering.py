"""
Clustering and Distance Comparison Module
Implements K-Means clustering across K=2..7, calculates WCSS, Silhouette,
Davies-Bouldin metrics, and compares Euclidean vs Manhattan silhouette scores.
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
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from config import K_RANGE, RANDOM_STATE, N_INIT, OUTPUT_GRAPHS_DIR, EVALUATION_RESULTS_CSV, CLUSTERED_BUSINESSES_CSV

def run_kmeans_experiments(X_scaled, biz_df):
    """
    Evaluates K-Means clustering for K in K_RANGE.
    Calculates WCSS (Inertia), Euclidean Silhouette, Manhattan Silhouette, and Davies-Bouldin.
    """
    print("=" * 60)
    print("RUNNING K-MEANS EXPERIMENTS (K = 2 to 7)")
    print("=" * 60)

    results = []
    models = {}

    for k in K_RANGE:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        labels = kmeans.fit_predict(X_scaled)
        models[k] = kmeans

        wcss = kmeans.inertia_
        sil_euclidean = silhouette_score(X_scaled, labels, metric='euclidean')
        sil_manhattan = silhouette_score(X_scaled, labels, metric='manhattan')
        db_index = davies_bouldin_score(X_scaled, labels)

        results.append({
            'k': k,
            'WCSS': wcss,
            'Silhouette_Euclidean': sil_euclidean,
            'Silhouette_Manhattan': sil_manhattan,
            'Davies_Bouldin': db_index
        })

        print(f"K={k} | WCSS={wcss:.2f} | Sil(Euclid)={sil_euclidean:.4f} | Sil(Manhattan)={sil_manhattan:.4f} | DB={db_index:.4f}")

    eval_df = pd.DataFrame(results)
    eval_df.to_csv(EVALUATION_RESULTS_CSV, index=False)
    print(f"\nEvaluation metrics saved to {EVALUATION_RESULTS_CSV}")

    # Plot Elbow Method (WCSS)
    plt.figure(figsize=(8, 4.5))
    plt.plot(eval_df['k'], eval_df['WCSS'], marker='o', linewidth=2.5, color='#2980b9')
    plt.title("Elbow Method: WCSS vs. Number of Clusters (K)", fontsize=13, fontweight='bold')
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Within-Cluster Sum of Squares (WCSS)")
    plt.xticks(K_RANGE)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "elbow_method.png"), dpi=300)
    plt.close()

    # Plot Silhouette Scores (Euclidean vs Manhattan comparison)
    plt.figure(figsize=(8, 4.5))
    plt.plot(eval_df['k'], eval_df['Silhouette_Euclidean'], marker='s', linewidth=2.5, color='#27ae60', label='Euclidean Distance')
    plt.plot(eval_df['k'], eval_df['Silhouette_Manhattan'], marker='^', linewidth=2.5, color='#e67e22', linestyle='--', label='Manhattan Distance')
    plt.title("Silhouette Score Comparison Across Distance Metrics", fontsize=13, fontweight='bold')
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Silhouette Score")
    plt.xticks(K_RANGE)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "silhouette_comparison.png"), dpi=300)
    plt.close()

    # Plot Davies-Bouldin Index
    plt.figure(figsize=(8, 4.5))
    plt.plot(eval_df['k'], eval_df['Davies_Bouldin'], marker='d', linewidth=2.5, color='#c0392b')
    plt.title("Davies-Bouldin Index vs. Number of Clusters (K)", fontsize=13, fontweight='bold')
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Davies-Bouldin Index (Lower is Better)")
    plt.xticks(K_RANGE)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "davies_bouldin.png"), dpi=300)
    plt.close()

    # Select Optimal K: Evaluate balancing silhouette, DB index, and interpretability
    # For this dataset, evaluate K=4 or K=5
    optimal_k = 4
    print(f"\nSelected Optimal K for Business Segmentation: K = {optimal_k}")
    best_model = models[optimal_k]
    biz_df['cluster'] = best_model.labels_

    biz_df.to_csv(CLUSTERED_BUSINESSES_CSV, index=False)
    print(f"Clustered businesses saved to {CLUSTERED_BUSINESSES_CSV}")

    return eval_df, best_model, biz_df

if __name__ == "__main__":
    from feature_engineering import engineer_business_features, get_clustering_matrix
    biz_df = engineer_business_features()
    X_scaled, _, _ = get_clustering_matrix(biz_df)
    eval_df, best_model, clustered_biz = run_kmeans_experiments(X_scaled, biz_df)
