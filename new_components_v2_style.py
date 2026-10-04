"""Shared presentation contract for SCAPP Components v2.

This module is an adapter, not a new theme source of truth.

Ownership:
- Streamlit 1.64 native ``--st-*`` variables own generic colors, native fonts,
  ordinary radii, and host (main/sidebar) theme context.
- ``st_style.py`` owns established SCAPP control metrics that must match native
  Streamlit controls.
- ``assets_style.py`` owns shared reader/content/table metrics.
- Domain modules (for example dictionary assets) keep domain semantic colors
  and behavior.
- Individual Components v2 keep unique geometry/layout in component-local CSS.

Nothing in this module is applied globally. Components opt into the contract
through explicit ``data-scapp-*`` attributes under an application-owned root.
"""

from __future__ import annotations

from assets_style import (
    DL_READER_CELL_PADDING,
    DL_READER_CODE_FONT_SIZE,
    DL_READER_FONT_SIZE,
    DL_READER_GAP,
    DL_READER_LINE_HEIGHT,
    DL_READER_PANEL_PADDING,
    READER_FONT_WEIGHT,
    READER_ID_WIDTH,
    READER_LETTER_SPACING,
    READER_WORD_SPACING,
)
from st_style import STREAMLIT_WIDGET_CONTROL_HEIGHT, STREAMLIT_WIDGET_FONT_SIZE


COMPONENTS_V2_STYLE_CONTRACT_VERSION = 1

# Components-v2-specific geometry. These values codify the accepted SCAPP
# custom-control presentation; generic theme values remain native --st-*.
SCAPP_V2_CONTROL_LINE_HEIGHT = "1.25"
SCAPP_V2_CONTROL_PADDING_X = "12px"
SCAPP_V2_CONTROL_OPTION_MIN_HEIGHT = "2.2rem"
SCAPP_V2_CONTROL_OPTION_PADDING_Y = ".4rem"
SCAPP_V2_TOGGLE_RADIUS = "2px"
SCAPP_V2_CHECKED_FONT_WEIGHT = "500"
SCAPP_V2_CONTROL_TRANSITION = "background-color .2s ease, border-color .2s ease, color .2s ease"
SCAPP_V2_DISABLED_OPACITY = ".45"


def _root(root_selector: str) -> str:
    """Return a normalized app-owned root selector."""
    root = str(root_selector or "").strip()
    if not root:
        raise ValueError("root_selector must not be empty")
    return root


