"""
Page 9: Strategic Recommendations.
Generated dynamically by Segment Role to survive re-clustering.
"""
import streamlit as st
from src.ui.components import render_header, render_empty_state
from src.ui.styles import SEGMENT_COLORS

def render(data_bundle):
    render_header(
        "City-Service Strategic Recommendations",
        "Targeted urban policy interventions, licensing audits, and tourism showcases derived from cluster patterns.",
        "CIVIC DECISION SUPPORT"
    )

    biz_df = data_bundle['biz']
    prof_df = data_bundle['prof']

    if biz_df is None or prof_df is None:
        render_empty_state("Segmentation Results Not Loaded", "Run the pipeline to generate cluster profiles.")
        return

    # Dynamic counts per segment
    counts = biz_df['cluster_name'].value_counts().to_dict()
    top_tier_count = counts.get('High-Satisfaction Top Tier', 0)
    moderate_count = counts.get('Moderate / Mixed Feedback', 0)
    detailed_count = counts.get('High-Engagement Detailed Feedback', 0)
    at_risk_count = counts.get('Critical Intervention / At-Risk', 0)

    rec1, rec2 = st.columns(2)
    with rec1:
        st.markdown(f"""
            <div class="saas-panel" style="border-left: 4px solid {SEGMENT_COLORS['High-Satisfaction Top Tier']};">
                <div style="font-weight:700; color:{SEGMENT_COLORS['High-Satisfaction Top Tier']}; font-size:15px; margin-bottom:8px;">
                    🏆 High-Satisfaction Top Tier ({top_tier_count:,} Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Benchmark customer satisfaction, near-zero negative sentiment, consistent high ratings.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Feature in official Municipal Tourism Guides and city cultural showcases.</li>
                        <li>Engage business owners as mentors in local commerce mentorship programs.</li>
                        <li>Fast-track annual permit and outdoor seating approvals.</li>
                    </ul>
                </div>
            </div>
            
            <div class="saas-panel" style="border-left: 4px solid {SEGMENT_COLORS['High-Engagement Detailed Feedback']};">
                <div style="font-weight:700; color:{SEGMENT_COLORS['High-Engagement Detailed Feedback']}; font-size:15px; margin-bottom:8px;">
                    💬 High-Engagement Detailed Feedback ({detailed_count:,} Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Highly vocal customer base, high frequency of service and food mentions, long descriptive reviews.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Target for operational benchmarking and culinary excellence certifications.</li>
                        <li>Offer digital commerce grants to capitalize on highly engaged customer base.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with rec2:
        st.markdown(f"""
            <div class="saas-panel" style="border-left: 4px solid {SEGMENT_COLORS['Moderate / Mixed Feedback']};">
                <div style="font-weight:700; color:{SEGMENT_COLORS['Moderate / Mixed Feedback']}; font-size:15px; margin-bottom:8px;">
                    ⚖️ Moderate / Mixed Feedback ({moderate_count:,} Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Satisfactory ratings with brief reviews and lower review volume.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Deploy Chamber of Commerce digital marketing and feedback collection workshops.</li>
                        <li>Encourage local neighborhood promotional campaigns to stimulate repeat foot traffic.</li>
                    </ul>
                </div>
            </div>

            <div class="saas-panel" style="border-left: 4px solid {SEGMENT_COLORS['Critical Intervention / At-Risk']};">
                <div style="font-weight:700; color:{SEGMENT_COLORS['Critical Intervention / At-Risk']}; font-size:15px; margin-bottom:8px;">
                    🚨 Critical Intervention / At-Risk ({at_risk_count:,} Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> High rate of customer complaints and 1-2 star reviews indicating operational friction.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Conduct proactive health, sanitation, and licensing compliance audits.</li>
                        <li>Offer municipal employee training and service turnaround subsidies prior to license renewals.</li>
                        <li>Establish confidential diagnostic feedback sessions between inspectors and managers.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
