"""
Dataset Integrity & Schema Analysis.
Audits completeness, missingness, and verified composite entity resolution.
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from src.ui.components import (
    render_header,
    render_empty_state,
    render_metric_card,
    render_chart_container,
    render_footer,
    render_info_callout,
    render_paginated_table,
    render_section_header
)
from src.ui.theme import get_plotly_theme, COLOR_SILVER_SOFT

def render(data_bundle):
    render_header(
        title="Dataset Architecture & Data Integrity",
        subtitle="Inspection of schema completeness, attribute sparsity, and verified establishment identification.",
        eyebrow="DATA AUDITING",
        breadcrumbs=["Platform", "Data & Segmentation", "Dataset Analysis"]
    )

    rev_df = data_bundle.get('rev')
    biz_df = data_bundle.get('biz_filtered', data_bundle.get('biz'))

    if rev_df is None or rev_df.empty:
        render_empty_state(
            title="Cleaned Transaction Dataset Absent",
            message="Please execute data cleaning pipeline to generate cleaned_reviews.csv.",
            action_command="python scripts/run_pipeline.py --step clean"
        )
        render_footer()
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Sampled Review Transactions", f"{len(rev_df):,}", "Uniform Stratified Sample")
    with c2:
        render_metric_card("Distinct Commercial Entities", f"{len(biz_df):,}" if biz_df is not None else "N/A", "Aggregated by (place, address)")
    with c3:
        render_metric_card("Attribute Dimensions", f"{rev_df.shape[1]} Columns", "Engineered and validated")

    render_info_callout(
        title="Composite Key Resolution",
        text="Auditing confirmed that the raw attribute 'Id' represents the Reviewer Account Identifier rather than a venue ID. "
             "Aggregating by 'Id' directly conflates multiple distinct city storefronts visited by the same user into a single profile. "
             "To enforce proper entity isolation, the pipeline synthesizes a deterministic primary composite key: MD5(place + address).",
        callout_type="info"
    )

    # Missing & Placeholder Value Bar Chart
    placeholder_counts = {}
    for col in rev_df.columns:
        p_count = ((rev_df[col] == 0) | (rev_df[col] == '0') | (rev_df[col].isnull())).sum()
        pct = (p_count / len(rev_df)) * 100.0
        if pct > 0.05:
            placeholder_counts[col] = round(pct, 2)

    placeholder_df = pd.DataFrame(list(placeholder_counts.items()), columns=['Feature', 'Missing_Pct'])
    placeholder_df = placeholder_df.sort_values(by='Missing_Pct', ascending=True)

    fig_missing = px.bar(
        placeholder_df,
        x="Missing_Pct",
        y="Feature",
        orientation="h",
        color_discrete_sequence=[COLOR_SILVER_SOFT]
    )
    fig_missing.update_layout(**get_plotly_theme("dark"))
    fig_missing.update_layout(xaxis_title="Missing / Zero Proportion (%)", yaxis_title="Dataset Attribute")

    render_chart_container(
        title="Attribute Sparsity & Missing Value Distribution",
        fig=fig_missing,
        insight=f"Aspect ratings ({', '.join(placeholder_df.tail(3)['Feature'].tolist())}) feature the highest sparsity, requiring dedicated feedback-rate features rather than arbitrary imputation.",
        help_text="Evaluates data completeness. Zeroes in specific columns like food, service, or atmosphere represent unprovided feedback rather than negative experiences."
    )

    render_section_header("Audited Review Sample Data View")
    preview_cols = ['place', 'place type', 'rating', 'User_name', 'en review', 'city']
    avail = [c for c in preview_cols if c in rev_df.columns]
    render_paginated_table(
        df=rev_df[avail],
        key_prefix="rev_data_view",
        page_size=10,
        download_filename="audited_review_sample.csv"
    )

    render_footer()
