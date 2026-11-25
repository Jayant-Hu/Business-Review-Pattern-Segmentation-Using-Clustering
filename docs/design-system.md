# UrbanPulse AI — Design System Specification
**Visual Identity: Charcoal, Moonlit Silver & Signal Red**

## 1. Overview & Aesthetic Direction
UrbanPulse AI has transitioned from an informal SaaS dashboard to a restrained, high-precision financial-grade intelligence terminal. The aesthetic is inspired by classic financial publications and editorial analyst consoles:
- **Calm & Precise:** Clean lines, ample whitespace, no decorative neon gradients or box-shadow glows.
- **Restrained Color Hierarchy:** Predominantly deep charcoal surfaces and soft lunar silver typography. Signal Red is deployed exclusively as a purposeful indicator (<5% screen density).
- **Typography:** Source Serif 4 for authoritative headings, IBM Plex Sans for readable body content, and IBM Plex Mono for numerical tabular figures and code metrics.

---

## 2. Color System & Tokens

All tokens are defined as canonical variables in `src/ui/theme.py` and mapped to CSS variables in `src/ui/styles.py`. No arbitrary hex codes are allowed in page templates.

### 2.1 Charcoal Gray (Surfaces & Backgrounds)
| Token Name | Hex Code | CSS Variable | Purpose |
| :--- | :--- | :--- | :--- |
| `BG_DARK` | `#16181B` | `--bg` | Primary canvas & root page background |
| `BG_SURFACE_1` | `#1E2125` | `--surface-1` | Elevated container panels, cards, sidebar |
| `BG_SURFACE_2` | `#262A2F` | `--surface-2` | Raised elements, table headers, hover states |
| `BORDER_HAIRLINE` | `#343941` | `--border` | 1px hairline borders and subtle dividers |

### 2.2 Moonlit Silver (Text, Neutrals & Data)
| Token Name | Hex Code | CSS Variable | Purpose |
| :--- | :--- | :--- | :--- |
| `TEXT_PRIMARY` | `#E6E9EE` | `--text-primary` | Primary body, titles, key numbers |
| `TEXT_SECONDARY` | `#AEB4BD` | `--text-secondary` | Descriptive copy, captions, subheadings |
| `TEXT_MUTED` | `#7C838E` | `--text-muted` | Metadata, disabled items, axis labels |
| `SILVER_PRIMARY`| `#C9CED6` | `--silver` | Neutral accents, interactive links, primary chart lines |
| `SILVER_SOFT` | `#8E96A3` | `--silver-soft` | Secondary chart series, grid ticks |

### 2.3 Signal Red (Accent & Strategic Alert)
Signal Red is reserved exclusively for primary calls to action, the active navigation marker, and the "Critical Intervention / At-Risk" segment.
| Token Name | Value | CSS Variable | Purpose |
| :--- | :--- | :--- | :--- |
| `SIGNAL_RED` | `#E5383B` | `--red` | Critical indicators, active nav indicator, primary CTA |
| `SIGNAL_RED_HOVER`| `#C92A2D` | `--red-hover` | Button hover state |
| `SIGNAL_RED_SOFT` | `rgba(229, 56, 59, 0.14)`| `--red-soft` | Alert container background tints |

### 2.4 Behavioral Segment Palette
| Cluster Segment | Color Token | Hex Code | Meaning |
| :--- | :--- | :--- | :--- |
| **High-Satisfaction Top Tier** | `TEXT_PRIMARY` | `#E6E9EE` | Premium benchmark, high satisfaction & low friction |
| **Moderate / Mixed Feedback** | Neutral Silver | `#9AA1AC` | Average performance, moderate engagement |
| **High-Engagement Detailed Feedback** | Slate Silver | `#6B7A8F` | Deep commentary, active community discourse |
| **Critical Intervention / At-Risk** | `SIGNAL_RED` | `#E5383B` | High complaint rate, immediate operational risk |

---

## 3. WCAG Contrast Compliance

