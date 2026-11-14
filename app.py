"""
Business Review Pattern Segmentation & City-Service Analytics
Production-grade SaaS Dashboard
"""
import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from config import (
    CLUSTERED_BUSINESSES_CSV,
    CLUSTER_PROFILES_CSV,
    EVALUATION_RESULTS_CSV,
    PROCESSED_REVIEWS_CSV,
    OUTPUT_GRAPHS_DIR,
    OUTPUT_RESULTS_DIR
)

# Page configuration
st.set_page_config(
    page_title="UrbanPulse | Business Review Pattern Segmentation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Navy SaaS Custom CSS Styling
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container styling */
    .main {
        background: radial-gradient(circle at 10% 20%, rgba(17, 24, 39, 0.8) 0%, rgba(11, 17, 32, 1) 90%);
    }

    /* Hero header */
    .saas-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
    }

    .saas-badge {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        color: #60A5FA;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .saas-title {
        color: #F8FAFC;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .saas-subtitle {
        color: #94A3B8;
        font-size: 13.5px;
        margin-top: 6px;
        margin-bottom: 0;
        line-height: 1.5;
    }

    /* Stat Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(17, 24, 39, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.3);
    }
    .metric-label {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1;
        margin-bottom: 6px;
    }
    .metric-delta {
        font-size: 11.5px;
        color: #34D399;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Content Cards */
    .saas-panel {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .panel-header {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Sidebar Minimal styling */
    section[data-testid="stSidebar"] {
        background-color: #0D1527 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Plotly unified dark template
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    legend=dict(font=dict(color="#CBD5E1")),
    colorway=["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]
)

# Data Loader with caching
@st.cache_data
def load_data():
    biz = pd.read_csv(CLUSTERED_BUSINESSES_CSV) if os.path.exists(CLUSTERED_BUSINESSES_CSV) else None
    prof = pd.read_csv(CLUSTER_PROFILES_CSV) if os.path.exists(CLUSTER_PROFILES_CSV) else None
    ev = pd.read_csv(EVALUATION_RESULTS_CSV) if os.path.exists(EVALUATION_RESULTS_CSV) else None
    rev = pd.read_csv(PROCESSED_REVIEWS_CSV) if os.path.exists(PROCESSED_REVIEWS_CSV) else None
    
    # Load comparison & stability
    comp_path = os.path.join(OUTPUT_RESULTS_DIR, "algorithm_comparison.csv")
    comp = pd.read_csv(comp_path) if os.path.exists(comp_path) else None
    
    stab_path = os.path.join(OUTPUT_RESULTS_DIR, "stability_results.csv")
    stab = pd.read_csv(stab_path) if os.path.exists(stab_path) else None
    
    pca_path = os.path.join(OUTPUT_RESULTS_DIR, "pca_projections.csv")
    pca = pd.read_csv(pca_path) if os.path.exists(pca_path) else None
    
    return biz, prof, ev, rev, comp, stab, pca

biz_df, profiles_df, eval_df, rev_df, comp_df, stab_df, pca_df = load_data()

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
        <div style="padding: 12px 4px 20px 4px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:18px; font-weight:bold;">⚡</div>
                <div>
                    <div style="font-weight:800; font-size:17px; color:#F8FAFC; letter-spacing:-0.02em;">UrbanPulse AI</div>
                    <div style="font-size:11px; color:#64748B; font-weight:500;">City Intelligence Platform</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "1. Overview",
            "2. Dataset Analysis",
            "3. Review Analytics",
            "4. K-Means Clustering",
            "5. Hierarchical Clustering",
            "6. PCA Visualization",
            "7. Evaluation Metrics",
            "8. Business Segmentation",
            "9. Recommendations"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
        <div style="font-size:11.5px; color:#64748B; padding: 4px;">
            <div style="font-weight:700; color:#94A3B8; margin-bottom:4px;">PIPELINE STATUS</div>
            <div>• Real Records: <b>1.17M Raw</b></div>
            <div>• Sample Size: <b>10,000 Reviews</b></div>
            <div>• Businesses: <b>3,276 Entities</b></div>
            <div>• Selected K: <b>4 Optimal Segments</b></div>
            <div>• ARI Stability: <b>0.9899 (99.0%)</b></div>
        </div>
    """, unsafe_allow_html=True)

# Top Bar Header Function
def render_header(title, subtitle, badge="UNSUPERVISED ML INSIGHTS"):
    st.markdown(f"""
        <div class="saas-header">
            <span class="saas-badge">{badge}</span>
            <h1 class="saas-title">{title}</h1>
            <p class="saas-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 1: OVERVIEW
# -------------------------------------------------------------
if page == "1. Overview":
    render_header(
        "Business Review Pattern Segmentation",
        "Empirical pattern discovery and unsupervised clustering for city-wide commercial service optimization.",
        "EXECUTIVE BRIEFING"
    )

    # 4 Key SaaS Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Analyzed Businesses</div>
                <div class="metric-value">{len(biz_df):,}</div>
                <div class="metric-delta">✓ Verified composite (place, address)</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Processed Reviews</div>
                <div class="metric-value">{len(rev_df):,}</div>
                <div class="metric-delta">✓ PII Sanitized & Deduplicated</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Optimal Clusters</div>
                <div class="metric-value">K = 4</div>
                <div class="metric-delta">✓ Silhouette 0.4393 | DB 0.9999</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Clustering Stability</div>
                <div class="metric-value">98.99%</div>
                <div class="metric-delta">✓ Adjusted Rand Index across 5 seeds</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual layout: Cluster Breakdown Donut + Architecture Overview
    col_left, col_right = st.columns([1.2, 1.8])
    
    with col_left:
        st.markdown('<div class="saas-panel"><div class="panel-header">🎯 Segment Distribution</div>', unsafe_allow_html=True)
        if profiles_df is not None:
            fig_donut = px.pie(
                profiles_df,
                names='cluster_name',
                values='business_count',
                hole=0.62,
                color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#EF4444']
            )
            fig_donut.update_layout(**PLOTLY_LAYOUT)
            fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div class="saas-panel">
                <div class="panel-header">⚡ Architecture & Civic Impact</div>
                <p style="color:#94A3B8; font-size:13px; line-height:1.6;">
                    The platform transforms high-volume, unstructured Google Local customer reviews into actionable 
                    municipal intelligence. Instead of relying solely on arithmetic mean ratings, the engine captures 
                    multidimensional behavioral signatures: <b>satisfaction polarity</b>, <b>feedback depth</b>, 
                    <b>rating variance</b>, and <b>service mentions</b>.
                </p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:14px;">
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:12px; border-radius:10px;">
                        <div style="font-weight:700; color:#60A5FA; font-size:13px; margin-bottom:4px;">Municipal Tourism & Recognition</div>
                        <div style="font-size:12px; color:#94A3B8;">Identify top-performing establishments (1,836 units) for civic showcases and city guides.</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:12px; border-radius:10px;">
                        <div style="font-weight:700; color:#F87171; font-size:13px; margin-bottom:4px;">At-Risk Commercial Intervention</div>
                        <div style="font-size:12px; color:#94A3B8;">Detect 796 businesses with critical dissatisfaction to deploy targeted service and training subsidies.</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 2: DATASET ANALYSIS
# -------------------------------------------------------------
elif page == "2. Dataset Analysis":
    render_header(
        "Dataset Architecture & Integrity Analysis",
        "Inspection of raw schema, missing value patterns, and verified entity identification.",
        "DATA AUDITING"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Dataset Size", "1,170,000 Records", "19 Columns")
    c2.metric("Sampled Reviews", "10,000 Records", "Uniform Stratified")
    c3.metric("Reviewer/Entity Ratio", "969 Users / 3,276 Businesses", "Id = Reviewer")

    st.markdown("""
        <div class="saas-panel">
            <div class="panel-header">🔍 Critical Architectural Finding: Entity Resolution</div>
            <p style="color:#CBD5E1; font-size:13px; line-height:1.6;">
                A rigorous audit of the dataset confirmed that the column <code>Id</code> represents the <b>Reviewer Identifier</b>, 
                not the Business ID. Aggregating by <code>Id</code> would collapse hundreds of unique city shops into a single user's profile.
                To eliminate entity conflation, our pipeline engineered a composite business key: <code>(place, address)</code>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Missing & Placeholder Value Bar Chart
    placeholder_data = pd.DataFrame([
        {"Feature": "atmosphere", "Missing / Placeholder %": 97.56},
        {"Feature": "food", "Missing / Placeholder %": 97.08},
        {"Feature": "meal_type", "Missing / Placeholder %": 96.99},
        {"Feature": "service", "Missing / Placeholder %": 94.30},
        {"Feature": "number of videos", "Missing / Placeholder %": 62.51},
        {"Feature": "level", "Missing / Placeholder %": 33.24},
        {"Feature": "number of photos", "Missing / Placeholder %": 19.13},
        {"Feature": "en review (empty)", "Missing / Placeholder %": 17.22},
        {"Feature": "address", "Missing / Placeholder %": 0.04}
    ])

    fig_missing = px.bar(
        placeholder_data,
        x="Missing / Placeholder %",
        y="Feature",
        orientation="h",
        color="Missing / Placeholder %",
        color_continuous_scale="Reds",
        title="Proportion of Null & '0' Placeholder Values Across Features (%)"
    )
    fig_missing.update_layout(**PLOTLY_LAYOUT)
    fig_missing.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_missing, use_container_width=True)

# -------------------------------------------------------------
# PAGE 3: REVIEW ANALYTICS
# -------------------------------------------------------------
elif page == "3. Review Analytics":
    render_header(
        "Customer Review Distribution & Frequency",
        "Exploration of customer sentiment polarity, rating frequency, and industry place categories.",
        "BEHAVIORAL SIGNALS"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="saas-panel"><div class="panel-header">⭐ Customer Rating Distribution</div>', unsafe_allow_html=True)
        if rev_df is not None:
            rating_counts = rev_df['rating'].value_counts().sort_index().reset_index()
            rating_counts.columns = ['Rating', 'Reviews']
            fig_ratings = px.bar(
                rating_counts,
                x='Rating',
                y='Reviews',
                color='Rating',
                color_continuous_scale='Blues',
                text='Reviews'
            )
            fig_ratings.update_layout(**PLOTLY_LAYOUT)
            fig_ratings.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_ratings, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="saas-panel"><div class="panel-header">🏬 Top 10 Commercial Categories</div>', unsafe_allow_html=True)
        if rev_df is not None:
            top_cats = rev_df['place type'].value_counts().head(10).reset_index()
            top_cats.columns = ['Category', 'Reviews']
            fig_cats = px.bar(
                top_cats,
                x='Reviews',
                y='Category',
                orientation='h',
                color='Reviews',
                color_continuous_scale='Viridis'
            )
            fig_cats.update_layout(**PLOTLY_LAYOUT)
            fig_cats.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_cats, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 4: K-MEANS CLUSTERING
# -------------------------------------------------------------
elif page == "4. K-Means Clustering":
    render_header(
        "K-Means Partitioning & Hyperparameter Selection",
        "Evaluating Within-Cluster Sum of Squares (WCSS) and Silhouette cohesion across K = 2..7.",
        "MODEL OPTIMIZATION"
    )

    if eval_df is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="saas-panel"><div class="panel-header">📉 Elbow Curve (Inertia / WCSS)</div>', unsafe_allow_html=True)
            fig_elbow = go.Figure()
            fig_elbow.add_trace(go.Scatter(
                x=eval_df['k'],
                y=eval_df['WCSS'],
                mode='lines+markers',
                line=dict(color='#3B82F6', width=3),
                marker=dict(size=9, color='#60A5FA')
            ))
            fig_elbow.add_vline(x=4, line_width=2, line_dash="dash", line_color="#EF4444", annotation_text="Selected K=4")
            fig_elbow.update_layout(**PLOTLY_LAYOUT)
            fig_elbow.update_layout(xaxis_title="Number of Clusters (K)", yaxis_title="WCSS (Inertia)")
            st.plotly_chart(fig_elbow, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="saas-panel"><div class="panel-header">📐 Distance Metric Comparison: Silhouette</div>', unsafe_allow_html=True)
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Scatter(
                x=eval_df['k'],
                y=eval_df['Silhouette_Euclidean'],
                mode='lines+markers',
                name='Euclidean Distance',
                line=dict(color='#10B981', width=2.5),
                marker=dict(size=8)
            ))
            fig_dist.add_trace(go.Scatter(
                x=eval_df['k'],
                y=eval_df['Silhouette_Manhattan'],
                mode='lines+markers',
                name='Manhattan Distance',
                line=dict(color='#F59E0B', width=2.5, dash='dash'),
                marker=dict(size=8)
            ))
            fig_dist.update_layout(**PLOTLY_LAYOUT)
            fig_dist.update_layout(xaxis_title="Number of Clusters (K)", yaxis_title="Silhouette Score")
            st.plotly_chart(fig_dist, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="saas-panel"><div class="panel-header">📊 Quantitative Cluster Evaluation Metrics</div>', unsafe_allow_html=True)
        st.dataframe(eval_df.style.highlight_max(axis=0, subset=['Silhouette_Euclidean', 'Silhouette_Manhattan'], color='#1E3A8A'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 5: HIERARCHICAL CLUSTERING
# -------------------------------------------------------------
elif page == "5. Hierarchical Clustering":
    render_header(
        "Agglomerative Hierarchical Clustering",
        "Ward linkage dendrogram analysis and comparative benchmark against K-Means partitioning.",
        "TAXONOMICAL STRUCTURE"
    )

    col_l, col_r = st.columns([1.4, 1.0])
    with col_l:
        st.markdown('<div class="saas-panel"><div class="panel-header">🌳 Ward Linkage Dendrogram (Truncated to 30 Merges)</div>', unsafe_allow_html=True)
        dendro_path = os.path.join(OUTPUT_GRAPHS_DIR, "dendrogram.png")
        if os.path.exists(dendro_path):
            st.image(dendro_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="saas-panel"><div class="panel-header">⚖️ Benchmark: K-Means vs. Agglomerative</div>', unsafe_allow_html=True)
        if comp_df is not None:
            st.dataframe(comp_df, use_container_width=True)
        st.markdown("""
            <div style="font-size:12.5px; color:#94A3B8; line-height:1.6; margin-top:12px;">
                <b>Methodological Takeaways:</b><br>
                1. <b>Ward Linkage</b> minimizes the total within-cluster variance, matching the objective function of K-Means.<br>
                2. Both methods converge around <b>Silhouette ~ 0.43</b> and <b>Davies-Bouldin ~ 0.99</b>, verifying that the 4 clusters represent real underlying behavioral separations rather than algorithm-specific artifacts.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 6: PCA VISUALIZATION
# -------------------------------------------------------------
elif page == "6. PCA Visualization":
    render_header(
        "Principal Component Analysis (PCA)",
        "2D dimensionality reduction for visual inspection of cluster boundary separation.",
        "DIMENSIONAL PROJECTION"
    )

    if pca_df is not None and biz_df is not None:
        merged_pca = pca_df.merge(biz_df[['business_id', 'cluster_name', 'avg_rating', 'sample_review_count']], on='business_id', how='left')
        
        # Interactive Plotly PCA scatter
        fig_pca = px.scatter(
            merged_pca,
            x='PCA1',
            y='PCA2',
            color='cluster_name',
            hover_name='place',
            hover_data=['avg_rating', 'sample_review_count'],
            opacity=0.75,
            color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#EF4444'],
            title="Interactive 2D Principal Component Projection (Explained Variance: 53.63%)"
        )
        fig_pca.update_layout(**PLOTLY_LAYOUT)
        fig_pca.update_traces(marker=dict(size=6, line=dict(width=0.5, color='rgba(255,255,255,0.2)')))
        st.plotly_chart(fig_pca, use_container_width=True)
    else:
        pca_img = os.path.join(OUTPUT_GRAPHS_DIR, "pca_clusters.png")
        if os.path.exists(pca_img):
            st.image(pca_img, use_container_width=True)

# -------------------------------------------------------------
# PAGE 7: EVALUATION METRICS
# -------------------------------------------------------------
elif page == "7. Evaluation Metrics":
    render_header(
        "Quantitative Model Evaluation & Stability",
        "Mathematical rigor: WCSS, Silhouette Cohesion, Davies-Bouldin Index, and Adjusted Rand Index.",
        "ACADEMIC RIGOR"
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="saas-panel"><div class="panel-header">🛡️ Cluster Assignment Stability (Adjusted Rand Index)</div>', unsafe_allow_html=True)
        if stab_df is not None:
            fig_stab = px.bar(
                stab_df,
                x='seed_comparison',
                y='ARI',
                color='ARI',
                color_continuous_scale='Greens',
                range_y=[0.95, 1.0],
                text='ARI'
            )
            fig_stab.update_layout(**PLOTLY_LAYOUT)
            fig_stab.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_stab, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="saas-panel"><div class="panel-header">📉 Davies-Bouldin Index (Lower is Better)</div>', unsafe_allow_html=True)
        if eval_df is not None:
            fig_db = px.line(
                eval_df,
                x='k',
                y='Davies_Bouldin',
                markers=True,
                title="Davies-Bouldin Metric Across K=2..7"
            )
            fig_db.update_layout(**PLOTLY_LAYOUT)
            fig_db.update_traces(line_color="#EF4444")
            st.plotly_chart(fig_db, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 8: BUSINESS SEGMENTATION
# -------------------------------------------------------------
elif page == "8. Business Segmentation":
    render_header(
        "Commercial Business Segmentation & Profiles",
        "Discovered cluster behavioral baselines and interactive multi-parameter filtering.",
        "SEGMENT EXPLORER"
    )

    if profiles_df is not None:
        st.markdown('<div class="saas-panel"><div class="panel-header">📋 Empirical Cluster Behavioral Profiles</div>', unsafe_allow_html=True)
        st.dataframe(profiles_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Interactive filtering section
    if biz_df is not None:
        st.markdown('<div class="saas-panel"><div class="panel-header">🔍 Filter Businesses by Segment & Category</div>', unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns([1.5, 1.5, 1.0])
        with f1:
            cluster_filter = st.multiselect(
                "Filter Cluster Segment:",
                options=sorted(biz_df['cluster_name'].dropna().unique().tolist()),
                default=sorted(biz_df['cluster_name'].dropna().unique().tolist())
            )
        with f2:
            all_cats = sorted(biz_df['place type'].dropna().unique().tolist())
            category_filter = st.multiselect(
                "Filter Category:",
                options=all_cats,
                default=all_cats[:5] if len(all_cats) >= 5 else all_cats
            )
        with f3:
            min_rating_filter = st.slider("Min Avg Rating:", 1.0, 5.0, 1.0, 0.1)

        filtered_df = biz_df[
            (biz_df['cluster_name'].isin(cluster_filter)) &
            (biz_df['place type'].isin(category_filter)) &
            (biz_df['avg_rating'] >= min_rating_filter)
        ]

        st.markdown(f"**Found {len(filtered_df):,} matching establishments:**")
        cols_to_show = ['place', 'place type', 'address', 'cluster_name', 'avg_rating', 'sample_review_count', 'positive_review_pct', 'negative_review_pct']
        st.dataframe(filtered_df[cols_to_show], use_container_width=True)

        # Download button
        csv_data = filtered_df[cols_to_show].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Segment Report (CSV)",
            data=csv_data,
            file_name="segmented_businesses_report.csv",
            mime="text/csv"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 9: RECOMMENDATIONS
# -------------------------------------------------------------
elif page == "9. Recommendations":
    render_header(
        "City-Service Strategic Recommendations",
        "Targeted urban policy interventions, licensing audits, and tourism showcases derived from cluster patterns.",
        "CIVIC DECISION SUPPORT"
    )

    rec1, rec2 = st.columns(2)
    with rec1:
        st.markdown("""
            <div class="saas-panel" style="border-left: 4px solid #10B981;">
                <div style="font-weight:700; color:#10B981; font-size:15px; margin-bottom:8px;">
                    🏆 Cluster 0: High-Satisfaction Top Tier (1,836 Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Average rating of 4.57 ⭐, 98.9% positive reviews, and near-zero negative sentiment.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Feature in official Municipal Tourism Guides and city cultural showcases.</li>
                        <li>Engage business owners as mentors in local commerce mentorship programs.</li>
                        <li>Fast-track annual permit and outdoor seating approvals.</li>
                    </ul>
                </div>
            </div>
            
            <div class="saas-panel" style="border-left: 4px solid #8B5CF6;">
                <div style="font-weight:700; color:#8B5CF6; font-size:15px; margin-bottom:8px;">
                    💬 Cluster 2: High-Engagement Detailed Feedback (157 Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> 96.9% service mentions, 96.3% food mentions, long descriptive reviews.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Target for operational benchmarking and culinary excellence certifications.</li>
                        <li>Offer digital commerce grants to capitalize on highly engaged customer base.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with rec2:
        st.markdown("""
            <div class="saas-panel" style="border-left: 4px solid #3B82F6;">
                <div style="font-weight:700; color:#3B82F6; font-size:15px; margin-bottom:8px;">
                    ⚖️ Cluster 1: Moderate / Mixed Feedback (487 Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Mean rating 4.33 ⭐ with lower review volume and brief customer notes.<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Deploy Chamber of Commerce digital marketing and feedback collection workshops.</li>
                        <li>Encourage local neighborhood promotional campaigns to stimulate repeat foot traffic.</li>
                    </ul>
                </div>
            </div>

            <div class="saas-panel" style="border-left: 4px solid #EF4444;">
                <div style="font-weight:700; color:#EF4444; font-size:15px; margin-bottom:8px;">
                    🚨 Cluster 3: Critical Intervention / At-Risk (796 Businesses)
                </div>
                <div style="font-size:13px; color:#94A3B8; line-height:1.6;">
                    <b>Characteristics:</b> Severe dissatisfaction (Mean rating: 2.33 ⭐, 45.6% negative reviews).<br><br>
                    <b>Strategic Civic Actions:</b>
                    <ul>
                        <li>Conduct proactive health, sanitation, and licensing compliance audits.</li>
                        <li>Offer municipal employee training and service turnaround subsidies prior to license renewals.</li>
                        <li>Establish confidential diagnostic feedback sessions between inspectors and managers.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
