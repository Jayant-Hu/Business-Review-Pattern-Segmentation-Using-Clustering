"""
Decision Advisor Engine & Profit Potential Index (PPI) Calculation.
Implements Bayesian shrinking of ratings, market demand proxy modeling,
competition saturation scoring, risk penalty calculation, haversine distances,
and automated customer voice keyword/aspect extraction.
"""
import re
import math
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from src.utils.paths import settings
from src.utils.logging import logger

HONESTY_DISCLAIMER = (
    "Disclaimer: Based on review behaviour as a proxy; not a financial forecast. "
    "Validate with local market research before investing."
)

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
    'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll',
    'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
    "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
    'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", 'place', 'good',
    'one', 'also', 'really', 'great', 'nice', 'like', 'get', 'ordered', 'time'
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points on the Earth in kilometers."""
    if any(pd.isna(v) for v in (lat1, lon1, lat2, lon2)):
        return float('nan')
    r = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

def calculate_bayesian_rating(n_reviews: float, mean_rating: float, prior_n: float = 5.0, prior_rating: float = 4.0) -> float:
    """Calculates Bayesian m-estimate shrunk rating towards the global prior mean."""
    return (n_reviews * mean_rating + prior_n * prior_rating) / (n_reviews + prior_n)

def compute_ppi_score(
    biz_count: int,
    total_reviews: int,
    avg_rating: float,
    positive_pct: float,
    negative_pct: float,
    rating_std: float,
    at_risk_share: float,
    w_sat: float = settings.PPI_WEIGHT_SATISFACTION,
    w_dem: float = settings.PPI_WEIGHT_DEMAND,
    w_comp: float = settings.PPI_WEIGHT_COMPETITION,
    w_risk: float = settings.PPI_WEIGHT_RISK
) -> Tuple[float, str, str, List[str], List[str]]:
    """
    Computes the Profit Potential Index (PPI) score (0-100), opportunity classification,
    confidence level, and plain-language 'Why this?' and 'Risks' based on real numbers.
    """
    # 1. Satisfaction sub-score (0-100)
    shrunk_rating = calculate_bayesian_rating(total_reviews, avg_rating)
    sat_score = ((shrunk_rating - 1.0) / 4.0) * 60.0 + (positive_pct / 100.0) * 40.0
    sat_score = max(0.0, min(100.0, sat_score))

    # 2. Demand sub-score (0-100) based on review volume per business proxy
    rev_per_biz = total_reviews / max(1, biz_count)
    demand_score = min(100.0, (math.log1p(rev_per_biz) / math.log1p(25.0)) * 100.0)

    # 3. Competition sub-score (0-100) -> higher when market is not oversaturated
    # 1-3 businesses = high opening (100), 4-10 = moderate (70), >20 = high saturation (40)
    comp_score = max(20.0, 100.0 - (biz_count * 2.5))

    # 4. Risk penalty (0-100) -> inverted, higher score = lower risk
    risk_score = 100.0 - ((negative_pct * 0.6) + (at_risk_share * 0.3) + min(30.0, rating_std * 15.0))
    risk_score = max(0.0, min(100.0, risk_score))

    # Normalize weights if user adjusted them
    total_w = w_sat + w_dem + w_comp + w_risk
    if total_w <= 0:
        total_w = 1.0
    w_sat /= total_w
    w_dem /= total_w
    w_comp /= total_w
    w_risk /= total_w

    ppi = (sat_score * w_sat) + (demand_score * w_dem) + (comp_score * w_comp) + (risk_score * w_risk)
    ppi = round(max(0.0, min(100.0, ppi)), 1)

    # Confidence level
    if total_reviews >= 30:
        confidence = "High (robust review sample)"
    elif total_reviews >= 10:
        confidence = "Medium (moderate review volume)"
    else:
        confidence = "Low (limited sample; interpret with caution)"

    # Opportunity Type Classification
    if ppi >= 75 and biz_count >= 3:
        opp_type = "Proven Market"
    elif ppi >= 68 and biz_count <= 2:
        opp_type = "Underserved Gap"
    elif at_risk_share >= 40.0 or negative_pct >= 25.0:
        opp_type = "Quality Gap"
    elif biz_count >= 15 and ppi < 65:
        opp_type = "Saturated Market"
    else:
        opp_type = "Weak Demand"

    # Automated plain-language "Why this?"
    why_points = []
    if positive_pct >= 80.0:
        why_points.append(f"Strong customer satisfaction signal: {positive_pct:.1f}% positive feedback.")
    if rev_per_biz >= 3.0:
        why_points.append(f"Active customer engagement averaging {rev_per_biz:.1f} reviews per establishment.")
    if biz_count <= 4:
        why_points.append(f"Low market crowding with only {biz_count} existing recorded businesses in this area.")
    if opp_type == "Quality Gap":
        why_points.append(f"High consumer dissatisfaction ({negative_pct:.1f}% negative reviews) creates opportunity for a superior quality entrant.")
    if not why_points:
        why_points.append(f"Moderate baseline metrics with {total_reviews} total community reviews.")

    # Automated plain-language "Risks"
    risk_points = []
    if negative_pct >= 20.0:
        risk_points.append(f"Elevated negative review rate ({negative_pct:.1f}% of reviews express friction or dissatisfaction).")
    if biz_count >= 10:
        risk_points.append(f"Established competition density ({biz_count} existing competitors recorded).")
    if total_reviews < 10:
        risk_points.append("Sparse review volume sample; local consumer footfall may vary.")
    if rating_std >= 1.0:
        risk_points.append(f"High rating volatility (standard deviation: {rating_std:.2f}), signaling inconsistent consumer experiences.")
    if not risk_points:
        risk_points.append("Standard business execution risk; ensure consistent service and quality standards.")

    return ppi, opp_type, confidence, why_points, risk_points

def extract_customer_voice(reviews_df: pd.DataFrame, place_names: List[str]) -> Dict[str, Any]:
    """
    Extracts customer sentiment themes, top keywords, aspect mention averages,
    and sanitized representative short quotes for selected businesses.
    """
    if reviews_df is None or reviews_df.empty:
        return {'positive_keywords': [], 'negative_keywords': [], 'aspects': {}, 'quotes': []}

    subset = reviews_df[reviews_df['place'].isin(place_names)].copy()
    if subset.empty:
        return {'positive_keywords': [], 'negative_keywords': [], 'aspects': {}, 'quotes': []}

    def _get_top_words(text_series, top_n=6):
        words = []
        for text in text_series.dropna():
            cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
            tokens = [w for w in cleaned.split() if len(w) > 3 and w not in STOPWORDS and not w.isdigit()]
            words.extend(tokens)
        counts = pd.Series(words).value_counts()
        return counts.head(top_n).index.tolist() if not counts.empty else []

    pos_reviews = subset[subset['rating'] >= 4.0]['en review']
    neg_reviews = subset[subset['rating'] <= 2.0]['en review']

    pos_words = _get_top_words(pos_reviews)
    neg_words = _get_top_words(neg_reviews)

    # Aspect feedback scores
    aspects = {}
    for aspect in ['food', 'service', 'atmosphere']:
        col = f'{aspect}_numeric'
        if col in subset.columns:
            non_zero = subset[subset[col] > 0][col]
            aspects[aspect.capitalize()] = round(float(non_zero.mean()), 1) if not non_zero.empty else None

    # Sanitized sample quotes (truncated to 110 chars)
    quotes = []
    quote_candidates = subset[subset['en review'].str.len() > 15].drop_duplicates(subset=['en review']).head(4)
    for _, q_row in quote_candidates.iterrows():
        text = str(q_row['en review']).strip()
        if len(text) > 110:
            text = text[:107] + "..."
        quotes.append({
            'rating': q_row['rating'],
            'text': text,
            'aspect': q_row.get('meal_type', 'General')
        })

    return {
        'positive_keywords': pos_words,
        'negative_keywords': neg_words,
        'aspects': aspects,
        'quotes': quotes
    }

def compute_competition_matrix(biz_df: pd.DataFrame, category: str, city: str) -> pd.DataFrame:
    """
    Returns top competitors in the area with Google Maps search link,
    nearest neighbor distances, and cluster segment.
    """
    if biz_df is None or biz_df.empty:
        return pd.DataFrame()

    subset = biz_df[(biz_df['place type'] == category) & (biz_df['city'] == city)].copy()
    if subset.empty:
        # Fallback to category across all cities if none in specific city
        subset = biz_df[biz_df['place type'] == category].head(10).copy()

    # Calculate nearest competitor distance (km) using geocoded coordinates
    if 'latitude' in subset.columns and 'longitude' in subset.columns:
        coords = subset[['latitude', 'longitude']].dropna().values
        distances = []
        for i, row in subset.iterrows():
            lat1, lon1 = row.get('latitude'), row.get('longitude')
            if pd.isna(lat1) or pd.isna(lon1) or len(coords) <= 1:
                distances.append(None)
                continue
            min_dist = float('inf')
            for lat2, lon2 in coords:
                if lat1 == lat2 and lon1 == lon2:
                    continue
                d = haversine_km(lat1, lon1, lat2, lon2)
                if d < min_dist:
                    min_dist = d
            distances.append(round(min_dist, 2) if min_dist != float('inf') else None)
        subset['nearest_competitor_km'] = distances

    # Add Google Maps link
    subset['maps_link'] = subset.apply(
        lambda r: f"https://www.google.com/maps/search/?api=1&query={r['latitude']},{r['longitude']}"
        if pd.notna(r.get('latitude')) and pd.notna(r.get('longitude'))
        else f"https://www.google.com/maps/search/?api=1&query={r['place']}+{r['city']}",
        axis=1
    )

    cols = ['place', 'avg_rating', 'sample_review_count', 'cluster_name', 'address', 'nearest_competitor_km', 'maps_link']
    existing_cols = [c for c in cols if c in subset.columns]
    return subset.sort_values(by='sample_review_count', ascending=False)[existing_cols]

def calculate_breakeven_helper(avg_ticket: float, monthly_fixed_cost: float, margin_pct: float) -> Dict[str, Any]:
    """Calculates break-even monthly customer and revenue targets."""
    if avg_ticket <= 0 or margin_pct <= 0:
        return {'monthly_customers': 0, 'monthly_revenue': 0, 'daily_customers': 0}
    gross_profit_per_customer = avg_ticket * (margin_pct / 100.0)
    required_customers = math.ceil(monthly_fixed_cost / gross_profit_per_customer)
    required_revenue = required_customers * avg_ticket
    return {
        'monthly_customers': required_customers,
        'daily_customers': math.ceil(required_customers / 30),
        'monthly_revenue': round(required_revenue, 2)
    }
