"""
Methodology & Model Card Page.
Presents:
- End-to-end technical architecture workflow
- 10-D Feature dictionary & mathematical transformations
- K selection criteria & empirical cluster evaluation
- Model limitations & data assumptions
- Mandatory Honesty Rule disclaimer
"""
import streamlit as st
import pandas as pd

from src.ui.components import (
    render_header,
    render_section_header,
    render_empty_state,
    render_footer,
    render_info_callout,
    render_badge
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
        "Technical Methodology & Model Card",
        "Architecture specifications, 10-dimensional feature engineering, validation benchmarks, and data limitations.",
        badge="MODEL CARD v2.4",
        breadcrumbs=["Platform", "Methodology", "Model Card"]
    )

    eval_df = data_bundle.get('eval')
    stab_df = data_bundle.get('stab')

    # Architecture Overview Tab
    tab_arch, tab_features, tab_eval, tab_limits = st.tabs([
        "🏗️ Architecture Pipeline",
        "📐 10-D Feature Engineering",
        "📊 Evaluation & Stability",
        "⚠️ Limitations & Disclaimer"
    ])

    with tab_arch:
        render_section_header("End-to-End Data Processing Pipeline")
        st.markdown("""
            <div class="saas-panel">
                <div style="font-family:'JetBrains Mono', monospace; font-size:12.5px; color:#60A5FA; line-height:1.7; background:rgba(0,0,0,0.3); padding:16px; border-radius:10px;">
                    [Raw Google Local Reviews (~1.17M rows)]<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [Data Cleaning & PII Sanitization] ─── Composite Key: MD5(place + address)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [10-Dimensional Feature Aggregation] ─── Log Skew Transformations<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [StandardScaler Feature Normalization]<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;┌─────┴───────────────────────┬────────────────────────┐<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [K-Means (K=4)]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Hierarchical Ward]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2D PCA Projection]<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;└─────┬───────────────────────┴────────────────────────┘<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [Data-Driven Segment Role Assignment] (Top Tier, Mixed, Engaged, At-Risk)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [Multi-Tier Geocoding Engine] ─── Google Maps API + Cached Centroids<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
                    [Decision Engine & PPI Scoring] ─── Bayesian Shrinkage & Haversine Matrix
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            **Pipeline Architecture Highlights:**
            - **Composite Establishment Key**: Google Local `Id` represents the reviewer account; establishing the composite key `(place, address)` prevents establishment merging errors.
            - **Reproducibility**: Fixed `random_state=42` throughout KMeans and PCA fitting.
            - **Persistence**: Models and transformation scalers serialized via `joblib` in `output/models/`.
        """)

    with tab_features:
        render_section_header("10-Dimensional Commercial Feature Space")
        feat_df = pd.DataFrame(FEATURE_DICTIONARY)
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

        render_info_callout(
            "Skewness Mitigation: Review counts and character lengths follow heavy power-law distributions. "
            "Applying logarithmic scaling y = log(1 + x) stabilizes variance prior to z-score standardization.",
            title="Statistical Scaling Note",
            callout_type="info"
        )

    with tab_eval:
        render_section_header("Cluster Optimization & Stability Benchmarks")
        if eval_df is not None and not eval_df.empty:
            st.markdown("##### Empirical Evaluation Across K (2 to 7):")
            st.dataframe(eval_df, use_container_width=True, hide_index=True)
        else:
            st.info("Evaluation metrics table not found in output artifacts.")

        if stab_df is not None and not stab_df.empty:
            st.markdown("##### Random Seed Stability (Adjusted Rand Index):")
            st.dataframe(stab_df, use_container_width=True, hide_index=True)

        st.markdown("""
            **Selection Criteria for K=4:**
            1. **Inertia Elbow**: Diminishing returns in WCSS reduction beyond K=4.
            2. **Silhouette Peak**: Euclidean silhouette score peaks cleanly at K=4.
            3. **Operational Utility**: Delivers 4 distinct, interpretable commercial profiles rather than fragmented sub-clusters.
        """)

    with tab_limits:
        render_section_header("Model Assumptions & Operational Limitations")
        st.markdown(f"""
            <div class="info-callout alert">
                <b>Mandatory Operating Principle:</b> {HONESTY_DISCLAIMER}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            1. **Customer Review Volume as a Proxy**: Online customer reviews represent a proxy for footfall, demand velocity, and satisfaction, but do not capture off-line customer behavior.
            2. **Geocoding Precision**: Addresses without full street numbers rely on postal code or neighborhood centroid fallback.
            3. **Language Bias**: Sentiment analysis is calculated primarily across English and translated reviews.
            4. **Survivorship Bias**: Closed establishments may be underrepresented in the current review snapshot.
        """)

    render_footer()
