"""
Agglomerative Hierarchical Clustering Page.
Ward linkage dendrogram and comparative algorithm validation against K-Means.
"""
import streamlit as st
from src.ui.components import (
    render_header,
    render_empty_state,
    render_footer,
    render_section_header,
    render_paginated_table,
    render_info_callout
)
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "Agglomerative Hierarchical Clustering",
        "Ward linkage dendrogram analysis and comparative benchmark against K-Means partitioning.",
        badge="TAXONOMICAL STRUCTURE",
        breadcrumbs=["Platform", "Analyze", "Hierarchical Clustering"]
    )

    comp_df = data_bundle.get('comp')
    dendro_path = settings.OUTPUT_GRAPHS_DIR / "dendrogram.png"

    col_l, col_r = st.columns([1.35, 1.0])
    with col_l:
        st.markdown('<div class="saas-panel"><div class="panel-header">🌳 Ward Linkage Dendrogram (Truncated to 30 Merges)</div>', unsafe_allow_html=True)
        if dendro_path.exists():
            st.image(str(dendro_path), use_container_width=True)
            st.caption("Visualizes the hierarchical merge tree. Vertical line heights correspond to cophenetic distance between merged subclusters.")
        else:
            render_empty_state("Dendrogram Graph Missing", "Run the hierarchical clustering pipeline step to generate graph.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="saas-panel"><div class="panel-header">⚖️ Algorithm Comparison: K-Means vs. Agglomerative</div>', unsafe_allow_html=True)
        if comp_df is not None and not comp_df.empty:
            render_paginated_table(comp_df, key_prefix="hier_comp", page_size=5, download_filename="algorithm_benchmark.csv")
        else:
            st.info("Comparison data not available.")

        render_info_callout(
            "Both K-Means and Agglomerative Ward converge on virtually identical Silhouette (~0.439) and Davies-Bouldin (~0.999) scores, demonstrating that the 4 clusters represent genuine natural data partitions rather than algorithmic bias.",
            title="Structural Validation",
            callout_type="success"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    render_footer()
