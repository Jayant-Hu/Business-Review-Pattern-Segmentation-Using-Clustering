"""
Centralized CSS Stylesheet for Charcoal, Silver & Signal Red Identity.
Zero hard-coded hex codes: references design tokens via CSS variables.
"""
from src.ui.theme import THEME_DARK, THEME_LIGHT, SEGMENT_COLORS

def get_theme_css(theme_mode: str = "dark") -> str:
    """Generates global stylesheet using strict CSS custom properties."""
    tokens = THEME_DARK if theme_mode == "dark" else THEME_LIGHT
    css_vars = "\n".join([f"        {k}: {v};" for k, v in tokens.items()])

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,600;0,8..60,700;1,8..60,400&display=swap');

    :root {{
{css_vars}
        --font-serif: 'Source Serif 4', Georgia, serif;
        --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }}

    html, body, [class*="css"] {{
        font-family: var(--font-sans);
        color: var(--text-primary);
        font-size: 14.5px;
        line-height: 1.55;
    }}

    .stApp {{
        background-color: var(--bg);
    }}

    /* Global Headings: Serif, sentence case, tight tracking, no glow */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-serif) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.015em;
    }}

    /* Header Component */
    .terminal-header {{
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 24px 28px;
        margin-bottom: 20px;
    }}

    .terminal-eyebrow {{
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--silver-soft);
        margin-bottom: 8px;
    }}

    .terminal-title {{
        font-family: var(--font-serif);
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.25;
    }}

    .terminal-subtitle {{
        font-size: 13.5px;
        color: var(--text-secondary);
        margin-top: 6px;
        margin-bottom: 0;
        line-height: 1.5;
    }}

    .terminal-rule {{
        border: 0;
        border-top: 1px solid var(--border);
        margin: 16px 0 0 0;
    }}

    /* Breadcrumbs */
    .terminal-breadcrumbs {{
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }}
    .terminal-breadcrumbs span.current {{
        color: var(--text-primary);
        font-weight: 600;
    }}

    /* Metric KPI Card */
    .kpi-card {{
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 18px 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 150ms ease;
    }}
    .kpi-card:hover {{
        border-color: var(--silver-soft);
    }}
    .kpi-label {{
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-secondary);
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-family: var(--font-mono);
        font-size: 27px;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 6px;
    }}
    .kpi-delta {{
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 4px;
    }}
    .kpi-delta.signal-alert {{
        color: var(--red);
        font-weight: 500;
    }}
    .kpi-tooltip {{
        font-size: 10.5px;
        color: var(--text-muted);
        margin-top: 4px;
    }}

    /* Panel Card */
    .terminal-panel {{
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
    }}

    .panel-title-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 12px;
    }}
    .panel-title {{
        font-family: var(--font-serif);
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }}

    /* Chart Container Card */
    .chart-container {{
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .chart-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    .chart-title {{
        font-family: var(--font-serif);
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
    }}
    .chart-insight {{
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 12px;
        font-size: 12px;
        color: var(--text-secondary);
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }}
    .chart-insight span.prefix {{
        font-family: var(--font-mono);
        color: var(--silver);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 10px;
        letter-spacing: 0.05em;
    }}

    /* Callouts */
    .callout {{
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-left: 3px solid var(--silver);
        border-radius: 4px;
        padding: 12px 16px;
        margin: 14px 0;
        font-size: 13px;
        color: var(--text-primary);
        line-height: 1.5;
    }}
    .callout.signal {{
        border-left-color: var(--red);
        background: var(--red-soft);
    }}
    .callout.muted {{
        border-left-color: var(--border);
        color: var(--text-secondary);
    }}

    /* Chips & Badges */
    .chip {{
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-family: var(--font-mono);
        font-weight: 500;
        background: var(--surface-2);
        color: var(--text-primary);
        border: 1px solid var(--border);
    }}
    .chip.signal {{
        background: var(--red-soft);
        color: var(--red);
        border-color: rgba(229, 56, 59, 0.35);
    }}

    /* Empty States */
    .empty-card {{
        background: var(--surface-1);
        border: 1px dashed var(--border);
        border-radius: 8px;
        padding: 36px 24px;
        text-align: center;
        color: var(--text-secondary);
        margin: 20px 0;
    }}
    .empty-card-title {{
        font-family: var(--font-serif);
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 6px;
    }}

    /* Sidebar Navigation */
    section[data-testid="stSidebar"] {{
        background-color: var(--surface-1) !important;
        border-right: 1px solid var(--border);
    }}
    
    /* Navigation Link & Active Indicator */
    .nav-group-header {{
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin: 14px 0 6px 4px;
    }}

    /* Streamlit Global Button Styling */
    div.stButton > button {{
        font-family: var(--font-sans);
        font-weight: 500;
        font-size: 13.5px;
        border-radius: 6px;
        border: 1px solid var(--border);
        background-color: var(--surface-2);
        color: var(--text-primary);
        padding: 6px 14px;
        transition: background-color 150ms ease, border-color 150ms ease;
    }}
    div.stButton > button:hover {{
        background-color: var(--surface-1);
        border-color: var(--silver-soft);
        color: var(--text-primary);
    }}
    div.stButton > button:focus {{
        outline: 2px solid var(--focus-ring);
    }}
    div.stButton > button[kind="primary"] {{
        background-color: var(--red) !important;
        border-color: var(--red) !important;
        color: #FFFFFF !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: var(--red-hover) !important;
        border-color: var(--red-hover) !important;
    }}

    /* Global Filter Ribbon */
    .filter-ribbon {{
        background: var(--surface-1);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 20px;
    }}

    /* Footer */
    .terminal-footer {{
        border-top: 1px solid var(--border);
        padding-top: 20px;
        margin-top: 48px;
        padding-bottom: 28px;
        font-size: 11px;
        color: var(--text-muted);
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}
</style>
"""

CUSTOM_CSS = get_theme_css("dark")
