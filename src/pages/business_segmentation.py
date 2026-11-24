"""
Commercial Business Segmentation & Profiles Page.
Displays cluster behavioral baselines, 2-segment comparison tool, and filtered establishment tables.
"""
import streamlit as st
import pandas as pd
from src.ui.components import (
    render_header,
    render_empty_state,
    render_footer,
    render_section_header,
    render_paginated_table,
    render_info_callout,
    render_badge
)
from src.services.analytics import compare_two_segments

def render(data_bundle):
    render_header(
        "Commercial Business Segmentation & Profiles",
        "Discovered cluster behavioral baselines, side-by-side segment comparisons, and filtered establishment explorer.",
        badge="SEGMENT EXPLORER",
        breadcrumbs=["Platform", "Analyze", "Business Segmentation"]
    )

    prof_df = data_bundle.get('prof')
    biz_df = data_bundle.get('biz_filtered', data_bundle.get('biz'))

    if biz_df is None or prof_df is None:
        render_empty_state(
            "Clustering Data Not Loaded",
            "Run the pipeline to generate clustered_businesses.csv and cluster_profiles.csv.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    # Section 1: Empirical Cluster Behavioral Profiles
    render_section_header("Empirical Cluster Behavioral Profiles")
    st.dataframe(prof_df, use_container_width=True, hide_index=True)

    # Section 2: Compare Any Two Segments Side-by-Side
    render_section_header("Compare Any Two Segments Side-by-Side")
    all_segments = sorted(biz_df['cluster_name'].dropna().unique().tolist())
    if len(all_segments) >= 2:
        c_a, c_b = st.columns(2)
        with c_a:
            seg_a = st.selectbox("Select Segment A:", all_segments, index=0, key="seg_cmp_a")
        with c_b:
            seg_b = st.selectbox("Select Segment B:", all_segments, index=min(1, len(all_segments)-1), key="seg_cmp_b")

        comparison_table = compare_two_segments(data_bundle.get('biz', biz_df), seg_a, seg_b)
        st.dataframe(comparison_table, use_container_width=True, hide_index=True)
    else:
        st.info("Insufficient segment data to perform 2-segment comparison.")

    # Section 3: Filtered Establishment Directory
    render_section_header("Segmented Establishment Directory")
    display_cols = [
        'place', 'place type', 'city', 'cluster_name',
        'avg_rating', 'sample_review_count', 'positive_review_pct', 'negative_review_pct', 'address'
    ]
    avail_cols = [c for c in display_cols if c in biz_df.columns]

    render_paginated_table(
        biz_df[avail_cols],
        key_prefix="segmented_biz_table",
        page_size=15,
        download_filename="segmented_establishments.csv"
    )

    render_footer()
