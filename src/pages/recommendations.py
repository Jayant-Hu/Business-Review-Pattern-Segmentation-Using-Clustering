"""
Strategic Civic & Commercial Recommendations.
Actionable operational roadmaps derived dynamically from empirical cluster roles.
"""
import streamlit as st
from src.ui.components import (
    render_header,
    render_empty_state,
    render_footer,
    render_section_header
)
from src.ui.theme import SEGMENT_COLORS

def render(data_bundle):
    render_header(
        title="Civic Policy & Commercial Strategy Directives",
        subtitle="Targeted urban economic interventions, licensing audits, and tourism showcases derived from cluster patterns.",
        eyebrow="CIVIC DECISION SUPPORT",
        breadcrumbs=["Platform", "Decision Engine", "Strategic Recommendations"]
    )

    biz_df = data_bundle.get('biz')
    prof_df = data_bundle.get('prof')

    if biz_df is None or prof_df is None:
        render_empty_state(
            title="Segmentation Results Not Loaded",
            message="Run the pipeline to generate cluster profiles.",
            action_command="python scripts/run_pipeline.py --step cluster"
        )
        render_footer()
        return

    # Dynamic counts per segment
    counts = biz_df['cluster_name'].value_counts().to_dict()
    top_tier_count = counts.get('High-Satisfaction Top Tier', 0)
    moderate_count = counts.get('Moderate / Mixed Feedback', 0)
    detailed_count = counts.get('High-Engagement Detailed Feedback', 0)
    at_risk_count = counts.get('Critical Intervention / At-Risk', 0)

    render_section_header("Segment Action Framework", subtitle="Operational directives tailored to identified commercial performance profiles")

    rec1, rec2 = st.columns(2)
    with rec1:
        st.markdown(f"""
            <div class="terminal-panel" style="border-top: 3px solid {SEGMENT_COLORS['High-Satisfaction Top Tier']};">
                <div class="panel-title-bar">
                    <h3 class="panel-title">High-Satisfaction Top Tier</h3>
                    <span class="chip">{top_tier_count:,} Venues</span>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.6;">
                    <b>Empirical Profile:</b> Benchmark customer satisfaction (4.57 avg rating), near-zero negative sentiment (0.1%), highly consistent consumer experience.<br><br>
                    <b>Strategic Policy Directives:</b>
                    <ul>
                        <li><b>Municipal Tourism Integration:</b> Feature in official city guides, cultural itineraries, and high-visibility municipal promotions.</li>
                        <li><b>Merchant Leadership:</b> Appoint venue leadership as peer advisors in local chamber of commerce modernization programs.</li>
                        <li><b>Regulatory Streamlining:</b> Fast-track annual permit renewals, outdoor seating allowances, and event licensing.</li>
                    </ul>
                </div>
            </div>
            
            <div class="terminal-panel" style="border-top: 3px solid {SEGMENT_COLORS['High-Engagement Detailed Feedback']};">
                <div class="panel-title-bar">
                    <h3 class="panel-title">High-Engagement Detailed Feedback</h3>
                    <span class="chip">{detailed_count:,} Venues</span>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.6;">
                    <b>Empirical Profile:</b> Highly articulate customer base, elevated service and food feedback rates, long descriptive reviews, moderate rating variance.<br><br>
                    <b>Strategic Policy Directives:</b>
                    <ul>
                        <li><b>Operational Benchmarking:</b> Target for hospitality certifications and operational performance diagnostics.</li>
                        <li><b>Commerce Grants:</b> Provide digital enablement and customer retention grants to capitalize on active community engagement.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with rec2:
        st.markdown(f"""
            <div class="terminal-panel" style="border-top: 3px solid {SEGMENT_COLORS['Moderate / Mixed Feedback']};">
                <div class="panel-title-bar">
                    <h3 class="panel-title">Moderate / Mixed Feedback</h3>
                    <span class="chip">{moderate_count:,} Venues</span>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.6;">
                    <b>Empirical Profile:</b> Satisfactory ratings (4.33 avg rating) but lower review depth and sparse aspect feedback.<br><br>
                    <b>Strategic Policy Directives:</b>
                    <ul>
                        <li><b>Consumer Outreach:</b> Deploy chamber of commerce digital feedback collection workshops to elevate community visibility.</li>
                        <li><b>Corridor Marketing:</b> Sponsor localized neighborhood retail campaigns to stimulate repeat footfall.</li>
                    </ul>
                </div>
            </div>

            <div class="terminal-panel" style="border-top: 3px solid {SEGMENT_COLORS['Critical Intervention / At-Risk']};">
                <div class="panel-title-bar">
                    <h3 class="panel-title" style="color:var(--red);">Critical Intervention / At-Risk</h3>
                    <span class="chip signal">{at_risk_count:,} Venues</span>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.6;">
                    <b>Empirical Profile:</b> High customer friction (45.6% negative sentiment, 2.33 avg rating), widespread consumer dissatisfaction signals.<br><br>
                    <b>Strategic Policy Directives:</b>
                    <ul>
                        <li><b>Compliance Auditing:</b> Conduct prioritized health, sanitation, and licensing compliance audits.</li>
                        <li><b>Workforce Subsidies:</b> Mandate employee training and operational turnaround programs prior to annual license renewals.</li>
                        <li><b>Confidential Diagnostics:</b> Establish structured feedback sessions between commercial inspectors and general managers.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    render_footer()