def build_components_v2_vars(root_selector: str) -> str:
    """Expose the shared SCAPP v2 contract as scoped CSS variables.

    Generic visual semantics intentionally point at Streamlit's native theme
    variables rather than Python copies. This lets the same component inherit
    the real main/sidebar theme context on Streamlit 1.64+.
    """
    root = _root(root_selector)
    return f"""{root} {{
    /* Native Streamlit 1.64 theme semantics. */
    --scapp-v2-bg: var(--st-background-color);
    --scapp-v2-bg-secondary: var(--st-secondary-background-color);
    --scapp-v2-text: var(--st-text-color);
    --scapp-v2-muted-text: color-mix(in srgb, var(--st-text-color) 70%, transparent);
    --scapp-v2-border: var(--st-border-color);
    --scapp-v2-control-border: var(--st-widget-border-color, var(--st-border-color));
    --scapp-v2-primary: var(--st-primary-color);
    --scapp-v2-font: var(--st-font);
    --scapp-v2-code-font: var(--st-code-font);
    --scapp-v2-code-bg: var(--st-code-background-color);
    --scapp-v2-base-radius: var(--st-base-radius);
    --scapp-v2-button-radius: var(--st-button-radius);
    --scapp-v2-dataframe-border: var(--st-dataframe-border-color, var(--st-border-color));
    --scapp-v2-dataframe-header-bg: var(--st-dataframe-header-background-color, var(--st-secondary-background-color));

    /* Canonical SCAPP control metrics from st_style.py. */
    --scapp-v2-control-font-size: {STREAMLIT_WIDGET_FONT_SIZE}px;
    --scapp-v2-control-height: {STREAMLIT_WIDGET_CONTROL_HEIGHT}px;

    /* Components-v2 shared control geometry. */
    --scapp-v2-control-line-height: {SCAPP_V2_CONTROL_LINE_HEIGHT};
    --scapp-v2-control-padding-x: {SCAPP_V2_CONTROL_PADDING_X};
    --scapp-v2-control-option-min-height: {SCAPP_V2_CONTROL_OPTION_MIN_HEIGHT};
    --scapp-v2-control-option-padding-y: {SCAPP_V2_CONTROL_OPTION_PADDING_Y};
    --scapp-v2-toggle-radius: {SCAPP_V2_TOGGLE_RADIUS};
    --scapp-v2-checked-font-weight: {SCAPP_V2_CHECKED_FONT_WEIGHT};
    --scapp-v2-disabled-opacity: {SCAPP_V2_DISABLED_OPACITY};

    /* Canonical content/table metrics from assets_style.py. */
    --scapp-v2-content-font-size: {DL_READER_FONT_SIZE};
    --scapp-v2-content-line-height: {DL_READER_LINE_HEIGHT};
    --scapp-v2-content-font-weight: {READER_FONT_WEIGHT};
    --scapp-v2-content-letter-spacing: {READER_LETTER_SPACING};
    --scapp-v2-content-word-spacing: {READER_WORD_SPACING};
    --scapp-v2-table-cell-padding: {DL_READER_CELL_PADDING};
    --scapp-v2-panel-padding: {DL_READER_PANEL_PADDING};
    --scapp-v2-panel-gap: {DL_READER_GAP};
    --scapp-v2-code-font-size: {DL_READER_CODE_FONT_SIZE};
    --scapp-v2-segment-id-width: {READER_ID_WIDTH};
}}"""


