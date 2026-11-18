"""
Reproducible K-Means Clustering Pipeline with Scikit-learn Pipelines,
Inertia (WCSS), Euclidean & Manhattan Silhouette, and Davies-Bouldin metrics.
"""
from typing import Tuple, Dict, Any
import joblib
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

from src.utils.paths import settings
from src.utils.logging import logger
from src.data.schema import CLUSTERING_FEATURES

def build_kmeans_pipeline(k: int = settings.SELECTED_K, random_state: int = settings.RANDOM_STATE) -> Pipeline:
    """Creates a production sklearn pipeline with StandardScaler and KMeans."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=k, random_state=random_state, n_init=settings.N_INIT))
    ])
    return pipeline

def train_kmeans_experiments(biz_df: pd.DataFrame) -> Tuple[pd.DataFrame, Pipeline, pd.DataFrame]:
    """
    Evaluates multiple K values (2 to 7).
    Calculates WCSS, Euclidean Silhouette, Manhattan Silhouette, and Davies-Bouldin.
    Fits and persists the optimal Pipeline model.
    """
    logger.info(f"Running K-Means experiments across K={settings.K_RANGE}...")
    
    X = biz_df[CLUSTERING_FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    eval_results = []
    models = {}
    
    for k in settings.K_RANGE:
        km = KMeans(n_clusters=k, random_state=settings.RANDOM_STATE, n_init=settings.N_INIT)
        labels = km.fit_predict(X_scaled)
        models[k] = km
        
        wcss = km.inertia_
        # Sample silhouette if large to optimize performance
        sample_size = min(len(X_scaled), 2000)
        sil_euclid = float(silhouette_score(X_scaled, labels, metric='euclidean', sample_size=sample_size, random_state=settings.RANDOM_STATE))
        sil_manhattan = float(silhouette_score(X_scaled, labels, metric='manhattan', sample_size=sample_size, random_state=settings.RANDOM_STATE))
        db_index = float(davies_bouldin_score(X_scaled, labels))
        
        eval_results.append({
            'k': k,
            'WCSS': float(wcss),
            'Silhouette_Euclidean': sil_euclid,
            'Silhouette_Manhattan': sil_manhattan,
            'Davies_Bouldin': db_index
        })
        logger.info(f"K={k} -> WCSS={wcss:.2f}, Sil(Euclid)={sil_euclid:.4f}, Sil(Manhattan)={sil_manhattan:.4f}, DB={db_index:.4f}")
        
    eval_df = pd.DataFrame(eval_results)
    settings.EVALUATION_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    eval_df.to_csv(settings.EVALUATION_RESULTS_CSV, index=False)
    
    # Fit and persist selected optimal pipeline
    optimal_k = settings.SELECTED_K
    optimal_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=optimal_k, random_state=settings.RANDOM_STATE, n_init=settings.N_INIT))
    ])
    optimal_pipeline.fit(X)
    
    settings.KMEANS_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(optimal_pipeline, settings.KMEANS_MODEL_PATH)
    logger.info(f"Optimal K-Means pipeline persisted to {settings.KMEANS_MODEL_PATH}")
    
    biz_df_clustered = biz_df.copy()
    biz_df_clustered['cluster'] = optimal_pipeline.named_steps['kmeans'].labels_
    
    return eval_df, optimal_pipeline, biz_df_clustered
