"""
Clustering Stability Analysis using Adjusted Rand Index across multiple seeds.
"""
from typing import List
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score

from src.utils.paths import settings
from src.utils.logging import logger
from src.data.schema import CLUSTERING_FEATURES

def evaluate_cluster_stability(biz_df: pd.DataFrame, seeds: List[int] = None) -> pd.DataFrame:
    """Evaluates reproducibility and cluster stability across multiple random seeds."""
    if seeds is None:
        seeds = [10, 42, 99, 123, 2024]
        
    logger.info(f"Running clustering stability assessment across seeds: {seeds}...")
    X = biz_df[CLUSTERING_FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Reference model at seed 42
    ref_km = KMeans(n_clusters=settings.SELECTED_K, random_state=42, n_init=settings.N_INIT)
    ref_labels = ref_km.fit_predict(X_scaled)
    
    ari_records = []
    for s in seeds:
        if s == 42:
            continue
        km = KMeans(n_clusters=settings.SELECTED_K, random_state=s, n_init=settings.N_INIT)
        labels = km.fit_predict(X_scaled)
        ari = float(adjusted_rand_score(ref_labels, labels))
        ari_records.append({
            'seed_comparison': f"Seed 42 vs {s}",
            'ARI': ari
        })
        logger.info(f"ARI Seed 42 vs {s}: {ari:.4f}")
        
    stab_df = pd.DataFrame(ari_records)
    settings.STABILITY_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    stab_df.to_csv(settings.STABILITY_RESULTS_CSV, index=False)
    logger.info(f"Stability results saved -> {settings.STABILITY_RESULTS_CSV} (Mean ARI={stab_df['ARI'].mean():.4f})")
    
    return stab_df
