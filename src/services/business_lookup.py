"""
Business Search & Peer Comparison Service.
Provides:
- Multi-field text filtering across business name, category, and city
- Peer neighborhood discovery (Euclidean nearest neighbors in scaled feature space)
- Category & city rank percentiles
- PDF profile generator for an individual business
"""
import io
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.data.schema import CLUSTERING_FEATURES
from src.services.decision_advisor import HONESTY_DISCLAIMER

def search_businesses(
    biz_df: pd.DataFrame,
    query: str,
    city_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    limit: int = 25
) -> pd.DataFrame:
    """Filters businesses by text query (name/address), city, and category."""
    if biz_df is None or biz_df.empty:
        return pd.DataFrame()

    filtered = biz_df.copy()

    if city_filter and city_filter != "All Cities":
        filtered = filtered[filtered['city'] == city_filter]

    if category_filter and category_filter != "All Categories":
        filtered = filtered[filtered['place type'] == category_filter]

    if query and query.strip():
        q = query.strip().lower()
        name_match = filtered['place'].astype(str).str.lower().str.contains(q, na=False)
        addr_match = filtered['address'].astype(str).str.lower().str.contains(q, na=False)
        cat_match = filtered['place type'].astype(str).str.lower().str.contains(q, na=False)
        filtered = filtered[name_match | addr_match | cat_match]

    return filtered.head(limit)

def find_similar_businesses(
    biz_df: pd.DataFrame,
    target_business_id: str,
    top_n: int = 5
) -> pd.DataFrame:
    """Finds nearest peer establishments in the scaled feature space."""
    if biz_df is None or biz_df.empty or target_business_id not in biz_df['business_id'].values:
        return pd.DataFrame()

    # Identify existing feature columns
    feat_cols = [c for c in CLUSTERING_FEATURES if c in biz_df.columns]
    if not feat_cols:
        # Fallback to standard numeric columns
        feat_cols = [c for c in ['avg_rating', 'sample_review_count', 'rating_std', 'positive_review_pct', 'negative_review_pct'] if c in biz_df.columns]

    if not feat_cols:
        return pd.DataFrame()

    # Extract feature matrix
    X = biz_df[feat_cols].copy().fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    target_idx = biz_df.index[biz_df['business_id'] == target_business_id].tolist()[0]
    target_vec = X_scaled[target_idx].reshape(1, -1)

    # Compute Euclidean distances in feature space
    dists = euclidean_distances(target_vec, X_scaled)[0]

    peers_df = biz_df.copy()
    peers_df['similarity_distance'] = dists
    # Exclude self and sort by distance
    peers_df = peers_df[peers_df['business_id'] != target_business_id].sort_values(by='similarity_distance')

    cols = ['place', 'place type', 'city', 'cluster_name', 'avg_rating', 'sample_review_count', 'positive_review_pct', 'similarity_distance']
    existing_cols = [c for c in cols if c in peers_df.columns]
    return peers_df.head(top_n)[existing_cols]

def calculate_local_percentile(biz_df: pd.DataFrame, business_row: pd.Series) -> Dict[str, Any]:
    """Computes ranking and percentile of a business within its city and category."""
    city = business_row.get('city')
    category = business_row.get('place type')
    rating = business_row.get('avg_rating', 0.0)

    # 1. City percentile
    city_cohort = biz_df[biz_df['city'] == city] if city and city != 'Unknown' else biz_df
    city_pct = (city_cohort['avg_rating'] < rating).mean() * 100.0 if not city_cohort.empty else 50.0
    city_rank = int((city_cohort['avg_rating'] > rating).sum() + 1)

    # 2. Category percentile
    cat_cohort = biz_df[biz_df['place type'] == category] if category else biz_df
    cat_pct = (cat_cohort['avg_rating'] < rating).mean() * 100.0 if not cat_cohort.empty else 50.0
    cat_rank = int((cat_cohort['avg_rating'] > rating).sum() + 1)

    return {
        'city_cohort_size': len(city_cohort),
        'city_rank': city_rank,
        'city_percentile': round(city_pct, 1),
        'category_cohort_size': len(cat_cohort),
        'category_rank': cat_rank,
        'category_percentile': round(cat_pct, 1)
    }

def generate_business_dossier_pdf(
    biz_row: pd.Series,
    percentiles: Dict[str, Any],
    peers_df: pd.DataFrame
) -> bytes:
    """Generates an executive PDF dossier for an individual commercial establishment."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'BizTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'BizSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    section_style = ParagraphStyle(
        'SectionH',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle('BText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
    disclaimer_style = ParagraphStyle('Disc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor('#DC2626'))

    story = []
    name = str(biz_row.get('place', 'Business Profile'))
    cat = str(biz_row.get('place type', 'General'))
    city = str(biz_row.get('city', 'Unknown City'))
    segment = str(biz_row.get('cluster_name', 'Unassigned'))

    story.append(Paragraph(f"Establishment Profile: {name}", header_style))
    story.append(Paragraph(f"Category: <b>{cat}</b> | Location: <b>{city}</b> | Assigned Segment: <b>{segment}</b>", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=10))

    # Core Performance Table
    metrics_data = [
        ["Performance Metric", "Observed Value", "Local Peer Standing"],
        ["Customer Rating", f"{biz_row.get('avg_rating', 0.0):.2f} ⭐", f"Top {100 - percentiles['category_percentile']:.1f}% in Category"],
        ["Sample Review Volume", f"{biz_row.get('sample_review_count', 0)} reviews", f"Rank #{percentiles['city_rank']} in {city}"],
        ["Positive Sentiment", f"{biz_row.get('positive_review_pct', 0.0):.1f}%", "4★ & 5★ Ratings Share"],
        ["Negative Sentiment", f"{biz_row.get('negative_review_pct', 0.0):.1f}%", "1★ & 2★ Dissatisfaction Share"],
        ["Rating Consistency", f"±{biz_row.get('rating_std', 0.0):.2f}", "Experience Standard Deviation"],
        ["Address", str(biz_row.get('address', 'N/A'))[:55], "Verified Location"]
    ]
    t_metrics = Table(metrics_data, colWidths=[2.2*inch, 2.0*inch, 2.8*inch])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    # Similar Businesses Table
    if peers_df is not None and not peers_df.empty:
        story.append(Paragraph("Nearest Behavioral Peers (Feature Space Neighbors)", section_style))
        peer_rows = [["Peer Establishment", "Category", "City", "Rating", "Reviews", "Segment"]]
        for _, pr in peers_df.head(5).iterrows():
            peer_rows.append([
                str(pr['place'])[:24],
                str(pr['place type'])[:16],
                str(pr['city'])[:14],
                f"{pr['avg_rating']} ⭐",
                str(pr['sample_review_count']),
                str(pr['cluster_name'])[:20]
            ])
        t_peers = Table(peer_rows, colWidths=[2.2*inch, 1.4*inch, 1.1*inch, 0.8*inch, 0.7*inch, 1.4*inch])
        t_peers.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_peers)
        story.append(Spacer(1, 14))

    # Mandatory Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#EF4444'), spaceAfter=6))
    story.append(Paragraph(f"<b>Notice:</b> {HONESTY_DISCLAIMER}", disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
