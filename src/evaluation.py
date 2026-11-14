"""
Cluster Evaluation and Stability Analysis Module
Computes cluster profiles, feature comparison bar charts, and performs stability
analysis using multiple random seeds and the Adjusted Rand Index (ARI).
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
from sklearn.metrics import adjusted_rand_score
from config import CLUSTERED_BUSINESSES_CSV, CLUSTER_PROFILES_CSV, OUTPUT_GRAPHS_DIR, OUTPUT_RESULTS_DIR, N_INIT

def analyze_cluster_profiles(biz_df):
    """
    Computes mean and median profiles for each cluster and names them based on observable data patterns.
    """
    print("=" * 60)
    print("ANALYZING CLUSTER PROFILES")
    print("=" * 60)

    numeric_cols = [
        'avg_rating', 'rating_std', 'sample_review_count',
        'positive_review_pct', 'negative_review_pct', 'avg_review_length',
        'detailed_review_pct', 'service_feedback_rate', 'food_feedback_rate',
        'atmosphere_feedback_rate'
    ]

    profile_mean = biz_df.groupby('cluster')[numeric_cols].mean().round(2)
    profile_median = biz_df.groupby('cluster')[numeric_cols].median().round(2)
    cluster_counts = biz_df['cluster'].value_counts().sort_index()

    # Formulate cluster labels based on the real profile statistics:
    # We inspect the mean rating, negative pct, and sample reviews
    cluster_names = {}
    for c in profile_mean.index:
        avg_r = profile_mean.loc[c, 'avg_rating']
        neg_pct = profile_mean.loc[c, 'negative_review_pct']
        serv_pct = profile_mean.loc[c, 'service_feedback_rate']
        rev_len = profile_mean.loc[c, 'avg_review_length']
        
        if avg_r >= 4.5 and neg_pct < 5:
            cluster_names[c] = "High-Satisfaction Top Tier"
        elif neg_pct >= 40 or avg_r <= 2.5:
            cluster_names[c] = "Critical Intervention / At-Risk"
        elif serv_pct > 15 or rev_len > 40:
            cluster_names[c] = "High-Engagement Detailed Feedback"
        else:
            cluster_names[c] = "Moderate / Mixed Feedback"

    biz_df['cluster_name'] = biz_df['cluster'].map(cluster_names)
    biz_df.to_csv(CLUSTERED_BUSINESSES_CSV, index=False)

    profile_mean['cluster_name'] = [cluster_names[c] for c in profile_mean.index]
    profile_mean['business_count'] = cluster_counts
    profile_mean.to_csv(CLUSTER_PROFILES_CSV)

    print("\nCluster Profiles (Mean Values):")
    print(profile_mean[['cluster_name', 'business_count', 'avg_rating', 'positive_review_pct', 'negative_review_pct']])

    # 1. Cluster size chart
    plt.figure(figsize=(8, 4.5))
    sns.barplot(x=list(cluster_names.values()), y=cluster_counts.values, palette="crest")
    plt.title("Business Count by Segment Cluster", fontsize=13, fontweight='bold')
    plt.xlabel("Segment")
    plt.ylabel("Number of Businesses")
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "cluster_sizes.png"), dpi=300)
    plt.close()

    # 2. Key Feature Comparison Chart across Clusters
    features_to_plot = ['avg_rating', 'positive_review_pct', 'negative_review_pct']
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for i, feat in enumerate(features_to_plot):
        sns.barplot(ax=axes[i], x=profile_mean['cluster_name'], y=profile_mean[feat], palette="viridis")
        axes[i].set_title(f"{feat.replace('_', ' ').title()}", fontweight='bold')
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=25, ha='right', fontsize=9)
        axes[i].set_xlabel("")
    plt.suptitle("Core Feedback Metrics Comparison across Business Clusters", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "feature_comparison.png"), dpi=300)
    plt.close()

    print(f"Cluster profile visualizations saved to {OUTPUT_GRAPHS_DIR}")
    return profile_mean

def run_stability_analysis(X_scaled, optimal_k=4, seeds=[10, 42, 99, 123, 2024]):
    """
    Evaluates clustering stability across diverse random initializations using Adjusted Rand Index.
    """
    print("\n" + "=" * 60)
    print("RUNNING CLUSTER STABILITY ANALYSIS (ADJUSTED RAND INDEX)")
    print("=" * 60)

    # Reference clustering (seed = 42)
    base_kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=N_INIT)
    base_labels = base_kmeans.fit_predict(X_scaled)

    ari_scores = []
    for s in seeds:
        if s == 42:
            continue
        km = KMeans(n_clusters=optimal_k, random_state=s, n_init=N_INIT)
        labels = km.fit_predict(X_scaled)
        score = adjusted_rand_score(base_labels, labels)
        ari_scores.append({'seed_comparison': f"Seed 42 vs {s}", 'ARI': score})
        print(f"ARI between Seed 42 and Seed {s}: {score:.4f}")

    ari_df = pd.DataFrame(ari_scores)
    ari_file = os.path.join(OUTPUT_RESULTS_DIR, "stability_results.csv")
    ari_df.to_csv(ari_file, index=False)
    print(f"Mean Adjusted Rand Index: {ari_df['ARI'].mean():.4f}")
    print(f"Stability results saved to {ari_file}")
    return ari_df

if __name__ == "__main__":
    from feature_engineering import get_clustering_matrix
    biz_df = pd.read_csv(CLUSTERED_BUSINESSES_CSV)
    X_scaled, _, _ = get_clustering_matrix(biz_df)
    analyze_cluster_profiles(biz_df)
    run_stability_analysis(X_scaled, optimal_k=4)
