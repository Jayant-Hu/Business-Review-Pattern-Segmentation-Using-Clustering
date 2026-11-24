"""
Centralized UI Styling, CSS rules, and Design System Tokens.
Supports Dark Navy SaaS theme and Modern Light theme with responsive variables.
"""

# Color Palette Tokens
THEME_DARK = {
    "--bg-base": "#0B1120",
    "--bg-panel": "rgba(17, 24, 39, 0.75)",
    "--bg-panel-solid": "#111827",
    "--bg-card": "linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(17, 24, 39, 0.8) 100%)",
    "--bg-card-hover": "rgba(30, 41, 59, 0.9)",
    "--border-subtle": "rgba(255, 255, 255, 0.08)",
    "--border-focus": "rgba(96, 165, 250, 0.4)",
    "--text-main": "#F8FAFC",
    "--text-muted": "#94A3B8",
    "--text-subtle": "#64748B",
    "--primary-blue": "#3B82F6",
    "--primary-blue-glow": "rgba(59, 130, 246, 0.2)",
    "--sidebar-bg": "#0D1527",
    "--badge-bg": "rgba(59, 130, 246, 0.15)",
    "--badge-border": "rgba(59, 130, 246, 0.3)",
    "--badge-text": "#60A5FA",
    "--card-shadow": "0 10px 30px rgba(0, 0, 0, 0.35)",
}

THEME_LIGHT = {
    "--bg-base": "#F8FAFC",
    "--bg-panel": "rgba(255, 255, 255, 0.9)",
    "--bg-panel-solid": "#FFFFFF",
    "--bg-card": "linear-gradient(145deg, #FFFFFF 0%, #F1F5F9 100%)",
    "--bg-card-hover": "#F8FAFC",
    "--border-subtle": "rgba(15, 23, 42, 0.1)",
    "--border-focus": "rgba(37, 99, 235, 0.5)",
    "--text-main": "#0F172A",
    "--text-muted": "#475569",
    "--text-subtle": "#94A3B8",
    "--primary-blue": "#2563EB",
    "--primary-blue-glow": "rgba(37, 99, 235, 0.15)",
    "--sidebar-bg": "#F1F5F9",
    "--badge-bg": "rgba(37, 99, 235, 0.1)",
    "--badge-border": "rgba(37, 99, 235, 0.25)",
    "--badge-text": "#1D4ED8",
    "--card-shadow": "0 4px 20px rgba(0, 0, 0, 0.08)",
}

SEGMENT_COLORS = {
    "High-Satisfaction Top Tier": "#10B981",       # Emerald Green
    "Moderate / Mixed Feedback": "#3B82F6",        # Royal Blue
    "High-Engagement Detailed Feedback": "#8B5CF6", # Violet
    "Critical Intervention / At-Risk": "#EF4444"   # Crimson
}

OPPORTUNITY_BADGES = {
    "Proven Market": {"bg": "rgba(16, 185, 129, 0.15)", "border": "rgba(16, 185, 129, 0.4)", "text": "#10B981"},
    "Underserved Gap": {"bg": "rgba(59, 130, 246, 0.15)", "border": "rgba(59, 130, 246, 0.4)", "text": "#60A5FA"},
    "Quality Gap": {"bg": "rgba(245, 158, 11, 0.15)", "border": "rgba(245, 158, 11, 0.4)", "text": "#F59E0B"},
    "Saturated": {"bg": "rgba(139, 92, 246, 0.15)", "border": "rgba(139, 92, 246, 0.4)", "text": "#C084FC"},
    "Weak Demand": {"bg": "rgba(239, 68, 68, 0.15)", "border": "rgba(239, 68, 68, 0.4)", "text": "#EF4444"},
}

