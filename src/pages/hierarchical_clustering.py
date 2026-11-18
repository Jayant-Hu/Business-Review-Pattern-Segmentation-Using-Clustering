"""
Page 5: Hierarchical Clustering.
"""
import streamlit as st
from src.ui.components import render_header, render_empty_state
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "Agglomerative Hierarchical Clustering",
        "Ward linkage dendrogram analysis and comparative benchmark against K-Means partitioning.",
        "TAXONOMICAL STRUCTURE"
    )

    comp_df = data_bundle['comp']
    dendro_path = settings.OUTPUT_GRAPHS_DIR / "dendrogram.png"

    col_l, col_r = st.columns([1.4, 1.0])
    with col_l:
        st.markdown('<div class="saas-panel"><div class="panel-header">🌳 Ward Linkage Dendrogram (Truncated to 30 Merges)</div>', unsafe_allow_html=True)
        if dendro_path.exists():
            st.image(str(dendro_path), width="100%")
        else:
            render_empty_state("Dendrogram Not Found", "Run the hierarchical clustering pipeline step.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="saas-panel"><div class="panel-header">⚖️ Benchmark: K-Means vs. Agglomerative</div>', unsafe_allow_html=True)
        if comp_df is not None:
            st.dataframe(comp_df, width="100%")
        st.markdown("""
            <div style="font-size:12.5px; color:#94A3B8; line-height:1.6; margin-top:12px;">
                <b>Methodological Takeaways:</b><br>
                1. <b>Ward Linkage</b> minimizes the total within-cluster variance, matching the objective function of K-Means.<br>
                2. Both methods converge around <b>Silhouette ~ 0.43</b> and <b>Davies-Bouldin ~ 0.99</b>, verifying that the 4 clusters represent real underlying behavioral separations rather than algorithm-specific artifacts.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
