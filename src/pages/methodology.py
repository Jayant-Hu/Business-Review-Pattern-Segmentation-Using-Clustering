"""
Methodology & Model Card.
Presents architecture specifications, feature dictionary, evaluation benchmarks, and operational limitations.
"""
import streamlit as st
import pandas as pd

from src.ui.components import (
    render_header,
    render_section_header,
    render_empty_state,
    render_footer,
    render_info_callout
)
from src.services.decision_advisor import HONESTY_DISCLAIMER

FEATURE_DICTIONARY = [
    {"Feature": "avg_rating", "Type": "Float", "Description": "Arithmetic mean star rating (1.0 to 5.0) awarded by reviewers."},
    {"Feature": "rating_std", "Type": "Float", "Description": "Standard deviation of ratings reflecting consistency vs. polarization."},
    {"Feature": "log_sample_review_count", "Type": "Float", "Description": "log(1 + review_count), stabilizing heavy right-skewed review counts."},
    {"Feature": "positive_review_pct", "Type": "Percentage", "Description": "Proportion of reviews with 4 or 5 stars (satisfaction indicator)."},
    {"Feature": "negative_review_pct", "Type": "Percentage", "Description": "Proportion of reviews with 1 or 2 stars (dissatisfaction indicator)."},
    {"Feature": "log_avg_review_length", "Type": "Float", "Description": "log(1 + avg_character_length), measuring engagement depth."},
    {"Feature": "detailed_review_pct", "Type": "Percentage", "Description": "Proportion of reviews with word count > 50 words."},
    {"Feature": "service_feedback_rate", "Type": "Float (0-1)", "Description": "Proportion of reviews explicitly rating service staff."},
    {"Feature": "food_feedback_rate", "Type": "Float (0-1)", "Description": "Proportion of reviews explicitly rating food quality."},
    {"Feature": "atmosphere_feedback_rate", "Type": "Float (0-1)", "Description": "Proportion of reviews rating ambiance and atmosphere."}
]

def render(data_bundle):
    render_header(
        title="Technical Methodology & Model Card",
        subtitle="System architecture specifications, 10-dimensional feature engineering, and statistical validation.",
        eyebrow="MODEL CARD v2.5",
        breadcrumbs=["Platform", "Methodology", "Model Card"]
    )

    eval_df = data_bundle.get('eval')
    stab_df = data_bundle.get('stab')

    tab_arch, tab_features, tab_eval, tab_limits = st.tabs([
        "Architecture Pipeline",
        "10-D Feature Space",
        "Evaluation & Stability",
        "Limitations & Disclaimer"
    ])

    with tab_arch:
        render_section_header("Data Pipeline Architecture", subtitle="Structured flow from raw transactions to decision scoring")
        st.markdown("""
            <div class="terminal-panel">
                <div style="font-family:var(--font-mono); font-size:12px; color:var(--text-secondary); line-height:1.7; background:var(--surface-2); padding:16px; border-radius:6px; border:1px solid var(--border);">
                    Raw Google Local Reviews (~1.17M records)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    Data Cleaning & PII Sanitization ─── Primary Composite Key: MD5(place + address)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    10-Dimensional Feature Matrix ─── Logarithmic Skew Transformations log(1 + x)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    StandardScaler Normalization<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;┌───┴───────────────────────┬───────────────────────┐<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    K-Means (Selected K=4)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Agglomerative Ward&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2D PCA Projection<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;└───┬───────────────────────┴───────────────────────┘<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    Statistical Role Labelling (Top Tier, Moderate, High Engagement, At-Risk)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    Geocoding Engine ─── Spatial Centroid Alignment & Cache<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    Decision Engine & PPI Scoring ─── Bayesian Shrinkage & Haversine Matrix
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tab_features:
        render_section_header("Feature Space Specifications", subtitle="10 behavioral dimensions engineered for establishment clustering")
        feat_df = pd.DataFrame(FEATURE_DICTIONARY)
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

        render_info_callout(
            title="Logarithmic Variance Stabilization",
            text="Review count and character length exhibit heavy power-law distributions. Applying logarithmic scaling y = log(1 + x) stabilizes variance prior to z-score standardization.",
            callout_type="info"
        )

    with tab_eval:
        render_section_header("Model Optimization & Stability", subtitle="Empirical validation benchmarks across candidate K parameters")
        if eval_df is not None and not eval_df.empty:
            st.dataframe(eval_df, use_container_width=True, hide_index=True)
        if stab_df is not None and not stab_df.empty:
            st.dataframe(stab_df, use_container_width=True, hide_index=True)

    with tab_limits:
        render_section_header("Operational Limitations & Assumptions", subtitle="Methodological parameters and proxy constraints")
        render_info_callout(
            title="Operational Reality Notice",
            text=HONESTY_DISCLAIMER,
            callout_type="warning"
        )
        st.markdown("""
            <div style="font-size:13px; color:var(--text-secondary); line-height:1.6;">
                1. <b>Customer Reviews as Proxy:</b> Online review volume represents customer engagement density and perceived sentiment, but does not substitute for financial revenue or footfall audits.<br>
                2. <b>Geocoding Precision:</b> Addresses lacking building-level street numbers utilize municipal neighborhood centroid approximations.<br>
                3. <b>Temporal Stability:</b> Cross-sectional review snapshots capture historical accumulated perception; periodic re-clustering is recommended.
            </div>
        """, unsafe_allow_html=True)

    render_footer()
