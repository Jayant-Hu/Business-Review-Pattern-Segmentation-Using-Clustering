"""
Reusable UI Components: Headers, Metric Cards, Panels, Gauges, Tables, and Footers.
Adheres strictly to the centralized design system without scattered inline styles.
"""
from typing import Optional, List, Dict, Any
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.ui.styles import SEGMENT_COLORS, OPPORTUNITY_BADGES
from src.ui.theme import get_plotly_theme
from src.services.decision_advisor import HONESTY_DISCLAIMER

def render_header(
    title: str,
    subtitle: str,
    badge: str = "UNSUPERVISED ML INSIGHTS",
    breadcrumbs: Optional[List[str]] = None
):
    """Renders consistent SaaS top hero header with optional breadcrumb navigation."""
    b_html = ""
    if breadcrumbs:
        trail = " / ".join([f"<span class='current'>{b}</span>" if i == len(breadcrumbs)-1 else b for i, b in enumerate(breadcrumbs)])
        b_html = f'<div class="breadcrumbs">{trail}</div>'

    st.markdown(f"""
        <div class="saas-header">
            {b_html}
            <span class="saas-badge">{badge}</span>
            <h1 class="saas-title">{title}</h1>
            <p class="saas-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    tooltip: Optional[str] = None,
    icon: Optional[str] = None
):
    """Renders a glassmorphism metric stat card with delta, tooltip, and icon."""
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ''
    delta_class = "metric-delta" if delta_positive else "metric-delta negative"
    delta_arrow = "▲" if delta_positive else "▼"
    delta_html = f'<div class="{delta_class}">{delta_arrow} {delta}</div>' if delta else ''
    tooltip_html = f'<div class="metric-tooltip">{tooltip}</div>' if tooltip else ''

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-top">
                <div class="metric-label">{label}</div>
                {icon_html}
            </div>
            <div>
                <div class="metric-value">{value}</div>
                {delta_html}
                {tooltip_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: Optional[str] = None, badge: Optional[str] = None):
    """Renders clean section dividers with typography and optional category badge."""
    badge_html = f'<span class="saas-badge" style="margin-bottom:4px; font-size:10px;">{badge}</span><br>' if badge else ''
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(f"""
        <div style="margin-top:24px; margin-bottom:8px;">
            {badge_html}
            <div class="section-title">{title}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

def render_info_callout(
    text: str,
    title: str = "Key Observation",
    callout_type: str = "info"
):
    """Displays structured callout box (info, warning, success, alert)."""
    st.markdown(f"""
        <div class="info-callout {callout_type}">
            <b>{title}:</b> {text}
        </div>
    """, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "blue") -> str:
    """Returns HTML for inline styled badge chips."""
    color_map = {
        "blue": ("rgba(59, 130, 246, 0.15)", "#3B82F6"),
        "green": ("rgba(16, 185, 129, 0.15)", "#10B981"),
        "amber": ("rgba(245, 158, 11, 0.15)", "#F59E0B"),
        "red": ("rgba(239, 68, 68, 0.15)", "#EF4444"),
        "purple": ("rgba(139, 92, 246, 0.15)", "#8B5CF6")
    }
    bg, fg = color_map.get(badge_type, color_map["blue"])
    return f'<span style="background:{bg}; color:{fg}; padding:3px 9px; border-radius:12px; font-weight:600; font-size:11px; border:1px solid {fg}40;">{text}</span>'

def render_empty_state(
    title: str,
    message: str,
    action_command: Optional[str] = "python scripts/run_pipeline.py"
):
    """Displays clean empty-state placeholder when missing pipeline artifacts."""
    cmd_html = f'<div style="margin-top:14px;"><code style="background:#1E293B; color:#60A5FA; padding:8px 16px; border-radius:8px; font-size:12px;">{action_command}</code></div>' if action_command else ''
    st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">⚡</div>
            <div class="empty-state-title">{title}</div>
            <div style="font-size:13.5px; max-width:540px; margin:0 auto; line-height:1.5;">{message}</div>
            {cmd_html}
        </div>
    """, unsafe_allow_html=True)

def render_gauge(
    value: float,
    max_value: float = 100.0,
    title: str = "Profit Potential Index",
    subtitle: str = ""
) -> go.Figure:
    """Creates Plotly radial gauge indicator."""
    val = min(max(float(value), 0.0), float(max_value))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><span style='font-size:10px; color:#94A3B8;'>{subtitle}</span>", 'font': {'size': 14, 'color': '#F8FAFC'}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': "#3B82F6", 'thickness': 0.28},
            'bgcolor': "rgba(30, 41, 59, 0.4)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.25)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.25)"},
                {'range': [70, max_value], 'color': "rgba(16, 185, 129, 0.25)"}
            ],
            'threshold': {
                'line': {'color': "#10B981", 'width': 3},
                'thickness': 0.8,
                'value': val
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
        height=240,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def render_chart_container(
    title: str,
    fig: go.Figure,
    insight: Optional[str] = None,
    help_text: Optional[str] = None
):
    """
    Renders standard chart card with header, help popover explaining how to read the chart,
    and automated data-driven insight callout.
    """
    theme_mode = st.session_state.get('ui_theme', 'dark')
    fig.update_layout(**get_plotly_theme(theme_mode))

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    c_head, c_help = st.columns([0.92, 0.08])
    with c_head:
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    with c_help:
        if help_text:
            with st.popover("ℹ️", use_container_width=True):
                st.markdown(f"**How to read this chart:**\n\n{help_text}")

    st.plotly_chart(fig, use_container_width=True)

    if insight:
        st.markdown(f"""
            <div class="chart-insight">
                <span>💡</span>
                <div><b>Data Observation:</b> {insight}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_paginated_table(
    df: pd.DataFrame,
    key_prefix: str,
    page_size: int = 15,
    download_filename: str = "table_export.csv"
):
    """Renders interactive sortable table with client-side pagination, search, and CSV export."""
    if df is None or df.empty:
        st.info("No records to display.")
        return

    # Search filter input
    s_col, d_col = st.columns([0.75, 0.25])
    with s_col:
        search_term = st.text_input(
            "Filter table rows...",
            key=f"{key_prefix}_search",
            placeholder="Type text to search rows...",
            label_visibility="collapsed"
        )
    with d_col:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
            key=f"{key_prefix}_download",
            use_container_width=True
        )

    # Filter by text search
    display_df = df
    if search_term and search_term.strip():
        term = search_term.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(term, regex=False)).any(axis=1)
        display_df = display_df[mask]

    total_rows = len(display_df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)

    # Page navigation controls
    if total_pages > 1:
        p_col1, p_col2, p_col3 = st.columns([0.2, 0.6, 0.2])
        with p_col2:
            page_num = st.number_input(
                f"Page (Total: {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"{key_prefix}_page"
            )
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        page_df = display_df.iloc[start_idx:end_idx]
        st.caption(f"Showing rows {start_idx + 1} to {end_idx} of {total_rows:,} matches")
    else:
        page_df = display_df
        st.caption(f"Displaying {total_rows:,} records")

    st.dataframe(page_df, use_container_width=True)

