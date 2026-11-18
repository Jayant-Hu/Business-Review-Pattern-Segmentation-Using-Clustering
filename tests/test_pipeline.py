"""
Unit and integration tests for data loading, cleaning, schema validation,
feature engineering, modeling determinism, segment naming, and geocoding.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.paths import settings
from src.data.schema import validate_raw_dataframe, validate_business_features, CLUSTERING_FEATURES
from src.data.cleaning import clean_reviews
from src.features.business_features import aggregate_business_features
from src.models.kmeans import build_kmeans_pipeline
from src.services.segment_naming import compute_cluster_profiles, derive_cluster_names
from src.geo.city_parser import parse_address_components
from src.geo.cache import GeocodeCache
from src.geo.geocoder import GeocoderService

@pytest.fixture
def sample_raw_df():
    """Provides a synthetic raw reviews dataframe for unit testing."""
    return pd.DataFrame([
        {
            'User_name': 'Reviewer 1',
            'points': 20,
            'level': 1,
            'number of reviews': 5,
            'number of photos': 0,
            'number of videos': 0,
            'number of ratings': 2,
            'Id': 'user_1001',
            'place': 'Bakery Alpha',
            'address': 'Olaya St, Riyadh 12211, Saudi Arabia',
            'place type': 'Bakery',
            'original review': 'Great bakery',
            'en review': 'Great bakery',
            'rating': 5,
            'food': 5,
            'service': 5,
            'atmosphere': 4,
            'meal_type': 'Breakfast'
        },
        {
            'User_name': 'Reviewer 2',
            'points': 10,
            'level': 0,
            'number of reviews': 1,
            'number of photos': 0,
            'number of videos': 0,
            'number of ratings': 1,
            'Id': 'user_1002',
            'place': 'Bakery Alpha',
            'address': 'Olaya St, Riyadh 12211, Saudi Arabia',
            'place type': 'Bakery',
            'original review': 'Average food',
            'en review': 'Average food',
            'rating': 4,
            'food': 4,
            'service': 3,
            'atmosphere': 0,
            'meal_type': '0'
        },
        {
            'User_name': 'Reviewer 3',
            'points': 5,
            'level': 0,
            'number of reviews': 1,
            'number of photos': 0,
            'number of videos': 0,
            'number of ratings': 1,
            'Id': 'user_1003',
            'place': 'Diner Beta',
            'address': 'Corniche Rd, Jeddah 21411, Saudi Arabia',
            'place type': 'Restaurant',
            'original review': 'Terrible experience',
            'en review': 'Terrible experience',
            'rating': 1,
            'food': 1,
            'service': 1,
            'atmosphere': 1,
            'meal_type': 'Dinner'
        }
    ])

def test_schema_validation_success(sample_raw_df):
    """Test raw dataframe validation passes on valid schema."""
    assert validate_raw_dataframe(sample_raw_df) is True

def test_clean_reviews_composite_key(sample_raw_df):
    """Test cleaning generates composite business key and removes PII."""
    cleaned = clean_reviews(sample_raw_df)
    assert 'business_id' in cleaned.columns
    assert 'User_name' not in cleaned.columns
    assert 'Id' not in cleaned.columns
    assert len(cleaned) == 3

def test_aggregate_business_features(sample_raw_df):
    """Test feature engineering correctly aggregates review transactions to businesses."""
    cleaned = clean_reviews(sample_raw_df)
    biz_df = aggregate_business_features(cleaned)
    assert len(biz_df) == 2  # 2 distinct businesses
    assert validate_business_features(biz_df) is True
    
    alpha = biz_df[biz_df['place'] == 'Bakery Alpha'].iloc[0]
    assert alpha['sample_review_count'] == 2
    assert alpha['avg_rating'] == 4.5
    assert alpha['positive_review_pct'] == 100.0

def test_model_determinism(sample_raw_df):
    """Test that fixed random seed produces identical cluster labels."""
    cleaned = clean_reviews(sample_raw_df)
    biz_df = aggregate_business_features(cleaned)
    # duplicate rows to allow K=2 clustering
    biz_expanded = pd.concat([biz_df] * 10, ignore_index=True)
    X = biz_expanded[CLUSTERING_FEATURES]
    
    pipe1 = build_kmeans_pipeline(k=2, random_state=42)
    labels1 = pipe1.fit_predict(X)
    
    pipe2 = build_kmeans_pipeline(k=2, random_state=42)
    labels2 = pipe2.fit_predict(X)
    
    np.testing.assert_array_equal(labels1, labels2)

def test_city_parser_gcc():
    """Test address parsing accurately extracts city and postal code."""
    res = parse_address_components("King Fahd Rd, Al Olaya, Riyadh 12214, Saudi Arabia")
    assert res['city'] == 'Riyadh'
    assert res['country'] == 'Saudi Arabia'
    assert res['postal_code'] == '12214'

def test_city_parser_arabic():
    """Test parsing Arabic text for city names."""
    res = parse_address_components("شارع التخصصي، الرياض، المملكة العربية السعودية")
    assert res['city'] == 'Riyadh'

def test_geocode_cache_hit_miss(tmp_path):
    """Test SQLite geocode cache insert and lookup."""
    db_file = tmp_path / "test_cache.db"
    cache = GeocodeCache(db_path=db_file)
    
    key = "Test Cafe || Riyadh 12345"
    assert cache.get(key) is None
    
    data = {'latitude': 24.71, 'longitude': 46.67, 'city': 'Riyadh', 'geocode_status': 'OK'}
    cache.set(key, data)
    
    retrieved = cache.get(key)
    assert retrieved is not None
    assert retrieved['latitude'] == 24.71
    assert retrieved['city'] == 'Riyadh'

def test_geocoder_fallback(tmp_path):
    """Test geocoder service falls back cleanly without crashing when network is off."""
    db_file = tmp_path / "test_geo.db"
    cache = GeocodeCache(db_path=db_file)
    service = GeocoderService(cache=cache)
    
    res = service.geocode_address("Sample Coffee", "Al Malqa, Riyadh, Saudi Arabia", use_network_fallback=False)
    assert res['latitude'] is not None
    assert res['longitude'] is not None
    assert res['city'] == 'Riyadh'
