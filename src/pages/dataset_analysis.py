"""
Dataset Integrity & Schema Analysis Page.
Audits raw distributions, null/zero placeholder patterns, and composite key entity resolution.
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

def render(data_bundle):
    render_header(
        "Dataset Architecture & Integrity Analysis",
        "Inspection of raw schema, missing value patterns, and verified entity identification.",
        badge="DATA AUDITING",
        breadcrumbs=["Platform", "Analyze", "Dataset Analysis"]
    )

    rev_df = data_bundle.get('rev')
    biz_df = data_bundle.get('biz_filtered', data_bundle.get('biz'))

    if rev_df is None or rev_df.empty:
        render_empty_state(
            "Cleaned Dataset Not Available",
            "Run data cleaning pipeline to generate cleaned_reviews.csv.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Sampled Reviews", f"{len(rev_df):,}", "Uniform Stratified Sample", icon="📑")
    with c2:
        render_metric_card("Verified Businesses", f"{len(biz_df):,}" if biz_df is not None else "N/A", "place + address", icon="🏢")
    with c3:
        render_metric_card("Review Attributes", f"{rev_df.shape[1]} Columns", "Sanitized & Engineered", icon="📊")

    render_info_callout(
        "A rigorous audit confirmed that the column 'Id' represents the Reviewer Account Identifier, not the business entity. "
        "Aggregating by 'Id' would collapse distinct establishments across cities into single profiles. "
        "The pipeline resolves this by engineering a deterministic composite key: MD5(place + address).",
        title="Entity Resolution Finding",
        callout_type="info"
    )

    # Missing & Placeholder Value Bar Chart
    placeholder_counts = {}
    for col in rev_df.columns:
        p_count = ((rev_df[col] == 0) | (rev_df[col] == '0') | (rev_df[col].isnull())).sum()
        pct = (p_count / len(rev_df)) * 100.0
        if pct > 0.05:
            placeholder_counts[col] = round(pct, 2)

    placeholder_df = pd.DataFrame(list(placeholder_counts.items()), columns=['Feature', 'Missing / Placeholder %'])
    placeholder_df = placeholder_df.sort_values(by='Missing / Placeholder %', ascending=True)

    fig_missing = px.bar(
        placeholder_df,
        x="Missing / Placeholder %",
        y="Feature",
        orientation="h",
        color="Missing / Placeholder %",
        color_continuous_scale="Reds"
    )
    fig_missing.update_layout(coloraxis_showscale=False)

    render_chart_container(
        "Proportion of Null & '0' Placeholder Values Across Features (%)",
        fig_missing,
        insight=f"Specific aspect ratings ({', '.join(placeholder_df.tail(3)['Feature'].tolist())}) feature the highest sparsity, requiring dedicated feedback-rate features rather than imputing missing scores.",
        help_text="Evaluates data completeness. Zeroes in specific columns like food, service, or atmosphere represent unprovided feedback rather than negative experiences."
    )

    render_section_header("Review Sample Dataset Preview")
    preview_cols = ['place', 'place type', 'rating', 'User_name', 'en review', 'city']
    avail = [c for c in preview_cols if c in rev_df.columns]
    render_paginated_table(
        rev_df[avail],
        key_prefix="rev_data_preview",
        page_size=10,
        download_filename="raw_review_sample.csv"
    )

    render_footer()