def render_onboarding_guide():
    """Renders dismissible first-run guided onboarding banner on Home page."""
    if st.session_state.get('dismiss_onboarding', False):
        return

    st.markdown("""
        <div class="onboarding-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span class="saas-badge" style="background:rgba(59,130,246,0.25); color:#93C5FD;">🚀 Quick Start Guide</span>
                    <h3 style="color:#F8FAFC; margin:4px 0 8px 0; font-size:16px;">Welcome to UrbanPulse AI</h3>
                    <p style="color:#CBD5E1; font-size:12.5px; margin:0; line-height:1.5;">
                        This platform analyzes customer review sentiment, engagement depth, and spatial demand patterns across GCC commercial corridors using unsupervised machine learning.
                    </p>
                    <div style="display:flex; gap:16px; margin-top:12px; font-size:12px; color:#94A3B8;">
                        <div><b>1. Explore</b>: Search businesses & view spatial density on the Map.</div>
                        <div><b>2. Decide</b>: Run the 3-step Business Advisor wizard to uncover top gaps.</div>
                        <div><b>3. Verify</b>: Review K-Means clustering, PCA loadings, and Methodology.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("✕ Dismiss Quick Start Banner", key="btn_dismiss_onboard"):
        st.session_state['dismiss_onboarding'] = True
        st.rerun()

def render_footer(last_run_timestamp: Optional[str] = "2026-11-24 15:30 UTC"):
    """Renders standardized corporate footer with metadata, disclaimer, and version info."""
    st.markdown(f"""
        <div class="saas-footer">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <b>UrbanPulse AI Platform v2.4.0</b> • Production Cluster Architecture
                </div>
                <div>
                    <span style="background:rgba(16, 185, 129, 0.15); color:#10B981; padding:3px 8px; border-radius:10px; font-weight:600; font-size:11px;">
                        ● Pipeline Status: Active ({last_run_timestamp})
                    </span>
                </div>
            </div>
            <div style="font-size:11px; color:#64748B; line-height:1.4;">
                <b>Legal & Financial Disclaimer:</b> {HONESTY_DISCLAIMER}
            </div>
            <div style="display:flex; justify-content:space-between; color:#475569; font-size:10.5px; margin-top:4px;">
                <span>Data Source: Google Local GCC Empirical Sample (~1.17M raw records)</span>
                <span>Clustering: Scikit-Learn K-Means (K=4), Agglomerative Ward, PCA</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