def build_components_v2_control_css(root_selector: str) -> str:
    """Return opt-in shared CSS for Components v2 controls.

    Markup contract:
    - ``data-scapp-control="button"``
    - ``data-scapp-control="select"``
    - ``data-scapp-control="input"``
    - ``data-scapp-control="toggle"`` with ``aria-pressed``
    - ``data-scapp-option`` for a custom option row

    Component-local classes may still own width, grid/flex placement, and other
    unique geometry. The shared contract owns only common visual/control
    metrics and state behavior.
    """
    root = _root(root_selector)
    control_selectors = [
        f'{root} [data-scapp-control="button"]',
        f'{root} [data-scapp-control="select"]',
        f'{root} [data-scapp-control="input"]',
        f'{root} [data-scapp-control="toggle"]',
    ]
    clickable_selectors = [
        f'{root} [data-scapp-control="button"]',
        f'{root} [data-scapp-control="toggle"]',
    ]
    input_like_selectors = [
        f'{root} [data-scapp-control="select"]',
        f'{root} [data-scapp-control="input"]',
    ]
    controls = ",\n".join(control_selectors)
    clickable = ",\n".join(clickable_selectors)
    input_like = ",\n".join(input_like_selectors)
    clickable_hover = ",\n".join(f"{selector}:hover:not(:disabled)" for selector in clickable_selectors)
    input_hover = ",\n".join(f"{selector}:hover:not(:disabled)" for selector in input_like_selectors)
    focus_visible = ",\n".join(f"{selector}:focus-visible" for selector in control_selectors)
    disabled = ",\n".join(f"{selector}:disabled" for selector in control_selectors)
    return f"""/* Shared single-line control contract. */
{controls} {{
    box-sizing: border-box;
    height: var(--scapp-v2-control-height);
    min-height: var(--scapp-v2-control-height);
    border: 1px solid var(--scapp-v2-control-border);
    color: var(--scapp-v2-text);
    background: var(--scapp-v2-bg);
    font-family: var(--scapp-v2-font);
    font-size: var(--scapp-v2-control-font-size);
    font-weight: 400;
    line-height: var(--scapp-v2-control-line-height);
    transition: {SCAPP_V2_CONTROL_TRANSITION};
}}

{clickable} {{
    padding: 0 var(--scapp-v2-control-padding-x);
    border-radius: var(--scapp-v2-button-radius);
    cursor: pointer;
}}

{input_like} {{
    padding: 0 var(--scapp-v2-control-padding-x);
    border-radius: var(--scapp-v2-base-radius);
}}

{root} [data-scapp-control="toggle"] {{
    border-radius: var(--scapp-v2-toggle-radius);
    color: var(--scapp-v2-muted-text);
}}

{root} [data-scapp-control="toggle"][aria-pressed="true"] {{
    background: var(--scapp-v2-bg-secondary);
    color: var(--scapp-v2-text);
    font-weight: var(--scapp-v2-checked-font-weight);
}}

{clickable_hover},
{input_hover} {{
    background: var(--scapp-v2-bg-secondary);
}}

{focus_visible} {{
    outline: 2px solid var(--scapp-v2-primary);
    outline-offset: 1px;
}}

{disabled} {{
    opacity: var(--scapp-v2-disabled-opacity);
    cursor: default;
}}

{root} [data-scapp-option] {{
    box-sizing: border-box;
    min-height: var(--scapp-v2-control-option-min-height);
    padding: var(--scapp-v2-control-option-padding-y) var(--scapp-v2-control-padding-x);
    border: 0;
    color: var(--scapp-v2-text);
    background: transparent;
    font-family: var(--scapp-v2-font);
    font-size: var(--scapp-v2-control-font-size);
    font-weight: 400;
    line-height: var(--scapp-v2-control-line-height);
    white-space: normal;
    overflow-wrap: anywhere;
}}

{root} [data-scapp-option]:hover,
{root} [data-scapp-option]:focus-visible,
{root} [data-scapp-option][aria-selected="true"] {{
    background: var(--scapp-v2-bg-secondary);
}}

{root} [data-scapp-option]:focus-visible {{
    outline: 2px solid var(--scapp-v2-primary);
    outline-offset: -2px;
}}"""


def build_components_v2_content_css(root_selector: str) -> str:
    """Return opt-in shared CSS for reader/content presentation.

    Markup contract:
    - ``data-scapp-content`` for reader/text content
    - ``data-scapp-panel`` when canonical reader panel spacing is desired
    - ``data-scapp-code`` for code/ID text
    - ``data-scapp-segment-id`` for the canonical segment-ID column

    Domain-specific emphasis, lookup colors, and unique component layout remain
    outside this helper.
    """
    root = _root(root_selector)
    return f"""{root} [data-scapp-content] {{
    color: var(--scapp-v2-text);
    background: var(--scapp-v2-bg);
    font-family: var(--scapp-v2-font);
    font-size: var(--scapp-v2-content-font-size);
    line-height: var(--scapp-v2-content-line-height);
    font-weight: var(--scapp-v2-content-font-weight);
    letter-spacing: var(--scapp-v2-content-letter-spacing);
    word-spacing: var(--scapp-v2-content-word-spacing);
}}

{root} [data-scapp-content] table,
{root} [data-scapp-content] th,
{root} [data-scapp-content] td {{
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    letter-spacing: inherit;
    word-spacing: inherit;
}}

{root} [data-scapp-panel] {{
    box-sizing: border-box;
    padding: var(--scapp-v2-panel-padding);
    gap: var(--scapp-v2-panel-gap);
}}

{root} [data-scapp-code],
{root} [data-scapp-segment-id] {{
    font-family: var(--scapp-v2-code-font);
    font-size: var(--scapp-v2-code-font-size);
}}

{root} [data-scapp-code] {{
    background: var(--scapp-v2-code-bg);
}}

{root} [data-scapp-segment-id] {{
    box-sizing: border-box;
    width: var(--scapp-v2-segment-id-width);
    min-width: var(--scapp-v2-segment-id-width);
    color: var(--scapp-v2-muted-text);
    white-space: nowrap;
    text-align: center;
}}"""


