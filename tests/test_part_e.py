"""
Unit Tests for Part E requirements:
- PPI monotonicity and weight sensitivity re-ranking
- PII sanitization regex masking & length caps
- Multi-segment comparison logic
- Bayesian shrinkage edge cases
- Confidence level classification
"""
import pytest
import pandas as pd
import numpy as np

from src.services.decision_advisor import (
    compute_ppi_score,
    calculate_bayesian_rating,
    calculate_breakeven_helper,
    haversine_km
)
from src.data.cleaning import sanitize_review_text
from src.services.analytics import compare_two_segments

def test_ppi_monotonicity():
    """Higher satisfaction with lower negative reviews must yield a higher or equal PPI."""
    score_low, _, _, _, _ = compute_ppi_score(
        biz_count=5, total_reviews=100, avg_rating=3.2,
        positive_pct=50.0, negative_pct=30.0, rating_std=1.2, at_risk_share=40.0
    )
    score_high, _, _, _, _ = compute_ppi_score(
        biz_count=5, total_reviews=100, avg_rating=4.7,
        positive_pct=95.0, negative_pct=2.0, rating_std=0.3, at_risk_share=0.0
    )
    assert score_high > score_low

def test_ppi_weights_reranking():
    """Modifying weight parameters changes the relative contribution."""
    ppi_sat_heavy, _, _, _, _ = compute_ppi_score(
        biz_count=2, total_reviews=15, avg_rating=4.9, positive_pct=98.0,
        negative_pct=0.0, rating_std=0.2, at_risk_share=0.0,
        w_sat=0.8, w_dem=0.1, w_comp=0.05, w_risk=0.05
    )
    ppi_dem_heavy, _, _, _, _ = compute_ppi_score(
        biz_count=2, total_reviews=15, avg_rating=4.9, positive_pct=98.0,
        negative_pct=0.0, rating_std=0.2, at_risk_share=0.0,
        w_sat=0.1, w_dem=0.8, w_comp=0.05, w_risk=0.05
    )
    assert ppi_sat_heavy > ppi_dem_heavy

def test_pii_sanitization():
    raw_text = "Contact support at test.user@example.com or call +1 555-123-4567. Follow @chef_john at https://mywebsite.com for details!"
    cleaned = sanitize_review_text(raw_text, max_len=180)
    assert "[email]" in cleaned
    assert "test.user@example.com" not in cleaned
    assert "[phone]" in cleaned
    assert "555-123-4567" not in cleaned
    assert "[link]" in cleaned
    assert "https://" not in cleaned
    assert "[user]" in cleaned
    assert "@chef_john" not in cleaned

def test_pii_truncation():
    long_text = "A " * 200
    cleaned = sanitize_review_text(long_text, max_len=50)
    assert len(cleaned) <= 55
    assert cleaned.endswith("...")

def test_compare_two_segments_logic():
    biz_df = pd.DataFrame([
        {'place': 'A1', 'place type': 'Cafe', 'cluster_name': 'SegA', 'avg_rating': 4.8, 'sample_review_count': 100, 'positive_review_pct': 90.0, 'negative_review_pct': 2.0},
        {'place': 'B1', 'place type': 'Cafe', 'cluster_name': 'SegB', 'avg_rating': 3.2, 'sample_review_count': 40, 'positive_review_pct': 40.0, 'negative_review_pct': 25.0}
    ])
    cmp_df = compare_two_segments(biz_df, 'SegA', 'SegB')
    assert not cmp_df.empty
    assert 'Metric' in cmp_df.columns
    assert 'SegA' in cmp_df.columns
    assert 'SegB' in cmp_df.columns
    assert 'Difference' in cmp_df.columns

def test_bayesian_rating_shrinkage_bounds():
    # Never exceed 5.0 and never below 1.0
    r_high = calculate_bayesian_rating(100, 5.0, prior_n=5.0, prior_rating=4.0)
    r_low = calculate_bayesian_rating(100, 1.0, prior_n=5.0, prior_rating=4.0)
    assert r_high <= 5.0
    assert r_low >= 1.0
