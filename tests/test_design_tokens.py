"""
Test suite to verify that the design system constraints are strictly adhered to:
1. No raw hex codes (e.g. #FFFFFF) exist in page modules (everything uses src/ui/theme.py tokens).
2. Theme tokens conform to WCAG contrast standards.
3. Theme tokens match the Charcoal, Silver & Signal Red specifications.
"""
import re
import glob
import os
import pytest
from src.ui import theme

def test_theme_tokens_defined():
    """Verify all primary tokens exist in src/ui/theme.py."""
    assert theme.BG_DARK == "#16181B"
    assert theme.BG_SURFACE_1 == "#1E2125"
    assert theme.BG_SURFACE_2 == "#262A2F"
    assert theme.BORDER_HAIRLINE == "#343941"
    assert theme.TEXT_PRIMARY == "#E6E9EE"
    assert theme.TEXT_SECONDARY == "#AEB4BD"
    assert theme.TEXT_MUTED == "#7C838E"
    assert theme.SILVER_PRIMARY == "#C9CED6"
    assert theme.SIGNAL_RED == "#E5383B"

def test_no_hardcoded_hex_in_pages():
    """Scan all page files to ensure no arbitrary hex codes are embedded."""
    page_files = glob.glob(os.path.join("src", "pages", "*.py"))
    assert len(page_files) > 0, "No page files found to test"

    # Regex for #RGB, #RRGGBB, #RRGGBBAA
    hex_pattern = re.compile(r'#[0-9a-fA-F]{3,8}')

    # Whitelist of permissible embedded snippets (e.g. in HTML string templates if unavoidable)
    # The requirement is that all styles are defined in theme.py or imported tokens.
    violations = []

    for filepath in page_files:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line_no, line in enumerate(lines, 1):
                # Exclude comment lines
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                # Search for hex codes
                matches = hex_pattern.findall(line)
                if matches:
                    # Filter out any non-color matches or harmless string literals
                    violations.append(f"{os.path.basename(filepath)}:{line_no} -> {matches} in line: {line.strip()[:60]}")

    if violations:
        pytest.fail("Discovered hardcoded hex codes in page files:\n" + "\n".join(violations))

def test_contrast_ratios():
    """Ensure text primary and secondary meet WCAG AA contrast ratio (> 4.5:1)."""
    def luminance(hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    def contrast(hex1, hex2):
        l1 = luminance(hex1)
        l2 = luminance(hex2)
        brightest = max(l1, l2)
        darkest = min(l1, l2)
        return (brightest + 0.05) / (darkest + 0.05)

    ratio_primary = contrast(theme.TEXT_PRIMARY, theme.BG_DARK)
    ratio_secondary = contrast(theme.TEXT_SECONDARY, theme.BG_DARK)
    ratio_red = contrast(theme.SIGNAL_RED, theme.BG_DARK)

    # WCAG 2.1 Level AA requires:
    # - 4.5:1 for normal text (Text Primary and Secondary)
    # - 3.0:1 for large text, graphical objects and user interface components (such as Signal Red accent markers)
    assert ratio_primary >= 4.5, f"Text Primary contrast ratio {ratio_primary:.2f} < 4.5"
    assert ratio_secondary >= 4.5, f"Text Secondary contrast ratio {ratio_secondary:.2f} < 4.5"
    assert ratio_red >= 3.0, f"Signal Red contrast ratio {ratio_red:.2f} < 3.0 (WCAG UI component threshold)"
