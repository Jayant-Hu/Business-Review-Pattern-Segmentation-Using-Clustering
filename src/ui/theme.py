"""
Standard Plotly Dark Theme Configurations.
"""
from typing import Dict, Any

PLOTLY_DARK_THEME: Dict[str, Any] = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    legend=dict(font=dict(color="#CBD5E1")),
    colorway=["#10B981", "#3B82F6", "#8B5CF6", "#EF4444", "#F59E0B", "#EC4899"]
)
