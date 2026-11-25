"""
Page: Business Decision Advisor.
Flagship decision-support tool providing:
- Guided 3-step recommendation wizard with sensitivity weight controls
- Profit Potential Index (PPI) gauges and opportunity classifications
- Detailed multi-tab breakdown: Market Snapshot, Competitor intelligence, Customer Voice, Location map, Break-even helper
- 'Best Business per Area' Leaderboard with export
- 'Best Area per Business Type' reverse lookup
- Multi-area / Multi-category radar comparison tool
- One-click PDF Executive Advisory Report download
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.ui.components import render_header, render_empty_state, render_footer
from src.ui.theme import (
    PLOTLY_DARK_THEME,
    BG_SURFACE_1,
    BG_SURFACE_2,
    BORDER_HAIRLINE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    SILVER_PRIMARY,
    SIGNAL_RED,
    SIGNAL_RED_SOFT,
    ACCENT_GREEN,
    ACCENT_BLUE
)
from src.services.decision_advisor import (
    HONESTY_DISCLAIMER,
    compute_ppi_score,
    extract_customer_voice,
    compute_competition_matrix,
    calculate_breakeven_helper
)
from src.services.report_generator import generate_advisor_pdf
from src.utils.paths import settings

def render(data_bundle):
    render_header(
        "Commercial Decision Advisor & Market Opportunity Engine",
        "Empirical review-driven market sizing, Profit Potential Index (PPI) scoring, and strategic location advisory.",
        "STRATEGIC ADVISORY",
        breadcrumbs=["Platform", "Decide", "Business Advisor"]
    )

    # Prominent Honesty Disclaimer Banner
    st.markdown(f"""
        <div style="background:{SIGNAL_RED_SOFT}; border:1px solid {SIGNAL_RED}; border-left:3px solid {SIGNAL_RED}; border-radius:4px; padding:12px 18px; margin-bottom:24px; font-size:12.5px; color:{TEXT_PRIMARY}; font-family:var(--font-sans);">
            <b style="color:{SIGNAL_RED};">Model Reality Notice:</b> {HONESTY_DISCLAIMER}
        </div>
    """, unsafe_allow_html=True)

    biz_df = data_bundle.get('biz')
    rev_df = data_bundle.get('rev')

    if biz_df is None or biz_df.empty:
        render_empty_state("Business Data Missing", "Run the pipeline to generate clustered_businesses.csv.")
        return

    # Top Navigation Sub-Tabs
    sub_tab = st.radio(
        "Advisor Tools:",
        ["Guided Advisor Wizard", "Best Business per Area Leaderboard", "Best Area per Category", "Multi-Entity Comparison Tool"],
        horizontal=True
    )

    # -------------------------------------------------------------
    # SUB-TAB 1: GUIDED ADVISOR WIZARD
    # -------------------------------------------------------------
    if sub_tab == "Guided Advisor Wizard":
        _render_wizard(biz_df, rev_df)

    # -------------------------------------------------------------
    # SUB-TAB 2: LEADERBOARD PER AREA
    # -------------------------------------------------------------
    elif sub_tab == "Best Business per Area Leaderboard":
        _render_leaderboard(biz_df)

    # -------------------------------------------------------------
    # SUB-TAB 3: BEST AREA PER CATEGORY
    # -------------------------------------------------------------
    elif sub_tab == "Best Area per Category":
        _render_category_lookup(biz_df)

    # -------------------------------------------------------------
    # SUB-TAB 4: MULTI-ENTITY COMPARISON
    # -------------------------------------------------------------
    elif sub_tab == "Multi-Entity Comparison Tool":
        _render_comparison_tool(biz_df)

    render_footer()

def _render_wizard(biz_df: pd.DataFrame, rev_df: pd.DataFrame):
    """Renders the 3-step interactive advisor wizard."""
    st.markdown(f"""
        <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:24px;">
            <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:14px; letter-spacing:-0.01em;">
                Market Opportunity Wizard
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:16px; font-size:12px; font-weight:600; color:{TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">
                <span style="color:{SILVER_PRIMARY};">Step 1: Choose Location</span> 
                <span style="color:{BORDER_HAIRLINE};">/</span>
                <span style="color:{SILVER_PRIMARY};">Step 2: Define Constraints & Sensitivity</span> 
                <span style="color:{BORDER_HAIRLINE};">/</span>
                <span style="color:{SIGNAL_RED};">Step 3: Recommendation Results</span>
            </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1.8])
    with c1:
        st.markdown(f"<div style='font-size:12px; font-weight:600; color:{TEXT_SECONDARY}; text-transform:uppercase; margin-bottom:4px;'>Step 1: Location Filter</div>", unsafe_allow_html=True)
        available_cities = sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
        selected_city = st.selectbox("Select Target City / Area:", ["Anywhere (Global Aggregate)"] + available_cities, index=1 if available_cities else 0)

    with c2:
        st.markdown(f"<div style='font-size:12px; font-weight:600; color:{TEXT_SECONDARY}; text-transform:uppercase; margin-bottom:4px;'>Step 2: Preference & Sensitivity Constraints</div>", unsafe_allow_html=True)
        col_pref1, col_pref2 = st.columns(2)
        with col_pref1:
            comp_tolerance = st.selectbox("Competition Tolerance:", ["Low Crowding (Preferred)", "Medium (Balanced)", "High (Aggressive)"], index=1)
        with col_pref2:
            min_reviews_req = st.slider("Minimum Market Reviews:", 5, 100, 10)

    # Sensitivity Weight Expander
    with st.expander("Customize Profit Potential Index (PPI) Formula Weights"):
        st.caption("Adjust the relative importance of each dimension. Scores recompute dynamically.")
        w_c1, w_c2, w_c3, w_c4 = st.columns(4)
        w_sat = w_c1.slider("Satisfaction Weight:", 0.1, 0.6, settings.PPI_WEIGHT_SATISFACTION, 0.05)
        w_dem = w_c2.slider("Demand Weight:", 0.1, 0.6, settings.PPI_WEIGHT_DEMAND, 0.05)
        w_comp = w_c3.slider("Low-Competition Weight:", 0.05, 0.5, settings.PPI_WEIGHT_COMPETITION, 0.05)
        w_risk = w_c4.slider("Risk Penalty Weight:", 0.05, 0.5, settings.PPI_WEIGHT_RISK, 0.05)

    st.markdown(f"""
        <div style="border-top:1px solid {BORDER_HAIRLINE}; margin:20px 0 16px 0;"></div>
        <div style="font-family:var(--font-serif); font-size:15px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:12px;">Step 3: Strategic Recommendations</div>
    """, unsafe_allow_html=True)

    # Filter businesses for the selected area
    target_df = biz_df if selected_city == "Anywhere (Global Aggregate)" else biz_df[biz_df['city'] == selected_city]

    # Group by category and compute PPI
    cat_summary = []
    for cat, group in target_df.groupby('place type'):
        total_rev = group['sample_review_count'].sum()
        if total_rev < min_reviews_req:
            continue
        biz_cnt = len(group)
        mean_rat = group['avg_rating'].mean()
        pos_pct = group['positive_review_pct'].mean()
        neg_pct = group['negative_review_pct'].mean()
        rat_std = group['rating_std'].mean() if 'rating_std' in group.columns else 0.5
        at_risk_cnt = (group['cluster_name'] == 'Critical Intervention / At-Risk').sum()
        at_risk_share = (at_risk_cnt / biz_cnt) * 100.0 if biz_cnt > 0 else 0.0

        ppi, opp_type, conf, why, risks = compute_ppi_score(
            biz_count=biz_cnt,
            total_reviews=total_rev,
            avg_rating=mean_rat,
            positive_pct=pos_pct,
            negative_pct=neg_pct,
            rating_std=rat_std,
            at_risk_share=at_risk_share,
            w_sat=w_sat,
            w_dem=w_dem,
            w_comp=w_comp,
            w_risk=w_risk
        )

        cat_summary.append({
            'category': cat,
            'ppi': ppi,
            'opp_type': opp_type,
            'confidence': conf,
            'biz_count': biz_cnt,
            'total_reviews': total_rev,
            'avg_rating': round(mean_rat, 2),
            'positive_pct': round(pos_pct, 1),
            'negative_pct': round(neg_pct, 1),
            'why': why,
            'risks': risks
        })

    if not cat_summary:
        st.warning(f"No commercial categories meet the minimum review threshold in {selected_city}. Lower the review filter.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cat_df = pd.DataFrame(cat_summary).sort_values(by='ppi', ascending=False).reset_index(drop=True)
    st.markdown(f"Discovered **{len(cat_df)} viable categories** ranked by Profit Potential Index (PPI):")

    # Display Top Recommendations
    top_n = min(4, len(cat_df))
    rec_cols = st.columns(top_n)
    for idx in range(top_n):
        row = cat_df.iloc[idx]
        with rec_cols[idx]:
            gauge_color = ACCENT_GREEN if row['ppi'] >= 70 else SILVER_PRIMARY if row['ppi'] >= 50 else SIGNAL_RED
            st.markdown(f"""
                <div style="background:{BG_SURFACE_2}; border:1px solid {BORDER_HAIRLINE}; border-top: 2px solid {gauge_color}; border-radius:4px; padding:16px;">
                    <div style="font-size:10px; color:{TEXT_MUTED}; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">RANK #{idx+1}</div>
                    <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:4px;">{row['category']}</div>
                    <div style="font-family:var(--font-mono); font-size:22px; font-weight:700; color:{gauge_color};">{row['ppi']} <span style="font-size:11px; color:{TEXT_MUTED};">/ 100</span></div>
                    <div style="font-size:11px; color:{SILVER_PRIMARY}; font-weight:500; margin-bottom:8px;">{row['opp_type']}</div>
                    <div style="font-size:11px; color:{TEXT_SECONDARY}; font-family:var(--font-mono);">{row['biz_count']} comps • {row['total_reviews']} revs</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Category Investigation
    st.markdown(f"<div style='font-family:var(--font-serif); font-size:15px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:10px;'>Category Dossier & Competitor Breakdown</div>", unsafe_allow_html=True)
    sel_cat = st.selectbox("Select Category to Inspect Details & Competitors:", cat_df['category'].tolist())
    chosen_rec = cat_df[cat_df['category'] == sel_cat].iloc[0]

    # Detail Tabs
    d_tab1, d_tab2, d_tab3, d_tab4, d_tab5, d_tab6 = st.tabs([
        "Market Snapshot",
        "Competitor Intelligence",
        "Customer Voice & Themes",
        "Area Location Map",
        "Break-even Helper",
        "Download PDF Report"
    ])

    with d_tab1:
        st.markdown(f"#### Market Profile: {sel_cat} in {selected_city}")
        ms1, ms2, ms3, ms4 = st.columns(4)
        ms1.metric("Establishments", f"{chosen_rec['biz_count']}")
        ms2.metric("Total Reviews", f"{chosen_rec['total_reviews']}")
        ms3.metric("Avg Rating", f"{chosen_rec['avg_rating']}")
        ms4.metric("Positive Feedback", f"{chosen_rec['positive_pct']}%")

        col_why, col_risk = st.columns(2)
        with col_why:
            st.markdown(f"""<div style="background:{BG_SURFACE_2}; border:1px solid {BORDER_HAIRLINE}; border-left:3px solid {ACCENT_GREEN}; border-radius:4px; padding:14px;">
                <b style="color:{ACCENT_GREEN}; font-size:12px; text-transform:uppercase; letter-spacing:0.04em;">Positive Strategic Signals:</b>
                <ul style="font-size:12.5px; color:{TEXT_SECONDARY}; padding-left:18px; margin-top:8px;">""" +
                "".join([f"<li>{p}</li>" for p in chosen_rec['why']]) + "</ul></div>", unsafe_allow_html=True)
        with col_risk:
            st.markdown(f"""<div style="background:{SIGNAL_RED_SOFT}; border:1px solid {SIGNAL_RED}; border-left:3px solid {SIGNAL_RED}; border-radius:4px; padding:14px;">
                <b style="color:{SIGNAL_RED}; font-size:12px; text-transform:uppercase; letter-spacing:0.04em;">Potential Operational Risks:</b>
                <ul style="font-size:12.5px; color:{TEXT_PRIMARY}; padding-left:18px; margin-top:8px;">""" +
                "".join([f"<li>{r}</li>" for r in chosen_rec['risks']]) + "</ul></div>", unsafe_allow_html=True)

    with d_tab2:
        st.markdown(f"#### Top Recorded Competitors: {sel_cat}")
        comp_df = compute_competition_matrix(target_df, sel_cat, selected_city if selected_city != "Anywhere (Global Aggregate)" else "Riyadh")
        if not comp_df.empty:
            st.dataframe(comp_df, use_container_width=True)
        else:
            st.info("No competitor records available.")

    with d_tab3:
        st.markdown(f"#### Customer Themes & Aspect Mentions: {sel_cat}")
        cat_biz_names = target_df[target_df['place type'] == sel_cat]['place'].unique().tolist()
        voice = extract_customer_voice(rev_df, cat_biz_names) if rev_df is not None else {'positive_keywords': [], 'negative_keywords': [], 'aspects': {}, 'quotes': []}

        cv1, cv2, cv3 = st.columns(3)
        with cv1:
            st.markdown(f"<div style='font-size:11px; text-transform:uppercase; color:{TEXT_MUTED}; font-weight:700;'>Positive Keywords</div>", unsafe_allow_html=True)
            if voice['positive_keywords']:
                for kw in voice['positive_keywords']:
                    st.markdown(f"- <span style='color:{ACCENT_GREEN}; font-family:var(--font-mono); font-size:12px;'>{kw}</span>", unsafe_allow_html=True)
            else:
                st.caption("No keywords detected.")
        with cv2:
            st.markdown(f"<div style='font-size:11px; text-transform:uppercase; color:{TEXT_MUTED}; font-weight:700;'>Friction Keywords</div>", unsafe_allow_html=True)
            if voice['negative_keywords']:
                for kw in voice['negative_keywords']:
                    st.markdown(f"- <span style='color:{SIGNAL_RED}; font-family:var(--font-mono); font-size:12px;'>{kw}</span>", unsafe_allow_html=True)
            else:
                st.caption("No friction keywords detected.")
        with cv3:
            st.markdown(f"<div style='font-size:11px; text-transform:uppercase; color:{TEXT_MUTED}; font-weight:700;'>Aspect Ratings</div>", unsafe_allow_html=True)
            for asp, score in voice['aspects'].items():
                if score:
                    st.write(f"• **{asp}**: {score:.1f} / 5.0")
                else:
                    st.write(f"• **{asp}**: N/A")

        if voice['quotes']:
            st.markdown(f"<div style='font-size:11px; text-transform:uppercase; color:{TEXT_MUTED}; font-weight:700; margin-top:12px;'>De-identified Review Excerpts</div>", unsafe_allow_html=True)
            for q in voice['quotes']:
                st.markdown(f"> *\"{q['text']}\"* — Rating: {q['rating']} / 5")

    with d_tab4:
        st.markdown(f"#### Spatial Map: {sel_cat} in {selected_city}")
        cat_geo = target_df[(target_df['place type'] == sel_cat) & target_df['latitude'].notnull()]
        if not cat_geo.empty:
            if hasattr(px, 'scatter_map'):
                fig_map = px.scatter_map(
                    cat_geo,
                    lat="latitude",
                    lon="longitude",
                    hover_name="place",
                    hover_data=["avg_rating", "sample_review_count", "cluster_name"],
                    color="cluster_name",
                    zoom=10,
                    height=450
                )
                fig_map.update_layout(map_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            else:
                fig_map = px.scatter_mapbox(
                    cat_geo,
                    lat="latitude",
                    lon="longitude",
                    hover_name="place",
                    hover_data=["avg_rating", "sample_review_count", "cluster_name"],
                    color="cluster_name",
                    zoom=10,
                    height=450
                )
                fig_map.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No spatial coordinates available for this category.")

    with d_tab5:
        st.markdown("#### User-Assumption Break-Even Demand Helper")
        st.caption("Enter estimated business financial assumptions. Compares required traffic with the area's review engagement signals.")
        be1, be2, be3 = st.columns(3)
        avg_ticket = be1.number_input("Average Customer Spend ($):", min_value=1.0, value=15.0, step=1.0)
        fixed_cost = be2.number_input("Monthly Fixed Costs ($):", min_value=100.0, value=5000.0, step=500.0)
        margin = be3.slider("Gross Margin %:", 10.0, 90.0, 60.0)

        be_res = calculate_breakeven_helper(avg_ticket, fixed_cost, margin)
        st.markdown(f"""
            <div style="background:{BG_SURFACE_2}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:16px;">
                <div style="font-size:12px; font-weight:600; color:{TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em;">Estimated Break-Even Threshold:</div>
                <div style="font-family:var(--font-mono); font-size:22px; font-weight:700; color:{TEXT_PRIMARY}; margin-top:4px;">
                    {be_res['monthly_customers']:,} customers/month <span style="font-size:13px; color:{TEXT_MUTED};">(~{be_res['daily_customers']} per day)</span>
                </div>
                <div style="font-size:12px; color:{TEXT_SECONDARY}; margin-top:6px; font-family:var(--font-sans);">
                    Required Monthly Revenue: <b>${be_res['monthly_revenue']:,.2f}</b><br>
                    Review proxy demand indicator for {sel_cat} in {selected_city}: <b>{chosen_rec['total_reviews']} total sample reviews recorded</b>.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with d_tab6:
        st.markdown("#### One-Click Advisory Report (PDF)")
        st.caption("Generate a branded, high-resolution executive summary PDF including market snapshots, competitor list, and honesty disclaimers.")
        
        pdf_bytes = generate_advisor_pdf(
            city=selected_city,
            category=sel_cat,
            ppi_score=chosen_rec['ppi'],
            opp_type=chosen_rec['opp_type'],
            confidence=chosen_rec['confidence'],
            stats={
                'biz_count': chosen_rec['biz_count'],
                'total_reviews': chosen_rec['total_reviews'],
                'avg_rating': chosen_rec['avg_rating'],
                'positive_pct': chosen_rec['positive_pct'],
                'negative_pct': chosen_rec['negative_pct']
            },
            why_points=chosen_rec['why'],
            risk_points=chosen_rec['risks'],
            competitors_df=comp_df if not comp_df.empty else None
        )

        st.download_button(
            label=f"Download Full PDF Report for {sel_cat} ({selected_city})",
            data=pdf_bytes,
            file_name=f"UrbanPulse_Advisory_{selected_city}_{sel_cat}.pdf".replace(" ", "_"),
            mime="application/pdf"
        )

    st.markdown('</div>', unsafe_allow_html=True)

def _render_leaderboard(biz_df: pd.DataFrame):
    """Renders the 'Best business per area' leaderboard table."""
    st.markdown(f"""
        <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:24px;">
            <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:4px;">
                Municipal Opportunity Leaderboard
            </div>
            <div style="font-size:12px; color:{TEXT_MUTED}; margin-bottom:16px;">
                Ranks top recommended categories and identifies high-risk commercial types for every analyzed city.
            </div>
    """, unsafe_allow_html=True)

    rows = []
    for city, group in biz_df.groupby('city'):
        if city == 'Unknown' or len(group) < 5:
            continue
        cat_perf = group.groupby('place type').agg(
            count=('sample_review_count', 'count'),
            reviews=('sample_review_count', 'sum'),
            rating=('avg_rating', 'mean'),
            neg_pct=('negative_review_pct', 'mean')
        ).reset_index()

        cat_perf['score'] = (cat_perf['rating'] * 15.0) + (cat_perf['reviews'] * 0.5) - (cat_perf['neg_pct'] * 0.4)
        sorted_cats = cat_perf.sort_values(by='score', ascending=False)
        top3 = ", ".join(sorted_cats.head(3)['place type'].tolist())
        avoid = sorted_cats.tail(1)['place type'].iloc[0] if len(sorted_cats) >= 4 else "N/A"

        rows.append({
            'City / Area': city,
            'Total Businesses': len(group),
            'Top 3 Recommended Opportunities': top3,
            'High-Friction Category (Caution)': avoid,
            'Avg City Rating': round(group['avg_rating'].mean(), 2)
        })

    leader_df = pd.DataFrame(rows).sort_values(by='Total Businesses', ascending=False)
    st.dataframe(leader_df, use_container_width=True)

    csv_data = leader_df.to_csv(index=False).encode('utf-8')
    st.download_button("Export Area Leaderboard (CSV)", data=csv_data, file_name="urbanpulse_city_leaderboard.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

def _render_category_lookup(biz_df: pd.DataFrame):
    """Reverse lookup: select a category, see ranked cities."""
    st.markdown(f"""
        <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:24px;">
            <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:12px;">
                Best Area per Business Type
            </div>
    """, unsafe_allow_html=True)
    all_cats = sorted(biz_df['place type'].dropna().unique().tolist())
    target_cat = st.selectbox("Choose Business Category to Rank Across Cities:", all_cats)

    cat_df = biz_df[biz_df['place type'] == target_cat]
    grouped = cat_df.groupby('city').agg(
        businesses=('business_id', 'count'),
        total_reviews=('sample_review_count', 'sum'),
        avg_rating=('avg_rating', 'mean'),
        positive_pct=('positive_review_pct', 'mean')
    ).reset_index()

    grouped = grouped[grouped['city'] != 'Unknown'].sort_values(by='businesses', ascending=False)
    st.dataframe(grouped, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _render_comparison_tool(biz_df: pd.DataFrame):
    """Side-by-side comparison of up to 3 cities or 3 categories with radar chart."""
    st.markdown(f"""
        <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:24px;">
            <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:12px;">
                Multi-Entity Benchmark Comparison
            </div>
    """, unsafe_allow_html=True)
    comp_mode = st.radio("Comparison Mode:", ["Compare Cities / Areas", "Compare Business Categories"], horizontal=True)

    if comp_mode == "Compare Cities / Areas":
        entities = sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
        chosen = st.multiselect("Select up to 3 Cities to Compare:", entities, default=entities[:2] if len(entities) >= 2 else entities)
        group_col = 'city'
    else:
        entities = sorted(biz_df['place type'].dropna().unique().tolist())
        chosen = st.multiselect("Select up to 3 Categories to Compare:", entities, default=entities[:2] if len(entities) >= 2 else entities)
        group_col = 'place type'

    if len(chosen) >= 2:
        radar_categories = ['Avg Rating (x20)', 'Positive %', 'Low Negative %', 'Review Volume Proxy', 'Service Quality Rate']
        fig_radar = go.Figure()

        table_rows = []
        silver_palette = [SILVER_PRIMARY, SILVER_SOFT, TEXT_MUTED]
        for idx, ent in enumerate(chosen):
            grp = biz_df[biz_df[group_col] == ent]
            avg_r = grp['avg_rating'].mean()
            pos_p = grp['positive_review_pct'].mean()
            low_neg = max(0.0, 100.0 - grp['negative_review_pct'].mean())
            vol_proxy = min(100.0, grp['sample_review_count'].mean() * 20.0)
            serv_rate = grp['service_feedback_rate'].mean() if 'service_feedback_rate' in grp.columns else 0.0

            color = silver_palette[idx % len(silver_palette)]
            fig_radar.add_trace(go.Scatterpolar(
                r=[avg_r * 20.0, pos_p, low_neg, vol_proxy, min(100.0, serv_rate * 2.0)],
                theta=radar_categories,
                fill='toself',
                name=ent,
                line=dict(color=color)
            ))

            table_rows.append({
                'Entity': ent,
                'Business Count': len(grp),
                'Avg Rating': round(avg_r, 2),
                'Positive %': round(pos_p, 1),
                'Negative %': round(grp['negative_review_pct'].mean(), 1),
                'Service Mention %': round(serv_rate, 1)
            })

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=BORDER_HAIRLINE, linecolor=BORDER_HAIRLINE),
                angularaxis=dict(gridcolor=BORDER_HAIRLINE, linecolor=BORDER_HAIRLINE)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_MUTED, family="var(--font-sans)"),
            showlegend=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        comp_summary = pd.DataFrame(table_rows)
        st.dataframe(comp_summary, use_container_width=True)

        best_rating_ent = comp_summary.sort_values(by='Avg Rating', ascending=False)['Entity'].iloc[0]
        st.markdown(f"""
            <div style="background:{BG_SURFACE_2}; border:1px solid {BORDER_HAIRLINE}; border-left:3px solid {SILVER_PRIMARY}; border-radius:4px; padding:12px 16px; margin-top:14px; font-size:12.5px; color:{TEXT_PRIMARY};">
                Benchmark Leader: <b>{best_rating_ent}</b> registers the highest overall satisfaction signals within this selection.
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
