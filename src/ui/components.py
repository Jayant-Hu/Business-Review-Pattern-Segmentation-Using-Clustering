"""
Reusable UI Components for Charcoal, Silver & Signal Red Interface.
Strictly adheres to editorial financial terminal aesthetics with zero emoji headings.
"""
from typing import Optional, List, Dict, Any
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.ui.theme import (
    SEGMENT_COLORS,
    OPPORTUNITY_BADGES,
    get_plotly_theme,
    COLOR_RED,
    COLOR_BORDER_DARK
)
from src.services.decision_advisor import HONESTY_DISCLAIMER

def render_header(
    title: str,
    subtitle: str,
    eyebrow: str = "ANALYTICAL REPORT",
    breadcrumbs: Optional[List[str]] = None
):
    """Renders editorial terminal header with uppercase eyebrow, serif title, and hairline rule."""
    b_html = ""
    if breadcrumbs:
        trail = " / ".join([f"<span class='current'>{b}</span>" if i == len(breadcrumbs)-1 else b for i, b in enumerate(breadcrumbs)])
        b_html = f'<div class="terminal-breadcrumbs">{trail}</div>'

    st.markdown(f"""
        <div class="terminal-header">
            {b_html}
            <div class="terminal-eyebrow">{eyebrow}</div>
            <h1 class="terminal-title">{title}</h1>
            <p class="terminal-subtitle">{subtitle}</p>
            <hr class="terminal-rule" />
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    tooltip: Optional[str] = None,
    is_signal: bool = False
):
    """Renders 1px bordered KPI card with monospace/tabular-nums value and subtle context line."""
    delta_class = "kpi-delta signal-alert" if (is_signal or not delta_positive) else "kpi-delta"
    marker = "● " if is_signal else ""
    delta_html = f'<div class="{delta_class}">{marker}{delta}</div>' if delta else ''
    tooltip_html = f'<div class="kpi-tooltip">{tooltip}</div>' if tooltip else ''

    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div>
                <div class="kpi-value">{value}</div>
                {delta_html}
                {tooltip_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: Optional[str] = None, eyebrow: Optional[str] = None):
    """Renders serif section divider without decorative icons."""
    eyebrow_html = f'<div class="terminal-eyebrow" style="margin-bottom:2px;">{eyebrow}</div>' if eyebrow else ''
    sub_html = f'<div style="font-size:12.5px; color:var(--text-secondary); margin-bottom:12px;">{subtitle}</div>' if subtitle else ''
    st.markdown(f"""
        <div style="margin-top:28px; margin-bottom:10px;">
            {eyebrow_html}
            <h2 style="font-size:18px; margin:0 0 4px 0;">{title}</h2>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

def render_info_callout(
    text: str,
    title: Optional[str] = None,
    callout_type: str = "info"
):
    """Renders thin left-bordered callout (silver for info, signal red for warning/alert)."""
    cls = "signal" if callout_type in ["warning", "alert"] else "muted" if callout_type == "muted" else ""
    title_html = f"<b>{title}:</b> " if title else ""
    st.markdown(f"""
        <div class="callout {cls}">
            {title_html}{text}
        </div>
    """, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "silver") -> str:
    """Returns HTML for clean editorial chip."""
    if badge_type in ["red", "signal", "Critical Intervention / At-Risk"]:
        return f'<span class="chip signal">{text}</span>'
    return f'<span class="chip">{text}</span>'

def render_empty_state(
    title: str,
    message: str,
    action_command: Optional[str] = "python scripts/run_pipeline.py"
):
    """Renders quiet, minimal placeholder when data or step artifacts are absent."""
    cmd_html = f'<div style="margin-top:14px;"><code style="background:var(--surface-2); border:1px solid var(--border); color:var(--silver); padding:6px 14px; border-radius:4px; font-family:var(--font-mono); font-size:11.5px;">{action_command}</code></div>' if action_command else ''
    st.markdown(f"""
        <div class="empty-card">
            <div class="empty-card-title">{title}</div>
            <div style="font-size:13px; max-width:500px; margin:0 auto; line-height:1.5;">{message}</div>
            {cmd_html}
        </div>
    """, unsafe_allow_html=True)

def render_gauge(
    value: float,
    max_value: float = 100.0,
    title: str = "Profit Potential Index",
    subtitle: str = ""
) -> go.Figure:
    """Constructs disciplined radial indicator using silver scale and signal red threshold."""
    val = min(max(float(value), 0.0), float(max_value))
    theme_mode = st.session_state.get('ui_theme', 'dark')

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><span style='font-size:10px; color:#7C838E;'>{subtitle}</span>", 'font': {'size': 13, 'family': 'Source Serif 4, serif'}},
        number={'font': {'family': 'IBM Plex Mono, monospace', 'size': 24, 'color': '#E6E9EE' if theme_mode == 'dark' else '#1B1E22'}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "#7C838E"},
            'bar': {'color': "#C9CED6", 'thickness': 0.24},
            'bgcolor': "rgba(38, 42, 47, 0.4)",
            'borderwidth': 1,
            'bordercolor': "#343941",
            'steps': [
                {'range': [0, 40], 'color': "rgba(229, 56, 59, 0.20)"},
                {'range': [40, 70], 'color': "rgba(142, 150, 163, 0.15)"},
                {'range': [70, max_value], 'color': "rgba(201, 206, 214, 0.25)"}
            ],
            'threshold': {
                'line': {'color': COLOR_RED, 'width': 2},
                'thickness': 0.8,
                'value': val
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="IBM Plex Sans, sans-serif"),
        height=220,
        margin=dict(l=20, r=20, t=36, b=16)
    )
    return fig

