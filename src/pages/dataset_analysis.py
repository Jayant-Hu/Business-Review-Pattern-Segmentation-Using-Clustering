"""
Page 2: Dataset Analysis.
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from src.ui.components import render_header, render_empty_state
from src.ui.theme import PLOTLY_DARK_THEME

def render(data_bundle):
    render_header(
        "Dataset Architecture & Integrity Analysis",
        "Inspection of raw schema, missing value patterns, and verified entity identification.",
        "DATA AUDITING"
    )

    rev_df = data_bundle['rev']
    biz_df = data_bundle['biz']

    if rev_df is None:
        render_empty_state("Cleaned Dataset Not Available", "Run data cleaning pipeline to generate cleaned_reviews.csv.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Sampled Reviews", f"{len(rev_df):,} Records", "Uniform Stratified")
    c2.metric("Verified Businesses", f"{len(biz_df):,} Entities" if biz_df is not None else "N/A", "place + address")
    c3.metric("Review Columns", f"{rev_df.shape[1]} Attributes", "Sanitized & Engineered")

    st.markdown("""
        <div class="saas-panel">
            <div class="panel-header">🔍 Critical Architectural Finding: Entity Resolution</div>
            <p style="color:#CBD5E1; font-size:13px; line-height:1.6;">
                A rigorous audit of the dataset confirmed that the column <code>Id</code> represents the <b>Reviewer Identifier</b>, 
                not the Business ID. Aggregating by <code>Id</code> would collapse hundreds of unique city shops into a single user's profile.
                To eliminate entity conflation, our pipeline engineered a composite business key: <code>(place, address)</code>.
            </p>
        </div>
    """, unsafe_allow_html=True)

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
        color_continuous_scale="Reds",
        title="Proportion of Null & '0' Placeholder Values Across Features (%)"
    )
    fig_missing.update_layout(**PLOTLY_DARK_THEME)
    fig_missing.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_missing, width="100%")
