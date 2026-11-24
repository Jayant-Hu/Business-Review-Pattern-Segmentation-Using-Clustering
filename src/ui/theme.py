"""
Standard Plotly Theme Configurations for Dark and Light Modes.
"""
from typing import Dict, Any

PLOTLY_DARK_THEME: Dict[str, Any] = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)', color="#94A3B8"),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)', color="#94A3B8"),
    legend=dict(font=dict(color="#CBD5E1")),
    colorway=["#10B981", "#3B82F6", "#8B5CF6", "#EF4444", "#F59E0B", "#EC4899"]
)

PLOTLY_LIGHT_THEME: Dict[str, Any] = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='rgba(15,23,42,0.08)', zerolinecolor='rgba(15,23,42,0.15)', color="#475569"),
    yaxis=dict(gridcolor='rgba(15,23,42,0.08)', zerolinecolor='rgba(15,23,42,0.15)', color="#475569"),
    legend=dict(font=dict(color="#334155")),
    colorway=["#059669", "#2563EB", "#7C3AED", "#DC2626", "#D97706", "#DB2777"]
)

def get_plotly_theme(theme_mode: str = "dark") -> Dict[str, Any]:
    """Returns the Plotly layout configuration for the active theme."""
    return PLOTLY_DARK_THEME if theme_mode == "dark" else PLOTLY_LIGHT_THEME
