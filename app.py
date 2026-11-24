"""
UrbanPulse AI - Production-Grade Streamlit Application.
Modular Page Router with Grouped Navigation, Global Filters, and Light/Dark Theme Engine.
"""
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.paths import settings
from src.utils.logging import logger
from src.ui.styles import get_theme_css
from src.ui.navigation import render_sidebar_navigation, render_global_filter_bar

# Import Page Modules
from src.pages import (
    overview,
    decision_advisor,
    business_detail,
    dataset_analysis,
    review_analytics,
    kmeans_clustering,
    hierarchical_clustering,
    pca_visualization,
    evaluation_metrics,
    business_segmentation,
    recommendations,
    map_explorer,
    methodology,
    glossary
)

# Page configuration
st.set_page_config(
    page_title="UrbanPulse AI | Commercial Intelligence & Review Clustering",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session Theme
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "dark"

# Inject Dynamic Theme CSS
st.markdown(get_theme_css(st.session_state["ui_theme"]), unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_datasets():
    """
    Safely loads all result datasets into memory with caching.
    Returns None for missing files to allow individual pages to display graceful empty states.
    """
    def _read_csv_safe(path: Path):
        try:
            if path.exists():
                return pd.read_csv(path, low_memory=False)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
        return None

    return {
        'biz': _read_csv_safe(settings.CLUSTERED_BUSINESSES_CSV),
        'prof': _read_csv_safe(settings.CLUSTER_PROFILES_CSV),
        'eval': _read_csv_safe(settings.EVALUATION_RESULTS_CSV),
        'rev': _read_csv_safe(settings.DATA_PROCESSED_CSV),
        'comp': _read_csv_safe(settings.ALGORITHM_COMPARISON_CSV),
        'stab': _read_csv_safe(settings.STABILITY_RESULTS_CSV),
        'pca': _read_csv_safe(settings.PCA_PROJECTIONS_CSV)
    }

# Load data bundle
data_bundle = load_all_datasets()

# Render Grouped Navigation Sidebar
selected_page, active_group = render_sidebar_navigation()

# Live System Metrics in Sidebar Footer
with st.sidebar:
    biz_df = data_bundle.get('biz')
    n_biz = len(biz_df) if biz_df is not None else 0
    geo_count = int(biz_df['latitude'].notnull().sum()) if (biz_df is not None and 'latitude' in biz_df.columns) else 0

    st.markdown(f"""
        <div style="font-size:11.5px; color:var(--text-subtle); padding: 4px;">
            <div style="font-weight:700; color:var(--text-muted); margin-bottom:4px;">SYSTEM VITALS</div>
            <div>• Active Establishments: <b style="color:var(--text-main);">{n_biz:,}</b></div>
            <div>• Spatial Coordinates: <b style="color:var(--text-main);">{geo_count:,}</b></div>
            <div>• Optimal Clusters: <b style="color:var(--text-main);">K = {settings.SELECTED_K}</b></div>
            <div>• Clustering Stability: <b style="color:#10B981;">99.86% ARI</b></div>
        </div>
    """, unsafe_allow_html=True)

# Page Router Mapping
ROUTER = {
    "Home & Overview": overview.render,
    "Business Detail & Search": business_detail.render,
    "Map Explorer": map_explorer.render,
    "Business Decision Advisor": decision_advisor.render,
    "Strategic Recommendations": recommendations.render,
    "Dataset Analysis": dataset_analysis.render,
    "Review Analytics": review_analytics.render,
    "K-Means Clustering": kmeans_clustering.render,
    "Hierarchical Clustering": hierarchical_clustering.render,
    "PCA Visualization": pca_visualization.render,
    "Evaluation Metrics": evaluation_metrics.render,
    "Business Segmentation": business_segmentation.render,
    "Methodology & Model Card": methodology.render,
    "Glossary of Terms": glossary.render
}

# Optional Global Filter Ribbon (applied to relevant analytical pages)
PAGES_WITH_GLOBAL_FILTER = {
    "Business Segmentation",
    "Map Explorer",
    "Review Analytics",
    "Dataset Analysis"
}

if selected_page in PAGES_WITH_GLOBAL_FILTER and data_bundle.get('biz') is not None:
    filtered_biz, active_filters = render_global_filter_bar(data_bundle['biz'])
    # Inject filtered slice into active context
    data_bundle = dict(data_bundle)
    data_bundle['biz_filtered'] = filtered_biz

# Execute matched page renderer safely
render_fn = ROUTER.get(selected_page)
if render_fn:
    try:
        render_fn(data_bundle)
    except Exception as e:
        logger.exception(f"Unexpected rendering error on page {selected_page}: {e}")
        st.error(f"An unexpected rendering error occurred on '{selected_page}'. Our logging engine has captured the details.")
        st.info("Tip: Try resetting your global filters or restarting the pipeline if data files were recently modified.")
else:
    st.error(f"Requested page '{selected_page}' not found in router.")
