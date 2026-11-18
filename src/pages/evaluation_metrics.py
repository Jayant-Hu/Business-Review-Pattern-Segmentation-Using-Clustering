"""
Page 7: Evaluation Metrics & Model Card.
"""
import streamlit as st
import plotly.express as px
from src.ui.components import render_header, render_empty_state
from src.ui.theme import PLOTLY_DARK_THEME

def render(data_bundle):
    render_header(
        "Quantitative Model Evaluation & Model Card",
        "Mathematical rigor: WCSS, Silhouette Cohesion, Davies-Bouldin Index, and Adjusted Rand Index.",
        "ACADEMIC RIGOR"
    )

    eval_df = data_bundle['eval']
    stab_df = data_bundle['stab']

    if eval_df is None or stab_df is None:
        render_empty_state("Evaluation Metrics Not Loaded", "Run pipeline to generate model metrics.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="saas-panel"><div class="panel-header">🛡️ Cluster Assignment Stability (Adjusted Rand Index)</div>', unsafe_allow_html=True)
        fig_stab = px.bar(
            stab_df,
            x='seed_comparison',
            y='ARI',
            color='ARI',
            color_continuous_scale='Greens',
            range_y=[0.95, 1.0],
            text='ARI'
        )
        fig_stab.update_layout(**PLOTLY_DARK_THEME)
        fig_stab.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_stab, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="saas-panel"><div class="panel-header">📉 Davies-Bouldin Index (Lower is Better)</div>', unsafe_allow_html=True)
        fig_db = px.line(
            eval_df,
            x='k',
            y='Davies_Bouldin',
            markers=True,
            title="Davies-Bouldin Metric Across K=2..7"
        )
        fig_db.update_layout(**PLOTLY_DARK_THEME)
        fig_db.update_traces(line_color="#EF4444")
        st.plotly_chart(fig_db, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Formal Model Card Section
    st.markdown("""
        <div class="saas-panel">
            <div class="panel-header">📑 Formal Machine Learning Model Card</div>
            <div style="font-size:13px; color:#94A3B8; line-height:1.7;">
                <b>• Model Architecture:</b> Scikit-Learn Pipeline combining <code>StandardScaler</code> and <code>KMeans(n_clusters=4, random_state=42, n_init=15)</code>.<br>
                <b>• Input Features (10-D):</b> <code>avg_rating</code>, <code>rating_std</code>, <code>log_sample_review_count</code>, <code>positive_review_pct</code>, <code>negative_review_pct</code>, <code>log_avg_review_length</code>, <code>detailed_review_pct</code>, <code>service_feedback_rate</code>, <code>food_feedback_rate</code>, <code>atmosphere_feedback_rate</code>.<br>
                <b>• Objective Function:</b> Minimization of inertia (within-cluster sum of squared Euclidean distances).<br>
                <b>• Hyperparameter Selection:</b> Evaluated K ∈ [2, 7]. K=4 selected as optimal Pareto balance between mathematical separation and city management actionability.<br>
                <b>• Intended Use:</b> Decision-support for municipal commercial diagnostics, tourism showcases, and business support funding.<br>
                <b>• Known Limitations:</b> Review data provenance is observational; sample counts represent snapshot frequencies rather than all-time historical traffic.
            </div>
        </div>
    """, unsafe_allow_html=True)
