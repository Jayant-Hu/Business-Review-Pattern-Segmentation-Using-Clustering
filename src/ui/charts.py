"""
Plotly Chart Builders in Charcoal, Silver & Signal Red Palette.
Uses restrained visual hierarchy, hairline gridlines, and tabular numerals.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.ui.theme import (
    SEGMENT_COLORS,
    COLOR_RED,
    COLOR_SILVER,
    COLOR_SILVER_SOFT,
    COLOR_BORDER_DARK,
    get_plotly_theme
)

def build_donut_chart(profiles_df: pd.DataFrame) -> go.Figure:
    """Builds clean cluster proportion donut chart."""
    fig = px.pie(
        profiles_df,
        names='cluster_name',
        values='business_count',
        hole=0.68,
        color='cluster_name',
        color_discrete_map=SEGMENT_COLORS
    )
    fig.update_layout(**get_plotly_theme("dark"))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center")
    )
    fig.update_traces(
        marker=dict(line=dict(color=COLOR_BORDER_DARK, width=1)),
        textinfo='percent',
        textfont=dict(family="IBM Plex Mono, monospace", size=11)
    )
    return fig

def build_elbow_chart(eval_df: pd.DataFrame, selected_k: int = 4) -> go.Figure:
    """Builds WCSS inertia trajectory chart with signal red marker on selected K."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['WCSS'],
        mode='lines+markers',
        line=dict(color=COLOR_SILVER, width=2),
        marker=dict(size=7, color=COLOR_SILVER_SOFT, line=dict(width=1, color=COLOR_BORDER_DARK)),
        name='Inertia (WCSS)'
    ))
    fig.add_vline(
        x=selected_k,
        line_width=1.5,
        line_dash="dot",
        line_color=COLOR_RED,
        annotation_text=f"Selected K={selected_k}",
        annotation_position="top right",
        annotation_font=dict(color=COLOR_RED, size=11, family="IBM Plex Mono")
    )
    fig.update_layout(**get_plotly_theme("dark"))
    fig.update_layout(xaxis_title="Cluster Count (K)", yaxis_title="Within-Cluster Sum of Squares")
    return fig

def build_silhouette_comparison_chart(eval_df: pd.DataFrame) -> go.Figure:
    """Builds Euclidean vs. Manhattan silhouette comparison chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['Silhouette_Euclidean'],
        mode='lines+markers',
        name='Euclidean Distance',
        line=dict(color=COLOR_SILVER, width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['Silhouette_Manhattan'],
        mode='lines+markers',
        name='Manhattan Distance',
        line=dict(color=COLOR_SILVER_SOFT, width=1.5, dash='dash'),
        marker=dict(size=6)
    ))
    fig.update_layout(**get_plotly_theme("dark"))
    fig.update_layout(xaxis_title="Cluster Count (K)", yaxis_title="Silhouette Score")
    return fig

def build_pca_scatter(merged_pca: pd.DataFrame) -> go.Figure:
    """Builds high-performance WebGL 2D PCA projection scatter plot."""
    fig = px.scatter(
        merged_pca,
        x='PCA1',
        y='PCA2',
        color='cluster_name',
        color_discrete_map=SEGMENT_COLORS,
        hover_name='place',
        hover_data=['avg_rating', 'sample_review_count'],
        opacity=0.82,
        render_mode='webgl'
    )
    fig.update_layout(**get_plotly_theme("dark"))
    fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color='rgba(0,0,0,0.4)')))
    fig.update_layout(xaxis_title="Principal Component 1", yaxis_title="Principal Component 2")
    return fig