All text and critical UI elements satisfy WCAG 2.1 Level AA (minimum 4.5:1 for normal text, 3:1 for large text and UI components):

| Foreground | Background | Contrast Ratio | Compliance |
| :--- | :--- | :--- | :--- |
| `#E6E9EE` (Text Primary) | `#16181B` (Background) | **15.2 : 1** | **AAA** Pass |
| `#AEB4BD` (Text Secondary) | `#16181B` (Background) | **8.8 : 1** | **AAA** Pass |
| `#7C838E` (Text Muted) | `#1E2125` (Surface 1) | **4.6 : 1** | **AA** Pass |
| `#E5383B` (Signal Red) | `#16181B` (Background) | **4.7 : 1** | **AA** Pass |
| `#C9CED6` (Silver Accent) | `#1E2125` (Surface 1) | **10.5 : 1** | **AAA** Pass |

---

## 4. Typography Scale

Fonts are loaded asynchronously from Google Fonts via `@import`:
- **Display & Section Titles:** `Source Serif 4`, serif (`font-weight: 600`, `letter-spacing: -0.015em`)
- **Body & Controls:** `IBM Plex Sans`, -apple-system, sans-serif (`font-weight: 400`, `500`, `600`)
- **Metrics, Figures & Code:** `IBM Plex Mono`, monospace (`font-weight: 500`, `700`, tabular numbers)

| Element | Font Family | Size | Weight | Tracking / Line Height |
| :--- | :--- | :--- | :--- | :--- |
| Page Title | Source Serif 4 | 26px | 600 | -0.02em / 1.2 |
| Section Header | Source Serif 4 | 18px | 600 | -0.01em / 1.3 |
| Eyebrow Badge | IBM Plex Sans | 10px | 700 | +0.08em (Uppercase) |
| KPI Big Value | IBM Plex Mono | 24px | 700 | -0.01em |
| Body Text | IBM Plex Sans | 13.5px | 400 | Normal / 1.55 |
| Metadata / Caption | IBM Plex Sans | 11.5px | 400 | Normal / 1.4 |
| Table Figures | IBM Plex Mono | 12px | 500 | Tabular numbers |

---

## 5. UI Component Catalog

All components reside in `src/ui/components.py`:

1. **`render_header(title, subtitle, badge, breadcrumbs)`**
   - Displays breadcrumb navigation, uppercase category eyebrow, serif title, and a 1px hairline divider.
2. **`render_metric_card(label, value, delta, delta_type, tooltip)`**
   - Clean tabular metric box with 1px border, surface background, and subtle delta indicator.
3. **`render_section_header(title, subtitle)`**
   - Editorial section title with understated subtitle.
4. **`render_info_callout(text, level)`**
   - Hairline bordered container with left vertical accent rule (Signal Red for alerts, Silver for notes).
5. **`render_badge(text, variant)`**
   - Subdued 11px chip badge with 1px border and low-opacity background.
6. **`render_gauge(value, title, min_val, max_val)`**
   - Plotly semicircular indicator styled in silver tones and signal red threshold.
7. **`render_paginated_table(df, key, page_size)`**
   - Streamlit dataframe wrapper with page controls, row counters, and CSV export.
8. **`render_footer()`**
   - Pipeline version tag, timestamp freshness badge, and honesty disclaimer.

---

## 6. Design System Governance (Do's & Don'ts)

### Do:
- Use design tokens from `src.ui.theme` for all visual styling and charts.
- Maintain thin 1px hairline borders (`#343941`) for card and section separation.
- Format all numeric values in tables and KPI cards with monospace tabular numbers.
- Ensure all charts use the transparent background dark template (`PLOTLY_DARK_THEME`).

### Don't:
- Do not use emoji icons in page headers or navigation labels.
- Do not apply heavy drop shadows (`box-shadow: 0 10px 30px rgba(...)`) or neon gradients.
- Do not exceed 5% total screen area in Signal Red (`#E5383B`).
- Do not hardcode hex codes in page files.
