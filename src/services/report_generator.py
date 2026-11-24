"""
PDF Report Generator for Business Decision Advisor.
Generates a downloadable branded PDF summary covering market snapshot,
opportunity scores, competitor tables, customer voice, and financial disclaimers.
"""
import io
from typing import Dict, Any, List
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.services.decision_advisor import HONESTY_DISCLAIMER

def generate_advisor_pdf(
    city: str,
    category: str,
    ppi_score: float,
    opp_type: str,
    confidence: str,
    stats: Dict[str, Any],
    why_points: List[str],
    risk_points: List[str],
    competitors_df: pd.DataFrame
) -> bytes:
    """Compiles a polished corporate PDF report buffer for a chosen area + category."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#DC2626')
    )

    story = []

    # Title & Header
    story.append(Paragraph("UrbanPulse AI | Business Decision Advisory Report", header_style))
    story.append(Paragraph(f"Location: <b>{city}</b> | Commercial Category: <b>{category}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=14))

    # Executive Summary Table
    summary_data = [
        ["Metric", "Value", "Benchmark / Status"],
        ["Profit Potential Index (PPI)", f"{ppi_score} / 100", f"Classification: {opp_type}"],
        ["Confidence Level", confidence, "Review Volume Statistical Reliability"],
        ["Business Count", str(stats.get('biz_count', 'N/A')), "Recorded establishments in area"],
        ["Total Reviews", str(stats.get('total_reviews', 'N/A')), "Sample customer feedback records"],
        ["Average Rating", f"{stats.get('avg_rating', 0.0):.2f} ⭐", f"Positive Share: {stats.get('positive_pct', 0.0):.1f}%"],
        ["Negative Share", f"{stats.get('negative_pct', 0.0):.1f}%", f"Dissatisfaction / Quality Gap Proxy"]
    ]

    t_summary = Table(summary_data, colWidths=[2.2*inch, 2.0*inch, 2.8*inch])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 14))

    # Why This? & Strategic Rationales
    story.append(Paragraph("Strategic Opportunities & Demand Signals", section_title))
    for p in why_points:
        story.append(Paragraph(f"• {p}", body_style))
    story.append(Spacer(1, 10))

    # Key Operational Risks
    story.append(Paragraph("Market Risks & Operational Friction Factors", section_title))
    for r in risk_points:
        story.append(Paragraph(f"• {r}", body_style))
    story.append(Spacer(1, 12))

    # Competitor Snapshot
    if competitors_df is not None and not competitors_df.empty:
        story.append(Paragraph("Area Competitor Intelligence (Top Records)", section_title))
        top_comp = competitors_df.head(5)
        comp_rows = [["Business Name", "Rating", "Reviews", "Segment", "Distance (km)"]]
        for _, row in top_comp.iterrows():
            dist_str = f"{row['nearest_competitor_km']} km" if pd.notna(row.get('nearest_competitor_km')) else "N/A"
            comp_rows.append([
                str(row['place'])[:24],
                f"{row['avg_rating']} ⭐",
                str(row['sample_review_count']),
                str(row['cluster_name'])[:20],
                dist_str
            ])
        t_comp = Table(comp_rows, colWidths=[2.5*inch, 0.9*inch, 0.9*inch, 1.8*inch, 0.9*inch])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_comp)
        story.append(Spacer(1, 16))

    # Mandatory Honesty Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#EF4444'), spaceAfter=8))
    story.append(Paragraph(f"<b>Notice:</b> {HONESTY_DISCLAIMER}", disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
