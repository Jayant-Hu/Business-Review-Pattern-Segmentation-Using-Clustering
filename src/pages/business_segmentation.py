"""
Commercial Business Segmentation & Profiles.
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
    render_badge
)
from src.services.analytics import compare_two_segments

def render(data_bundle):
    render_header(
        title="Commercial Establishment Segmentation",
        subtitle="Discovered cluster behavioral baselines, side-by-side segment comparisons, and filtered establishment directory.",
        eyebrow="SEGMENT EXPLORER",
        breadcrumbs=["Platform", "Data & Segmentation", "Business Segmentation"]
    )

    prof_df = data_bundle.get('prof')
    biz_df = data_bundle.get('biz_filtered', data_bundle.get('biz'))

    if biz_df is None or prof_df is None:
        render_empty_state(
            title="Segmentation Results Not Loaded",
            message="Run the pipeline to generate clustered_businesses.csv and cluster_profiles.csv.",
            action_command="python scripts/run_pipeline.py --step cluster"
        )
        render_footer()
        return

    # Section 1: Empirical Cluster Behavioral Profiles
    render_section_header("Empirical Cluster Behavioral Profiles", subtitle="Derived statistical baselines for the 4 identified behavioral cohorts")
    st.dataframe(prof_df, use_container_width=True, hide_index=True)

    # Section 2: Compare Any Two Segments Side-by-Side
    render_section_header("Compare Segments", subtitle="Side-by-side metric differential analysis between any two segments")
    all_segments = sorted(biz_df['cluster_name'].dropna().unique().tolist())
    if len(all_segments) >= 2:
        c_a, c_b = st.columns(2)
        with c_a:
            seg_a = st.selectbox("Segment A:", all_segments, index=0, key="seg_cmp_a")
        with c_b:
            seg_b = st.selectbox("Segment B:", all_segments, index=min(1, len(all_segments)-1), key="seg_cmp_b")

        comparison_table = compare_two_segments(data_bundle.get('biz', biz_df), seg_a, seg_b)
        st.dataframe(comparison_table, use_container_width=True, hide_index=True)

    # Section 3: Filtered Establishment Directory
    render_section_header("Segmented Establishment Directory", subtitle="Query individual commercial establishments with assigned behavioral segment")
    display_cols = [
        'place', 'place type', 'city', 'cluster_name',
        'avg_rating', 'sample_review_count', 'positive_review_pct', 'negative_review_pct', 'address'
    ]
    avail_cols = [c for c in display_cols if c in biz_df.columns]

    render_paginated_table(
        df=biz_df[avail_cols],
        key_prefix="segmented_biz_table",
        page_size=15,
        download_filename="segmented_establishments.csv"
    )

    # Detail Expander for Sample Inspection
    with st.expander("Establishment Profile Inspector", expanded=False):
        if not biz_df.empty:
            sample_place = st.selectbox("Select establishment to inspect details:", biz_df['place'].head(30).tolist())
            row = biz_df[biz_df['place'] == sample_place].iloc[0]
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Category", str(row.get('place type', 'General')))
            d2.metric("Location", str(row.get('city', 'Unknown')))
            d3.metric("Customer Rating", f"{row.get('avg_rating', 0.0):.2f} ⭐")
            d4.metric("Assigned Segment", str(row.get('cluster_name', 'Unassigned')))
            st.caption(f"Physical Address: {row.get('address', 'N/A')}")

    render_footer()
