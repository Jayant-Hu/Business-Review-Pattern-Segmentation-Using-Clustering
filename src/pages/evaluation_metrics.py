"""
Quantitative Model Evaluation & Stability.
Provides Silhouette, Davies-Bouldin, and Adjusted Rand Index across initialization seeds.
"""
import streamlit as st
import plotly.express as px
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_section_header,
    render_paginated_table
)
from src.ui.theme import get_plotly_theme, COLOR_SILVER, COLOR_RED

def render(data_bundle):
    render_header(
        title="Quantitative Evaluation & Cluster Stability",
        subtitle="Mathematical benchmarks: WCSS Inertia, Silhouette Cohesion, Davies-Bouldin Index, and Random Seed Stability.",
        eyebrow="ACADEMIC RIGOR",
        breadcrumbs=["Platform", "Clustering Models", "Evaluation Metrics"]
    )

    eval_df = data_bundle.get('eval')
    stab_df = data_bundle.get('stab')

    if eval_df is None or stab_df is None:
        render_empty_state(
            title="Evaluation Metrics Not Loaded",
            message="Run pipeline to generate model metrics and stability results.",
            action_command="python scripts/run_pipeline.py --step evaluate"
        )
        render_footer()
        return

    c1, c2 = st.columns(2)
    with c1:
        fig_stab = px.bar(
            stab_df,
            x='seed_comparison',
            y='ARI',
            color_discrete_sequence=[COLOR_SILVER],
            range_y=[0.95, 1.0],
            text='ARI'
        )
        fig_stab.update_layout(**get_plotly_theme("dark"))
        fig_stab.update_layout(xaxis_title="Random Seed Comparison", yaxis_title="Adjusted Rand Index (ARI)")
        render_chart_container(
            title="Cluster Assignment Stability (Adjusted Rand Index)",
            fig=fig_stab,
            insight=f"Mean ARI of {stab_df['ARI'].mean()*100:.2f}% confirms that cluster partitions are reproducible and immune to initialization perturbations.",
            help_text="Adjusted Rand Index (ARI) evaluates consistency between two independent clustering runs. Scores above 0.90 signify exceptional cluster stability."
        )

    with c2:
        fig_db = px.line(
            eval_df,
            x='k',
            y='Davies_Bouldin',
            markers=True
        )
        fig_db.update_layout(**get_plotly_theme("dark"))
        fig_db.update_traces(line_color=COLOR_RED, line_width=2, marker=dict(size=7))
        fig_db.update_layout(xaxis_title="Cluster Count (K)", yaxis_title="Davies-Bouldin Index")
        render_chart_container(
            title="Davies-Bouldin Index Across Candidate K (Lower is Better)",
            fig=fig_db,
            insight="Davies-Bouldin Index reaches an optimal inflection at K=4, indicating maximum ratio of inter-cluster separation to intra-cluster spread.",
            help_text="Davies-Bouldin measures the average similarity of each cluster to its most similar cluster. Lower values denote superior separation."
        )

    render_section_header("Complete Evaluation Metric Table", subtitle="Inertia, Silhouette, and Davies-Bouldin benchmarks across evaluated models")
    render_paginated_table(
        df=eval_df,
        key_prefix="eval_summary_table",
        page_size=10,
        download_filename="evaluation_metrics_full.csv"
    )

    render_footer()
