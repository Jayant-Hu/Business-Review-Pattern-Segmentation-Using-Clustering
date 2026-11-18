"""
Page 4: K-Means Clustering.
"""
import streamlit as st
from src.ui.components import render_header, render_empty_state
from src.ui.charts import build_elbow_chart, build_silhouette_comparison_chart
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "K-Means Partitioning & Hyperparameter Selection",
        "Evaluating Within-Cluster Sum of Squares (WCSS) and Silhouette cohesion across K = 2..7.",
        "MODEL OPTIMIZATION"
    )

    eval_df = data_bundle['eval']
    if eval_df is None:
        render_empty_state("Evaluation Results Missing", "Run K-Means experiments to generate evaluation_results.csv.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="saas-panel"><div class="panel-header">📉 Elbow Curve (Inertia / WCSS)</div>', unsafe_allow_html=True)
        fig_elbow = build_elbow_chart(eval_df, selected_k=settings.SELECTED_K)
        st.plotly_chart(fig_elbow, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="saas-panel"><div class="panel-header">📐 Distance Metric Comparison: Silhouette</div>', unsafe_allow_html=True)
        fig_dist = build_silhouette_comparison_chart(eval_df)
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="saas-panel"><div class="panel-header">📊 Quantitative Cluster Evaluation Metrics</div>', unsafe_allow_html=True)
    st.dataframe(eval_df.style.highlight_max(axis=0, subset=['Silhouette_Euclidean', 'Silhouette_Manhattan'], color='#1E3A8A'), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
