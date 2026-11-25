"""
Restrained Grouped Navigation and Global Filter Ribbon.
Features editorial brand block, signal red active markers, and cross-page state filtering.
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import streamlit as st

PAGE_GROUPS = {
    "Overview": [
        "Home & Overview"
    ],
    "Explore": [
        "Business Detail & Search",
        "Map Explorer"
    ],
    "Decision Engine": [
        "Business Decision Advisor",
        "Strategic Recommendations"
    ],
    "Clustering Models": [
        "K-Means Clustering",
        "Hierarchical Clustering",
        "PCA Visualization",
        "Evaluation Metrics"
    ],
    "Data & Segmentation": [
        "Business Segmentation",
        "Dataset Analysis",
        "Review Analytics"
    ],
    "Methodology": [
        "Methodology & Model Card",
        "Glossary of Terms"
    ]
}

def render_sidebar_navigation() -> Tuple[str, str]:
    """
    Renders grouped sidebar navigation with active signal red indicator
    and theme toggle.
    """
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home & Overview"
    if "ui_theme" not in st.session_state:
        st.session_state["ui_theme"] = "dark"

    with st.sidebar:
        # Editorial Brand Block
        st.markdown("""
            <div style="padding: 16px 4px 20px 4px;">
                <div style="font-family:var(--font-serif); font-size:20px; font-weight:700; color:var(--text-primary); letter-spacing:-0.03em;">
                    UrbanPulse<span style="color:var(--red); font-size:24px; line-height:0;">.</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono); margin-top:3px; letter-spacing:0.04em;">
                    Review Pattern Segmentation
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Light / Dark theme switch
        t_c1, t_c2 = st.columns([0.65, 0.35])
        with t_c1:
            st.caption("Theme")
        with t_c2:
            is_light = st.toggle("Light", value=(st.session_state["ui_theme"] == "light"), key="nav_theme_toggle")
            new_theme = "light" if is_light else "dark"
            if new_theme != st.session_state["ui_theme"]:
                st.session_state["ui_theme"] = new_theme
                st.rerun()

        st.markdown("<hr style='border:0; border-top:1px solid var(--border); margin:12px 0 16px 0;'>", unsafe_allow_html=True)

        # Flattened page list for selection
        all_pages = []
        page_to_group = {}
        for group, pages in PAGE_GROUPS.items():
            for p in pages:
                all_pages.append(p)
                page_to_group[p] = group

        curr_page = st.session_state["current_page"]
        default_idx = all_pages.index(curr_page) if curr_page in all_pages else 0

        # Render styled radio navigation
        st.markdown("<div class='nav-group-header'>Navigation Modules</div>", unsafe_allow_html=True)
        selected_page = st.radio(
            "Navigation Modules",
            options=all_pages,
            index=default_idx,
            label_visibility="collapsed"
        )
        st.session_state["current_page"] = selected_page
        active_group = page_to_group.get(selected_page, "Overview")

        st.markdown("<hr style='border:0; border-top:1px solid var(--border); margin:18px 0 14px 0;'>", unsafe_allow_html=True)

    return selected_page, active_group

def render_global_filter_bar(biz_df: Optional[pd.DataFrame]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Persistent filter bar with minimal hairline styling and session state preservation."""
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

    cities = ["All Cities"] + sorted([c for c in biz_df['city'].dropna().unique() if c != 'Unknown'])
    categories = ["All Categories"] + sorted([c for c in biz_df['place type'].dropna().unique()])
    segments = ["All Segments"] + sorted([c for c in biz_df['cluster_name'].dropna().unique() if c])

    with st.expander(f"Data Filter: {gf['city']} • {gf['category']} • {gf['segment']}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([0.25, 0.25, 0.25, 0.15, 0.1])
        with c1:
            c_idx = cities.index(gf["city"]) if gf["city"] in cities else 0
            sel_city = st.selectbox("Location", cities, index=c_idx, key="gf_city")
        with c2:
            cat_idx = categories.index(gf["category"]) if gf["category"] in categories else 0
            sel_cat = st.selectbox("Category", categories, index=cat_idx, key="gf_cat")
        with c3:
            s_idx = segments.index(gf["segment"]) if gf["segment"] in segments else 0
            sel_seg = st.selectbox("Segment", segments, index=s_idx, key="gf_seg")
        with c4:
            max_rev = int(biz_df['sample_review_count'].max()) if 'sample_review_count' in biz_df.columns else 500
            sel_min_rev = st.number_input("Min Reviews", min_value=1, max_value=max(10, max_rev), value=gf["min_reviews"], key="gf_min_rev")
        with c5:
            st.write("")
            st.write("")
            if st.button("Reset", key="gf_reset_btn", use_container_width=True):
                st.session_state["global_filters"] = {
                    "city": "All Cities",
                    "category": "All Categories",
                    "segment": "All Segments",
                    "min_reviews": 1
                }
                st.rerun()

        st.session_state["global_filters"] = {
            "city": sel_city,
            "category": sel_cat,
            "segment": sel_seg,
            "min_reviews": sel_min_rev
        }
        gf = st.session_state["global_filters"]

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
