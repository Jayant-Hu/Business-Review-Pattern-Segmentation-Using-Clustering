"""
Review Analytics & Rating Distribution Page.
Explores sentiment polarity, rating frequency, and category review volume.
"""
import streamlit as st
import plotly.express as px
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_section_header,
    render_paginated_table
)

def render(data_bundle):
    render_header(
        "Customer Review Distribution & Frequency",
        "Exploration of customer sentiment polarity, rating frequency, and industry place categories.",
        badge="BEHAVIORAL SIGNALS",
        breadcrumbs=["Platform", "Analyze", "Review Analytics"]
    )

    rev_df = data_bundle.get('rev')
    if rev_df is None or rev_df.empty:
        render_empty_state(
            "Reviews Not Loaded",
            "Processed review data not found.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    col1, col2 = st.columns(2)
    with col1:
        rating_counts = rev_df['rating'].value_counts().sort_index().reset_index()
        rating_counts.columns = ['Rating', 'Reviews']
        fig_ratings = px.bar(
            rating_counts,
            x='Rating',
            y='Reviews',
            color='Rating',
            color_continuous_scale='Blues',
            text='Reviews'
        )
        fig_ratings.update_layout(coloraxis_showscale=False)
        pos_share = (rev_df['rating'] >= 4).mean() * 100.0
        render_chart_container(
            "Customer Rating Distribution (1 to 5 Stars)",
            fig_ratings,
            insight=f"Ratings exhibit a strong positive skew: {pos_share:.1f}% of reviews award 4 or 5 stars, while 1-star ratings represent the primary signal for critical interventions.",
            help_text="Histogram of star ratings awarded across all sample reviews. Power-law positive skew is standard across Google Local platforms."
        )

    with col2:
        top_cats = rev_df['place type'].value_counts().head(10).reset_index()
        top_cats.columns = ['Category', 'Reviews']
        fig_cats = px.bar(
            top_cats,
            x='Reviews',
            y='Category',
            orientation='h',
            color='Reviews',
            color_continuous_scale='Viridis'
        )
        fig_cats.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        top_cat_name = top_cats.iloc[0]['Category']
        render_chart_container(
            "Top 10 Commercial Categories by Review Volume",
            fig_cats,
            insight=f"'{top_cat_name}' generates the largest review volume ({top_cats.iloc[0]['Reviews']:,} reviews), dominating overall consumer engagement.",
            help_text="Horizontal bar chart illustrating commercial sectors with the highest public review activity."
        )

    render_footer()