def build_components_v2_table_css(root_selector: str) -> str:
    """Return opt-in shared CSS for semantic content tables.

    Apply ``data-scapp-table`` to a table only when the component wants the
    canonical reader/content table presentation. This is intentionally
    different from a dataframe-like surface.
    """
    root = _root(root_selector)
    return f"""{root} table[data-scapp-table] {{
    border-collapse: collapse;
    color: var(--scapp-v2-text);
    background: var(--scapp-v2-bg);
    font-family: var(--scapp-v2-font);
    font-size: var(--scapp-v2-content-font-size);
    line-height: var(--scapp-v2-content-line-height);
}}

{root} table[data-scapp-table] th,
{root} table[data-scapp-table] td {{
    padding: var(--scapp-v2-table-cell-padding);
    border: 1px solid var(--scapp-v2-border);
    vertical-align: top;
}}

{root} table[data-scapp-table] thead th {{
    background: var(--scapp-v2-bg-secondary);
    font-weight: 600;
}}"""


def build_components_v2_dataframe_css(root_selector: str) -> str:
    """Return opt-in CSS for a dataframe-like table surface.

    Use this only when the component intentionally mirrors a Streamlit
    dataframe/table header treatment. Ordinary content tables should use
    :func:`build_components_v2_table_css`.
    """
    root = _root(root_selector)
    return f"""{root} table[data-scapp-dataframe] {{
    border-collapse: collapse;
    color: var(--scapp-v2-text);
    background: var(--scapp-v2-bg);
    font-family: var(--scapp-v2-font);
    font-size: var(--scapp-v2-control-font-size);
    line-height: var(--scapp-v2-control-line-height);
}}

{root} table[data-scapp-dataframe] th,
{root} table[data-scapp-dataframe] td {{
    padding: var(--scapp-v2-table-cell-padding);
    border: 1px solid var(--scapp-v2-dataframe-border);
}}

{root} table[data-scapp-dataframe] thead th {{
    background: var(--scapp-v2-dataframe-header-bg);
    font-weight: 600;
}}"""


def build_components_v2_style_css(
    root_selector: str,
    *,
    controls: bool = True,
    content: bool = True,
    tables: bool = True,
    dataframe: bool = False,
) -> str:
    """Compose the shared Components v2 style contract for one root.

    This function emits only scoped, opt-in rules. It does not restyle arbitrary
    component markup. Individual renderers decide which semantic data attributes
    to adopt during migration.
    """
    root = _root(root_selector)
    blocks = [build_components_v2_vars(root)]
    if controls:
        blocks.append(build_components_v2_control_css(root))
    if content:
        blocks.append(build_components_v2_content_css(root))
    if tables:
        blocks.append(build_components_v2_table_css(root))
    if dataframe:
        blocks.append(build_components_v2_dataframe_css(root))
    return "\n\n".join(blocks)


__all__ = [
    "COMPONENTS_V2_STYLE_CONTRACT_VERSION",
    "SCAPP_V2_CONTROL_LINE_HEIGHT",
    "SCAPP_V2_CONTROL_PADDING_X",
    "SCAPP_V2_CONTROL_OPTION_MIN_HEIGHT",
    "SCAPP_V2_CONTROL_OPTION_PADDING_Y",
    "SCAPP_V2_TOGGLE_RADIUS",
    "build_components_v2_vars",
    "build_components_v2_control_css",
    "build_components_v2_content_css",
    "build_components_v2_table_css",
    "build_components_v2_dataframe_css",
    "build_components_v2_style_css",
]
