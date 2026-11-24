"""
Unit tests for Business Search & Lookup Service.
"""
import pytest
import pandas as pd
import numpy as np

from src.services.business_lookup import (
    search_businesses,
    find_similar_businesses,
    calculate_local_percentile,
    generate_business_dossier_pdf
)

@pytest.fixture
def sample_biz_df() -> pd.DataFrame:
    records = []
    cities = ["Dubai", "Abu Dhabi", "Dubai", "Sharjah"]
    categories = ["Restaurant", "Cafe", "Restaurant", "Retail"]
    names = ["Burj Dining", "Corniche Cafe", "Marina Grill", "Al Rolla Mart"]

    for i in range(4):
        rec = {
            "business_id": f"biz_{i}",
            "place": names[i],
            "place type": categories[i],
            "city": cities[i],
            "address": f"Street {i}, {cities[i]}",
            "cluster_name": "High-Satisfaction Top Tier" if i % 2 == 0 else "Moderate Feedback",
            "avg_rating": 4.5 - (i * 0.4),
            "rating_std": 0.5 + (i * 0.1),
            "log_sample_review_count": np.log1p(100 * (i + 1)),
            "positive_review_pct": 85.0 - (i * 10),
            "negative_review_pct": 5.0 + (i * 5),
            "log_avg_review_length": np.log1p(40.0 + (i * 10)),
            "detailed_review_pct": 20.0 + (i * 5),
            "service_feedback_rate": 0.4,
            "food_feedback_rate": 0.5,
            "atmosphere_feedback_rate": 0.3,
            "sample_review_count": 100 * (i + 1),
        }
        records.append(rec)
    return pd.DataFrame(records)

def test_search_businesses(sample_biz_df: pd.DataFrame):
    # Query match
    res = search_businesses(sample_biz_df, query="Grill")
    assert len(res) == 1
    assert res.iloc[0]["place"] == "Marina Grill"

    # City filter
    res_city = search_businesses(sample_biz_df, query="", city_filter="Dubai")
    assert len(res_city) == 2

    # Category filter
    res_cat = search_businesses(sample_biz_df, query="", category_filter="Restaurant")
    assert len(res_cat) == 2

    # Combined query and filter
    res_combo = search_businesses(sample_biz_df, query="Burj", city_filter="Dubai", category_filter="Restaurant")
    assert len(res_combo) == 1
    assert res_combo.iloc[0]["place"] == "Burj Dining"

def test_find_similar_businesses(sample_biz_df: pd.DataFrame):
    target_id = "biz_0"
    peers = find_similar_businesses(sample_biz_df, target_business_id=target_id, top_n=2)
    assert len(peers) == 2
    # Ensure target establishment is excluded
    assert "biz_0" not in peers.index
    assert "similarity_distance" in peers.columns
    # Ensure sorted in ascending distance
    dists = peers["similarity_distance"].tolist()
    assert dists == sorted(dists)

def test_calculate_local_percentile(sample_biz_df: pd.DataFrame):
    target_row = sample_biz_df.iloc[0]  # highest rating: 4.5
    pcts = calculate_local_percentile(sample_biz_df, target_row)
    assert pcts["city_cohort_size"] == 2
    assert pcts["city_rank"] == 1
    assert pcts["city_percentile"] > 0
    assert pcts["category_cohort_size"] == 2
    assert pcts["category_rank"] == 1

def test_generate_business_dossier_pdf(sample_biz_df: pd.DataFrame):
    target_row = sample_biz_df.iloc[0]
    pcts = calculate_local_percentile(sample_biz_df, target_row)
    peers = find_similar_businesses(sample_biz_df, target_business_id=target_row["business_id"], top_n=2)

    pdf_bytes = generate_business_dossier_pdf(target_row, pcts, peers)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
