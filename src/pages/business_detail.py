"""
Page: Business Detail & Global Search.
Provides:
- Real-time global search with autocomplete suggestions across name, category, and city
- Detailed business header card with segment badge, address, and Google Maps link
- KPI stat row (ratings, reviews, consistency, sentiment breakdown)
- Rating distribution chart and customer voice aspect ratings
- Nearest behavioral peers in the 10-D feature space
- Local category and city rank percentiles
- Interactive location pin
- Export dossier as PDF and CSV
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.components import render_header, render_empty_state
from src.ui.styles import SEGMENT_COLORS
from src.ui.theme import PLOTLY_DARK_THEME
from src.services.decision_advisor import HONESTY_DISCLAIMER, extract_customer_voice
from src.services.business_lookup import (
    search_businesses,
    find_similar_businesses,
    calculate_local_percentile,
    generate_business_dossier_pdf
)

def render(data_bundle):
    render_header(
        "Commercial Establishment Explorer & Search",
        "Deep-dive establishment profile, local category percentiles, behavioral peers, and review diagnostics.",
        "BUSINESS DOSSIER"
    )

    biz_df = data_bundle['biz']
    rev_df = data_bundle['rev']

    if biz_df is None or biz_df.empty:
        render_empty_state("Business Data Missing", "Run the pipeline to generate clustered_businesses.csv.")
        return

    # -------------------------------------------------------------
    # 1. GLOBAL SEARCH & AUTOCOMPLETE SELECTOR
    # -------------------------------------------------------------
    st.markdown('<div class="saas-panel"><div class="panel-header">🔍 Global Establishment Search</div>', unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns([2.0, 1.2, 1.2])
    with col_s1:
        search_query = st.text_input("Search by Business Name or Address Keyword:", "", placeholder="e.g. Arabica, Bakery, Olaya, Riyadh...")
    with col_s2:
        cities = ["All Cities"] + sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
        selected_city = st.selectbox("Filter City:", cities)
    with col_s3:
        categories = ["All Categories"] + sorted(biz_df['place type'].dropna().unique().tolist())
        selected_cat = st.selectbox("Filter Category:", categories)

    search_matches = search_businesses(biz_df, search_query, selected_city, selected_cat, limit=40)

    if search_matches.empty:
        st.warning("No establishments match your search criteria. Try a different keyword or reset filters.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Autocomplete suggestion picker
    options_dict = {
        f"{row['place']} ({row['place type']} • {row['city']})": row['business_id']
        for _, row in search_matches.iterrows()
    }
    selected_label = st.selectbox("Select Business to Inspect:", list(options_dict.keys()), index=0)
    target_id = options_dict[selected_label]
    biz_row = biz_df[biz_df['business_id'] == target_id].iloc[0]

    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. BUSINESS DETAIL HERO CARD & KPIS
    # -------------------------------------------------------------
    seg_name = biz_row.get('cluster_name', 'Unassigned')
    seg_color = SEGMENT_COLORS.get(seg_name, '#3B82F6')
    lat = biz_row.get('latitude')
    lng = biz_row.get('longitude')
    maps_link = (
        f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        if pd.notna(lat) and pd.notna(lng)
        else f"https://www.google.com/maps/search/?api=1&query={biz_row['place']}+{biz_row['city']}"
    )

    percentiles = calculate_local_percentile(biz_df, biz_row)

    st.markdown(f"""
        <div class="saas-panel" style="border-left: 5px solid {seg_color};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                <div>
                    <span style="background:{seg_color}22; color:{seg_color}; border:1px solid {seg_color}55; border-radius:14px; padding:3px 10px; font-size:11px; font-weight:700;">
                        {seg_name}
                    </span>
                    <h2 style="color:#F8FAFC; margin:8px 0 4px 0; font-size:24px; font-weight:800;">{biz_row['place']}</h2>
                    <div style="font-size:13px; color:#94A3B8;">
                        <b>{biz_row['place type']}</b> • 📍 {biz_row['city']} • {biz_row['address']}
                    </div>
                </div>
                <div style="text-align:right;">
                    <a href="{maps_link}" target="_blank" style="display:inline-block; background:#1E293B; border:1px solid rgba(255,255,255,0.15); color:#60A5FA; padding:8px 14px; border-radius:8px; font-size:12.5px; text-decoration:none; font-weight:600;">
                        ↗ Open in Google Maps
                    </a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Customer Rating", f"{biz_row['avg_rating']:.2f} ⭐", f"±{biz_row['rating_std']:.2f} std")
    k2.metric("Sample Reviews", f"{biz_row['sample_review_count']} reviews", "De-identified snapshot")
    k3.metric("Positive Share", f"{biz_row['positive_review_pct']:.1f}%", "4★ & 5★ ratings")
    k4.metric("City Standing", f"#{percentiles['city_rank']} in {biz_row['city']}", f"Top {100 - percentiles['city_percentile']:.1f}%")
    k5.metric("Category Standing", f"#{percentiles['category_rank']} in {biz_row['place type']}", f"Top {100 - percentiles['category_percentile']:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. MULTI-TAB DIAGNOSTIC DETAILS
    # -------------------------------------------------------------
    tab_reviews, tab_peers, tab_location, tab_dossier = st.tabs([
        "💬 Review Themes & Aspect Ratings",
        "👥 Behavioral Peer Establishments",
        "🗺️ Spatial Location & Surroundings",
        "📄 Export Business Dossier (PDF/CSV)"
    ])

    with tab_reviews:
        col_rev_l, col_rev_r = st.columns([1.2, 1.8])
        
        with col_rev_l:
            st.markdown('<div class="saas-panel"><div class="panel-header">⭐ Rating Distribution</div>', unsafe_allow_html=True)
            if rev_df is not None:
                biz_reviews = rev_df[rev_df['place'] == biz_row['place']]
                if not biz_reviews.empty:
                    rc_df = biz_reviews['rating'].value_counts().sort_index().reset_index()
                    rc_df.columns = ['Rating', 'Count']
                    fig_r = px.bar(rc_df, x='Rating', y='Count', color='Rating', color_continuous_scale='Blues')
                    fig_r.update_layout(**PLOTLY_DARK_THEME)
                    fig_r.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(fig_r, use_container_width=True)
                else:
                    st.caption("No review breakdown records in sample.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_rev_r:
            st.markdown('<div class="saas-panel"><div class="panel-header">🗣️ Customer Voice Keywords & Excerpts</div>', unsafe_allow_html=True)
            voice = extract_customer_voice(rev_df, [biz_row['place']])
            cv_col1, cv_col2 = st.columns(2)
            with cv_col1:
                st.markdown("<b>Positive Themes:</b>", unsafe_allow_html=True)
                if voice['positive_keywords']:
                    for kw in voice['positive_keywords'][:5]:
                        st.markdown(f"• <span style='color:#34D399;'>{kw}</span>", unsafe_allow_html=True)
                else:
                    st.caption("No distinct positive keywords.")
            with cv_col2:
                st.markdown("<b>Friction Themes:</b>", unsafe_allow_html=True)
                if voice['negative_keywords']:
                    for kw in voice['negative_keywords'][:5]:
                        st.markdown(f"• <span style='color:#F87171;'>{kw}</span>", unsafe_allow_html=True)
                else:
                    st.caption("No friction themes detected.")

            if voice['quotes']:
                st.markdown("<b>Sample Customer Quotes (De-identified):</b>", unsafe_allow_html=True)
                for q in voice['quotes']:
                    st.markdown(f"> *\"{q['text']}\"* — Rated {q['rating']} ⭐")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_peers:
        st.markdown('<div class="saas-panel"><div class="panel-header">👥 Nearest Behavioral Peers (10-D Feature Space Neighbors)</div>', unsafe_allow_html=True)
        st.caption("Identified using Euclidean distance across standardized ratings, feedback volume, review length, and aspect mention rates.")
        peers_df = find_similar_businesses(biz_df, biz_row['business_id'], top_n=6)
        if not peers_df.empty:
            st.dataframe(peers_df, use_container_width=True)
        else:
            st.info("No peers discovered.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_location:
        st.markdown(f'<div class="saas-panel"><div class="panel-header">📍 Geographic Pin: {biz_row["place"]}</div>', unsafe_allow_html=True)
        if pd.notna(lat) and pd.notna(lng):
            pin_df = pd.DataFrame([{
                'latitude': lat,
                'longitude': lng,
                'place': biz_row['place'],
                'cluster_name': seg_name,
                'avg_rating': biz_row['avg_rating'],
                'sample_review_count': biz_row['sample_review_count']
            }])
            if hasattr(px, 'scatter_map'):
                fig_pin = px.scatter_map(
                    pin_df,
                    lat="latitude",
                    lon="longitude",
                    hover_name="place",
                    hover_data=["avg_rating", "sample_review_count", "cluster_name"],
                    zoom=13,
                    height=420
                )
                fig_pin.update_layout(map_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            else:
                fig_pin = px.scatter_mapbox(
                    pin_df,
                    lat="latitude",
                    lon="longitude",
                    hover_name="place",
                    hover_data=["avg_rating", "sample_review_count", "cluster_name"],
                    zoom=13,
                    height=420
                )
                fig_pin.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            fig_pin.update_traces(marker=dict(size=14, color=seg_color))
            st.plotly_chart(fig_pin, use_container_width=True)
        else:
            st.info("Exact geographic coordinates are not available for this establishment.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_dossier:
        st.markdown('<div class="saas-panel"><div class="panel-header">📄 Export Business Dossier</div>', unsafe_allow_html=True)
        st.caption("Generate an executive PDF profile or download full raw CSV attributes for this establishment.")
        
        pdf_col, csv_col = st.columns(2)
        with pdf_col:
            dossier_pdf = generate_business_dossier_pdf(biz_row, percentiles, peers_df if not peers_df.empty else None)
            st.download_button(
                label=f"📄 Download PDF Profile ({biz_row['place'][:20]})",
                data=dossier_pdf,
                file_name=f"Dossier_{biz_row['place']}.pdf".replace(" ", "_"),
                mime="application/pdf"
            )
        with csv_col:
            single_csv = biz_df[biz_df['business_id'] == target_id].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Establishment Raw Record (CSV)",
                data=single_csv,
                file_name=f"Record_{biz_row['place']}.csv".replace(" ", "_"),
                mime="text/csv"
            )
        st.markdown('</div>', unsafe_allow_html=True)
