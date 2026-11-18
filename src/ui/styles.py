"""
Centralized UI Styling, CSS rules, and Color System.
Delivers a high-contrast dark-navy SaaS aesthetic.
"""

# Color Palette Constants
COLOR_NAVY_BG = "#0B1120"
COLOR_NAVY_PANEL = "rgba(17, 24, 39, 0.75)"
COLOR_PRIMARY_BLUE = "#3B82F6"
COLOR_ACCENT_GREEN = "#10B981"
COLOR_ACCENT_AMBER = "#F59E0B"
COLOR_ACCENT_RED = "#EF4444"
COLOR_ACCENT_PURPLE = "#8B5CF6"
COLOR_TEXT_MAIN = "#F8FAFC"
COLOR_TEXT_MUTED = "#94A3B8"

SEGMENT_COLORS = {
    "High-Satisfaction Top Tier": "#10B981",       # Emerald Green
    "Moderate / Mixed Feedback": "#3B82F6",        # Royal Blue
    "High-Engagement Detailed Feedback": "#8B5CF6", # Violet
    "Critical Intervention / At-Risk": "#EF4444"   # Crimson
}

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

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

    /* Metric Card */
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

    /* Panels */
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

    /* Empty state card */
    .empty-state-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 36px 20px;
        text-align: center;
        color: #94A3B8;
        margin: 20px 0;
    }
    .empty-state-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }
    .empty-state-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 6px;
    }

    /* Sidebar minimal */
    section[data-testid="stSidebar"] {
        background-color: #0D1527 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
</style>
"""
