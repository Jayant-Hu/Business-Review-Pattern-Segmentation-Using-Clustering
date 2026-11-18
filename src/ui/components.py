"""
Reusable UI Components: Header, Metric Cards, Panels, Empty States.
"""
from typing import Optional
import streamlit as st

def render_header(title: str, subtitle: str, badge: str = "UNSUPERVISED ML INSIGHTS"):
    """Renders consistent SaaS top hero header."""
    st.markdown(f"""
        <div class="saas-header">
            <span class="saas-badge">{badge}</span>
            <h1 class="saas-title">{title}</h1>
            <p class="saas-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: Optional[str] = None):
    """Renders an individual glassmorphism metric stat card."""
    delta_html = f'<div class="metric-delta">✓ {delta}</div>' if delta else ''
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def render_empty_state(title: str, message: str, action_command: Optional[str] = "python scripts/run_pipeline.py"):
    """Displays a clean, informative empty-state banner when data files are missing."""
    cmd_html = f'<div style="margin-top:12px;"><code style="background:#1E293B; color:#60A5FA; padding:6px 14px; border-radius:6px;">{action_command}</code></div>' if action_command else ''
    st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">📂</div>
            <div class="empty-state-title">{title}</div>
            <div style="font-size:13px; max-width:500px; margin:0 auto;">{message}</div>
            {cmd_html}
        </div>
    """, unsafe_allow_html=True)
