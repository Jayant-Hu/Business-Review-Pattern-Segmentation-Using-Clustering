"""
Page 10: Interactive Map Explorer.
Dual rendering:
1. Google Maps JavaScript API (with custom HTML embed, color markers, info windows, clustering).
2. Open-tile / PyDeck fallback with heatmap layer and hotspot ranking.
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
from src.ui.components import render_header, render_empty_state, render_footer
from src.ui.theme import (
    SEGMENT_COLORS,
    BG_SURFACE_1,
    BG_SURFACE_2,
    BORDER_HAIRLINE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    SILVER_PRIMARY,
    SIGNAL_RED
)
from src.utils.paths import settings
from src.services.analytics import compute_city_hotspots

def render(data_bundle):
    render_header(
        "Interactive Geospatial Map Explorer",
        "Geocoded business locations color-coded by cluster segment, density heatmap, and municipal hotspots.",
        badge="GEOSPATIAL INTELLIGENCE",
        breadcrumbs=["Platform", "Explore", "Map Explorer"]
    )

    biz_df = data_bundle.get('biz')
    if biz_df is None or 'latitude' not in biz_df.columns:
        render_empty_state("Geocoded Data Missing", "Run `python scripts/run_pipeline.py --step geocode` to populate coordinates.")
        return

    # Filter out rows with invalid or missing coordinates
    geo_df = biz_df.dropna(subset=['latitude', 'longitude']).copy()
    if geo_df.empty:
        render_empty_state("No Coordinates Found", "All latitude/longitude values are null. Run the geocoding pipeline step.")
        return

    # Check for Google Maps Key
    google_key = settings.get_google_maps_key()

    # Map Controls & Filters
    st.markdown(f"""
        <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:20px;">
            <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:14px;">
                Geospatial View Controls & Filters
            </div>
    """, unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.4])
    
    with f1:
        map_style = st.radio("Map Engine:", ["PyDeck / OpenStreetMap", "Google Maps JS"] if google_key else ["PyDeck / OpenStreetMap (Open Tile)"])
    with f2:
        layer_mode = st.selectbox("Layer Mode:", ["Color-Coded Markers", "Density Heatmap", "Marker & Heatmap Combined"])
    with f3:
        all_cities = ["All Cities"] + sorted([c for c in geo_df['city'].dropna().unique() if c != 'Unknown'])
        selected_city = st.selectbox("Filter City:", all_cities)
    with f4:
        all_segments = sorted(geo_df['cluster_name'].dropna().unique().tolist())
        selected_segments = st.multiselect("Segments:", all_segments, default=all_segments)

    # Apply filters
    filtered_geo = geo_df[geo_df['cluster_name'].isin(selected_segments)].copy()
    if selected_city != "All Cities":
        filtered_geo = filtered_geo[filtered_geo['city'] == selected_city]

    # Map stats
    geocoded_pct = (len(geo_df) / len(biz_df)) * 100.0 if len(biz_df) > 0 else 0
    st.markdown(f"""
        <div style="font-size:12px; color:{TEXT_MUTED}; font-family:var(--font-mono); margin-bottom:6px;">
            Displaying {len(filtered_geo):,} of {len(geo_df):,} geocoded establishments ({geocoded_pct:.1f}% spatial coverage).
            {"<span style='color:" + SILVER_PRIMARY + "; margin-left:10px;'>● Google Maps API Active</span>" if google_key else "<span style='color:" + TEXT_MUTED + "; margin-left:10px;'>● Dark Tile Layer Active</span>"}
        </div>
        </div>
    """, unsafe_allow_html=True)

    # Render Map
    if "Google Maps" in map_style and google_key:
        _render_google_maps(filtered_geo, google_key)
    else:
        _render_pydeck_map(filtered_geo, layer_mode)

    st.markdown("<br>", unsafe_allow_html=True)

    # Hotspot Analysis Table
    col_l, col_r = st.columns([1.5, 1.0])
    with col_l:
        st.markdown(f"""
            <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:20px;">
                <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:12px;">
                    Municipal Hotspot Concentration
                </div>
        """, unsafe_allow_html=True)
        hotspots = compute_city_hotspots(biz_df)
        if not hotspots.empty:
            st.dataframe(hotspots, use_container_width=True)
            csv_hotspots = hotspots.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download City Hotspots (CSV)",
                data=csv_hotspots,
                file_name="city_hotspots_report.csv",
                mime="text/csv"
            )
        else:
            st.info("City hotspot data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown(f"""
            <div style="background:{BG_SURFACE_1}; border:1px solid {BORDER_HAIRLINE}; border-radius:4px; padding:20px; margin-bottom:20px;">
                <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY}; margin-bottom:12px;">
                    Establishment Dossier Inspector
                </div>
        """, unsafe_allow_html=True)
        if not filtered_geo.empty:
            sample_biz = filtered_geo.iloc[0]
            st.markdown(f"""
                <div style="font-family:var(--font-serif); font-size:16px; font-weight:600; color:{TEXT_PRIMARY};">{sample_biz['place']}</div>
                <div style="font-size:12px; color:{SILVER_PRIMARY}; margin-bottom:8px; font-family:var(--font-sans);">{sample_biz['place type']} • {sample_biz['city']}</div>
                <div style="font-size:12px; color:{TEXT_SECONDARY}; line-height:1.6;">
                    <b>Address:</b> {sample_biz['address']}<br>
                    <b>Segment:</b> <span style="color:{SEGMENT_COLORS.get(sample_biz['cluster_name'], SILVER_PRIMARY)}; font-weight:600;">{sample_biz['cluster_name']}</span><br>
                    <b>Rating:</b> {sample_biz['avg_rating']:.1f} ({sample_biz['sample_review_count']} reviews)<br>
                    <b>Positive:</b> {sample_biz['positive_review_pct']:.1f}% | <b>Negative:</b> {sample_biz['negative_review_pct']:.1f}%
                </div>
            """, unsafe_allow_html=True)
            
            # Google Maps Directions link
            lat = sample_biz['latitude']
            lng = sample_biz['longitude']
            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            st.markdown(f'<div style="margin-top:12px;"><a href="{gmaps_url}" target="_blank" style="color:{SILVER_PRIMARY}; font-size:12px; text-decoration:none;">Open in Google Maps ↗</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    render_footer()

def _render_pydeck_map(df: pd.DataFrame, layer_mode: str):
    """Renders performant PyDeck map with custom dark charcoal theme."""
    # Define RGB color tuple for each segment in the restrained palette
    color_map = {
        'High-Satisfaction Top Tier': [230, 233, 238, 220],          # Moonlit Silver Top
        'Moderate / Mixed Feedback': [154, 161, 172, 220],           # Silver Muted
        'High-Engagement Detailed Feedback': [107, 122, 143, 220],   # Slate Neutral
        'Critical Intervention / At-Risk': [229, 56, 59, 230]        # Signal Red
    }
    
    render_df = df.copy()
    render_df['color'] = render_df['cluster_name'].map(lambda x: color_map.get(x, [142, 150, 163, 200]))
    
    # Calculate center coordinates
    center_lat = float(render_df['latitude'].mean()) if not render_df.empty else 24.7136
    center_lng = float(render_df['longitude'].mean()) if not render_df.empty else 46.6753
    
    layers = []
    
    if "Markers" in layer_mode:
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=render_df,
            get_position=["longitude", "latitude"],
            get_color="color",
            get_radius=120,
            pickable=True,
            auto_highlight=True
        )
        layers.append(scatter_layer)
        
    if "Heatmap" in layer_mode:
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=render_df,
            get_position=["longitude", "latitude"],
            get_weight="sample_review_count",
            radius_pixels=40
        )
        layers.append(heatmap_layer)

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lng,
        zoom=9,
        pitch=0
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "{place}\nCategory: {place type}\nSegment: {cluster_name}\nAvg Rating: {avg_rating}"}
    )
    st.pydeck_chart(deck)

def _render_google_maps(df: pd.DataFrame, api_key: str):
    """Embeds native Google Maps JavaScript API with clustered markers."""
    center_lat = float(df['latitude'].mean()) if not df.empty else 24.7136
    center_lng = float(df['longitude'].mean()) if not df.empty else 46.6753
    
    # Prepare JSON data for markers (limit to 1000 for browser DOM performance)
    subset = df.head(1000)
    markers_json = subset[['place', 'latitude', 'longitude', 'cluster_name', 'avg_rating', 'place type']].to_json(orient='records')
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          #map {{ height: 520px; width: 100%; border-radius: 4px; border: 1px solid {BORDER_HAIRLINE}; }}
        </style>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=visualization"></script>
        <script src="https://unpkg.com/@googlemaps/markerclusterer/dist/index.min.js"></script>
      </head>
      <body>
        <div id="map"></div>
        <script>
          const locations = {markers_json};
          const colorMap = {{
            'High-Satisfaction Top Tier': '{TEXT_PRIMARY}',
            'Moderate / Mixed Feedback': '{TEXT_SECONDARY}',
            'High-Engagement Detailed Feedback': '{SILVER_SOFT}',
            'Critical Intervention / At-Risk': '{SIGNAL_RED}'
          }};

          function initMap() {{
            const center = {{ lat: {center_lat}, lng: {center_lng} }};
            const map = new google.maps.Map(document.getElementById("map"), {{
              zoom: 10,
              center: center,
              styles: [
                {{ elementType: "geometry", stylers: [{{ color: "{BG_DARK}" }}] }},
                {{ elementType: "labels.text.stroke", stylers: [{{ color: "{BG_DARK}" }}] }},
                {{ elementType: "labels.text.fill", stylers: [{{ color: "{TEXT_SECONDARY}" }}] }},
                {{ featureType: "road", elementType: "geometry", stylers: [{{ color: "{BG_SURFACE_2}" }}] }}
              ]
            }});

            const infoWindow = new google.maps.InfoWindow();
            const markers = locations.map(loc => {{
              const color = colorMap[loc.cluster_name] || '{SILVER_PRIMARY}';
              const marker = new google.maps.Marker({{
                position: {{ lat: loc.latitude, lng: loc.longitude }},
                title: loc.place,
                icon: {{
                  path: google.maps.SymbolPath.CIRCLE,
                  scale: 6,
                  fillColor: color,
                  fillOpacity: 0.9,
                  strokeWeight: 1,
                  strokeColor: '{BORDER_HAIRLINE}'
                }}
              }});

              marker.addListener("click", () => {{
                infoWindow.setContent(`
                  <div style="font-family:sans-serif; padding:6px; color:{BG_DARK};">
                    <b>${{loc.place}}</b><br>
                    <span style="font-size:12px; color:{TEXT_MUTED};">${{loc.place type}}</span><br>
                    <b>Rating:</b> ${{loc.avg_rating}}<br>
                    <b>Segment:</b> ${{loc.cluster_name}}
                  </div>
                `);
                infoWindow.open(map, marker);
              }});
              return marker;
            }});

            new markerClusterer.MarkerClusterer({{ map, markers }});
          }}
          window.onload = initMap;
        </script>
      </body>
    </html>
    """
    st.components.v1.html(html_code, height=540)
