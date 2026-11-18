"""
Page 6: PCA Visualization.
"""
import streamlit as st
from src.ui.components import render_header, render_empty_state
from src.ui.charts import build_pca_scatter
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "Principal Component Analysis (PCA)",
        "2D dimensionality reduction for visual inspection of cluster boundary separation.",
        "DIMENSIONAL PROJECTION"
    )

    pca_df = data_bundle['pca']
    biz_df = data_bundle['biz']

    if pca_df is None or biz_df is None:
        render_empty_state("PCA Data Not Found", "Run the PCA pipeline step to compute 2D projections.")
        return

    merged_pca = pca_df.merge(
        biz_df[['business_id', 'cluster_name', 'avg_rating', 'sample_review_count']],
        on='business_id',
        how='left'
    )
    
    st.markdown('<div class="saas-panel"><div class="panel-header">🔬 Interactive 2D Principal Component Projection (Variance Explained: 53.63%)</div>', unsafe_allow_html=True)
    fig_pca = build_pca_scatter(merged_pca)
    st.plotly_chart(fig_pca, width="100%")
    st.markdown('</div>', unsafe_allow_html=True)
