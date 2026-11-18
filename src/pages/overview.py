"""
Page 1: Overview.
"""
import streamlit as st
from src.ui.components import render_header, render_metric_card, render_empty_state
from src.ui.charts import build_donut_chart
from src.services.analytics import compute_overall_metrics

def render(data_bundle):
    render_header(
        "Business Review Pattern Segmentation",
        "Empirical pattern discovery and unsupervised clustering for city-wide commercial service optimization.",
        "EXECUTIVE BRIEFING"
    )

    biz_df = data_bundle['biz']
    rev_df = data_bundle['rev']
    eval_df = data_bundle['eval']
    prof_df = data_bundle['prof']
    stab_df = data_bundle['stab']

    if biz_df is None or prof_df is None:
        render_empty_state("Clustering Data Not Loaded", "Run the preprocessing and clustering pipeline to compute real metrics.")
        return

    # Compute dynamic metrics from data
    metrics = compute_overall_metrics(biz_df, rev_df, eval_df, stab_df)

    # 4 Dynamic SaaS Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Analyzed Businesses", f"{metrics['total_businesses']:,}", "Verified composite key")
    with c2:
        render_metric_card("Processed Reviews", f"{metrics['total_reviews']:,}", "PII Sanitized & Deduplicated")
    with c3:
        render_metric_card("Optimal Clusters", f"K = {metrics['optimal_k']}", f"Silhouette {metrics['silhouette']} | DB {metrics['davies_bouldin']}")
    with c4:
        render_metric_card("Clustering Stability", f"{metrics['mean_ari_pct']}%", "Adjusted Rand Index across 5 seeds")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1.8])
    with col_left:
        st.markdown('<div class="saas-panel"><div class="panel-header">🎯 Segment Distribution</div>', unsafe_allow_html=True)
        fig_donut = build_donut_chart(prof_df)
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div class="saas-panel">
                <div class="panel-header">⚡ Architecture & Civic Impact</div>
                <p style="color:#94A3B8; font-size:13px; line-height:1.6;">
                    The platform transforms high-volume, unstructured Google Local customer reviews into actionable 
                    municipal intelligence. Instead of relying solely on arithmetic mean ratings, the engine captures 
                    multidimensional behavioral signatures: <b>satisfaction polarity</b>, <b>feedback depth</b>, 
                    <b>rating variance</b>, and <b>service mentions</b>.
                </p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:14px;">
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:12px; border-radius:10px;">
                        <div style="font-weight:700; color:#60A5FA; font-size:13px; margin-bottom:4px;">Municipal Tourism & Recognition</div>
                        <div style="font-size:12px; color:#94A3B8;">Spotlight high-performing establishments for civic showcases and city guides.</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:12px; border-radius:10px;">
                        <div style="font-weight:700; color:#F87171; font-size:13px; margin-bottom:4px;">At-Risk Commercial Intervention</div>
                        <div style="font-size:12px; color:#94A3B8;">Detect establishments with critical dissatisfaction to deploy targeted service and training subsidies.</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
