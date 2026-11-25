"""
Principal Component Analysis (PCA) 2D Projection.
Validates cluster boundary geometry and sentiment separation in orthogonal subspace.
"""
import streamlit as st
import pandas as pd
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_section_header
)
from src.ui.charts import build_pca_scatter

def render(data_bundle):
    render_header(
        title="Principal Component Analysis",
        subtitle="2D dimensionality reduction for geometric validation of cluster boundary separation.",
        eyebrow="DIMENSIONAL PROJECTION",
        breadcrumbs=["Platform", "Clustering Models", "PCA Visualization"]
    )

    pca_df = data_bundle.get('pca')
    biz_df = data_bundle.get('biz')

    if pca_df is None or biz_df is None:
        render_empty_state(
            title="PCA Projections Not Found",
            message="Run the PCA pipeline step to compute 2D projections.",
            action_command="python scripts/run_pipeline.py --step cluster"
        )
        render_footer()
        return

    merged_pca = pca_df.merge(
        biz_df[['business_id', 'avg_rating', 'sample_review_count']],
        on='business_id',
        how='left'
    )
    if 'cluster_name' not in merged_pca.columns and 'cluster_name_x' in merged_pca.columns:
        merged_pca['cluster_name'] = merged_pca['cluster_name_x']
    elif 'cluster_name' not in merged_pca.columns and 'cluster_name_y' in merged_pca.columns:
        merged_pca['cluster_name'] = merged_pca['cluster_name_y']

    fig_pca = build_pca_scatter(merged_pca)
    render_chart_container(
        title="2D Principal Component Projection (Variance Explained: 53.63%)",
        fig=fig_pca,
        insight="High-Satisfaction Top Tier venues separate sharply along the primary sentiment vector, while Critical Intervention venues form a compact polarized cluster.",
        help_text="Each point represents an individual establishment mapped from 10 dimensions to 2 orthogonal components. Points closer together exhibit similar customer behavioral profiles."
    )

    render_section_header("Principal Component Loadings", subtitle="Interpretation of primary geometric axes")
    st.markdown("""
        <div class="terminal-panel">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div style="background:var(--surface-2); padding:14px; border-radius:6px; border:1px solid var(--border);">
                    <div style="font-family:var(--font-mono); font-weight:600; color:var(--text-primary); font-size:12px; margin-bottom:6px; text-transform:uppercase;">Component 1: Sentiment Polarity</div>
                    <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.5;">
                        Strong positive loadings on <code>avg_rating</code> and <code>positive_review_pct</code>, with inverse loading on <code>negative_review_pct</code>. Distinguishes satisfied customer bases from high-friction venues.
                    </div>
                </div>
                <div style="background:var(--surface-2); padding:14px; border-radius:6px; border:1px solid var(--border);">
                    <div style="font-family:var(--font-mono); font-weight:600; color:var(--text-primary); font-size:12px; margin-bottom:6px; text-transform:uppercase;">Component 2: Feedback Depth</div>
                    <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.5;">
                        Strong positive loadings on <code>log_avg_review_length</code> and <code>detailed_review_pct</code>. Captures descriptive review engagement versus rapid star-only ratings.
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    render_footer()
