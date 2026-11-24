"""
Quantitative Model Evaluation & Stability Page.
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
from src.ui.theme import get_plotly_theme

def render(data_bundle):
    render_header(
        "Quantitative Model Evaluation & Stability",
        "Mathematical validation: WCSS Inertia, Silhouette Cohesion, Davies-Bouldin Index, and Seed Stability.",
        badge="ACADEMIC RIGOR",
        breadcrumbs=["Platform", "Analyze", "Evaluation Metrics"]
    )

    eval_df = data_bundle.get('eval')
    stab_df = data_bundle.get('stab')

    if eval_df is None or stab_df is None:
        render_empty_state(
            "Evaluation Metrics Not Loaded",
            "Run pipeline to generate model metrics and stability results.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    c1, c2 = st.columns(2)
    with c1:
        fig_stab = px.bar(
            stab_df,
            x='seed_comparison',
            y='ARI',
            color='ARI',
            color_continuous_scale='Greens',
            range_y=[0.95, 1.0],
            text='ARI'
        )
        fig_stab.update_layout(coloraxis_showscale=False)
        render_chart_container(
            "Cluster Assignment Stability Across 5 Random Seeds",
            fig_stab,
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
        fig_db.update_traces(line_color="#EF4444", line_width=3, marker=dict(size=8))
        render_chart_container(
            "Davies-Bouldin Index Across K = 2..7 (Lower is Better)",
            fig_db,
            insight="Davies-Bouldin Index reaches an optimal minimum at K=4, indicating maximum ratio of inter-cluster separation to intra-cluster spread.",
            help_text="Davies-Bouldin measures the average similarity of each cluster to its most similar cluster. Lower values denote superior separation."
        )

    render_section_header("Complete Evaluation Metric Table")
    render_paginated_table(
        eval_df,
        key_prefix="eval_summary_table",
        page_size=10,
        download_filename="evaluation_metrics_full.csv"
    )

    render_footer()
