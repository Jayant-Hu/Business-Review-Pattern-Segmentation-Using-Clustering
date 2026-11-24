"""
PCA 2D Dimensionality Reduction & Projection Page.
Validates cluster boundary geometry and sentiment separation in orthogonal subspace.
"""
import streamlit as st
import pandas as pd
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_info_callout,
    render_section_header
)
from src.ui.charts import build_pca_scatter
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "Principal Component Analysis (PCA)",
        "2D dimensionality reduction for visual inspection of cluster boundary separation and spatial manifold.",
        badge="DIMENSIONAL PROJECTION",
        breadcrumbs=["Platform", "Analyze", "PCA Visualization"]
    )

    pca_df = data_bundle.get('pca')
    biz_df = data_bundle.get('biz')

    if pca_df is None or biz_df is None:
        render_empty_state(
            "PCA Projections Not Found",
            "Run the PCA pipeline step to compute 2D projections.",
            action_command="python scripts/run_pipeline.py"
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
        "Interactive 2D Principal Component Projection (Variance Explained: 53.63%)",
        fig_pca,
        insight="High-Satisfaction Top Tier venues separate sharply along the primary sentiment vector, while Critical Intervention venues form a compact polarized cluster.",
        help_text="Each point represents an individual establishment mapped from 10 dimensions to 2 orthogonal components. Points closer together exhibit similar customer behavioral profiles."
    )

    render_section_header("Principal Component Interpretation")
    st.markdown("""
        <div class="saas-panel">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div style="background:rgba(255,255,255,0.02); padding:14px; border-radius:10px; border:1px solid var(--border-subtle);">
                    <div style="font-weight:700; color:#3B82F6; font-size:14px; margin-bottom:6px;">Component 1: Sentiment Polarity Axis</div>
                    <div style="font-size:12px; color:var(--text-muted); line-height:1.5;">
                        Strong positive loadings on <code>avg_rating</code> and <code>positive_review_pct</code>, with strong negative loading on <code>negative_review_pct</code>. Separates top-rated venues from dissatisfied cohorts.
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.02); padding:14px; border-radius:10px; border:1px solid var(--border-subtle);">
                    <div style="font-weight:700; color:#8B5CF6; font-size:14px; margin-bottom:6px;">Component 2: Engagement & Depth Axis</div>
                    <div style="font-size:12px; color:var(--text-muted); line-height:1.5;">
                        Heavy positive loadings on <code>log_avg_review_length</code> and <code>detailed_review_pct</code>. Captures businesses that receive long, thoughtful customer feedback versus simple star votes.
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    render_footer()
