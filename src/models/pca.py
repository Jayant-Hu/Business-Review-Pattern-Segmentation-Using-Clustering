"""
Principal Component Analysis (PCA) 2D Projection.
Clustering remains strictly on the 10-dimensional space; PCA is used for 2D visual layout.
"""
from typing import Tuple
import joblib
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.utils.paths import settings
from src.utils.logging import logger
from src.data.schema import CLUSTERING_FEATURES

def compute_pca_projection(biz_df: pd.DataFrame) -> Tuple[pd.DataFrame, PCA]:
    """Computes 2D PCA projection for visualization and persists the fitted model."""
    logger.info("Computing 2D Principal Component Analysis (PCA)...")
    
    X = biz_df[CLUSTERING_FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=2, random_state=settings.RANDOM_STATE)
    X_pca = pca.fit_transform(X_scaled)
    
    var_ratio = pca.explained_variance_ratio_
    logger.info(f"PCA Variance Explained: PC1={var_ratio[0]*100:.2f}%, PC2={var_ratio[1]*100:.2f}% (Total={sum(var_ratio)*100:.2f}%)")
    
    # Save PCA model
    settings.PCA_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pca, settings.PCA_MODEL_PATH)
    
    projections = biz_df[['business_id', 'place', 'cluster', 'cluster_name']].copy()
    projections['PCA1'] = X_pca[:, 0]
    projections['PCA2'] = X_pca[:, 1]
    
    settings.PCA_PROJECTIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    projections.to_csv(settings.PCA_PROJECTIONS_CSV, index=False)
    logger.info(f"PCA projections saved to {settings.PCA_PROJECTIONS_CSV}")
    
    biz_df_out = biz_df.copy()
    biz_df_out['PCA1'] = X_pca[:, 0]
    biz_df_out['PCA2'] = X_pca[:, 1]
    
    return biz_df_out, pca
