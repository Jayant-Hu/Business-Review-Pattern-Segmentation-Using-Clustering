"""
Business Detail & Directory Search.
Provides real-time directory search, venue performance dossier, percentiles, and behavioral peers.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui.components import render_header, render_empty_state, render_footer, render_section_header
from src.ui.theme import SEGMENT_COLORS, get_plotly_theme, COLOR_SILVER, COLOR_RED
from src.services.decision_advisor import HONESTY_DISCLAIMER, extract_customer_voice
from src.services.business_lookup import (
    search_businesses,
    find_similar_businesses,
    calculate_local_percentile,
    generate_business_dossier_pdf
)

def render(data_bundle):
    render_header(
        title="Commercial Establishment Directory & Search",
        subtitle="Individual establishment profiles, local cohort percentiles, feature-space peer discovery, and dossier export.",
        eyebrow="BUSINESS DOSSIER",
        breadcrumbs=["Platform", "Explore", "Directory Search"]
    )

    biz_df = data_bundle.get('biz')
    rev_df = data_bundle.get('rev')

    if biz_df is None or biz_df.empty:
        render_empty_state(
            title="Business Data Missing",
            message="Run the clustering pipeline to generate clustered_businesses.csv.",
            action_command="python scripts/run_pipeline.py --step cluster"
        )
        render_footer()
        return

    # Search & Filter Controls
    st.markdown("""
        <div class="terminal-panel">
            <div class="panel-title-bar">
                <h3 class="panel-title">Establishment Search</h3>
            </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns([2.0, 1.2, 1.2])
    with col_s1:
        search_query = st.text_input("Search Name or Address", "", placeholder="Enter keyword...", label_visibility="collapsed")
    with col_s2:
        all_cities = ["All Cities"] + sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
        filter_city = st.selectbox("Location", all_cities, index=0, label_visibility="collapsed")
    with col_s3:
        all_cats = ["All Categories"] + sorted(biz_df['place type'].dropna().unique().tolist())
        filter_cat = st.selectbox("Category", all_cats, index=0, label_visibility="collapsed")

    # Filtered matches
    matches = search_businesses(biz_df, query=search_query, city_filter=filter_city, category_filter=filter_cat, limit=40)
    
    if matches.empty:
        st.warning("No establishments match your search criteria.")
        st.markdown('</div>', unsafe_allow_html=True)
        render_footer()
        return

    # Business selector dropdown
    match_options = {f"{r['place']} ({r['city']} - {r['place type']})": r['business_id'] for _, r in matches.iterrows()}
    selected_label = st.selectbox("Select establishment to inspect dossier:", list(match_options.keys()))
    target_id = match_options[selected_label]
    biz_row = biz_df[biz_df['business_id'] == target_id].iloc[0]
    st.markdown('</div>', unsafe_allow_html=True)

    # Establishment Hero Dossier Card
    seg_name = biz_row.get('cluster_name', 'Unassigned')
    seg_color = SEGMENT_COLORS.get(seg_name, COLOR_SILVER)

    st.markdown(f"""
        <div class="terminal-panel" style="border-top: 3px solid {seg_color};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="chip">{biz_row.get('place type', 'General')}</span>
                    <h2 style="font-size:24px; margin:6px 0 2px 0;">{biz_row['place']}</h2>
                    <div style="font-size:12.5px; color:var(--text-secondary);">{biz_row.get('address', 'Address not recorded')} • {biz_row.get('city', 'Unknown City')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:var(--font-mono); font-size:26px; font-weight:600; color:var(--text-primary);">{biz_row.get('avg_rating', 0.0):.2f} <span style="font-size:16px;">★</span></div>
                    <div style="font-size:12px; color:var(--text-muted); font-family:var(--font-mono);">{biz_row.get('sample_review_count', 0)} Community Reviews</div>
                    <div style="margin-top:4px;"><span class="chip" style="border-color:{seg_color}; color:{seg_color};">{seg_name}</span></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Local Percentiles & Cohort Standing
    pcts = calculate_local_percentile(biz_df, biz_row)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.metric(
            label="Category Percentile",
            value=f"Top {100.0 - pcts['category_percentile']:.1f}%",
            delta=f"Rank #{pcts['category_rank']} of {pcts['category_cohort_size']}"
        )
    with col_p2:
        st.metric(
            label="City Percentile",
            value=f"Top {100.0 - pcts['city_percentile']:.1f}%",
            delta=f"Rank #{pcts['city_rank']} of {pcts['city_cohort_size']}"
        )
    with col_p3:
        st.metric(
            label="Positive Sentiment Share",
            value=f"{biz_row.get('positive_review_pct', 0.0):.1f}%",
            delta="4★ and 5★ reviews"
        )
    with col_p4:
        st.metric(
            label="Rating Volatility (Std Dev)",
            value=f"±{biz_row.get('rating_std', 0.0):.2f}",
            delta="Consistency indicator"
        )

    # Detailed Analysis Tabs
    t_peers, t_voice, t_map, t_export = st.tabs([
        "Behavioral Peer Establishments",
        "Customer Review Voice",
        "Geographic Coordinate Pin",
        "Export Dossier"
    ])

    with t_peers:
        render_section_header("Nearest Behavioral Peers in 10-D Space", subtitle="Establishments exhibiting the closest multidimensional customer response profile")
        peers_df = find_similar_businesses(biz_df, target_business_id=target_id, top_n=5)
        if not peers_df.empty:
            st.dataframe(peers_df, use_container_width=True, hide_index=True)
            st.caption("Similarity distance is computed via Euclidean metric across the normalized 10-dimensional behavioral feature matrix.")
        else:
            st.info("Insufficient variance to calculate nearest behavioral peers.")

    with t_voice:
        render_section_header("Customer Voice & Aspect Mentions", subtitle="Extracted review themes and verified aspect ratings")
        if rev_df is not None and not rev_df.empty:
            voice = extract_customer_voice(rev_df, [biz_row['place']])
            cv1, cv2 = st.columns(2)
            with cv1:
                st.markdown("**Positive Theme Keywords:**")
                st.write(", ".join(voice['positive_keywords']) if voice['positive_keywords'] else "Standard praise")
                st.markdown("**Negative Friction Keywords:**")
                st.write(", ".join(voice['negative_keywords']) if voice['negative_keywords'] else "Minimal friction")
            with cv2:
                st.markdown("**Aspect Feedback Scores:**")
                for asp, sc in voice['aspects'].items():
                    val = f"{sc} ★" if sc is not None else "N/A"
                    st.write(f"• **{asp}**: {val}")
        else:
            st.info("Detailed transaction reviews not available for aspect extraction.")

    with t_map:
        render_section_header("Geographic Coordinate Pin", subtitle="Verified or centroid geocoded coordinates")
        lat = biz_row.get('latitude')
        lng = biz_row.get('longitude')
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
                    zoom=13,
                    height=380
                )
                fig_pin.update_layout(map_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            else:
                fig_pin = px.scatter_mapbox(
                    pin_df,
                    lat="latitude",
                    lon="longitude",
                    hover_name="place",
                    zoom=13,
                    height=380
                )
                fig_pin.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_pin, use_container_width=True)
            gmaps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            st.markdown(f'<a href="{gmaps_link}" target="_blank" style="font-size:12px; color:var(--silver); font-family:var(--font-mono);">Open in Google Maps</a>', unsafe_allow_html=True)
        else:
            st.info("Geographic coordinates unavailable for this establishment.")

    with t_export:
        render_section_header("Export Establishment Dossier", subtitle="Download structured report")
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            peers_export = find_similar_businesses(biz_df, target_business_id=target_id, top_n=5)
            pdf_bytes = generate_business_dossier_pdf(biz_row, pcts, peers_export)
            st.download_button(
                label="Download Dossier PDF",
                data=pdf_bytes,
                file_name=f"{biz_row['place'].replace(' ', '_')}_dossier.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        with c_ex2:
            row_csv = pd.DataFrame([biz_row]).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Metrics CSV",
                data=row_csv,
                file_name=f"{biz_row['place'].replace(' ', '_')}_metrics.csv",
                mime="text/csv",
                use_container_width=True
            )

    render_footer()
