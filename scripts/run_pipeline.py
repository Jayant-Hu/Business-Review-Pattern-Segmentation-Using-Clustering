"""
End-to-end Pipeline Execution CLI.
Executes data sampling -> cleaning -> feature engineering -> clustering -> hierarchical -> PCA -> evaluation -> geocoding.
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.paths import settings
from src.utils.logging import logger
from src.data.loader import load_or_create_sample
from src.data.cleaning import clean_reviews
from src.features.business_features import aggregate_business_features
from src.models.kmeans import train_kmeans_experiments
from src.models.hierarchical import run_hierarchical_benchmark
from src.models.pca import compute_pca_projection
from src.models.stability import evaluate_cluster_stability
from src.services.segment_naming import compute_cluster_profiles, apply_segment_names
from src.geo.geocoder import GeocoderService
from src.services.analytics import compute_city_hotspots

def run_pipeline(step: str = "all", force_recompute: bool = False, geocode_limit: int = None):
    """Executes designated pipeline stages."""
    logger.info(f"Starting UrbanPulse Pipeline (step={step})...")
    
    # 1. Data Sampling & Cleaning
    if step in ["all", "data", "clean"]:
        raw_sample = load_or_create_sample(force_recompute=force_recompute)
        clean_df = clean_reviews(raw_sample)
    else:
        import pandas as pd
        clean_df = pd.read_csv(settings.DATA_PROCESSED_CSV)
        
    # 2. Feature Engineering
    if step in ["all", "features"]:
        biz_df = aggregate_business_features(clean_df)
    else:
        import pandas as pd
        biz_df = pd.read_csv(settings.BUSINESS_FEATURES_CSV)
        
    # 3. K-Means Modeling & Dynamic Segment Naming
    if step in ["all", "model", "cluster"]:
        eval_df, pipeline, biz_clustered = train_kmeans_experiments(biz_df)
        profiles = compute_cluster_profiles(biz_clustered)
        biz_named, profiles_named = apply_segment_names(biz_clustered, profiles)
        
        # Save profiles
        profiles_named.to_csv(settings.CLUSTER_PROFILES_CSV)
        biz_named.to_csv(settings.CLUSTERED_BUSINESSES_CSV, index=False)
        biz_df = biz_named
    else:
        import pandas as pd
        biz_df = pd.read_csv(settings.CLUSTERED_BUSINESSES_CSV)
        
    # 4. Hierarchical Clustering
    if step in ["all", "hierarchical"]:
        comp_df, _ = run_hierarchical_benchmark(biz_df)
        
    # 5. PCA Projection
    if step in ["all", "pca"]:
        biz_pca, _ = compute_pca_projection(biz_df)
        biz_df = biz_pca
        
    # 6. Stability Assessment
    if step in ["all", "evaluate", "stability"]:
        stab_df = evaluate_cluster_stability(biz_df)
        
    # 7. Geocoding Layer
    if step in ["all", "geocode"]:
        geocoder = GeocoderService()
        biz_geocoded = geocoder.geocode_businesses_dataframe(biz_df, max_records=geocode_limit)
        biz_geocoded.to_csv(settings.CLUSTERED_BUSINESSES_CSV, index=False)
        compute_city_hotspots(biz_geocoded)
        logger.info(f"Pipeline complete with geocoding saved to {settings.CLUSTERED_BUSINESSES_CSV}")
        
    logger.info("UrbanPulse Pipeline execution finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UrbanPulse ML & Analytics Pipeline Runner")
    parser.add_argument(
        "--step",
        type=str,
        default="all",
        choices=["all", "data", "clean", "features", "cluster", "hierarchical", "pca", "stability", "geocode"],
        help="Pipeline stage to execute"
    )
    parser.add_argument("--force", action="store_true", help="Force recomputation of samples and models")
    parser.add_argument("--geocode-limit", type=int, default=None, help="Limit number of businesses to geocode (useful for quick tests)")
    args = parser.parse_args()
    
    run_pipeline(step=args.step, force_recompute=args.force, geocode_limit=args.geocode_limit)
