"""
Customer Review Distribution & Frequency Analysis.
Examines star rating density, volume polarity, and industry sector proportions.
"""
import streamlit as st
import plotly.express as px
from src.ui.components import (
    render_header,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_paginated_table
)
from src.ui.theme import get_plotly_theme, COLOR_SILVER, COLOR_SILVER_SOFT

def render(data_bundle):
    render_header(
        title="Review Rating Distribution & Category Volume",
        subtitle="Empirical density of customer feedback scores and industry category allocations.",
        eyebrow="BEHAVIORAL SIGNALS",
        breadcrumbs=["Platform", "Data & Segmentation", "Review Analytics"]
    )

    rev_df = data_bundle.get('rev')
    if rev_df is None or rev_df.empty:
        render_empty_state(
            title="Review Transactions Not Found",
            message="Cleaned transaction dataset is required for review frequency analysis.",
            action_command="python scripts/run_pipeline.py --step clean"
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
            color_discrete_sequence=[COLOR_SILVER],
            text='Reviews'
        )
        fig_ratings.update_layout(**get_plotly_theme("dark"))
        fig_ratings.update_layout(xaxis_title="Star Rating (1 to 5)", yaxis_title="Review Count")
        pos_share = (rev_df['rating'] >= 4).mean() * 100.0
        render_chart_container(
            title="Rating Frequency Distribution",
            fig=fig_ratings,
            insight=f"{pos_share:.1f}% of reviews award 4 or 5 stars, while 1-star ratings represent the primary signal for critical intervention.",
            help_text="Frequency of ratings awarded across all sample transactions. Positive skew is common in commercial directories."
        )

    with col2:
        top_cats = rev_df['place type'].value_counts().head(10).reset_index()
        top_cats.columns = ['Category', 'Reviews']
        fig_cats = px.bar(
            top_cats,
            x='Reviews',
            y='Category',
            orientation='h',
            color_discrete_sequence=[COLOR_SILVER_SOFT]
        )
        fig_cats.update_layout(**get_plotly_theme("dark"))
        fig_cats.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="Total Reviews", yaxis_title="Category")
        top_cat_name = top_cats.iloc[0]['Category']
        render_chart_container(
            title="Top 10 Commercial Categories by Transaction Volume",
            fig=fig_cats,
            insight=f"'{top_cat_name}' generates the largest review volume ({top_cats.iloc[0]['Reviews']:,} reviews), dominating overall consumer engagement.",
            help_text="Commercial sectors generating the highest raw transaction volumes in regional corridors."
        )

    render_footer()
