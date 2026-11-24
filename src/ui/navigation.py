"""
Global Navigation, Grouped Sidebar Menu, and Persistent Cross-Page Filter Ribbon.
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import streamlit as st

PAGE_GROUPS = {
    "🧭 Explore": [
        "Home & Overview",
        "Business Detail & Search",
        "Map Explorer"
    ],
    "🎯 Decide": [
        "Business Decision Advisor",
        "Strategic Recommendations"
    ],
    "🔬 Analyze": [
        "Dataset Analysis",
        "Review Analytics",
        "K-Means Clustering",
        "Hierarchical Clustering",
        "PCA Visualization",
        "Evaluation Metrics",
        "Business Segmentation"
    ],
    "📚 Methodology": [
        "Methodology & Model Card",
        "Glossary of Terms"
    ]
}

PAGE_ICONS = {
    "Home & Overview": "⚡",
    "Business Detail & Search": "🔍",
    "Map Explorer": "🗺️",
    "Business Decision Advisor": "🎯",
    "Strategic Recommendations": "💡",
    "Dataset Analysis": "📊",
    "Review Analytics": "💬",
    "K-Means Clustering": "🔷",
    "Hierarchical Clustering": "🌳",
    "PCA Visualization": "📈",
    "Evaluation Metrics": "📏",
    "Business Segmentation": "👥",
    "Methodology & Model Card": "📋",
    "Glossary of Terms": "📖"
}

def render_sidebar_navigation() -> Tuple[str, str]:
    """
    Renders grouped sidebar navigation with category hierarchy, live system stats,
    and a Light/Dark theme toggle.
    Returns: (selected_page_name, active_group_name)
    """
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home & Overview"
    if "ui_theme" not in st.session_state:
        st.session_state["ui_theme"] = "dark"

    with st.sidebar:
        # Header Brand
        st.markdown("""
            <div style="padding: 10px 4px 16px 4px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:38px; height:38px; border-radius:10px; background:linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:20px; font-weight:bold; box-shadow:0 4px 12px rgba(59,130,246,0.3);">⚡</div>
                    <div>
                        <div style="font-weight:800; font-size:17.5px; color:var(--text-main); letter-spacing:-0.02em;">UrbanPulse AI</div>
                        <div style="font-size:11px; color:var(--text-muted); font-weight:600;">Commercial Intelligence Platform</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Light / Dark theme toggle
        t_col1, t_col2 = st.columns([0.6, 0.4])
        with t_col1:
            st.caption("Display Mode")
        with t_col2:
            is_light = st.toggle("☀️ Light", value=(st.session_state["ui_theme"] == "light"), key="theme_toggle")
            new_theme = "light" if is_light else "dark"
            if new_theme != st.session_state["ui_theme"]:
                st.session_state["ui_theme"] = new_theme
                st.rerun()

        st.markdown("<hr style='margin:10px 0; border-color:var(--border-subtle);'>", unsafe_allow_html=True)

        # Flat page selection with group headers for clean UX
        all_pages = []
        for group, pages in PAGE_GROUPS.items():
            all_pages.extend(pages)

        # Determine current index
        curr_page = st.session_state["current_page"]
        default_idx = all_pages.index(curr_page) if curr_page in all_pages else 0

        # Group Selector & Radio Navigation
        formatted_options = []
        page_to_group = {}
        for group, pages in PAGE_GROUPS.items():
            for p in pages:
                icon = PAGE_ICONS.get(p, "•")
                formatted_options.append(f"{icon} {p}")
                page_to_group[p] = group

        raw_selected = st.radio(
            "Navigation",
            options=formatted_options,
            index=default_idx,
            label_visibility="collapsed"
        )
        selected_page = raw_selected.split(" ", 1)[1] if " " in raw_selected else raw_selected
        st.session_state["current_page"] = selected_page
        active_group = page_to_group.get(selected_page, "Explore")

        st.markdown("<hr style='margin:14px 0 10px 0; border-color:var(--border-subtle);'>", unsafe_allow_html=True)

    return selected_page, active_group

def render_global_filter_bar(biz_df: Optional[pd.DataFrame]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Renders an expandable persistent filter bar at the top of pages.
    Persists selections across session state and returns filtered slice of biz_df.
    """
    if "global_filters" not in st.session_state:
        st.session_state["global_filters"] = {
            "city": "All Cities",
            "category": "All Categories",
            "segment": "All Segments",
            "min_reviews": 1
        }

    gf = st.session_state["global_filters"]

    if biz_df is None or biz_df.empty:
        return biz_df, gf

    # Extract filter choices
    cities = ["All Cities"] + sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
    categories = ["All Categories"] + sorted([c for c in biz_df['place type'].dropna().unique()])
    segments = ["All Segments"] + sorted([c for c in biz_df['cluster_name'].dropna().unique() if c])

    with st.expander(f"🌐 **Global Data Filter** (Active: {gf['city']}, {gf['category']}, {gf['segment']})", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([0.25, 0.25, 0.25, 0.15, 0.1])
        with c1:
            city_idx = cities.index(gf["city"]) if gf["city"] in cities else 0
            sel_city = st.selectbox("Location / City", cities, index=city_idx, key="gf_city")
        with c2:
            cat_idx = categories.index(gf["category"]) if gf["category"] in categories else 0
            sel_cat = st.selectbox("Category", categories, index=cat_idx, key="gf_cat")
        with c3:
            seg_idx = segments.index(gf["segment"]) if gf["segment"] in segments else 0
            sel_seg = st.selectbox("Assigned Segment", segments, index=seg_idx, key="gf_seg")
        with c4:
            max_rev = int(biz_df['sample_review_count'].max()) if 'sample_review_count' in biz_df.columns else 500
            sel_min_rev = st.number_input("Min Reviews", min_value=1, max_value=max(10, max_rev), value=gf["min_reviews"], key="gf_min_rev")
        with c5:
            st.write("")
            st.write("")
            if st.button("↺ Reset", key="gf_reset", use_container_width=True):
                st.session_state["global_filters"] = {
                    "city": "All Cities",
                    "category": "All Categories",
                    "segment": "All Segments",
                    "min_reviews": 1
                }
                st.rerun()

        # Update session state
        st.session_state["global_filters"] = {
            "city": sel_city,
            "category": sel_cat,
            "segment": sel_seg,
            "min_reviews": sel_min_rev
        }
        gf = st.session_state["global_filters"]

    # Apply filters to business dataframe
    filtered_df = biz_df.copy()
    if gf["city"] != "All Cities":
        filtered_df = filtered_df[filtered_df['city'] == gf["city"]]
    if gf["category"] != "All Categories":
        filtered_df = filtered_df[filtered_df['place type'] == gf["category"]]
    if gf["segment"] != "All Segments":
        filtered_df = filtered_df[filtered_df['cluster_name'] == gf["segment"]]
    if gf["min_reviews"] > 1 and 'sample_review_count' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sample_review_count'] >= gf["min_reviews"]]

    return filtered_df, gf
