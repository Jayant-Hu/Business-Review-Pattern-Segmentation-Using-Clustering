"""
Feature Engineering: Aggregating Review-Level Records into Business Feature Matrix.
"""
import pandas as pd
import numpy as np
from src.utils.paths import settings
from src.utils.logging import logger
from src.data.schema import validate_business_features, CLUSTERING_FEATURES

def aggregate_business_features(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms transaction-level reviews into unique commercial business profiles:
    - Customer rating mean and standard deviation
    - Sentiment breakdowns (positive %, neutral %, negative %)
    - Engagement metrics (review length, detailed feedback rate)
    - Quality aspect mention rates (service, food, atmosphere)
    """
    logger.info(f"Aggregating {len(clean_df)} reviews to business-level feature matrix...")
    
    df = clean_df.copy()
    df['is_positive'] = (df['rating'] >= 4.0).astype(int)
    df['is_neutral'] = (df['rating'] == 3.0).astype(int)
    df['is_negative'] = (df['rating'] <= 2.0).astype(int)
    
    grouped = df.groupby(['business_id', 'place', 'address', 'place type'])
    
    biz_df = grouped.agg(
        sample_review_count=('rating', 'count'),
        avg_rating=('rating', 'mean'),
        rating_std=('rating', lambda x: float(x.std(ddof=0)) if len(x) > 1 else 0.0),
        positive_reviews=('is_positive', 'sum'),
        neutral_reviews=('is_neutral', 'sum'),
        negative_reviews=('is_negative', 'sum'),
        avg_review_length=('review_char_len', 'mean'),
        written_reviews=('has_text_review', 'sum'),
        service_mentions=('has_service_feedback', 'sum'),
        food_mentions=('has_food_feedback', 'sum'),
        atmosphere_mentions=('has_atmosphere_feedback', 'sum')
    ).reset_index()
    
    # Calculate rates & percentages
    count = biz_df['sample_review_count']
    biz_df['positive_review_pct'] = (biz_df['positive_reviews'] / count) * 100.0
    biz_df['neutral_review_pct'] = (biz_df['neutral_reviews'] / count) * 100.0
    biz_df['negative_review_pct'] = (biz_df['negative_reviews'] / count) * 100.0
    biz_df['detailed_review_pct'] = (biz_df['written_reviews'] / count) * 100.0
    biz_df['service_feedback_rate'] = (biz_df['service_mentions'] / count) * 100.0
    biz_df['food_feedback_rate'] = (biz_df['food_mentions'] / count) * 100.0
    biz_df['atmosphere_feedback_rate'] = (biz_df['atmosphere_mentions'] / count) * 100.0
    
    # Skew mitigation transforms
    biz_df['log_sample_review_count'] = np.log1p(biz_df['sample_review_count'])
    biz_df['log_avg_review_length'] = np.log1p(biz_df['avg_review_length'])
    
    validate_business_features(biz_df)
    
    settings.BUSINESS_FEATURES_CSV.parent.mkdir(parents=True, exist_ok=True)
    biz_df.to_csv(settings.BUSINESS_FEATURES_CSV, index=False)
    logger.info(f"Engineered features for {len(biz_df)} businesses -> {settings.BUSINESS_FEATURES_CSV}")
    
    return biz_df
