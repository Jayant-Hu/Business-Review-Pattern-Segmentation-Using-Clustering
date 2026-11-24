"""
Schema definitions and validation utilities for raw and processed datasets.
"""
from typing import List, Dict, Any
import pandas as pd
from src.utils.exceptions import DataValidationError

# Expected raw columns
RAW_COLUMNS = [
    'User_name', 'points', 'level', 'number of reviews', 'number of photos',
    'number of videos', 'number of ratings', 'Id', 'place', 'address',
    'place type', 'original review', 'en review', 'rating', 'food',
    'service', 'atmosphere', 'meal_type'
]

# Business clustering features
CLUSTERING_FEATURES = [
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

def validate_raw_dataframe(df: pd.DataFrame) -> bool:
    """Validates that incoming raw reviews dataframe contains required minimal columns."""
    required = {'place', 'rating', 'Id'}
    missing = required - set(df.columns)
    if missing:
        raise DataValidationError(f"Raw dataframe missing essential columns: {missing}")
    return True

def validate_business_features(df: pd.DataFrame) -> bool:
    """Validates that engineered business dataframe contains all clustering features."""
    missing = set(CLUSTERING_FEATURES) - set(df.columns)
    if missing:
        raise DataValidationError(f"Business dataframe missing clustering features: {missing}")
    return True
