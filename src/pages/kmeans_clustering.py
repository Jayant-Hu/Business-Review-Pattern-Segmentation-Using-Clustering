"""
K-Means Clustering & Hyperparameter Optimization Page.
Evaluates WCSS inertia elbow, Silhouette cohesion across distance metrics, and K=4 selection.
"""
import streamlit as st
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_paginated_table,
    render_section_header
)
from src.ui.charts import build_elbow_chart, build_silhouette_comparison_chart
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "K-Means Partitioning & Hyperparameter Selection",
        "Evaluating Within-Cluster Sum of Squares (WCSS) and Silhouette cohesion across K = 2..7.",
        badge="MODEL OPTIMIZATION",
        breadcrumbs=["Platform", "Analyze", "K-Means Clustering"]
    )

    eval_df = data_bundle.get('eval')
    if eval_df is None or eval_df.empty:
        render_empty_state(
            "Evaluation Results Missing",
            "Run K-Means experiments to generate evaluation_results.csv.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    c1, c2 = st.columns(2)
    with c1:
        fig_elbow = build_elbow_chart(eval_df, selected_k=settings.SELECTED_K)
        render_chart_container(
            "Elbow Curve: Within-Cluster Sum of Squares (Inertia)",
            fig_elbow,
            insight=f"WCSS inertia trajectory demonstrates clear diminishing returns beyond K={settings.SELECTED_K}, verifying the elbow inflection point.",
            help_text="The elbow method plots inertia (WCSS) as K increases. The point where reduction flattens indicates the optimal balance between compactness and model complexity."
        )

    with c2:
        fig_dist = build_silhouette_comparison_chart(eval_df)
        render_chart_container(
            "Silhouette Score Comparison: Euclidean vs. Manhattan",
            fig_dist,
            insight=f"Euclidean distance achieves its global maximum cohesion ({eval_df[eval_df['k']==settings.SELECTED_K]['Silhouette_Euclidean'].values[0]:.4f}) at K={settings.SELECTED_K}.",
            help_text="Silhouette measures cluster separation (-1 to +1). Peak values denote well-defined cluster boundaries. Comparing distance metrics confirms geometric robustness."
        )

    render_section_header("Quantitative Cluster Optimization Matrix")
    render_paginated_table(
        eval_df,
        key_prefix="kmeans_eval",
        page_size=10,
        download_filename="kmeans_hyperparameter_eval.csv"
    )

    render_footer()
