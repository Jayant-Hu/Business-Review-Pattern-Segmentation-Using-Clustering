"""
Glossary & Analytical Terminology.
Defines ML metrics, clustering concepts, Bayesian shrinkage, and decision science formulas in plain language.
"""
from typing import Dict, Any, List
import streamlit as st
from src.ui.components import render_header, render_footer, render_badge

GLOSSARY_ITEMS: List[Dict[str, Any]] = [
    {
        "term": "Silhouette Score",
        "category": "Validation Metrics",
        "badge": "silver",
        "short_def": "Measures how similar an establishment is to its own cluster compared to neighboring clusters.",
        "detailed_def": "Values range from -1 to +1. A score near +1 indicates tight, distinct cluster boundaries; 0 indicates overlapping boundaries; negative values suggest incorrect assignments. Both Euclidean and Manhattan metrics are benchmarked."
    },
    {
        "term": "Davies-Bouldin Index",
        "category": "Validation Metrics",
        "badge": "silver",
        "short_def": "Ratio of within-cluster scatter to between-cluster separation.",
        "detailed_def": "Lower values indicate superior clustering. A lower index signifies clusters that are compact internally while well-separated from one another. K=4 achieves an optimal balance between mathematical compactness and business interpretability."
    },
    {
        "term": "Adjusted Rand Index (ARI)",
        "category": "Validation Metrics",
        "badge": "silver",
        "short_def": "Measures agreement and reproducibility of cluster partitions across distinct random initialization seeds.",
        "detailed_def": "Ranges from 0 (random assignment) to 1.0 (identical partition). An ARI score above 0.90 indicates high clustering stability. Our pipeline demonstrates a mean ARI of 99.86% across 5 random seeds."
    },
    {
        "term": "Bayesian Rating Shrinkage",
        "category": "Decision Science",
        "badge": "silver",
        "short_def": "Shrinks observed ratings towards the global corridor prior to eliminate small-sample bias.",
        "detailed_def": "Prevents unrepresentative 5-star ratings with only 1 review from outranking highly credible 4.8-star venues with 500 reviews: R_shrunk = (v * R + m * C) / (v + m), where m is the confidence review count."
    },
    {
        "term": "Profit Potential Index (PPI)",
        "category": "Decision Science",
        "badge": "signal",
        "short_def": "Multi-factor index (0–100) scoring commercial opportunity using customer review patterns as demand proxies.",
        "detailed_def": "Blends satisfaction (Bayesian rating and positive sentiment), demand velocity (reviews per venue), competitive saturation (inverse competitor density), and risk stability (standard deviation penalty)."
    },
    {
        "term": "Opportunity Types",
        "category": "Decision Science",
        "badge": "silver",
        "short_def": "Strategic archetypes categorizing market dynamics for commercial planning.",
        "detailed_def": "• Proven Market: High customer volume + high satisfaction ratings.<br>• Underserved Gap: Strong demand velocity + few existing competitors.<br>• Quality Gap: High review volume but depressed average ratings.<br>• Saturated Market: Many venues competing for fragmented, shared volume.<br>• Weak Demand: Low customer review activity and depressed ratings."
    },
    {
        "term": "Ward's Minimum Variance Linkage",
        "category": "Clustering Algorithms",
        "badge": "silver",
        "short_def": "Agglomerative hierarchical clustering criterion minimizing total within-cluster variance.",
        "detailed_def": "At each step, merges the pair of clusters that leads to the minimum increase in total sum of squared Euclidean deviations. Produces balanced, spherical clusters well-suited for commercial profiling."
    },
    {
        "term": "Principal Component Analysis (PCA)",
        "category": "Clustering Algorithms",
        "badge": "silver",
        "short_def": "Dimensionality reduction transforming 10 behavioral dimensions into orthogonal 2D projections.",
        "detailed_def": "PCA1 and PCA2 capture the greatest axes of variance across review counts, engagement length, and sentiment polarity, allowing 2D scatter visualization while preserving high-dimensional geometry."
    },
    {
        "term": "Composite Business Key",
        "category": "Data Engineering",
        "badge": "silver",
        "short_def": "Composite identifier (place, address) preventing reviewer ID conflation.",
        "detailed_def": "In raw Google Local datasets, the 'Id' column identifies the reviewer account, not the establishment. To correctly aggregate commercial entities, the pipeline generates a deterministic MD5 hash of normalised (place, address) pairs as the primary business ID."
    },
    {
        "term": "Haversine Distance",
        "category": "Geospatial",
        "badge": "silver",
        "short_def": "Great-circle geodesic distance between two coordinate pairs on a spherical surface.",
        "detailed_def": "Computes shortest distance over the Earth's surface in kilometers using latitude and longitude coordinates. Used in the competitor distance matrix to evaluate local crowding."
    }
]

def render(data_bundle):
    render_header(
        title="Glossary of Terms & Technical Definitions",
        subtitle="Analytical reference defining clustering criteria, statistical shrinkage, and decision metrics in plain language.",
        eyebrow="DOCUMENTATION",
        breadcrumbs=["Platform", "Methodology", "Glossary"]
    )

    c_search, c_filter = st.columns([0.7, 0.3])
    with c_search:
        search_query = st.text_input("Filter definitions", placeholder="Search by term or description...", label_visibility="collapsed")
    with c_filter:
        categories = ["All Categories", "Validation Metrics", "Decision Science", "Clustering Algorithms", "Data Engineering", "Geospatial"]
        selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")

    filtered_items = GLOSSARY_ITEMS
    if selected_cat != "All Categories":
        filtered_items = [it for it in filtered_items if it["category"] == selected_cat]
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered_items = [
            it for it in filtered_items
            if q in it["term"].lower() or q in it["short_def"].lower() or q in it["detailed_def"].lower()
        ]

    st.markdown(f"<div style='font-family:var(--font-mono); font-size:11.5px; color:var(--text-muted); margin-bottom:12px;'>Displaying {len(filtered_items)} definitions</div>", unsafe_allow_html=True)

    for item in filtered_items:
        with st.expander(f"{item['term']} — {item['short_def']}", expanded=True):
            st.markdown(f"""
                <div style="margin-bottom:6px;">
                    {render_badge(item['category'], item['badge'])}
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.55;">
                    {item['detailed_def']}
                </div>
            """, unsafe_allow_html=True)

    render_footer()