def get_theme_css(theme_mode: str = "dark") -> str:
    """Generates dynamic CSS string with root custom properties for the selected theme."""
    tokens = THEME_DARK if theme_mode == "dark" else THEME_LIGHT
    css_vars = "\n".join([f"        {k}: {v};" for k, v in tokens.items()])

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
{css_vars}
    }}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-main);
    }}

    .stApp {{
        background-color: var(--bg-base);
    }}

    .main {{
        background: radial-gradient(circle at 10% 20%, rgba(17, 24, 39, 0.6) 0%, var(--bg-base) 90%);
    }}

    /* Hero header */
    .saas-header {{
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
        backdrop-filter: blur(12px);
    }}

    .breadcrumbs {{
        font-size: 11px;
        color: var(--text-subtle);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }}
    .breadcrumbs span.current {{
        color: var(--badge-text);
    }}

    .saas-badge {{
        display: inline-block;
        padding: 4px 12px;
        background: var(--badge-bg);
        border: 1px solid var(--badge-border);
        border-radius: 20px;
        color: var(--badge-text);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}

    .saas-title {{
        color: var(--text-main);
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
    }}

    .saas-subtitle {{
        color: var(--text-muted);
        font-size: 13.5px;
        margin-top: 6px;
        margin-bottom: 0;
        line-height: 1.5;
    }}

    /* Global Filter Ribbon */
    .global-filter-ribbon {{
        background: var(--bg-panel);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    /* Metric Cards */
    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: var(--card-shadow);
        transition: transform 0.2s ease, border-color 0.2s ease;
        position: relative;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        border-color: var(--border-focus);
    }}
    .metric-card-top {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }}
    .metric-label {{
        color: var(--text-muted);
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .metric-icon {{
        font-size: 18px;
        opacity: 0.85;
    }}
    .metric-value {{
        color: var(--text-main);
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 6px;
    }}
    .metric-delta {{
        font-size: 11.5px;
        color: #10B981;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 600;
    }}
    .metric-delta.negative {{
        color: #EF4444;
    }}
    .metric-tooltip {{
        font-size: 10.5px;
        color: var(--text-subtle);
        margin-top: 4px;
    }}

    /* Panels & Containers */
    .saas-panel {{
        background: var(--bg-panel);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
    }}

    .panel-header {{
        font-size: 15.5px;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .section-title {{
        font-size: 18px;
        font-weight: 800;
        color: var(--text-main);
        letter-spacing: -0.01em;
        margin-top: 10px;
        margin-bottom: 4px;
    }}
    .section-subtitle {{
        font-size: 12.5px;
        color: var(--text-muted);
        margin-bottom: 14px;
    }}

    /* Callout & Insights */
    .info-callout {{
        background: rgba(59, 130, 246, 0.08);
        border-left: 4px solid var(--primary-blue);
        border-radius: 0 10px 10px 0;
        padding: 12px 16px;
        margin: 12px 0 18px 0;
        font-size: 12.5px;
        color: var(--text-main);
        line-height: 1.5;
    }}
    .info-callout.warning {{
        background: rgba(245, 158, 11, 0.08);
        border-left-color: #F59E0B;
    }}
    .info-callout.success {{
        background: rgba(16, 185, 129, 0.08);
        border-left-color: #10B981;
    }}
    .info-callout.alert {{
        background: rgba(239, 68, 68, 0.08);
        border-left-color: #EF4444;
    }}

    /* Chart Container Card */
    .chart-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 18px 20px 14px 20px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
    }}
    .chart-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .chart-title {{
        font-size: 15px;
        font-weight: 700;
        color: var(--text-main);
    }}
    .chart-insight {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 10px;
        font-size: 11.5px;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .chart-insight b {{
        color: var(--text-main);
    }}

    /* Empty state card */
    .empty-state-card {{
        background: var(--bg-card);
        border: 1px dashed var(--border-subtle);
        border-radius: 14px;
        padding: 40px 24px;
        text-align: center;
        color: var(--text-muted);
        margin: 20px 0;
    }}
    .empty-state-icon {{
        font-size: 36px;
        margin-bottom: 12px;
    }}
    .empty-state-title {{
        font-size: 17px;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 6px;
    }}

    /* Quick Start & Onboarding Cards */
    .onboarding-card {{
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }}

    /* Sidebar Navigation */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-subtle);
    }}

    /* Footer styling */
    .saas-footer {{
        border-top: 1px solid var(--border-subtle);
        padding-top: 24px;
        margin-top: 48px;
        padding-bottom: 24px;
        font-size: 11.5px;
        color: var(--text-subtle);
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
</style>
"""

# Default backward-compatible stylesheet
CUSTOM_CSS = get_theme_css("dark")
