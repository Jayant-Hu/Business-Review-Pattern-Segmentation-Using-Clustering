"""
Dynamic, Data-Driven Segment Naming Service.
Derives human-interpretable labels from quantitative cluster profile statistics,
ensuring designations are independent of arbitrary cluster index integers.
"""
from typing import Dict, Any
import pandas as pd
from src.utils.logging import logger

def compute_cluster_profiles(biz_df: pd.DataFrame) -> pd.DataFrame:
    """Computes arithmetic mean and median statistics for each cluster."""
    numeric_cols = [
        'avg_rating', 'rating_std', 'sample_review_count',
        'positive_review_pct', 'negative_review_pct', 'avg_review_length',
        'detailed_review_pct', 'service_feedback_rate', 'food_feedback_rate',
        'atmosphere_feedback_rate'
    ]
    
    profiles = biz_df.groupby('cluster')[numeric_cols].mean().round(2)
    profiles['business_count'] = biz_df['cluster'].value_counts()
    return profiles

def derive_cluster_names(profiles_df: pd.DataFrame) -> Dict[int, str]:
    """
    Dynamically maps cluster indices to descriptive titles based on statistical rules:
    - High-Satisfaction Top Tier: highest avg_rating and lowest negative %
    - Critical Intervention / At-Risk: highest negative_review_pct or lowest avg_rating
    - High-Engagement Detailed Feedback: highest review length / aspect mentions
    - Moderate / Mixed Feedback: balanced/intermediate ratings and neutral sentiment
    """
    logger.info("Deriving data-driven cluster designations from profile statistics...")
    assigned_names: Dict[int, str] = {}
    remaining_clusters = set(profiles_df.index)
    
    # 1. Identify Critical / At-Risk (highest negative % or lowest rating)
    at_risk_cluster = int(profiles_df['negative_review_pct'].idxmax())
    assigned_names[at_risk_cluster] = "Critical Intervention / At-Risk"
    remaining_clusters.remove(at_risk_cluster)
    
    # 2. Identify High-Satisfaction Top Tier (highest avg rating among remaining)
    top_tier_cluster = int(profiles_df.loc[list(remaining_clusters), 'avg_rating'].idxmax())
    assigned_names[top_tier_cluster] = "High-Satisfaction Top Tier"
    remaining_clusters.remove(top_tier_cluster)
    
    # 3. Identify High-Engagement Detailed Feedback (highest aspect feedback / length among remaining)
    if remaining_clusters:
        high_eng_cluster = int(profiles_df.loc[list(remaining_clusters), 'service_feedback_rate'].idxmax())
        assigned_names[high_eng_cluster] = "High-Engagement Detailed Feedback"
        remaining_clusters.remove(high_eng_cluster)
        
    # 4. Remaining cluster(s) -> Moderate / Mixed Feedback
    for c in remaining_clusters:
        assigned_names[c] = "Moderate / Mixed Feedback"
        
    logger.info(f"Dynamic cluster assignments: {assigned_names}")
    return assigned_names

def apply_segment_names(biz_df: pd.DataFrame, profiles_df: pd.DataFrame) -> pd.DataFrame:
    """Applies dynamic cluster naming to businesses and saves updated profiles."""
    cluster_names = derive_cluster_names(profiles_df)
    biz_df['cluster_name'] = biz_df['cluster'].map(cluster_names)
    profiles_df['cluster_name'] = profiles_df.index.map(cluster_names)
    return biz_df, profiles_df
