"""
UrbanPulse AI - Production-Grade Streamlit Application.
Thin Entrypoint and Modular Page Router.
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
from src.ui.styles import CUSTOM_CSS

# Import Page Modules
from src.pages import (
    overview,
    decision_advisor,
    dataset_analysis,
    review_analytics,
    kmeans_clustering,
    hierarchical_clustering,
    pca_visualization,
    evaluation_metrics,
    business_segmentation,
    recommendations,
    map_explorer
)

# Page configuration
st.set_page_config(
    page_title="UrbanPulse AI | Business Review Pattern Segmentation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom SaaS CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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

# Minimal SaaS Sidebar Navigation
with st.sidebar:
    st.markdown("""
        <div style="padding: 12px 4px 18px 4px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:18px; font-weight:bold;">⚡</div>
                <div>
                    <div style="font-weight:800; font-size:17px; color:#F8FAFC; letter-spacing:-0.02em;">UrbanPulse AI</div>
                    <div style="font-size:11px; color:#64748B; font-weight:500;">City Intelligence Platform</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    page_selection = st.radio(
        "Navigation",
        [
            "1. Overview",
            "2. Business Advisor (Decision Engine)",
            "3. Dataset Analysis",
            "4. Review Analytics",
            "5. K-Means Clustering",
            "6. Hierarchical Clustering",
            "7. PCA Visualization",
            "8. Evaluation Metrics",
            "9. Business Segmentation",
            "10. Recommendations",
            "11. Map Explorer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Compute live summary metrics for sidebar footer
    biz_df = data_bundle['biz']
    n_biz = len(biz_df) if biz_df is not None else 0
    geo_count = biz_df['latitude'].notnull().sum() if (biz_df is not None and 'latitude' in biz_df.columns) else 0
    
    st.markdown(f"""
        <div style="font-size:11.5px; color:#64748B; padding: 4px;">
            <div style="font-weight:700; color:#94A3B8; margin-bottom:4px;">SYSTEM METRICS</div>
            <div>• Active Businesses: <b>{n_biz:,}</b></div>
            <div>• Geocoded Locations: <b>{geo_count:,}</b></div>
            <div>• Optimal Segments: <b>K = {settings.SELECTED_K}</b></div>
            <div>• Engine: <b>Production Sklearn</b></div>
        </div>
    """, unsafe_allow_html=True)

# Page Router
ROUTER = {
    "1. Overview": overview.render,
    "2. Business Advisor (Decision Engine)": decision_advisor.render,
    "3. Dataset Analysis": dataset_analysis.render,
    "4. Review Analytics": review_analytics.render,
    "5. K-Means Clustering": kmeans_clustering.render,
    "6. Hierarchical Clustering": hierarchical_clustering.render,
    "7. PCA Visualization": pca_visualization.render,
    "8. Evaluation Metrics": evaluation_metrics.render,
    "9. Business Segmentation": business_segmentation.render,
    "10. Recommendations": recommendations.render,
    "11. Map Explorer": map_explorer.render
}

# Execute matched page renderer
render_fn = ROUTER.get(page_selection)
if render_fn:
    render_fn(data_bundle)
else:
    st.error(f"Unknown page: {page_selection}")
