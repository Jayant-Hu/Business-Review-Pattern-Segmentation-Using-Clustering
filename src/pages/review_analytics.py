"""
Page 3: Review Analytics.
"""
import streamlit as st
import plotly.express as px
from src.ui.components import render_header, render_empty_state
from src.ui.theme import PLOTLY_DARK_THEME

def render(data_bundle):
    render_header(
        "Customer Review Distribution & Frequency",
        "Exploration of customer sentiment polarity, rating frequency, and industry place categories.",
        "BEHAVIORAL SIGNALS"
    )

    rev_df = data_bundle['rev']
    if rev_df is None:
        render_empty_state("Reviews Not Loaded", "Processed review data not found.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="saas-panel"><div class="panel-header">⭐ Customer Rating Distribution</div>', unsafe_allow_html=True)
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
        fig_ratings.update_layout(**PLOTLY_DARK_THEME)
        fig_ratings.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_ratings, width="100%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="saas-panel"><div class="panel-header">🏬 Top 10 Commercial Categories</div>', unsafe_allow_html=True)
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
        fig_cats.update_layout(**PLOTLY_DARK_THEME)
        fig_cats.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_cats, width="100%")
        st.markdown('</div>', unsafe_allow_html=True)
