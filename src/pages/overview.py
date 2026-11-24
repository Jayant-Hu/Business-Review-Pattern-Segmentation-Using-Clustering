"""
Home & Executive Overview Page.
Provides:
- Hero section and live computed system KPIs
- Dismissible onboarding guide
- Quick-start action card ("Find the best business for my area")
- Top 5 market opportunities right now (live PPI)
- Most at-risk commercial cohorts
- Segment distribution donut chart with automated insight
- Standardized footer with data freshness
"""
import streamlit as st
import pandas as pd

from src.ui.components import (
    render_header,
    render_metric_card,
    render_empty_state,
    render_chart_container,
    render_onboarding_guide,
    render_footer,
    render_badge
)
from src.ui.charts import build_donut_chart
from src.services.analytics import compute_overall_metrics
from src.services.decision_advisor import compute_opportunity_leaderboard, OPPORTUNITY_DEFINITIONS

def render(data_bundle):
    render_header(
        "Commercial Intelligence & Review Segmentation",
        "Unsupervised behavioral clustering, Bayesian opportunity scoring, and commercial gap discovery across GCC corridors.",
        badge="EXECUTIVE BRIEFING",
        breadcrumbs=["Platform", "Home & Overview"]
    )

    # First-run onboarding banner
    render_onboarding_guide()

    biz_df = data_bundle.get('biz')
    rev_df = data_bundle.get('rev')
    eval_df = data_bundle.get('eval')
    prof_df = data_bundle.get('prof')
    stab_df = data_bundle.get('stab')

    if biz_df is None or prof_df is None:
        render_empty_state(
            "Clustering Data Not Loaded",
            "Please run the preprocessing and clustering pipeline to compute real metrics.",
            action_command="python scripts/run_pipeline.py"
        )
        render_footer()
        return

    # Compute dynamic metrics from data
    metrics = compute_overall_metrics(biz_df, rev_df, eval_df, stab_df)

    # Calculate additional live metrics
    geo_count = int(biz_df['latitude'].notnull().sum()) if 'latitude' in biz_df.columns else 0
    top_tier = biz_df[biz_df['cluster_name'] == 'High-Satisfaction Top Tier']
    high_sat_pct = (len(top_tier) / len(biz_df) * 100.0) if len(biz_df) > 0 else 0.0
    at_risk = biz_df[biz_df['cluster_name'] == 'Critical Intervention / At-Risk']
    at_risk_count = len(at_risk)
    at_risk_pct = (at_risk_count / len(biz_df) * 100.0) if len(biz_df) > 0 else 0.0

    # 6 Dynamic SaaS Metric Cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        render_metric_card("Active Businesses", f"{metrics['total_businesses']:,}", "Verified composite key", icon="🏢")
    with m2:
        render_metric_card("Empirical Reviews", f"{metrics['total_reviews']:,}", "Sanitized & Deduplicated", icon="💬")
    with m3:
        render_metric_card("High Satisfaction", f"{high_sat_pct:.1f}%", f"{len(top_tier):,} top-tier venues", icon="⭐")
    with m4:
        render_metric_card("At-Risk Share", f"{at_risk_pct:.1f}%", f"{at_risk_count} venues need focus", delta_positive=False, icon="⚠️")
    with m5:
        render_metric_card("Geocoded Density", f"{geo_count:,}", f"{(geo_count/len(biz_df)*100):.1f}% coordinates", icon="📍")
    with m6:
        render_metric_card("Cluster Stability", f"{metrics['mean_ari_pct']}%", "ARI across 5 seeds", icon="🛡️")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Start Action Card
    qs_col1, qs_col2 = st.columns([0.72, 0.28])
    with qs_col1:
        st.markdown("""
            <div style="background:linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%); border:1px solid rgba(59, 130, 246, 0.35); border-radius:14px; padding:18px 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="background:rgba(59,130,246,0.2); color:#60A5FA; padding:3px 8px; border-radius:8px; font-weight:700; font-size:11px;">DECISION SHORTCUT</span>
                    <span style="color:#94A3B8; font-size:12px;">• Ready to discover market gaps?</span>
                </div>
                <div style="font-size:16px; font-weight:800; color:#F8FAFC;">Find the Highest-Potential Business for Your Area</div>
                <div style="font-size:12.5px; color:#94A3B8; margin-top:4px;">
                    Filter by city, tune competition sensitivity, and receive ranked categories with Bayesian demand scores and competitor maps.
                </div>
            </div>
        """, unsafe_allow_html=True)
    with qs_col2:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Launch Decision Advisor", key="btn_quickstart_advisor", use_container_width=True):
            st.session_state['current_page'] = "Business Decision Advisor"
            st.rerun()
        if st.button("🔍 Search Commercial Directory", key="btn_quickstart_search", use_container_width=True):
            st.session_state['current_page'] = "Business Detail & Search"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Intelligence: Top 5 Opportunities & Most At-Risk
    col_opp, col_risk = st.columns([1.1, 0.9])
    with col_opp:
        st.markdown('<div class="saas-panel"><div class="panel-header">🎯 Top 5 Market Opportunities Right Now</div>', unsafe_allow_html=True)
        st.caption("Ranked by empirical Profit Potential Index (PPI) using Bayesian shrinkage & demand velocity.")
        
        # Calculate real leaderboard
        leaderboard = compute_opportunity_leaderboard(biz_df, min_businesses=2)
        if not leaderboard.empty:
            top_5 = leaderboard.head(5)
            for _, row in top_5.iterrows():
                badge_type = "green" if row['opportunity_type'] == "Proven Market" else "blue" if row['opportunity_type'] == "Underserved Gap" else "amber"
                b_html = render_badge(row['opportunity_type'], badge_type)
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; background:rgba(255,255,255,0.02); border-bottom:1px solid rgba(255,255,255,0.05); border-radius:8px; margin-bottom:6px;">
                        <div>
                            <div style="font-weight:700; font-size:13px; color:#F8FAFC;">{row['category']} <span style="font-size:11px; color:#64748B;">in {row['city']}</span></div>
                            <div style="font-size:11px; color:#94A3B8;">{row['business_count']} venues • Avg {row['avg_rating']:.2f} ⭐ ({row['shrunk_rating']:.2f} Bayesian)</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:800; font-size:15px; color:#3B82F6;">{row['ppi_score']:.1f} <span style="font-size:10px; color:#64748B;">PPI</span></div>
                            <div>{b_html}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Insufficient volume to compute leaderboard.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_risk:
        st.markdown('<div class="saas-panel"><div class="panel-header">⚠️ High-Intervention Commercial Cohorts</div>', unsafe_allow_html=True)
        st.caption("City sectors with elevated negative feedback share requiring targeted intervention.")

        # Identify areas with highest negative feedback rate
        risk_areas = (
            biz_df.groupby(['city', 'place type'])
            .agg(
                count=('business_id', 'count'),
                avg_neg=('negative_review_pct', 'mean'),
                avg_rat=('avg_rating', 'mean')
            )
            .reset_index()
        )
        risk_areas = risk_areas[risk_areas['count'] >= 2].sort_values(by='avg_neg', ascending=False).head(5)

        if not risk_areas.empty:
            for _, r in risk_areas.iterrows():
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; background:rgba(239, 68, 68, 0.04); border-bottom:1px solid rgba(239, 68, 68, 0.15); border-radius:8px; margin-bottom:6px;">
                        <div>
                            <div style="font-weight:700; font-size:13px; color:#F8FAFC;">{r['place type']} <span style="font-size:11px; color:#64748B;">in {r['city']}</span></div>
                            <div style="font-size:11px; color:#EF4444;">{r['avg_neg']:.1f}% negative reviews • {r['avg_rat']:.2f} avg rating</div>
                        </div>
                        <div>
                            {render_badge('Intervention Needed', 'red')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No elevated risk sectors detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Segment Donut & Architecture
    c_donut, c_arch = st.columns([1.1, 0.9])
    with c_donut:
        fig_donut = build_donut_chart(prof_df)
        largest_seg = prof_df.sort_values(by='business_count', ascending=False).iloc[0]
        insight_msg = f"{largest_seg['cluster_name']} accounts for the largest proportion ({largest_seg['business_count']:,} businesses, {largest_seg['share_pct']:.1f}%)."
        render_chart_container(
            "Cluster Distribution Across Commercial Establishments",
            fig_donut,
            insight=insight_msg,
            help_text="Donut slice represents the relative volume of businesses assigned to each of the 4 K-Means behavioral segments."
        )

    with c_arch:
        st.markdown("""
            <div class="saas-panel">
                <div class="panel-header">⚡ How to Use UrbanPulse AI</div>
                <div style="display:flex; flex-direction:column; gap:14px; margin-top:8px;">
                    <div style="display:flex; gap:12px; align-items:flex-start;">
                        <div style="background:#1E293B; color:#60A5FA; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:12px; flex-shrink:0;">1</div>
                        <div>
                            <div style="font-weight:700; color:#F8FAFC; font-size:13px;">Explore & Benchmark</div>
                            <div style="font-size:12px; color:#94A3B8;">Use the Directory & Search or Map Explorer to find any business, inspect reviews, and see behavioral peers.</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:12px; align-items:flex-start;">
                        <div style="background:#1E293B; color:#60A5FA; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:12px; flex-shrink:0;">2</div>
                        <div>
                            <div style="font-weight:700; color:#F8FAFC; font-size:13px;">Find Commercial Gaps</div>
                            <div style="font-size:12px; color:#94A3B8;">Run the Business Advisor wizard to evaluate location demand, calculate break-even targets, and inspect competitors.</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:12px; align-items:flex-start;">
                        <div style="background:#1E293B; color:#60A5FA; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:12px; flex-shrink:0;">3</div>
                        <div>
                            <div style="font-weight:700; color:#F8FAFC; font-size:13px;">Review ML Methodology</div>
                            <div style="font-size:12px; color:#94A3B8;">Inspect K-Means inertia, silhouette curves, PCA projections, and mathematical formulas in the Model Card.</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    render_footer()
