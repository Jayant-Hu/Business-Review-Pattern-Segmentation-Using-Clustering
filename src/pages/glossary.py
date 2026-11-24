"""
Glossary & Analytical Terminology Page.
Defines ML metrics, clustering concepts, Bayesian shrinkage, and decision science terms in plain language.
"""
from typing import Dict, Any, List
import streamlit as st
from src.ui.components import render_header, render_footer, render_badge

GLOSSARY_ITEMS: List[Dict[str, Any]] = [
    {
        "term": "Silhouette Score",
        "category": "ML Validation",
        "badge": "blue",
        "short_def": "Measures how similar an establishment is to its own cluster compared to neighboring clusters.",
        "detailed_def": "Values range from -1 to +1. A score near +1 indicates tight, distinct cluster boundaries; 0 indicates overlapping decision boundaries; negative values suggest points are assigned to the wrong cluster. In this platform, Euclidean and Manhattan distance variants are compared to identify stable clusters."
    },
    {
        "term": "Davies-Bouldin Index",
        "category": "ML Validation",
        "badge": "blue",
        "short_def": "Ratio of within-cluster scatter to between-cluster separation.",
        "detailed_def": "Lower values indicate better clustering. A lower index signifies clusters that are compact internally while well-separated from one another. In our pipeline, K=4 achieves an optimal balance between cluster compactness and business interpretability."
    },
    {
        "term": "Adjusted Rand Index (ARI)",
        "category": "ML Validation",
        "badge": "blue",
        "short_def": "Measures the agreement and stability of cluster assignments across different random initialization seeds.",
        "detailed_def": "Ranges from 0 (random assignment) to 1.0 (identical partition). An ARI score above 0.90 indicates high clustering stability. Our pipeline demonstrates a mean ARI of 99.86% across 5 random seeds, confirming cluster reproducibility."
    },
    {
        "term": "Bayesian Rating Shrinkage",
        "category": "Decision Science",
        "badge": "green",
        "short_def": "Shrinks observed ratings towards the city/category prior to prevent small-sample distortion.",
        "detailed_def": "A venue with a single 5.0-star review should not outrank a venue with 500 reviews and a 4.8-star average. Empirical Bayes shrinkage dampens unrepresentative extreme scores when review counts are low: \\(\\hat{R} = \\frac{v}{v + m} R + \\frac{m}{v + m} C\\), where \\(m\\) is the confidence threshold."
    },
    {
        "term": "Profit Potential Index (PPI)",
        "category": "Decision Science",
        "badge": "green",
        "short_def": "A multi-factor index (0–100) scoring commercial opportunity using customer review patterns as demand proxies.",
        "detailed_def": "Blends satisfaction (Bayesian rating & positive sentiment), demand velocity (reviews per venue), competitive saturation (inverse competitor density), and risk stability (standard deviation penalty). Note: this is a behavioral proxy, not a financial forecast."
    },
    {
        "term": "Opportunity Types",
        "category": "Decision Science",
        "badge": "green",
        "short_def": "Strategic archetypes categorizing market dynamics for commercial planning.",
        "detailed_def": "• <b>Proven Market</b>: High customer volume + high satisfaction ratings.<br>• <b>Underserved Gap</b>: Strong demand velocity + few existing competitors.<br>• <b>Quality Gap</b>: High review volume but depressed average ratings (clear opening for quality).<br>• <b>Saturated</b>: Many venues competing for fragmented, shared volume.<br>• <b>Weak Demand</b>: Low customer review activity and depressed ratings."
    },
    {
        "term": "Ward's Minimum Variance Linkage",
        "category": "Algorithms",
        "badge": "purple",
        "short_def": "Agglomerative hierarchical clustering criterion minimizing total within-cluster variance.",
        "detailed_def": "At each step, merges the pair of clusters that leads to the minimum increase in total sum of squared Euclidean deviations. Produces balanced, spherical clusters well-suited for commercial profiling."
    },
    {
        "term": "Principal Component Analysis (PCA)",
        "category": "Algorithms",
        "badge": "purple",
        "short_def": "Dimensionality reduction transforming 10 behavioral dimensions into orthogonal 2D projections.",
        "detailed_def": "PCA1 and PCA2 capture the greatest axes of variance across review counts, engagement length, and sentiment polarity. Allows 2D scatter visualization while preserving the geometric structure of high-dimensional feature spaces."
    },
    {
        "term": "Composite Business Key",
        "category": "Data Engineering",
        "badge": "amber",
        "short_def": "Composite identifier (place, address) preventing reviewer ID confusion.",
        "detailed_def": "In raw Google Local datasets, the 'Id' column identifies the reviewer, not the establishment. To correctly aggregate commercial entities, the pipeline generates a deterministic MD5 hash of normalised (place, address) pairs as the primary business ID."
    },
    {
        "term": "Haversine Distance",
        "category": "Geospatial",
        "badge": "amber",
        "short_def": "Great-circle distance between two geographic coordinate pairs on a spherical surface.",
        "detailed_def": "Computes the shortest distance over the Earth's surface in kilometers using latitude and longitude. Used in the competitor distance matrix to find the closest rival venues."
    }
]

def render(data_bundle):
    render_header(
        "Analytical Glossary & Terminology",
        "Comprehensive definitions of evaluation metrics, clustering algorithms, and decision formulas in plain language.",
        badge="DOCUMENTATION",
        breadcrumbs=["Platform", "Methodology", "Glossary"]
    )

    c_search, c_filter = st.columns([0.7, 0.3])
    with c_search:
        search_query = st.text_input("🔍 Search glossary terms...", placeholder="Filter by term or definition...", key="glossary_search")
    with c_filter:
        categories = ["All Categories", "ML Validation", "Decision Science", "Algorithms", "Data Engineering", "Geospatial"]
        selected_cat = st.selectbox("Category Filter", categories, key="glossary_cat")

    # Filter items
    filtered_items = GLOSSARY_ITEMS
    if selected_cat != "All Categories":
        filtered_items = [it for it in filtered_items if it["category"] == selected_cat]
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered_items = [
            it for it in filtered_items
            if q in it["term"].lower() or q in it["short_def"].lower() or q in it["detailed_def"].lower()
        ]

    st.markdown(f"<div style='font-size:12px; color:#94A3B8; margin-bottom:14px;'>Displaying <b>{len(filtered_items)}</b> terms:</div>", unsafe_allow_html=True)

    for item in filtered_items:
        with st.expander(f"**{item['term']}** — *{item['short_def']}*", expanded=True):
            st.markdown(f"""
                <div style="margin-bottom:8px;">
                    {render_badge(item['category'], item['badge'])}
                </div>
                <div style="font-size:13.5px; color:#CBD5E1; line-height:1.6;">
                    {item['detailed_def']}
                </div>
            """, unsafe_allow_html=True)

    render_footer()
