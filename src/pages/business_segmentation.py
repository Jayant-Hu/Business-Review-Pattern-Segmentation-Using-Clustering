"""
Page 8: Business Segmentation & Comparative Analysis.
"""
import streamlit as st
import pandas as pd
from src.ui.components import render_header, render_empty_state
from src.services.analytics import compare_two_segments

def render(data_bundle):
    render_header(
        "Commercial Business Segmentation & Profiles",
        "Discovered cluster behavioral baselines, segment comparison, and interactive filtering.",
        "SEGMENT EXPLORER"
    )

    prof_df = data_bundle['prof']
    biz_df = data_bundle['biz']

    if biz_df is None or prof_df is None:
        render_empty_state("Clustering Data Not Loaded", "Run the pipeline to generate clustered_businesses.csv.")
        return

    st.markdown('<div class="saas-panel"><div class="panel-header">📋 Empirical Cluster Behavioral Profiles</div>', unsafe_allow_html=True)
    st.dataframe(prof_df, width="100%")
    st.markdown('</div>', unsafe_allow_html=True)

    # Compare Any Two Segments Tool
    st.markdown('<div class="saas-panel"><div class="panel-header">⚖️ Compare Any Two Segments</div>', unsafe_allow_html=True)
    all_segments = sorted(biz_df['cluster_name'].dropna().unique().tolist())
    if len(all_segments) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            seg_a = st.selectbox("Select Segment A:", all_segments, index=0)
        with col_b:
            seg_b = st.selectbox("Select Segment B:", all_segments, index=min(1, len(all_segments)-1))
            
        comparison_table = compare_two_segments(biz_df, seg_a, seg_b)
        st.dataframe(comparison_table, width="100%")
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive filtering section
    st.markdown('<div class="saas-panel"><div class="panel-header">🔍 Filter Businesses by Segment & Category</div>', unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns([1.5, 1.5, 1.0])
    with f1:
        cluster_filter = st.multiselect(
            "Filter Cluster Segment:",
            options=all_segments,
            default=all_segments
        )
    with f2:
        all_cats = sorted(biz_df['place type'].dropna().unique().tolist())
        category_filter = st.multiselect(
            "Filter Category:",
            options=all_cats,
            default=all_cats[:5] if len(all_cats) >= 5 else all_cats
        )
    with f3:
        min_rating_filter = st.slider("Min Avg Rating:", 1.0, 5.0, 1.0, 0.1)

    filtered_df = biz_df[
        (biz_df['cluster_name'].isin(cluster_filter)) &
        (biz_df['place type'].isin(category_filter)) &
        (biz_df['avg_rating'] >= min_rating_filter)
    ]

    st.markdown(f"**Found {len(filtered_df):,} matching establishments:**")
    cols_to_show = ['place', 'place type', 'address', 'city', 'cluster_name', 'avg_rating', 'sample_review_count', 'positive_review_pct', 'negative_review_pct']
    existing_cols = [c for c in cols_to_show if c in filtered_df.columns]
    st.dataframe(filtered_df[existing_cols], width="100%")

    # Export Download Buttons (CSV)
    csv_data = filtered_df[existing_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Segment Report (CSV)",
        data=csv_data,
        file_name="segmented_businesses_report.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
