"""
Feature Engineering Module
Aggregates review-level records into business-level analytical features,
performs skew transformations, and standard scaling.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from config import PROCESSED_REVIEWS_CSV, BUSINESS_FEATURES_CSV

def engineer_business_features(df=None):
    """
    Transforms review transactions into a business-level feature matrix:
    - avg_rating: Mean customer satisfaction score (1 to 5)
    - rating_std: Consistency of reviews (variance in customer experience)
    - sample_review_count: Frequency of customer mentions in the dataset sample
    - positive_review_pct: Proportion of 4-5 star reviews (%)
    - neutral_review_pct: Proportion of 3 star reviews (%)
    - negative_review_pct: Proportion of 1-2 star reviews (%)
    - avg_review_length: Detail/depth of customer feedback
    - detailed_review_pct: Proportion of reviews with written feedback
    - service_feedback_rate: Proportion of reviews mentioning service quality
    - food_feedback_rate: Proportion of reviews mentioning food quality
    - atmosphere_feedback_rate: Proportion of reviews mentioning atmosphere
    """
    if df is None:
        df = pd.read_csv(PROCESSED_REVIEWS_CSV)

    print("Aggregating review-level records to business-level features...")
    
    # Define sentiment breakdown
    df['is_positive'] = (df['rating'] >= 4.0).astype(int)
    df['is_neutral'] = (df['rating'] == 3.0).astype(int)
    df['is_negative'] = (df['rating'] <= 2.0).astype(int)

    # Group by business identifier
    grouped = df.groupby(['business_id', 'place', 'address', 'place type'])

    biz_df = grouped.agg(
        sample_review_count=('rating', 'count'),
        avg_rating=('rating', 'mean'),
        rating_std=('rating', lambda x: x.std(ddof=0) if len(x) > 1 else 0.0),
        positive_reviews=('is_positive', 'sum'),
        neutral_reviews=('is_neutral', 'sum'),
        negative_reviews=('is_negative', 'sum'),
        avg_review_length=('review_char_len', 'mean'),
        written_reviews=('has_text_review', 'sum'),
        service_mentions=('has_service_feedback', 'sum'),
        food_mentions=('has_food_feedback', 'sum'),
        atmosphere_mentions=('has_atmosphere_feedback', 'sum')
    ).reset_index()

    # Calculate derived percentages
    biz_df['positive_review_pct'] = (biz_df['positive_reviews'] / biz_df['sample_review_count']) * 100.0
    biz_df['neutral_review_pct'] = (biz_df['neutral_reviews'] / biz_df['sample_review_count']) * 100.0
    biz_df['negative_review_pct'] = (biz_df['negative_reviews'] / biz_df['sample_review_count']) * 100.0
    biz_df['detailed_review_pct'] = (biz_df['written_reviews'] / biz_df['sample_review_count']) * 100.0
    biz_df['service_feedback_rate'] = (biz_df['service_mentions'] / biz_df['sample_review_count']) * 100.0
    biz_df['food_feedback_rate'] = (biz_df['food_mentions'] / biz_df['sample_review_count']) * 100.0
    biz_df['atmosphere_feedback_rate'] = (biz_df['atmosphere_mentions'] / biz_df['sample_review_count']) * 100.0

    # Skew transformation: sample_review_count and avg_review_length are heavy right-tailed
    biz_df['log_sample_review_count'] = np.log1p(biz_df['sample_review_count'])
    biz_df['log_avg_review_length'] = np.log1p(biz_df['avg_review_length'])

    # Save business features
    os.makedirs(os.path.dirname(BUSINESS_FEATURES_CSV), exist_ok=True)
    biz_df.to_csv(BUSINESS_FEATURES_CSV, index=False)
    print(f"Aggregated {len(biz_df)} businesses. Feature matrix saved to {BUSINESS_FEATURES_CSV}")

    return biz_df

def get_clustering_matrix(biz_df):
    """
    Selects numerical features for clustering, keeping metadata separate.
    Scales features with StandardScaler.
    """
    clustering_features = [
        'avg_rating',
        'rating_std',
        'log_sample_review_count',
        'positive_review_pct',
        'negative_review_pct',
        'log_avg_review_length',
        'detailed_review_pct',
        'service_feedback_rate',
        'food_feedback_rate',
        'atmosphere_feedback_rate'
    ]

    X = biz_df[clustering_features].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, clustering_features, scaler

if __name__ == "__main__":
    b_df = engineer_business_features()
    X_scaled, features, scaler = get_clustering_matrix(b_df)
    print("Features for Clustering:", features)
    print("Scaled feature matrix shape:", X_scaled.shape)
