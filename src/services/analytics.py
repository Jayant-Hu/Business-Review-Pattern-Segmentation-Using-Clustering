"""
Analytical calculations service: Computes real-time summaries, city hotspot rankings,
and comparative segment statistics dynamically from DataFrame records.
"""
from typing import Dict, Any, Tuple
import pandas as pd
from src.utils.paths import settings
from src.utils.logging import logger

def compute_overall_metrics(biz_df: pd.DataFrame, rev_df: pd.DataFrame, eval_df: pd.DataFrame, stab_df: pd.DataFrame) -> Dict[str, Any]:
    """Computes top-level KPI metrics dynamically without hardcoded values."""
    total_businesses = len(biz_df) if biz_df is not None else 0
    total_reviews = len(rev_df) if rev_df is not None else 0
    
    avg_rating = float(biz_df['avg_rating'].mean()) if (biz_df is not None and 'avg_rating' in biz_df.columns) else 0.0
    
    # Selected K metrics
    optimal_k = settings.SELECTED_K
    silhouette = 0.0
    davies_bouldin = 0.0
    if eval_df is not None and 'k' in eval_df.columns:
        row = eval_df[eval_df['k'] == optimal_k]
        if not row.empty:
            silhouette = float(row['Silhouette_Euclidean'].iloc[0])
            davies_bouldin = float(row['Davies_Bouldin'].iloc[0])
            
    mean_ari = float(stab_df['ARI'].mean()) if (stab_df is not None and 'ARI' in stab_df.columns) else 0.0
    
    return {
        'total_businesses': total_businesses,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2),
        'optimal_k': optimal_k,
        'silhouette': round(silhouette, 4),
        'davies_bouldin': round(davies_bouldin, 4),
        'mean_ari_pct': round(mean_ari * 100.0, 2)
    }

def compute_city_hotspots(biz_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes municipal hotspot rankings:
    Identifies cities with the highest count and proportion of At-Risk businesses
    and Top-Tier businesses to direct city-service resources.
    """
    if biz_df is None or 'city' not in biz_df.columns or 'cluster_name' not in biz_df.columns:
        return pd.DataFrame()
        
    df = biz_df[biz_df['city'] != 'Unknown'].copy()
    if df.empty:
        return pd.DataFrame()
        
    grouped = df.groupby('city').agg(
        total_businesses=('business_id', 'count'),
        avg_city_rating=('avg_rating', 'mean'),
        top_tier_count=('cluster_name', lambda x: (x == 'High-Satisfaction Top Tier').sum()),
        at_risk_count=('cluster_name', lambda x: (x == 'Critical Intervention / At-Risk').sum())
    ).reset_index()
    
    grouped['at_risk_rate_pct'] = (grouped['at_risk_count'] / grouped['total_businesses']) * 100.0
    grouped['top_tier_rate_pct'] = (grouped['top_tier_count'] / grouped['total_businesses']) * 100.0
    
    # Sort by total business volume descending
    hotspots = grouped.sort_values(by='total_businesses', ascending=False).round(2)
    
    settings.CITY_HOTSPOTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    hotspots.to_csv(settings.CITY_HOTSPOTS_CSV, index=False)
    return hotspots

def compare_two_segments(biz_df: pd.DataFrame, seg_a: str, seg_b: str) -> pd.DataFrame:
    """Produces comparative side-by-side metric table between two selected segments."""
    features = [
        'avg_rating', 'sample_review_count', 'positive_review_pct',
        'negative_review_pct', 'avg_review_length', 'service_feedback_rate',
        'food_feedback_rate', 'atmosphere_feedback_rate'
    ]
    
    df_a = biz_df[biz_df['cluster_name'] == seg_a][features].mean().round(2)
    df_b = biz_df[biz_df['cluster_name'] == seg_b][features].mean().round(2)
    
    comp = pd.DataFrame({
        f"Segment A: {seg_a}": df_a,
        f"Segment B: {seg_b}": df_b
    })
    comp['Absolute Difference'] = (comp[f"Segment A: {seg_a}"] - comp[f"Segment B: {seg_b}"]).abs().round(2)
    return comp
