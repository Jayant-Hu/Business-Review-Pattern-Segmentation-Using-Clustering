"""
Plotly Chart Builders for Cluster Metrics, Distributions, and Projections.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.ui.theme import PLOTLY_DARK_THEME
from src.ui.styles import SEGMENT_COLORS

def build_donut_chart(profiles_df: pd.DataFrame) -> go.Figure:
    """Builds interactive cluster distribution donut chart."""
    colors = [SEGMENT_COLORS.get(name, '#3B82F6') for name in profiles_df['cluster_name']]
    fig = px.pie(
        profiles_df,
        names='cluster_name',
        values='business_count',
        hole=0.62,
        color='cluster_name',
        color_discrete_map=SEGMENT_COLORS
    )
    fig.update_layout(**PLOTLY_DARK_THEME)
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
    return fig

def build_elbow_chart(eval_df: pd.DataFrame, selected_k: int = 4) -> go.Figure:
    """Builds WCSS inertia elbow curve."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['WCSS'],
        mode='lines+markers',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=9, color='#60A5FA')
    ))
    fig.add_vline(x=selected_k, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text=f"Selected K={selected_k}")
    fig.update_layout(**PLOTLY_DARK_THEME)
    fig.update_layout(xaxis_title="Number of Clusters (K)", yaxis_title="WCSS (Inertia)")
    return fig

def build_silhouette_comparison_chart(eval_df: pd.DataFrame) -> go.Figure:
    """Builds Euclidean vs. Manhattan silhouette score comparison chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['Silhouette_Euclidean'],
        mode='lines+markers',
        name='Euclidean Distance',
        line=dict(color='#10B981', width=2.5),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=eval_df['k'],
        y=eval_df['Silhouette_Manhattan'],
        mode='lines+markers',
        name='Manhattan Distance',
        line=dict(color='#F59E0B', width=2.5, dash='dash'),
        marker=dict(size=8)
    ))
    fig.update_layout(**PLOTLY_DARK_THEME)
    fig.update_layout(xaxis_title="Number of Clusters (K)", yaxis_title="Silhouette Score")
    return fig

def build_pca_scatter(merged_pca: pd.DataFrame) -> go.Figure:
    """Builds interactive WebGL 2D PCA scatter plot."""
    fig = px.scatter(
        merged_pca,
        x='PCA1',
        y='PCA2',
        color='cluster_name',
        color_discrete_map=SEGMENT_COLORS,
        hover_name='place',
        hover_data=['avg_rating', 'sample_review_count'],
        opacity=0.75,
        render_mode='webgl'  # optimized high-speed rendering
    )
    fig.update_layout(**PLOTLY_DARK_THEME)
    fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color='rgba(255,255,255,0.2)')))
    return fig