def render_chart_container(
    title: str,
    fig: go.Figure,
    insight: Optional[str] = None,
    help_text: Optional[str] = None
):
    """Framed chart component with serif title, help popover, and tabular insight."""
    theme_mode = st.session_state.get('ui_theme', 'dark')
    fig.update_layout(**get_plotly_theme(theme_mode))

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    c_head, c_help = st.columns([0.94, 0.06])
    with c_head:
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    with c_help:
        if help_text:
            with st.popover("i", use_container_width=True):
                st.markdown(f"**Interpretation Guide:**\n\n{help_text}")

    st.plotly_chart(fig, use_container_width=True)

    if insight:
        st.markdown(f"""
            <div class="chart-insight">
                <span class="prefix">Observation</span>
                <div>{insight}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def render_paginated_table(
    df: pd.DataFrame,
    key_prefix: str,
    page_size: int = 15,
    download_filename: str = "export.csv"
):
    """Renders table with surface-2 header, search filter, page selector, and CSV export."""
    if df is None or df.empty:
        st.info("No records matching current parameters.")
        return

    s_col, d_col = st.columns([0.8, 0.2])
    with s_col:
        search_term = st.text_input(
            "Filter rows",
            key=f"{key_prefix}_search",
            placeholder="Search records...",
            label_visibility="collapsed"
        )
    with d_col:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
            key=f"{key_prefix}_dl",
            use_container_width=True
        )

    display_df = df
    if search_term and search_term.strip():
        term = search_term.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(term, regex=False)).any(axis=1)
        display_df = display_df[mask]

    total_rows = len(display_df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)

    if total_pages > 1:
        p_c1, p_c2, p_c3 = st.columns([0.2, 0.6, 0.2])
        with p_c2:
            page_num = st.number_input(
                f"Page ({total_pages} total)",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"{key_prefix}_pg"
            )
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        page_df = display_df.iloc[start_idx:end_idx]
        st.caption(f"Showing rows {start_idx + 1}–{end_idx} of {total_rows:,}")
    else:
        page_df = display_df
        st.caption(f"Displaying {total_rows:,} records")

    st.dataframe(page_df, use_container_width=True)

def render_footer(last_run_timestamp: Optional[str] = "2026-11-26 01:00 UTC"):
    """Renders quiet, editorial terminal footer."""
    st.markdown(f"""
        <div class="terminal-footer">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <b>UrbanPulse Analytics</b> • Institutional Version 2.5
                </div>
                <div>
                    <span style="font-family:var(--font-mono); color:var(--silver-soft);">
                        Status: Operational ({last_run_timestamp})
                    </span>
                </div>
            </div>
            <div style="color:var(--text-muted); line-height:1.45;">
                {HONESTY_DISCLAIMER}
            </div>
            <div style="display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:10.5px; margin-top:2px;">
                <span>Source: Google Local Regional Corridor Sample (1.17M raw transactions)</span>
                <span>Unsupervised ML Core: Scikit-Learn K-Means (K=4), Ward Dendrogram, 2D PCA</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
