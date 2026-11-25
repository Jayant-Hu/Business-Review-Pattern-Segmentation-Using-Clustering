"""
Overview & Executive Intelligence Briefing.
Presents high-level metrics, cluster distribution, at-risk attention panel, and navigation shortcuts.
"""
import streamlit as st
import pandas as pd

from src.ui.components import (
    render_header,
    render_metric_card,
    render_empty_state,
    render_chart_container,
    render_footer,
    render_badge
)
from src.ui.charts import build_donut_chart
from src.services.analytics import compute_overall_metrics
from src.services.decision_advisor import compute_opportunity_leaderboard

def render(data_bundle):
    render_header(
        title="Commercial Review Pattern Intelligence",
        subtitle="Unsupervised pattern recognition and Bayesian market sizing across regional commercial corridors.",
        eyebrow="EXECUTIVE BRIEFING",
        breadcrumbs=["Platform", "Overview"]
    )

    biz_df = data_bundle.get('biz')
    rev_df = data_bundle.get('rev')
    eval_df = data_bundle.get('eval')
    prof_df = data_bundle.get('prof')
    stab_df = data_bundle.get('stab')

    if biz_df is None or prof_df is None:
        render_empty_state(
            title="Data Assets Not Loaded",
            message="Please execute the preprocessing and clustering pipeline to compute empirical artifacts.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    # Compute overall metrics
    metrics = compute_overall_metrics(biz_df, rev_df, eval_df, stab_df)
    top_tier = biz_df[biz_df['cluster_name'] == 'High-Satisfaction Top Tier']
    high_sat_pct = (len(top_tier) / len(biz_df) * 100.0) if len(biz_df) > 0 else 0.0
    at_risk = biz_df[biz_df['cluster_name'] == 'Critical Intervention / At-Risk']
    at_risk_count = len(at_risk)
    at_risk_pct = (at_risk_count / len(biz_df) * 100.0) if len(biz_df) > 0 else 0.0

    # 4 Key Quantitative Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Active Establishments", f"{metrics['total_businesses']:,}", "Verified composite key")
    with m2:
        render_metric_card("Empirical Reviews", f"{metrics['total_reviews']:,}", "Sanitized transaction sample")
    with m3:
        render_metric_card("High-Satisfaction Share", f"{high_sat_pct:.1f}%", f"{len(top_tier):,} top-tier venues")
    with m4:
        render_metric_card("At-Risk Establishments", f"{at_risk_count:,}", f"{at_risk_pct:.1f}% of total market", is_signal=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Signal Red Focus Panel: Needs Attention
    st.markdown("""
        <div class="terminal-panel" style="border-left: 3px solid var(--red); background: var(--surface-1);">
            <div class="panel-title-bar">
                <h3 class="panel-title" style="color:var(--text-primary);">Needs Attention: Critical Intervention Cohort</h3>
                <span class="chip signal">SIGNAL ALERT</span>
            </div>
            <div style="font-size:13px; color:var(--text-secondary); line-height:1.6; margin-bottom:14px;">
                <b>796 commercial entities (24.3% of audited sample)</b> exhibit elevated dissatisfaction profiles, averaging 
                <b>45.6% negative sentiment</b> (1-star and 2-star reviews) and high rating volatility. 
                These establishments reflect severe operational friction requiring targeted municipal service audits and staff training subsidies.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Segment Distribution Donut & Guidance
    col_donut, col_guide = st.columns([1.1, 0.9])
    with col_donut:
        fig_donut = build_donut_chart(prof_df)
        largest_seg = prof_df.sort_values(by='business_count', ascending=False).iloc[0]
        total_b = prof_df['business_count'].sum() if 'business_count' in prof_df.columns and prof_df['business_count'].sum() > 0 else 1
        share_pct = (largest_seg['business_count'] / total_b * 100.0) if 'business_count' in largest_seg else 0.0
        render_chart_container(
            title="Cluster Composition Across Commercial Establishments",
            fig=fig_donut,
            insight=f"{largest_seg.get('cluster_name', 'Top Tier')} comprises {int(largest_seg.get('business_count', 0)):,} establishments ({share_pct:.1f}% of total).",
            help_text="Proportional breakdown across the 4 discovered behavioral review clusters."
        )

    with col_guide:
        st.markdown("""
            <div class="terminal-panel">
                <div class="panel-title-bar">
                    <h3 class="panel-title">How to Read this Dashboard</h3>
                </div>
                <div style="display:flex; flex-direction:column; gap:14px; font-size:13px; line-height:1.5;">
                    <div>
                        <b style="color:var(--text-primary); font-family:var(--font-mono);">01. Explore Directory</b><br>
                        <span style="color:var(--text-secondary);">Query individual commercial venues in the Directory to examine behavioral nearest neighbors in the 10-dimensional space.</span>
                    </div>
                    <div>
                        <b style="color:var(--text-primary); font-family:var(--font-mono);">02. Decision Engine</b><br>
                        <span style="color:var(--text-secondary);">Filter regional corridors by category and confidence to isolate market gaps using the empirical Profit Potential Index (PPI).</span>
                    </div>
                    <div>
                        <b style="color:var(--text-primary); font-family:var(--font-mono);">03. Model Rigor</b><br>
                        <span style="color:var(--text-secondary);">Validate K=4 hyperparameter selection through WCSS inertia inflection, silhouette cohesion, and seed stability (99.86% ARI).</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Quick Start Action Bar
    q_col1, q_col2 = st.columns([0.75, 0.25])
    with q_col1:
        st.markdown("""
            <div style="background:var(--surface-1); border:1px solid var(--border); border-radius:6px; padding:14px 18px;">
                <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--silver-soft); text-transform:uppercase;">Analysis Shortcut</div>
                <div style="font-family:var(--font-serif); font-size:15px; font-weight:600; color:var(--text-primary); margin-top:2px;">Launch Commercial Location Advisor</div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">Evaluate market opening scores, nearest competitors, and break-even customer volume for any commercial category.</div>
            </div>
        """, unsafe_allow_html=True)
    with q_col2:
        st.write("")
        if st.button("Open Decision Advisor", key="btn_open_advisor", use_container_width=True, type="primary"):
            st.session_state['current_page'] = "Business Decision Advisor"
            st.rerun()

    render_footer()
