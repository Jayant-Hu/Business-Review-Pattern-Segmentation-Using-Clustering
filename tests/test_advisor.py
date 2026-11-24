"""
Tests for Business Decision Advisor:
- Bayesian shrunk ratings
- PPI score bounds and opportunity classification
- Break-even helper calculations
- Haversine distance computations
- PDF report generator buffer output
"""
import pytest
import pandas as pd
from src.services.decision_advisor import (
    calculate_bayesian_rating,
    compute_ppi_score,
    calculate_breakeven_helper,
    haversine_km,
    extract_customer_voice
)
from src.services.report_generator import generate_advisor_pdf

def test_calculate_bayesian_rating():
    # 0 reviews shrinks directly to prior 4.0
    r0 = calculate_bayesian_rating(0, 5.0, prior_n=5.0, prior_rating=4.0)
    assert r0 == 4.0

    # Large reviews sample maintains true mean
    r100 = calculate_bayesian_rating(100, 5.0, prior_n=5.0, prior_rating=4.0)
    assert round(r100, 2) == 4.95

def test_compute_ppi_score_bounds_and_output():
    ppi, opp_type, conf, why, risks = compute_ppi_score(
        biz_count=3,
        total_reviews=50,
        avg_rating=4.8,
        positive_pct=95.0,
        negative_pct=2.0,
        rating_std=0.3,
        at_risk_share=0.0
    )
    assert 0.0 <= ppi <= 100.0
    assert opp_type in ["Proven Market", "Underserved Gap", "Quality Gap", "Saturated Market", "Weak Demand"]
    assert len(why) > 0
    assert len(risks) > 0
    assert "High" in conf

def test_breakeven_helper():
    res = calculate_breakeven_helper(avg_ticket=20.0, monthly_fixed_cost=4000.0, margin_pct=50.0)
    # Gross profit per customer = $10. Required customers = 400
    assert res['monthly_customers'] == 400
    assert res['monthly_revenue'] == 8000.0
    assert res['daily_customers'] == 14

def test_haversine_km():
    # Distance between Riyadh (24.7136, 46.6753) and Jeddah (21.5433, 39.1728) is ~850 km
    d = haversine_km(24.7136, 46.6753, 21.5433, 39.1728)
    assert 800.0 < d < 900.0

def test_customer_voice_extraction():
    reviews_df = pd.DataFrame([
        {'place': 'Cafe X', 'rating': 5, 'en review': 'Delicious espresso and clean atmosphere', 'food_numeric': 5, 'service_numeric': 5, 'atmosphere_numeric': 5, 'meal_type': 'Coffee'},
        {'place': 'Cafe X', 'rating': 1, 'en review': 'Slow service and cold food', 'food_numeric': 1, 'service_numeric': 1, 'atmosphere_numeric': 1, 'meal_type': 'Coffee'}
    ])
    voice = extract_customer_voice(reviews_df, ['Cafe X'])
    assert 'positive_keywords' in voice
    assert 'negative_keywords' in voice
    assert len(voice['quotes']) > 0

def test_advisor_pdf_generation():
    pdf_bytes = generate_advisor_pdf(
        city="Riyadh",
        category="Coffee shop",
        ppi_score=85.5,
        opp_type="Proven Market",
        confidence="High",
        stats={'biz_count': 5, 'total_reviews': 80, 'avg_rating': 4.7, 'positive_pct': 92.0, 'negative_pct': 3.0},
        why_points=["Strong customer demand."],
        risk_points=["Competition density."],
        competitors_df=pd.DataFrame([{'place': 'Elite Roasters', 'avg_rating': 4.8, 'sample_review_count': 30, 'cluster_name': 'High-Satisfaction Top Tier', 'nearest_competitor_km': 1.2}])
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b'%PDF')
