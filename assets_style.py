"""Canonical shared content/reader/table presentation, independent of dictionaries.

Historical DL_READER_* symbol names stay available here and through the
compatibility exports of dict_lookup_assets. Dictionary data/CSS/JS stay there.
"""

from __future__ import annotations

from collections.abc import Iterable

# Canonical shared reader/content/table tokens. Dictionary modules import and
# re-export the historical DL_READER_* names for existing callers.
DL_READER_FONT_FAMILY = "'Source Sans', 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
DL_READER_MONO_FONT_FAMILY = "'SpaceMono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
DL_READER_FONT_SIZE = "1rem"
DL_READER_LINE_HEIGHT = "1.6"
DL_READER_CHANT_FONT_SIZE = "1.6rem"
DL_READER_CHANT_LINE_HEIGHT = "1.6"
DL_READER_CODE_FONT_SIZE = ".75rem"
DL_READER_CODE_BACKGROUND = "#ecebe4"
DL_READER_BG_MAIN = "#fdfdf8"
DL_READER_BG_SEC = "#ecebe3"
DL_READER_BG_SIDEBAR = "#f0f0ec"
DL_READER_BORDER_COLOR = "#d3d2ca"
DL_READER_PRIMARY_COLOR = "#3d3a2a"
DL_READER_MUTED_TEXT_COLOR = "rgba(61, 58, 42, 0.7)"
DL_READER_TEXT_COLOR = "#3d3a2a"
DL_READER_CELL_PADDING = "8px"
DL_READER_CELL_PADDING_LARGE = "8px"
DL_READER_PANEL_PADDING = "15px"
DL_READER_GAP = "20px"


READER_FONT_WEIGHT = "400"
READER_LETTER_SPACING = "normal"
READER_WORD_SPACING = "normal"
READER_ID_WIDTH = "60px"


def build_content_table_vars(root_selector: str) -> str:
    """Expose existing content metrics to an isolated table, without global CSS."""
    root = str(root_selector or "").strip()
    if not root:
        raise ValueError("root_selector must not be empty")
    return f"""{root} {{
    --scapp-content-font: {DL_READER_FONT_FAMILY};
    --scapp-content-size: {DL_READER_FONT_SIZE};
    --scapp-content-line-height: {DL_READER_LINE_HEIGHT};
    --scapp-content-weight: {READER_FONT_WEIGHT};
    --scapp-content-bg: {DL_READER_BG_MAIN};
    --scapp-content-text: {DL_READER_TEXT_COLOR};
    --scapp-content-muted: {DL_READER_MUTED_TEXT_COLOR};
    --scapp-content-border: {DL_READER_BORDER_COLOR};
    --scapp-content-cell-padding: {DL_READER_CELL_PADDING};
}}"""


def _clean_selectors(selectors: Iterable[str] | None) -> list[str]:
    """Normalize an internal selector list while preserving order."""
    if not selectors:
        return []

    clean: list[str] = []
    seen: set[str] = set()
    for selector in selectors:
        value = str(selector or "").strip()
        if value and value not in seen:
            seen.add(value)
            clean.append(value)
    return clean


def build_reader_typography_reset_css(
    root_selector: str,
    *,
    inherit_selectors: Iterable[str] | None = None,
    id_selector: str | None = None,
    id_width: str = READER_ID_WIDTH,
) -> str:
    """Return a scoped reader typography baseline.

    Shared baseline:
    - Source Sans / Source Sans Pro reader stack;
    - 1rem body text;
    - 1.6 line-height;
    - font-weight 400;
    - normal letter/word spacing;
    - optional 60px monospace/.75rem segment-ID column.

    ``inherit_selectors`` are full selectors supplied by the renderer. They are
    made typographically transparent so table/cell/lookup wrappers do not
    silently switch font metrics. Semantic emphasis such as ``strong``/``em``
    is preserved because this helper does not reset font-weight/font-style on
    descendant selectors.
    """
    root = str(root_selector or "").strip()
    if not root:
        raise ValueError("root_selector must not be empty")

    blocks = [
        f"""{root} {{
    font-family: var(--dl-font-reader, {DL_READER_FONT_FAMILY});
    font-size: var(--dl-reader-font-size, {DL_READER_FONT_SIZE});
    line-height: var(--dl-reader-line-height, {DL_READER_LINE_HEIGHT});
    font-weight: {READER_FONT_WEIGHT};
    letter-spacing: {READER_LETTER_SPACING};
    word-spacing: {READER_WORD_SPACING};
}}"""
    ]

    inherited = _clean_selectors(inherit_selectors)
    if inherited:
        selector_block = ",\n".join(inherited)
        blocks.append(
            f"""{selector_block} {{
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    letter-spacing: {READER_LETTER_SPACING};
    word-spacing: {READER_WORD_SPACING};
}}"""
        )

    id_sel = str(id_selector or "").strip()
    if id_sel:
        width = str(id_width or READER_ID_WIDTH).strip() or READER_ID_WIDTH
        blocks.append(
            f"""{id_sel} {{
    width: {width};
    min-width: {width};
    box-sizing: border-box;
    white-space: nowrap;
    text-align: center;
    font-family: var(--dl-font-mono, {DL_READER_MONO_FONT_FAMILY});
    font-size: var(--dl-code-font-size, {DL_READER_CODE_FONT_SIZE});
    line-height: var(--dl-reader-line-height, {DL_READER_LINE_HEIGHT});
    font-weight: {READER_FONT_WEIGHT};
    letter-spacing: {READER_LETTER_SPACING};
    word-spacing: {READER_WORD_SPACING};
    color: var(--dl-muted, {DL_READER_MUTED_TEXT_COLOR});
}}"""
        )

    return "\n\n".join(blocks)
