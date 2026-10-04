"""
Shared CSS assets for Streamlit dictionary lookup / reader iframes.

Mục tiêu của module này là gom các style đang lặp trong các hàm reader/lookup
mà không đổi hành vi chức năng chính. Giai đoạn đầu nên dùng theo kiểu inject
CSS vào <style> của từng `html_code`, thay vì link file CSS ngoài.

Thiết kế:
- Design tokens dùng CSS custom properties (`--dl-*`).
- Reader CSS hỗ trợ class mới có prefix `dl-` và một số class legacy hiện có.
- Lookup CSS riêng cho các popup/lookup view nhỏ vì `.main-wrapper` ở nhóm này
  là scroll container, không phải flex layout.
- Popup CSS dùng chung cho iframe popup và parent-document popup.

Gợi ý dùng::

    from dict_lookup_assets import build_reader_css

    css = build_reader_css(dict_width="300px")
    html_code = f"<style>{css}</style>" + html_body

"""

from __future__ import annotations

from textwrap import dedent
import re
import html as html_lib
import unicodedata

from assets_style import (
    DL_READER_FONT_FAMILY,
    DL_READER_MONO_FONT_FAMILY,
    DL_READER_FONT_SIZE,
    DL_READER_LINE_HEIGHT,
    DL_READER_CHANT_FONT_SIZE,
    DL_READER_CHANT_LINE_HEIGHT,
    DL_READER_CODE_FONT_SIZE,
    DL_READER_CODE_BACKGROUND,
    DL_READER_BG_MAIN,
    DL_READER_BG_SEC,
    DL_READER_BG_SIDEBAR,
    DL_READER_BORDER_COLOR,
    DL_READER_PRIMARY_COLOR,
    DL_READER_MUTED_TEXT_COLOR,
    DL_READER_TEXT_COLOR,
    DL_READER_CELL_PADDING,
    DL_READER_CELL_PADDING_LARGE,
    DL_READER_PANEL_PADDING,
    DL_READER_GAP,
)


# -----------------------------------------------------------------------------
# CSS profiles
# -----------------------------------------------------------------------------

CSS_PROFILE_READER = "reader"
CSS_PROFILE_LOOKUP = "lookup"
CSS_PROFILE_POPUP = "popup"


# -----------------------------------------------------------------------------
# Design tokens
# -----------------------------------------------------------------------------

# These values mirror the user's Streamlit theme baseline. They are exposed as
# Python constants so the typography can be tuned in one place before CSS is
# generated.
# Dictionary surface colors. Keep all lookup/sidebar/popup surfaces aligned
# with Streamlit secondaryBackgroundColor by default.
DL_DICT_BACKGROUND = DL_READER_BG_SEC
DL_DICT_INNER_BACKGROUND = DL_READER_BG_SEC
DL_SIDEBAR_DICT_BACKGROUND = DL_READER_BG_SEC
DL_POPUP_BACKGROUND = DL_READER_BG_SEC
DL_LOOKUP_BACKGROUND = DL_READER_BG_SEC
DL_WORD_PADDING = "0 1px"
DL_GLOSSARY_WORD_PADDING = "0 2px"
DL_GLOSSARY_WORD_PADDING_X = "2px"
DL_POPUP_TITLE_FONT_SIZE = "1.2rem"
DL_POPUP_BADGE_FONT_SIZE = "0.65rem"
# Component scrollbars should stay visually lighter than the browser/Streamlit
# page scrollbar while remaining discoverable inside lookup iframes/popups.
DL_SCROLLBAR_WIDTH = "4px"
DL_SCROLLBAR_THUMB_COLOR = "rgba(61, 58, 42, 0.24)"
DL_SCROLLBAR_THUMB_HOVER_COLOR = "rgba(61, 58, 42, 0.36)"
DL_SCROLLBAR_TRACK_COLOR = "transparent"
DL_SCROLLBAR_RADIUS = "999px"

DICT_LOOKUP_TOKENS_CSS = f"""
:root {{
    font-size: 16px;
    --dl-bg-main: {DL_READER_BG_MAIN};
    --dl-bg-sidebar: {DL_READER_BG_SIDEBAR};
    --dl-border-main: {DL_READER_BORDER_COLOR};
    --dl-primary: {DL_READER_PRIMARY_COLOR};
    --dl-bg: {DL_READER_BG_SEC};
    --dl-dict-bg: {DL_DICT_BACKGROUND};
    --dl-dict-inner-bg: {DL_DICT_INNER_BACKGROUND};
    --dl-sidebar-dict-bg: {DL_SIDEBAR_DICT_BACKGROUND};
    --dl-popup-bg: {DL_POPUP_BACKGROUND};
    --dl-lookup-bg: {DL_LOOKUP_BACKGROUND};
    --dl-bg-hover: #d3d2ca;
    --dl-border: {DL_READER_BORDER_COLOR};
    --dl-border-soft: #eee;
    --dl-scrollbar-width: {DL_SCROLLBAR_WIDTH};
    --dl-scrollbar-thumb: {DL_SCROLLBAR_THUMB_COLOR};
    --dl-scrollbar-thumb-hover: {DL_SCROLLBAR_THUMB_HOVER_COLOR};
    --dl-scrollbar-track: {DL_SCROLLBAR_TRACK_COLOR};
    --dl-scrollbar-radius: {DL_SCROLLBAR_RADIUS};
    --dl-scrollbar: var(--dl-scrollbar-thumb);

    --dl-text: {DL_READER_TEXT_COLOR};
    --dl-text-soft: #444;
    --dl-muted: {DL_READER_MUTED_TEXT_COLOR};
    --dl-muted-light: {DL_READER_MUTED_TEXT_COLOR};

    --dl-pali: #d63031;
    --dl-en: #5d7367;
    --dl-highlight: #ffeb3b;

    --dl-gap: {DL_READER_GAP};
    --dl-reader-gap: {DL_READER_GAP};
    --dl-panel-width: 320px;
    --dl-panel-padding: {DL_READER_PANEL_PADDING};
    --dl-cell-padding: {DL_READER_CELL_PADDING};
    --dl-cell-padding-large: {DL_READER_CELL_PADDING_LARGE};
    --dl-radius: 3px;
    --dl-popup-width: 480px;
    --dl-popup-max-height: 400px;
    --dl-popup-z-index: 999999;

    --dl-font-ui: {DL_READER_FONT_FAMILY};
    --dl-font-reader: {DL_READER_FONT_FAMILY};
    --dl-font-mono: {DL_READER_MONO_FONT_FAMILY};
    --dl-reader-font-size: {DL_READER_FONT_SIZE};
    --dl-reader-line-height: {DL_READER_LINE_HEIGHT};
    --dl-reader-chant-font-size: {DL_READER_CHANT_FONT_SIZE};
    --dl-reader-chant-line-height: {DL_READER_CHANT_LINE_HEIGHT};
    --dl-code-font-size: {DL_READER_CODE_FONT_SIZE};
    --dl-code-bg: {DL_READER_CODE_BACKGROUND};
    --dl-word-padding: {DL_WORD_PADDING};
    --dl-glossary-word-padding: {DL_GLOSSARY_WORD_PADDING};
    --dl-glossary-word-padding-x: {DL_GLOSSARY_WORD_PADDING_X};
    --dl-popup-title-font-size: {DL_POPUP_TITLE_FONT_SIZE};
    --dl-popup-badge-font-size: {DL_POPUP_BADGE_FONT_SIZE};
}}
"""


# -----------------------------------------------------------------------------
# Base iframe CSS
# -----------------------------------------------------------------------------

DICT_LOOKUP_BASE_CSS = """
html,
body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: var(--dl-bg-main, #fdfdf8);
    color: var(--dl-text);
}

body {
    font-family: var(--dl-font-reader);
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
    font-weight: 400;
    text-size-adjust: 100%;
    -webkit-text-size-adjust: 100%;
    -webkit-font-smoothing: auto;
}

.dl-root {
    height: 100vh;
    box-sizing: border-box;
}
"""


# -----------------------------------------------------------------------------
# Reader layout CSS
#
# IMPORTANT:
# - `.main-wrapper` is intentionally included only in reader profile.
# - Lookup popup views also use `.main-wrapper`, but there it means a vertical
#   scroll container rather than flex layout.
# -----------------------------------------------------------------------------

DICT_LOOKUP_READER_LAYOUT_CSS = """
.dl-layout,
.main-wrapper {
    display: flex;
    height: 100vh;
    gap: var(--dl-gap);
    box-sizing: border-box;
}

.dl-layout--padded,
.main-wrapper {
    padding: 5px;
}

.dl-layout--reader {
    gap: var(--dl-reader-gap);
    padding-bottom: 5px;
}

.dl-text,
.text-col,
.text-container {
    flex: 1 1 auto;
    overflow-y: auto;
    height: 100%;
}

.dl-text--reader,
.text-col {
    padding-right: 5px;
}

.dl-dict-panel,
.dict-col-container,
.dict-container {
    flex: 0 0 var(--dl-panel-width);
    display: flex;
    flex-direction: column;
    background: var(--dl-dict-bg, var(--dl-bg));
    border: 1px solid var(--dl-border);
    border-radius: 0;
    overflow: hidden;
}

.dl-dict-box,
.sub-dict-box,
.dict-box {
    flex: 1 1 50%;
    background: var(--dl-dict-inner-bg, var(--dl-dict-bg, var(--dl-bg)));
    height: 50%;
    overflow-y: auto;
    padding: var(--dl-panel-padding);
    box-sizing: border-box;
}

.dl-dict-box--single,
.single-box,
.dict-single {
    flex: 1 1 100%;
    height: 100%;
}

.dl-dict-box--bottom,
.bottom-box,
.dict-bottom {
    border-top: 2px dashed var(--dl-border);
}
"""


# -----------------------------------------------------------------------------
# Reader table / content CSS
#
# The new preferred selector is `.dl-table`. Legacy selectors are scoped under
# `.text-col` / `.text-container` to avoid styling every table in injected
# dictionary HTML.
# -----------------------------------------------------------------------------

DICT_LOOKUP_TABLE_CSS = """
.dl-table,
.text-col > table,
.text-container table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--dl-border);
    table-layout: fixed;
    margin: 0;
}

.dl-table td,
.text-col > table td,
.text-container table td {
    padding: var(--dl-cell-padding);
    border: 1px solid var(--dl-border);
    vertical-align: top;
    word-wrap: break-word;
    line-height: var(--dl-reader-line-height);
}

.dl-table--large td,
.text-container table td {
    padding: var(--dl-cell-padding-large);
}

.dl-id-col,
.id-col {
    width: 60px;
    font-size: var(--dl-code-font-size);
    color: var(--dl-muted);
    font-family: var(--dl-font-mono), monospace;
    text-align: center;
}

.dl-id-col--compact,
.id-col {
    white-space: nowrap;
}

.dl-pli-col,
.pli-col {
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
}

.dl-en-col,
.en-col {
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
    color: var(--dl-text-soft);
}

.dl-combined-col,
.combined-col {
    vertical-align: top;
}

.dl-content-col,
.content-col {
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
}

.dl-pli-line,
.pli-line {
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
    margin-bottom: 8px;
}

.dl-en-line,
.en-line {
    font-size: var(--dl-reader-font-size);
    line-height: var(--dl-reader-line-height);
    color: var(--dl-muted);
    font-style: normal;
}

.dl-sutta-header td,
.sutta-header td {
    background: transparent;
    font-weight: 600;
    padding: var(--dl-cell-padding);
    font-size: var(--dl-reader-font-size);
    color: var(--dl-text);
}

.dl-sutta-count,
.sutta-header span {
    font-size: var(--dl-code-font-size);
    color: var(--dl-muted);
}
"""


# -----------------------------------------------------------------------------
# Word interaction CSS
#
# Keep the existing class names because JS currently depends on them:
# `.pali-word`, `.eng-word`, `.eng-sub-word`, `.active`, `.active-en`.
# -----------------------------------------------------------------------------

DICT_LOOKUP_WORD_CSS = """
.pali-word,
.eng-word,
.eng-sub-word,
.dpd-eng-word,
.pts-eng-word {
    cursor: pointer;
    border-radius: var(--dl-radius);
    /* Only animate paint properties. Never animate geometry on lookup words. */
    transition: background-color 0.15s, color 0.15s;
}

.pali-word {
    padding: var(--dl-word-padding);
    display: inline;
}

.pali-word:hover {
    background: var(--dl-bg-hover);
    color: var(--dl-pali);
}

.pali-word.active {
    border-bottom: 2px solid var(--dl-pali);
    color: var(--dl-pali);
}

.eng-word {
    display: inline;
    padding: 0 1px;
    margin: 0;
    border: none;
    text-decoration: none;
}

.eng-word:hover,
.eng-sub-word:hover,
.dpd-eng-word:hover,
.pts-eng-word:hover {
    background: var(--dl-bg-hover);
    color: var(--dl-en);
}

.eng-word.active-en,
.eng-sub-word.active-en,
.dpd-eng-word.active-en,
.pts-eng-word.active-en {
    /* Active state must not change line metrics or wrapping. */
    border: none;
    margin: 0;
    text-decoration: none;
    color: var(--dl-en);
}

.eng-sub-word,
.dpd-eng-word,
.pts-eng-word {
    display: inline;
    padding: 0;
    margin: 0;
    border: none;
    text-decoration: none;
}

.eng-sub-word:hover,
.dpd-eng-word:hover,
.pts-eng-word:hover {
    padding: 0;
    margin: 0;
    border: none;
    text-decoration: none;
}

.eng-sub-word.active-en,
.dpd-eng-word.active-en {
    background: var(--dl-en);
    color: white;
    padding: 0;
    margin: 0;
    border: none;
    text-decoration: none;
    border-radius: 2px;
}

.pts-eng-word.active-en {
    padding: 0;
    margin: 0;
    border: none;
    text-decoration: none;
}

.dl-code,
code,
pre {
    font-family: var(--dl-font-mono);
    font-size: var(--dl-code-font-size);
}

code {
    background: var(--dl-code-bg);
}

.highlight-text {
    background-color: var(--dl-highlight);
    color: #000;
    padding: 0 2px;
    border-radius: var(--dl-radius);
    font-weight: 500;
}
"""


# -----------------------------------------------------------------------------
# Popup CSS
#
# Supports both old `.en-popup` and new `.dl-en-popup` class names.
# `.en-popup-close` is used for parent popups generated dynamically; the local
# iframe popup still often uses `#en-popup-close`.
# -----------------------------------------------------------------------------

DICT_LOOKUP_POPUP_CSS = """
.en-popup,
.dl-en-popup {
    display: none;
    position: fixed;
    z-index: var(--dl-popup-z-index);
    width: var(--dl-popup-width);
    max-width: calc(100vw - 16px);
    max-height: var(--dl-popup-max-height);
    overflow-y: auto;
    background: var(--dl-dict-bg, var(--dl-bg));
    border: 1px solid var(--dl-border);
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
    padding: 12px;
    box-sizing: border-box;
    color: var(--dl-text);
    font-family: var(--dl-font-reader);
}

.en-popup.visible,
.dl-en-popup.visible {
    display: block;
}

/* Hover-driven English popups are interactive: the shared hover lifecycle
   keeps them open while the pointer is inside so users can scroll/copy. */
.dl-hover-popup {
    pointer-events: auto;
}

#en-popup-close,
.en-popup-close,
.dl-en-popup-close {
    float: right;
    border: none;
    background: transparent;
    font-size: var(--dl-popup-title-font-size);
    line-height: 1;
    cursor: pointer;
    color: var(--dl-en);
    padding: 0 0 4px 8px;
}

#en-popup-close:hover,
.en-popup-close:hover,
.dl-en-popup-close:hover {
    color: var(--dl-pali);
}

.dl-popup-heading {
    font-size: var(--dl-popup-title-font-size);
    font-weight: 600;
    border-bottom: 2px solid var(--dl-border);
    margin-bottom: 10px;
    padding-bottom: 5px;
    display: flex;
    align-items: center;
}

.dl-popup-heading--pali {
    color: var(--dl-pali);
}

.dl-popup-heading--en {
    color: var(--dl-en);
}

.dl-popup-badge {
    font-size: var(--dl-popup-badge-font-size);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    margin-right: 8px;
    text-transform: uppercase;
}

.dl-popup-badge--pali {
    background: var(--dl-pali);
}

.dl-popup-badge--en {
    background: var(--dl-en);
}
"""


# -----------------------------------------------------------------------------
# Small lookup iframe CSS
#
# For lookup_pali_dictionary / lookup_pts_dictionary style blocks where
# `.main-wrapper` means a scroll container, not a flex reader layout.
# -----------------------------------------------------------------------------

DICT_LOOKUP_SMALL_VIEW_CSS = """
.main-wrapper,
.dl-lookup-wrapper {
    height: 100vh;
    background: var(--dl-lookup-bg, var(--dl-bg));
    overflow-y: auto;
    box-sizing: border-box;
    padding: 4px 6px;
}

.dpd-dict-view,
.pts-dict-view,
.dl-lookup-view {
    box-sizing: border-box;
    background: var(--dl-lookup-bg, var(--dl-bg));
    width: 100%;
}
"""


# -----------------------------------------------------------------------------
# Scrollbar CSS
# -----------------------------------------------------------------------------

DICT_LOOKUP_SCROLLBAR_CSS = """
* {
    scrollbar-width: thin;
    scrollbar-color: var(--dl-scrollbar-thumb) var(--dl-scrollbar-track);
}

::-webkit-scrollbar {
    width: var(--dl-scrollbar-width);
    height: var(--dl-scrollbar-width);
}

::-webkit-scrollbar-track {
    background: var(--dl-scrollbar-track);
}

::-webkit-scrollbar-thumb {
    background: var(--dl-scrollbar-thumb);
    border-radius: var(--dl-scrollbar-radius);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--dl-scrollbar-thumb-hover);
}

::-webkit-scrollbar-corner {
    background: transparent;
}
"""


# -----------------------------------------------------------------------------
# Profile builders
# -----------------------------------------------------------------------------

_PROFILE_BLOCKS = {
    CSS_PROFILE_READER: (
        DICT_LOOKUP_TOKENS_CSS,
        DICT_LOOKUP_BASE_CSS,
        DICT_LOOKUP_READER_LAYOUT_CSS,
        DICT_LOOKUP_TABLE_CSS,
        DICT_LOOKUP_WORD_CSS,
        DICT_LOOKUP_POPUP_CSS,
    ),
    CSS_PROFILE_LOOKUP: (
        DICT_LOOKUP_TOKENS_CSS,
        DICT_LOOKUP_BASE_CSS,
        DICT_LOOKUP_SMALL_VIEW_CSS,
        DICT_LOOKUP_WORD_CSS,
        DICT_LOOKUP_POPUP_CSS,
    ),
    CSS_PROFILE_POPUP: (
        DICT_LOOKUP_TOKENS_CSS,
        DICT_LOOKUP_WORD_CSS,
        DICT_LOOKUP_POPUP_CSS,
    ),
}


def _clean_css(css: str) -> str:
    """Dedent and strip a CSS fragment."""
    return dedent(css or "").strip()


def _build_css_vars(
    *,
    dict_width: str | None = None,
    popup_width: str | None = None,
    extra_vars: dict[str, str] | None = None,
) -> str:
    """Build a small :root override block for CSS custom properties."""
    pairs: list[tuple[str, str]] = []

    if dict_width:
        pairs.append(("--dl-panel-width", dict_width))

    if popup_width:
        pairs.append(("--dl-popup-width", popup_width))

    if extra_vars:
        for key, value in extra_vars.items():
            if not key.startswith("--dl-"):
                raise ValueError(f"CSS variable must start with '--dl-': {key!r}")
            pairs.append((key, value))

    if not pairs:
        return ""

    lines = [":root {"]
    lines.extend(f"    {key}: {value};" for key, value in pairs)
    lines.append("}")
    return "\n".join(lines)


def build_typography_css(extra_vars: dict[str, str] | None = None) -> str:
    """Return CSS variables mirroring the Streamlit typography baseline.

    ``extra_vars`` can override ``--dl-*`` variables for visual tuning without
    touching individual reader CSS blocks.
    """
    if not extra_vars:
        return DICT_LOOKUP_TOKENS_CSS
    override = _build_css_vars(extra_vars=extra_vars)
    return "\n".join(part for part in [DICT_LOOKUP_TOKENS_CSS.strip(), override] if part)


def normalize_reader_surface_position(position: str | None = "main") -> str:
    """Normalize embedded reader/view dictionary-panel placement.

    Reader/view panels should visually merge with the region that owns them:
    main-page panels use the main background, while sidebar targets use the
    sidebar background. Popup and standalone lookup surfaces are intentionally
    handled by their own helpers.
    """
    value = str(position or "main").strip().lower()
    if value == "sidebar":
        return "sidebar"
    return "main"


def build_reader_surface_vars(position: str | None = "main") -> dict[str, str]:
    """Return ``--dl-*`` overrides for embedded reader/view dictionary panels."""
    normalized = normalize_reader_surface_position(position)
    background = (
        DL_READER_BG_SIDEBAR
        if normalized == "sidebar"
        else DL_READER_BG_MAIN
    )
    return {
        "--dl-dict-bg": background,
        "--dl-dict-inner-bg": background,
        "--dl-sidebar-dict-bg": DL_READER_BG_SIDEBAR,
    }


def normalize_lookup_surface_position(position: str | None = "sidebar") -> str:
    """Normalize lookup card placement for background selection."""
    value = str(position or "sidebar").strip().lower()
    if value in {"main", "page", "content", "body"}:
        return "main"
    return "sidebar"


def build_lookup_surface_vars(position: str | None = "sidebar") -> dict[str, str]:
    """Return ``--dl-*`` variables for standalone lookup surfaces.

    Lookup cards now blend into the primary surface that owns them: main-page
    cards use the main background and sidebar cards use the sidebar background.
    Popup surfaces remain controlled separately by ``build_popup_css()``.
    """
    normalized = normalize_lookup_surface_position(position)
    background = (
        DL_READER_BG_MAIN
        if normalized == "main"
        else DL_READER_BG_SIDEBAR
    )
    return {
        "--dl-lookup-bg": background,
        "--dl-dict-bg": background,
        "--dl-dict-inner-bg": background,
    }


def build_lookup_surface_html(
    html_content: object,
    *,
    position: str | None = "sidebar",
    class_name: str = "dl-lookup-surface-card",
) -> str:
    """Wrap direct Streamlit markdown lookup HTML in a placement-aware surface."""
    normalized = normalize_lookup_surface_position(position)
    background = (
        DL_READER_BG_MAIN
        if normalized == "main"
        else DL_READER_BG_SIDEBAR
    )
    safe_class = html_lib.escape(str(class_name), quote=True)
    content = "" if html_content is None else str(html_content)
    return (
        f'<div class="{safe_class}" style="'
        f'background:{background}; color:{DL_READER_TEXT_COLOR}; '
        f'border:1px solid {DL_READER_BORDER_COLOR}; padding:12px 14px; '
        f'box-sizing:border-box; font-family:{DL_READER_FONT_FAMILY}; '
        f'font-size:{DL_READER_FONT_SIZE}; line-height:{DL_READER_LINE_HEIGHT};'
        f'">{content}</div>'
    )



# -----------------------------------------------------------------------------
# Pāli glossary helpers
# -----------------------------------------------------------------------------

PALI_LETTER_CLASS = r"a-zA-Zāīūṅñṭḍṇḷṃṁ"
PALI_TOKEN_CLEAN_RE = re.compile(rf"[^{PALI_LETTER_CLASS}]", flags=re.IGNORECASE)


def normalize_pali_text_base(text: object) -> str:
    """Normalize Unicode and fold ṁ into ṃ for stable Pāli glossary matching."""
    s = "" if text is None else str(text)
    s = unicodedata.normalize("NFC", s)
    return s.replace("ṁ", "ṃ")


def normalize_pali_token_key(word: object) -> str:
    """Normalize a single Pāli token key, e.g. ``sādhukaṁ;`` -> ``sādhukaṃ``."""
    s = normalize_pali_text_base(word)
    return PALI_TOKEN_CLEAN_RE.sub("", s).lower().strip()


def extract_pali_tokens(text: object) -> list[str]:
    """Extract Pāli-looking tokens from text, including diacritics used in romanized Pāli."""
    s = normalize_pali_text_base(text)
    return re.findall(rf"[{PALI_LETTER_CLASS}]+", s, flags=re.IGNORECASE)


def normalize_pali_phrase_key(text: object) -> str:
    """Normalize a Pāli phrase key, preserving token order and folding whitespace."""
    tokens = extract_pali_tokens(text)
    return " ".join(t.lower() for t in tokens).strip()


def is_pali_phrase_key(key: str) -> bool:
    """Return True when the normalized glossary key is a phrase."""
    return bool(key and " " in key.strip())


def build_pali_glossary_map(
    glossary: dict[str, str] | None,
    *,
    allow_glossary_phrases: bool = False,
) -> dict[str, dict[str, str]]:
    """Normalize a user Pāli glossary for lookup/highlight."""
    if not glossary:
        return {}

    result: dict[str, dict[str, str]] = {}

    for term, meaning in glossary.items():
        raw_term = str(term).strip()
        raw_meaning = "" if meaning is None else str(meaning).strip()

        # Empty meanings are intentionally kept so glossary terms can be
        # highlighted before the user has filled in definitions.
        if not raw_term:
            continue

        phrase_key = normalize_pali_phrase_key(raw_term)
        if not phrase_key:
            continue

        is_phrase = is_pali_phrase_key(phrase_key)
        if is_phrase and not allow_glossary_phrases:
            continue

        result[phrase_key] = {
            "term": raw_term,
            "meaning": raw_meaning,
            "has_meaning": bool(raw_meaning),
            "is_phrase": is_phrase,
        }

    return result


def pali_term_to_regex(term: str) -> str:
    """Convert a Pāli glossary term to a safe regex fragment."""
    term = normalize_pali_text_base(term).strip()
    pieces: list[str] = []

    for ch in term:
        if ch.isspace():
            pieces.append(r"\s+")
        elif ch in {"ṃ", "ṁ"}:
            pieces.append("[ṃṁ]")
        else:
            pieces.append(re.escape(ch))

    return "".join(pieces)


def compile_pali_phrase_glossary_pattern(glossary_map: dict[str, dict[str, str]]):
    """Compile a regex that matches phrase glossary terms, longest first."""
    phrase_items = [item for item in glossary_map.values() if item.get("is_phrase")]
    if not phrase_items:
        return None

    phrase_items = sorted(
        phrase_items,
        key=lambda x: len(normalize_pali_phrase_key(x["term"])),
        reverse=True,
    )

    escaped_terms = [
        pali_term_to_regex(item["term"])
        for item in phrase_items
        if normalize_pali_phrase_key(item["term"])
    ]

    if not escaped_terms:
        return None

    return re.compile(
        rf"(?<![{PALI_LETTER_CLASS}])(" + "|".join(escaped_terms) + rf")(?![{PALI_LETTER_CLASS}])",
        flags=re.IGNORECASE,
    )


def filter_active_pali_glossary(
    glossary_map: dict[str, dict[str, str]],
    source_texts: list[str],
    *,
    allow_glossary_phrases: bool = False,
) -> dict[str, dict[str, str]]:
    """Keep only glossary entries that actually occur in the current Pāli texts."""
    if not glossary_map:
        return {}

    full_text = "\n".join(str(t) for t in source_texts)
    token_keys = {
        normalize_pali_token_key(token)
        for text in source_texts
        for token in str(text).split()
        if normalize_pali_token_key(token)
    }

    active: dict[str, dict[str, str]] = {}

    for key, item in glossary_map.items():
        if not item.get("is_phrase"):
            if key in token_keys:
                active[key] = item
            continue

        if not allow_glossary_phrases:
            continue

        pattern_text = pali_term_to_regex(item["term"])
        pattern = re.compile(
            rf"(?<![{PALI_LETTER_CLASS}]){pattern_text}(?![{PALI_LETTER_CLASS}])",
            flags=re.IGNORECASE,
        )

        if pattern.search(full_text):
            active[key] = item

    return active


def build_pali_glossary_html_block(term: str, meaning: str) -> str:
    """Build a safe HTML block shown above DPD when a glossary hit is selected.

    Empty meanings return an empty string; highlight remains controlled by the
    glossary map, while merge logic decides whether to show DPD or a placeholder.
    """
    raw_meaning = "" if meaning is None else str(meaning).strip()
    if not raw_meaning:
        return ""

    safe_term = html_lib.escape(str(term))
    safe_meaning = html_lib.escape(raw_meaning).replace("\n", "<br>")

    return f"""
    <div class="pali-glossary-box">
        <div class="pali-glossary-title">In Glossary: {safe_term}</div>
        <div class="pali-glossary-meaning">{safe_meaning}</div>
    </div>
    """


def merge_pali_glossary_into_lookup_dict(
    pali_lookup_dict: dict[str, str] | None,
    active_glossary_map: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Merge active glossary entries into a Pāli lookup dictionary."""
    if pali_lookup_dict is None:
        pali_lookup_dict = {}

    if not active_glossary_map:
        return pali_lookup_dict

    clean_to_dpd: dict[str, str] = {}

    for raw_key, raw_meaning in pali_lookup_dict.items():
        clean_key = normalize_pali_phrase_key(raw_key)
        if not clean_key:
            continue

        raw_meaning = str(raw_meaning).strip()
        if not raw_meaning:
            continue

        if clean_key in clean_to_dpd:
            if raw_meaning not in clean_to_dpd[clean_key]:
                clean_to_dpd[clean_key] += "<hr>" + raw_meaning
        else:
            clean_to_dpd[clean_key] = raw_meaning

    empty_glossary_placeholder = (
        "<div class='pali-glossary-box'>"
        "<div class='pali-glossary-title'>In Glossary</div>"
        "<div class='pali-glossary-meaning'>Chưa có nghĩa thuật ngữ.</div>"
        "</div>"
    )

    for lookup_key, item in active_glossary_map.items():
        glossary_block = build_pali_glossary_html_block(
            item.get("term", lookup_key),
            item.get("meaning", ""),
        )

        if item.get("is_phrase"):
            # Phrase entries usually do not have a direct DPD equivalent. If the
            # user has not filled in a meaning yet, keep click behavior explicit.
            merged_meaning = glossary_block or empty_glossary_placeholder
        else:
            old_meaning = str(clean_to_dpd.get(lookup_key, "")).strip()

            if glossary_block and old_meaning:
                merged_meaning = glossary_block + old_meaning
            elif glossary_block:
                merged_meaning = glossary_block
            elif old_meaning:
                # Empty glossary meaning: keep highlight, but let DPD remain the
                # displayed lookup content.
                merged_meaning = old_meaning
            else:
                # Glossary term exists but neither a glossary meaning nor DPD
                # entry is available. Keep click behavior explicit.
                merged_meaning = empty_glossary_placeholder

        pali_lookup_dict[lookup_key] = merged_meaning

    return pali_lookup_dict


def wrap_pali_token_for_lookup(
    token_text: str,
    active_glossary_map: dict[str, dict[str, str]],
) -> str:
    """Wrap one non-whitespace Pāli chunk for lookup."""
    lookup_key = normalize_pali_token_key(token_text)
    if not lookup_key:
        return html_lib.escape(token_text)

    is_glossary_hit = (
        lookup_key in active_glossary_map
        and not active_glossary_map[lookup_key].get("is_phrase")
    )

    data_word = lookup_key if is_glossary_hit else token_text
    css_class = "pali-word pali-glossary-hit" if is_glossary_hit else "pali-word"

    return (
        f"<span class='{html_lib.escape(css_class, quote=True)}' "
        f"data-word='{html_lib.escape(data_word, quote=True)}'>"
        f"{html_lib.escape(token_text)}</span>"
    )


def wrap_pali_text_token_mode(
    text: object,
    active_glossary_map: dict[str, dict[str, str]],
) -> str:
    """Wrap Pāli text in token mode while preserving whitespace."""
    text = "" if text is None else str(text)
    parts = re.split(r"(\s+)", text)
    out: list[str] = []

    for part in parts:
        if not part:
            continue
        if part.isspace():
            out.append(part)
        else:
            out.append(wrap_pali_token_for_lookup(part, active_glossary_map))

    return "".join(out)


def wrap_pali_text_phrase_mode(
    text: object,
    active_glossary_map: dict[str, dict[str, str]],
) -> str:
    """Wrap Pāli text with phrase glossary hits matched before token hits."""
    text = "" if text is None else str(text)
    pattern = compile_pali_phrase_glossary_pattern(active_glossary_map)

    if pattern is None:
        return wrap_pali_text_token_mode(text, active_glossary_map)

    html_parts: list[str] = []
    last_pos = 0

    for match in pattern.finditer(text):
        start, end = match.span()

        if start > last_pos:
            html_parts.append(wrap_pali_text_token_mode(text[last_pos:start], active_glossary_map))

        matched_text = match.group(0)
        phrase_key = normalize_pali_phrase_key(matched_text)
        glossary_item = active_glossary_map.get(phrase_key)

        if glossary_item and glossary_item.get("is_phrase"):
            html_parts.append(
                "<span class='pali-word pali-glossary-hit pali-glossary-phrase-hit' "
                f"data-word='{html_lib.escape(phrase_key, quote=True)}'>"
                f"{html_lib.escape(matched_text)}</span>"
            )
        else:
            html_parts.append(wrap_pali_text_token_mode(matched_text, active_glossary_map))

        last_pos = end

    if last_pos < len(text):
        html_parts.append(wrap_pali_text_token_mode(text[last_pos:], active_glossary_map))

    return "".join(html_parts)


def build_pali_glossary_css() -> str:
    """CSS for Pāli glossary hits and glossary meaning blocks."""
    return dedent(
        """
        .pali-glossary-hit {
            background-color: rgba(255, 218, 80, 0.35) !important;
            border-bottom: 1.5px solid rgba(120, 90, 0, 0.55);
        }

        .pali-glossary-hit:hover {
            background-color: rgba(255, 218, 80, 0.55) !important;
        }

        .pali-glossary-hit.active {
            background-color: rgba(255, 218, 80, 0.65) !important;
        }

        .pali-glossary-phrase-hit {
            padding-left: var(--dl-glossary-word-padding-x);
            padding-right: var(--dl-glossary-word-padding-x);
        }

        .pali-glossary-box {
            border: 1px solid #d3d2ca;
            border-left: 4px solid #8a6d1d;
            background: rgba(255, 218, 80, 0.13);
            padding: 8px 10px;
            margin-bottom: 10px;
            border-radius: 6px;
        }

        .pali-glossary-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #8a6d1d;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .pali-glossary-meaning {
            color: inherit;
            line-height: 1.45;
        }
        """
    ).strip()




def wrap_pali_chanting_text(text: object) -> tuple[str, set[str]]:
    """Wrap Pāli chanting text into clickable tokens while preserving whitespace.

    Returns ``(html, lookup_keys)``. ``lookup_keys`` includes both the visible
    raw token and its normalized Pāli key so IPA lookup data can match either
    legacy raw-token keys or normalized keys.
    """
    s = "" if text is None else str(text)
    parts = re.split(r"(\s+)", s)
    html_parts: list[str] = []
    lookup_keys: set[str] = set()

    for part in parts:
        if not part:
            continue

        if part.isspace():
            html_parts.append(part)
            continue

        clean_key = normalize_pali_token_key(part)

        if not clean_key:
            html_parts.append(html_lib.escape(part))
            continue

        raw_key = normalize_pali_text_base(part)
        lookup_keys.add(raw_key)
        lookup_keys.add(clean_key)

        safe_raw_attr = html_lib.escape(raw_key, quote=True)
        safe_clean_attr = html_lib.escape(clean_key, quote=True)
        safe_text = html_lib.escape(part)

        html_parts.append(
            "<span class='pali-word chanting-pali-word' "
            f"data-word='{safe_raw_attr}' data-clean='{safe_clean_attr}'>"
            f"{safe_text}</span>"
        )

    return "".join(html_parts), lookup_keys



def build_sidebar_dict_target_html(
    target_id: str,
    placeholder: str = "Chạm từ để tra cứu...",
    *,
    class_name: str = "dl-sidebar-dict-target",
    position: str | None = None,
) -> str:
    """Build a stable parent-document dictionary target.

    Reader/view callers pass ``position="sidebar"`` or ``"main"`` so the
    target blends into that primary surface. The default remains the historical
    secondary dictionary background for standalone lookup cards. JavaScript may
    replace the inner HTML without changing this outer surface.
    """
    safe_target_id = html_lib.escape(str(target_id), quote=True)
    safe_class = html_lib.escape(str(class_name), quote=True)
    if position is None:
        background = DL_SIDEBAR_DICT_BACKGROUND
    else:
        normalized = normalize_reader_surface_position(position)
        background = (
            DL_READER_BG_SIDEBAR
            if normalized == "sidebar"
            else DL_READER_BG_MAIN
        )

    return f"""
    <style>
    .dl-sidebar-dict-target:empty {{ display: none; }}
    .dl-sidebar-dict-target {{
        font-family: "Source Sans", "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-main, #3d3a2a);
        background: {background};
        border: 1px solid var(--border-main, #d3d2ca);
        padding: 12px 14px;
        box-sizing: border-box;
    }}

    .dl-sidebar-dict-target code,
    .dl-sidebar-dict-target pre {{
        font-family: "SpaceMono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: .75rem;
        background: var(--code-background-color, #ecebe4);
    }}
    </style>
    <div id="{safe_target_id}" class="{safe_class}"></div>
    """


def build_chanting_sidebar_target_html(
    target_id: str,
    placeholder: str = "Bấm vào một chữ Pāli để xem IPA...",
) -> str:
    """Build a parent/sidebar target for ``render_chanting_reader``."""
    safe_target_id = html_lib.escape(str(target_id), quote=True)
    return f"""
    <style>
    .pali-chanting-sidebar-target:empty {{ display: none; }}
    .pali-chanting-sidebar-target {{
        font-family: "Source Sans", "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-main, #3d3a2a);
        background: #f0f0ec;
        border: 1px solid var(--border-main, #d3d2ca);
        padding: 12px 14px;
        box-sizing: border-box;
    }}

    .pali-chanting-sidebar-target code,
    .pali-chanting-sidebar-target pre {{
        font-family: "SpaceMono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: .75rem;
        background: var(--code-background-color, #ecebe4);
    }}
    </style>
    <div id="{safe_target_id}" class="pali-chanting-sidebar-target"></div>
    """


def build_dict_lookup_css(
    *,
    profile: str = CSS_PROFILE_READER,
    dict_width: str | None = None,
    popup_width: str | None = None,
    extra_vars: dict[str, str] | None = None,
    extra_css: str = "",
    include_scrollbar: bool = True,
) -> str:
    """
    Build CSS for dictionary iframe/popup usage.

    Parameters
    ----------
    profile:
        One of: "reader", "lookup", "popup".
        - "reader": full reader iframe with dictionary panel + text/table column.
        - "lookup": small lookup iframe where `.main-wrapper` is a scroll box.
        - "popup": parent popup style only.
    dict_width:
        Optional value for `--dl-panel-width`, e.g. "300px".
    popup_width:
        Optional value for `--dl-popup-width`, e.g. "320px".
    extra_vars:
        Optional additional CSS variables. Keys must start with `--dl-`.
    extra_css:
        Function-specific CSS appended last. Use this for mode-specific size
        changes such as reading font size or line height.
    include_scrollbar:
        Include shared scrollbar styling.
    """
    if profile not in _PROFILE_BLOCKS:
        allowed = ", ".join(sorted(_PROFILE_BLOCKS))
        raise ValueError(f"Unknown CSS profile {profile!r}. Allowed: {allowed}")

    blocks = [_clean_css(block) for block in _PROFILE_BLOCKS[profile]]

    var_overrides = _build_css_vars(
        dict_width=dict_width,
        popup_width=popup_width,
        extra_vars=extra_vars,
    )
    if var_overrides:
        blocks.append(var_overrides)

    if include_scrollbar:
        blocks.append(_clean_css(DICT_LOOKUP_SCROLLBAR_CSS))

    if extra_css:
        blocks.append(_clean_css(extra_css))

    return "\n\n".join(block for block in blocks if block)


def build_reader_css(
    *,
    dict_width: str | None = None,
    popup_width: str | None = None,
    extra_vars: dict[str, str] | None = None,
    extra_css: str = "",
    include_scrollbar: bool = True,
) -> str:
    """Convenience wrapper for full reader iframe CSS."""
    return build_dict_lookup_css(
        profile=CSS_PROFILE_READER,
        dict_width=dict_width,
        popup_width=popup_width,
        extra_vars=extra_vars,
        extra_css=extra_css,
        include_scrollbar=include_scrollbar,
    )


def build_lookup_css(
    *,
    popup_width: str | None = None,
    extra_vars: dict[str, str] | None = None,
    extra_css: str = "",
    include_scrollbar: bool = True,
) -> str:
    """Convenience wrapper for small lookup iframe CSS."""
    return build_dict_lookup_css(
        profile=CSS_PROFILE_LOOKUP,
        popup_width=popup_width,
        extra_vars=extra_vars,
        extra_css=extra_css,
        include_scrollbar=include_scrollbar,
    )


def build_popup_css(
    *,
    popup_width: str | None = None,
    extra_vars: dict[str, str] | None = None,
    extra_css: str = "",
    include_scrollbar: bool = False,
) -> str:
    """Convenience wrapper for popup CSS injected into parent document."""
    return build_dict_lookup_css(
        profile=CSS_PROFILE_POPUP,
        popup_width=popup_width,
        extra_vars=extra_vars,
        extra_css=extra_css,
        include_scrollbar=include_scrollbar,
    )


def as_style_tag(css: str, *, style_id: str | None = None) -> str:
    """Wrap CSS in a <style> tag for direct insertion into HTML strings."""
    attrs = f' id="{style_id}"' if style_id else ""
    return f"<style{attrs}>\n{_clean_css(css)}\n</style>"




# -----------------------------------------------------------------------------
# Shared cleanup/runtime instrumentation JavaScript
# -----------------------------------------------------------------------------

DICT_LOOKUP_RUNTIME_JS = r"""
(function(global) {
    const parentWin = global.parent || global;
    const runtimeKey = "__dictLookupRuntime";

    function safeNow() {
        try {
            return Date.now();
        } catch (err) {
            return 0;
        }
    }

    function compactMeta(meta) {
        const src = meta || {};
        const out = {};
        Object.keys(src).forEach(function(key) {
            const value = src[key];
            const valueType = typeof value;
            if (
                value === null
                || valueType === "string"
                || valueType === "number"
                || valueType === "boolean"
            ) {
                out[key] = value;
            }
        });
        return out;
    }

    if (!parentWin[runtimeKey]) {
        parentWin[runtimeKey] = {
            version: 1,
            instances: {},
            history: [],
            snapshots: [],
            maxHistory: 80,
            maxSnapshots: 30,
            detailedHistory: false,
            configVersion: 2,

            getConfig: function() {
                return {
                    version: this.version,
                    configVersion: this.configVersion || 1,
                    maxHistory: this.maxHistory || 80,
                    maxSnapshots: this.maxSnapshots || 30,
                    detailedHistory: this.detailedHistory !== false
                };
            },

            configure: function(options) {
                const opts = options || {};

                if (typeof opts.maxHistory === "number" && opts.maxHistory >= 0) {
                    this.maxHistory = Math.floor(opts.maxHistory);
                }

                if (typeof opts.maxSnapshots === "number" && opts.maxSnapshots >= 0) {
                    this.maxSnapshots = Math.floor(opts.maxSnapshots);
                }

                if (typeof opts.detailedHistory === "boolean") {
                    this.detailedHistory = opts.detailedHistory;
                }

                this.pruneDiagnostics();
                return this.getConfig();
            },

            pruneDiagnostics: function(options) {
                const opts = options || {};
                const maxHistory = (
                    typeof opts.maxHistory === "number"
                        ? Math.max(0, Math.floor(opts.maxHistory))
                        : (this.maxHistory || 80)
                );
                const maxSnapshots = (
                    typeof opts.maxSnapshots === "number"
                        ? Math.max(0, Math.floor(opts.maxSnapshots))
                        : (this.maxSnapshots || 30)
                );

                const beforeHistory = (this.history || []).length;
                const beforeSnapshots = (this.snapshots || []).length;

                if (!this.history) {
                    this.history = [];
                }
                if (!this.snapshots) {
                    this.snapshots = [];
                }

                if (this.history.length > maxHistory) {
                    this.history.splice(0, this.history.length - maxHistory);
                }

                if (this.snapshots.length > maxSnapshots) {
                    this.snapshots.splice(0, this.snapshots.length - maxSnapshots);
                }

                return {
                    ok: true,
                    before: { history: beforeHistory, snapshots: beforeSnapshots },
                    after: { history: this.history.length, snapshots: this.snapshots.length },
                    maxHistory: maxHistory,
                    maxSnapshots: maxSnapshots
                };
            },

            register: function(instanceKey, meta) {
                const key = String(instanceKey || "anonymous");
                const existing = this.instances[key];

                if (existing && existing.api && !existing.disposed) {
                    try {
                        existing.api.dispose("replaced_by_new_instance");
                    } catch (err) {}
                }

                const instance = {
                    key: key,
                    meta: compactMeta(meta),
                    createdAt: safeNow(),
                    events: [],
                    artifacts: [],
                    cleanupLabels: [],
                    stateLabels: [],
                    disposed: false,
                    disposedAt: null,
                    disposeReason: null
                };

                const runtime = this;

                const api = {
                    key: key,
                    instance: instance,

                    trackEvent: function(targetLabel, eventName, optionsLabel) {
                        instance.events.push({
                            target: targetLabel || "unknown",
                            event: eventName || "unknown",
                            options: optionsLabel || ""
                        });
                        return api;
                    },

                    trackArtifact: function(docLabel, id) {
                        instance.artifacts.push({
                            doc: docLabel || "document",
                            id: id || ""
                        });
                        return api;
                    },

                    trackCleanup: function(label) {
                        instance.cleanupLabels.push(label || "cleanup");
                        return api;
                    },

                    trackState: function(label) {
                        instance.stateLabels.push(label || "state");
                        return api;
                    },

                    dispose: function(reason) {
                        if (instance.disposed) {
                            return;
                        }

                        instance.disposed = true;
                        instance.disposedAt = safeNow();
                        instance.disposeReason = reason || "disposed";

                        const summary = runtime._summarize(instance, {
                            includeDetails: runtime.detailedHistory !== false
                        });
                        runtime.history.push(summary);

                        if (runtime.history.length > runtime.maxHistory) {
                            runtime.history.splice(0, runtime.history.length - runtime.maxHistory);
                        }

                        if (runtime.instances[key] === instance) {
                            delete runtime.instances[key];
                        }
                    }
                };

                instance.api = api;
                this.instances[key] = instance;
                return api;
            },

            _summarize: function(instance, options) {
                const opts = options || {};
                const includeDetails = opts.includeDetails !== false;

                const summary = {
                    key: instance.key,
                    meta: instance.meta,
                    createdAt: instance.createdAt,
                    disposedAt: instance.disposedAt,
                    lifetimeMs: (
                        instance.createdAt && instance.disposedAt
                            ? instance.disposedAt - instance.createdAt
                            : null
                    ),
                    disposeReason: instance.disposeReason,
                    eventCount: instance.events.length,
                    artifactCount: instance.artifacts.length,
                    cleanupCount: instance.cleanupLabels.length,
                    stateCount: instance.stateLabels.length
                };

                if (includeDetails) {
                    summary.events = instance.events.slice();
                    summary.artifacts = instance.artifacts.slice();
                    summary.cleanupLabels = instance.cleanupLabels.slice();
                    summary.stateLabels = instance.stateLabels.slice();
                }

                return summary;
            },

            _queryAllSafe: function(doc, selector) {
                try {
                    return Array.prototype.slice.call(doc.querySelectorAll(selector));
                } catch (err) {
                    return [];
                }
            },

            _shortNode: function(el) {
                if (!el) {
                    return null;
                }

                let textLength = 0;
                try {
                    textLength = (el.textContent || "").length;
                } catch (err) {}

                return {
                    id: el.id || "",
                    tag: (el.tagName || "").toLowerCase(),
                    className: String(el.className || ""),
                    childCount: el.children ? el.children.length : 0,
                    textLength: textLength
                };
            },

            getDomStats: function() {
                const doc = parentWin.document;
                if (!doc) {
                    return { available: false };
                }

                const popupNodes = this._queryAllSafe(
                    doc,
                    '[id*="popup"], .en-popup, .dl-en-popup, .dpd-parent-en-popup, .pts-parent-en-popup'
                );
                const styleNodes = this._queryAllSafe(
                    doc,
                    'style[id*="popup"], style[id*="dict"], style[id*="lookup"]'
                );
                const targetIds = [
                    'pali-dict-target',
                    'eng-dict-target',
                    'pali-target',
                    'en-target'
                ];
                const targetNodes = targetIds
                    .map(function(id) { return doc.getElementById(id); })
                    .filter(Boolean);

                const duplicateIdMap = {};
                this._queryAllSafe(doc, '[id]').forEach(function(el) {
                    const id = el.id;
                    if (!id) return;
                    duplicateIdMap[id] = (duplicateIdMap[id] || 0) + 1;
                });

                const duplicateIds = Object.keys(duplicateIdMap)
                    .filter(function(id) { return duplicateIdMap[id] > 1; })
                    .map(function(id) { return { id: id, count: duplicateIdMap[id] }; });

                return {
                    available: true,
                    popupCount: popupNodes.length,
                    styleCount: styleNodes.length,
                    targetCount: targetNodes.length,
                    duplicateIds: duplicateIds.slice(0, 40),
                    popups: popupNodes.slice(0, 40).map(this._shortNode),
                    styles: styleNodes.slice(0, 40).map(this._shortNode),
                    targets: targetNodes.map(this._shortNode)
                };
            },

            getMemoryStats: function() {
                try {
                    const perf = parentWin.performance || {};
                    const memory = perf.memory;
                    if (!memory) {
                        return { available: false };
                    }
                    return {
                        available: true,
                        jsHeapSizeLimit: memory.jsHeapSizeLimit || null,
                        totalJSHeapSize: memory.totalJSHeapSize || null,
                        usedJSHeapSize: memory.usedJSHeapSize || null
                    };
                } catch (err) {
                    return { available: false };
                }
            },

            getStats: function(options) {
                const opts = options || {};
                const current = {};
                const keys = Object.keys(this.instances || {});

                keys.forEach(function(key) {
                    const instance = parentWin[runtimeKey].instances[key];
                    current[key] = parentWin[runtimeKey]._summarize(instance, {
                        includeDetails: opts.compact !== true
                    });
                });

                const stats = {
                    version: this.version,
                    instanceCount: keys.length,
                    instanceKeys: keys,
                    instances: current,
                    history: this.history.slice(-20),
                    config: this.getConfig ? this.getConfig() : {
                        maxHistory: this.maxHistory || 80,
                        maxSnapshots: this.maxSnapshots || 30
                    }
                };

                if (opts.dom !== false) {
                    stats.dom = this.getDomStats();
                }

                if (opts.memory) {
                    stats.memory = this.getMemoryStats();
                }

                return stats;
            },

            getLeakReport: function() {
                const stats = this.getStats({ memory: true });
                const dom = stats.dom || {};
                const warnings = [];

                if (stats.instanceCount > 8) {
                    warnings.push({
                        type: "many_runtime_instances",
                        message: "Runtime đang giữ nhiều instance hiện hành.",
                        value: stats.instanceCount
                    });
                }

                if (dom.popupCount > 8) {
                    warnings.push({
                        type: "many_popup_nodes",
                        message: "Parent document có nhiều popup node.",
                        value: dom.popupCount
                    });
                }

                if (dom.styleCount > 12) {
                    warnings.push({
                        type: "many_style_nodes",
                        message: "Parent document có nhiều style node liên quan dictionary/popup.",
                        value: dom.styleCount
                    });
                }

                if (dom.duplicateIds && dom.duplicateIds.length) {
                    warnings.push({
                        type: "duplicate_ids",
                        message: "Parent document có ID bị trùng.",
                        value: dom.duplicateIds
                    });
                }

                return {
                    ok: warnings.length === 0,
                    warnings: warnings,
                    stats: stats
                };
            },

            cleanupInstance: function(instanceKey, reason) {
                const key = String(instanceKey || "anonymous");
                const instance = this.instances[key];
                if (instance && instance.api) {
                    instance.api.dispose(reason || "manual_runtime_cleanup");
                }
            },

            resetStats: function() {
                this.history = [];
            },

            clearDiagnostics: function() {
                this.history = [];
                this.snapshots = [];
                return { ok: true };
            }
        };
    }


    (function ensureRuntimeUpgrade(rt) {
        if (!rt) {
            return;
        }

        rt.version = Math.max(rt.version || 1, 4);

        if (!rt.getConfig || rt.configVersion !== 2) {
            rt.configVersion = 2;
            rt.maxHistory = typeof rt.maxHistory === "number" ? rt.maxHistory : 80;
            rt.maxSnapshots = typeof rt.maxSnapshots === "number" ? rt.maxSnapshots : 30;
            rt.detailedHistory = typeof rt.detailedHistory === "boolean" ? rt.detailedHistory : false;

            rt.getConfig = function() {
                return {
                    version: this.version,
                    configVersion: this.configVersion || 1,
                    maxHistory: this.maxHistory || 80,
                    maxSnapshots: this.maxSnapshots || 30,
                    detailedHistory: this.detailedHistory !== false
                };
            };

            rt.pruneDiagnostics = function(options) {
                const opts = options || {};
                const maxHistory = (
                    typeof opts.maxHistory === "number"
                        ? Math.max(0, Math.floor(opts.maxHistory))
                        : (this.maxHistory || 80)
                );
                const maxSnapshots = (
                    typeof opts.maxSnapshots === "number"
                        ? Math.max(0, Math.floor(opts.maxSnapshots))
                        : (this.maxSnapshots || 30)
                );

                if (!this.history) this.history = [];
                if (!this.snapshots) this.snapshots = [];

                const beforeHistory = this.history.length;
                const beforeSnapshots = this.snapshots.length;

                if (this.history.length > maxHistory) {
                    this.history.splice(0, this.history.length - maxHistory);
                }

                if (this.snapshots.length > maxSnapshots) {
                    this.snapshots.splice(0, this.snapshots.length - maxSnapshots);
                }

                return {
                    ok: true,
                    before: { history: beforeHistory, snapshots: beforeSnapshots },
                    after: { history: this.history.length, snapshots: this.snapshots.length },
                    maxHistory: maxHistory,
                    maxSnapshots: maxSnapshots
                };
            };

            rt.configure = function(options) {
                const opts = options || {};
                if (typeof opts.maxHistory === "number" && opts.maxHistory >= 0) {
                    this.maxHistory = Math.floor(opts.maxHistory);
                }
                if (typeof opts.maxSnapshots === "number" && opts.maxSnapshots >= 0) {
                    this.maxSnapshots = Math.floor(opts.maxSnapshots);
                }
                if (typeof opts.detailedHistory === "boolean") {
                    this.detailedHistory = opts.detailedHistory;
                }
                this.pruneDiagnostics();
                return this.getConfig();
            };

            rt.clearDiagnostics = function() {
                this.history = [];
                this.snapshots = [];
                return { ok: true };
            };
        }

        if (!rt._summarizeVersion || rt._summarizeVersion < 2) {
            rt._summarizeVersion = 2;
            rt._summarize = function(instance, options) {
                const opts = options || {};
                const includeDetails = opts.includeDetails !== false;
                const summary = {
                    key: instance.key,
                    meta: instance.meta,
                    createdAt: instance.createdAt,
                    disposedAt: instance.disposedAt,
                    lifetimeMs: (
                        instance.createdAt && instance.disposedAt
                            ? instance.disposedAt - instance.createdAt
                            : null
                    ),
                    disposeReason: instance.disposeReason,
                    eventCount: instance.events ? instance.events.length : 0,
                    artifactCount: instance.artifacts ? instance.artifacts.length : 0,
                    cleanupCount: instance.cleanupLabels ? instance.cleanupLabels.length : 0,
                    stateCount: instance.stateLabels ? instance.stateLabels.length : 0
                };

                if (includeDetails) {
                    summary.events = (instance.events || []).slice();
                    summary.artifacts = (instance.artifacts || []).slice();
                    summary.cleanupLabels = (instance.cleanupLabels || []).slice();
                    summary.stateLabels = (instance.stateLabels || []).slice();
                }

                return summary;
            };
        }

        if (!rt.getActiveArtifactIds) {
            rt.getActiveArtifactIds = function() {
                const ids = {};
                Object.keys(this.instances || {}).forEach(function(key) {
                    const instance = rt.instances[key];
                    (instance.artifacts || []).forEach(function(item) {
                        if (item && item.id) {
                            ids[item.id] = true;
                        }
                    });
                });
                return Object.keys(ids);
            };
        }

        if (!rt.getLifecycleReport || rt.lifecycleReportVersion !== 3) {
            rt.lifecycleReportVersion = 3;
            rt.getLifecycleReport = function() {
                const stats = this.getStats ? this.getStats({ memory: true }) : { instanceCount: 0, instanceKeys: [] };
                const activeArtifactIds = this.getActiveArtifactIds ? this.getActiveArtifactIds() : [];
                const activeMap = {};
                activeArtifactIds.forEach(function(id) { activeMap[id] = true; });

                const doc = parentWin.document;
                const orphanCandidates = [];
                const activeArtifactNodes = [];

                if (doc) {
                    activeArtifactIds.forEach(function(id) {
                        try {
                            const el = doc.getElementById(id);
                            if (el) {
                                activeArtifactNodes.push(el);
                            }
                        } catch (err) {}
                    });
                }

                function isCoveredByActiveArtifact(id, el) {
                    if (!id || !el) {
                        return false;
                    }

                    if (activeMap[id]) {
                        return true;
                    }

                    for (let i = 0; i < activeArtifactNodes.length; i += 1) {
                        const artifactNode = activeArtifactNodes[i];
                        try {
                            if (artifactNode && artifactNode.contains && artifactNode.contains(el)) {
                                return true;
                            }
                        } catch (err) {}
                    }

                    return false;
                }

                const nodes = [];

                if (doc && this._queryAllSafe) {
                    this._queryAllSafe(
                        doc,
                        '[id*="popup"], .en-popup, .dl-en-popup, .dpd-parent-en-popup, .pts-parent-en-popup'
                    ).forEach(function(el) {
                        nodes.push({ kind: "popup", el: el });
                    });

                    this._queryAllSafe(
                        doc,
                        'style[id*="popup"], style[id*="dict"], style[id*="lookup"]'
                    ).forEach(function(el) {
                        nodes.push({ kind: "style", el: el });
                    });
                }

                nodes.forEach(function(entry) {
                    const el = entry.el;
                    const id = el && el.id;
                    if (!id) return;
                    if (isCoveredByActiveArtifact(id, el)) return;
                    if (id === "en-popup" || id === "en-popup-content" || id === "en-popup-close") return;
                    orphanCandidates.push({ kind: entry.kind, id: id, node: rt._shortNode ? rt._shortNode(el) : { id: id } });
                });

                return {
                    ok: orphanCandidates.length === 0,
                    activeArtifactIds: activeArtifactIds,
                    activeArtifactRootCount: activeArtifactNodes.length,
                    orphanCandidates: orphanCandidates.slice(0, 40),
                    stats: stats
                };
            };
        }

        if (!rt.sweepLegacyArtifacts) {
            rt.sweepLegacyArtifacts = function(options) {
                const opts = options || {};
                const dryRun = opts.dryRun !== false;
                const doc = parentWin.document;
                const ids = opts.ids || [
                    "en-popup-parent",
                    "en-popup-parent-style"
                ];
                const removed = [];

                if (!doc) {
                    return { dryRun: dryRun, removed: removed, available: false };
                }

                ids.forEach(function(id) {
                    try {
                        const nodes = Array.prototype.slice.call(doc.querySelectorAll("#" + id));
                        nodes.forEach(function(el) {
                            removed.push({ id: id, tag: (el.tagName || "").toLowerCase() });
                            if (!dryRun) {
                                try { el.innerHTML = ""; } catch (err) {}
                                if (el.parentNode) {
                                    el.parentNode.removeChild(el);
                                }
                            }
                        });
                    } catch (err) {}
                });

                return { dryRun: dryRun, removed: removed, available: true };
            };
        }

        if (!rt.clearHistory) {
            rt.clearHistory = function() {
                this.history = [];
            };
        }

        if (!rt.takeSnapshot) {
            rt.takeSnapshot = function(label, options) {
                const opts = options || {};
                const stats = this.getStats ? this.getStats({ memory: !!opts.memory }) : { instanceCount: 0, instanceKeys: [] };
                const dom = stats.dom || {};
                const memory = stats.memory || null;

                if (!this.snapshots) {
                    this.snapshots = [];
                }

                const snapshot = {
                    id: "snapshot-" + safeNow() + "-" + Math.random().toString(36).slice(2, 8),
                    label: label || "snapshot",
                    createdAt: safeNow(),
                    instanceCount: stats.instanceCount || 0,
                    instanceKeys: (stats.instanceKeys || []).slice(),
                    dom: {
                        popupCount: dom.popupCount || 0,
                        styleCount: dom.styleCount || 0,
                        targetCount: dom.targetCount || 0,
                        duplicateIdCount: dom.duplicateIds ? dom.duplicateIds.length : 0
                    },
                    memory: memory && memory.available ? {
                        usedJSHeapSize: memory.usedJSHeapSize || null,
                        totalJSHeapSize: memory.totalJSHeapSize || null,
                        jsHeapSizeLimit: memory.jsHeapSizeLimit || null
                    } : null
                };

                this.snapshots.push(snapshot);

                const maxSnapshots = opts.maxSnapshots || this.maxSnapshots || 30;
                if (this.snapshots.length > maxSnapshots) {
                    this.snapshots.splice(0, this.snapshots.length - maxSnapshots);
                }

                return snapshot;
            };
        }

        if (!rt.getSnapshots) {
            rt.getSnapshots = function() {
                return (this.snapshots || []).slice();
            };
        }

        if (!rt.clearSnapshots) {
            rt.clearSnapshots = function() {
                this.snapshots = [];
                return { ok: true };
            };
        }

        if (!rt.getSnapshotDiff) {
            rt.getSnapshotDiff = function(fromRef, toRef) {
                const snapshots = this.snapshots || [];

                function resolve(ref, fallbackIndex) {
                    if (!snapshots.length) return null;
                    if (ref === undefined || ref === null) {
                        return snapshots[fallbackIndex];
                    }
                    if (typeof ref === "number") {
                        return snapshots[ref] || null;
                    }
                    return snapshots.find(function(item) {
                        return item.id === ref || item.label === ref;
                    }) || null;
                }

                const from = resolve(fromRef, Math.max(0, snapshots.length - 2));
                const to = resolve(toRef, snapshots.length - 1);

                if (!from || !to) {
                    return {
                        available: false,
                        reason: "not_enough_snapshots",
                        snapshotCount: snapshots.length
                    };
                }

                const fromMemory = from.memory || {};
                const toMemory = to.memory || {};

                return {
                    available: true,
                    from: from,
                    to: to,
                    delta: {
                        instanceCount: (to.instanceCount || 0) - (from.instanceCount || 0),
                        popupCount: (to.dom.popupCount || 0) - (from.dom.popupCount || 0),
                        styleCount: (to.dom.styleCount || 0) - (from.dom.styleCount || 0),
                        targetCount: (to.dom.targetCount || 0) - (from.dom.targetCount || 0),
                        duplicateIdCount: (to.dom.duplicateIdCount || 0) - (from.dom.duplicateIdCount || 0),
                        usedJSHeapSize: (
                            fromMemory.usedJSHeapSize && toMemory.usedJSHeapSize
                                ? toMemory.usedJSHeapSize - fromMemory.usedJSHeapSize
                                : null
                        )
                    }
                };
            };
        }

        if (!rt.healthCheck) {
            rt.healthCheck = function(options) {
                const opts = options || {};
                const stats = this.getStats ? this.getStats({ memory: !!opts.memory }) : { instanceCount: 0, instanceKeys: [] };
                const lifecycle = this.getLifecycleReport ? this.getLifecycleReport() : null;
                const dom = stats.dom || {};
                const memory = stats.memory || null;

                const thresholds = {
                    maxInstanceCount: opts.maxInstanceCount || 8,
                    maxPopupCount: opts.maxPopupCount || 8,
                    maxStyleCount: opts.maxStyleCount || 12,
                    maxDuplicateIdCount: opts.maxDuplicateIdCount || 0,
                    maxOrphanCount: opts.maxOrphanCount || 0,
                    memoryWarnRatio: opts.memoryWarnRatio || 0.85
                };

                const checks = [];

                function addCheck(name, ok, severity, message, value, recommendation) {
                    checks.push({
                        name: name,
                        ok: !!ok,
                        severity: ok ? "ok" : (severity || "warning"),
                        message: message,
                        value: value,
                        recommendation: recommendation || ""
                    });
                }

                addCheck(
                    "runtime_instance_count",
                    (stats.instanceCount || 0) <= thresholds.maxInstanceCount,
                    "warning",
                    "Số runtime instance hiện hành không vượt ngưỡng.",
                    stats.instanceCount || 0,
                    "Nếu số này tăng sau mỗi rerun, kiểm tra cleanupKey và thứ tự gọi cleanup trước khi register instance mới."
                );

                addCheck(
                    "popup_node_count",
                    (dom.popupCount || 0) <= thresholds.maxPopupCount,
                    "warning",
                    "Số popup node trong parent document không vượt ngưỡng.",
                    dom.popupCount || 0,
                    "Nếu tăng liên tục, kiểm tra addArtifact/removeArtifact cho popup parent và local popup."
                );

                addCheck(
                    "style_node_count",
                    (dom.styleCount || 0) <= thresholds.maxStyleCount,
                    "warning",
                    "Số style node liên quan dictionary/popup không vượt ngưỡng.",
                    dom.styleCount || 0,
                    "Nếu tăng liên tục, kiểm tra parentPopupStyleId/styleId và cleanup style artifact."
                );

                const duplicateIds = dom.duplicateIds || [];
                addCheck(
                    "duplicate_id_count",
                    duplicateIds.length <= thresholds.maxDuplicateIdCount,
                    "error",
                    "Không có ID DOM bị trùng trong parent document.",
                    duplicateIds,
                    "ID trùng có thể làm JS ghi nhầm target sidebar hoặc popup. Cần tách instanceKey/targetId nếu cùng trang render nhiều reader."
                );

                const orphanCandidates = lifecycle && lifecycle.orphanCandidates ? lifecycle.orphanCandidates : [];
                addCheck(
                    "orphan_artifact_count",
                    orphanCandidates.length <= thresholds.maxOrphanCount,
                    "warning",
                    "Không có popup/style dictionary không thuộc runtime instance hiện hành.",
                    orphanCandidates,
                    "Nếu có orphan cũ, dùng sweepLegacyArtifacts dry-run trước; chỉ xóa thật khi chắc đó là legacy artifact."
                );

                const historyLength = (stats.history || []).length;
                addCheck(
                    "history_bounded",
                    historyLength <= (this.maxHistory || 80),
                    "warning",
                    "Runtime history được giới hạn kích thước.",
                    historyLength,
                    "Nếu history quá lớn, kiểm tra maxHistory hoặc gọi clearHistory sau khi debug."
                );

                const snapshotLength = (this.snapshots || []).length;
                addCheck(
                    "snapshots_bounded",
                    snapshotLength <= (this.maxSnapshots || 30),
                    "warning",
                    "Runtime snapshots được giới hạn kích thước.",
                    snapshotLength,
                    "Nếu snapshots quá lớn, gọi clearSnapshots/clearDiagnostics hoặc giảm maxSnapshots bằng configure()."
                );

                if (opts.memory) {
                    const memoryOk = !!(memory && memory.available);
                    if (!memoryOk) {
                        addCheck(
                            "memory_stats_available",
                            true,
                            "info",
                            "Browser không cung cấp performance.memory; bỏ qua kiểm tra heap.",
                            false,
                            "Dùng Chrome/Chromium nếu cần quan sát JS heap."
                        );
                    } else {
                        const ratio = (
                            memory.jsHeapSizeLimit && memory.usedJSHeapSize
                                ? memory.usedJSHeapSize / memory.jsHeapSizeLimit
                                : 0
                        );
                        addCheck(
                            "memory_heap_ratio",
                            ratio <= thresholds.memoryWarnRatio,
                            "warning",
                            "Tỷ lệ used JS heap chưa vượt ngưỡng cảnh báo.",
                            {
                                ratio: ratio,
                                usedJSHeapSize: memory.usedJSHeapSize,
                                jsHeapSizeLimit: memory.jsHeapSizeLimit
                            },
                            "Nếu heap tăng đều sau nhiều rerun, chụp snapshot trước/sau và kiểm tra dictState cleanup."
                        );
                    }
                }

                const failed = checks.filter(function(item) { return !item.ok; });
                const errors = failed.filter(function(item) { return item.severity === "error"; });
                const warnings = failed.filter(function(item) { return item.severity !== "error"; });

                return {
                    ok: failed.length === 0,
                    severity: errors.length ? "error" : (warnings.length ? "warning" : "ok"),
                    checks: checks,
                    failedChecks: failed,
                    recommendations: failed.map(function(item) { return item.recommendation; }).filter(Boolean),
                    stats: stats,
                    lifecycle: lifecycle
                };
            };
        }

        if (!rt.getHealthReport) {
            rt.getHealthReport = function(options) {
                return this.healthCheck ? this.healthCheck(options || {}) : null;
            };
        }

    })(parentWin[runtimeKey]);

    global.dlRuntimeRegisterInstance = function(instanceKey, meta) {
        return parentWin[runtimeKey].register(instanceKey, meta || {});
    };

    global.dlRuntimeStats = function(options) {
        return parentWin[runtimeKey].getStats(options || {});
    };

    global.dlRuntimeLeakReport = function() {
        return parentWin[runtimeKey].getLeakReport();
    };

    global.dlRuntimeLifecycleReport = function() {
        const rt = parentWin[runtimeKey];
        return rt && rt.getLifecycleReport ? rt.getLifecycleReport() : null;
    };

    global.dlRuntimeSweepLegacyArtifacts = function(options) {
        const rt = parentWin[runtimeKey];
        return rt && rt.sweepLegacyArtifacts ? rt.sweepLegacyArtifacts(options || {}) : null;
    };

    global.dlRuntimeHealthCheck = function(options) {
        const rt = parentWin[runtimeKey];
        return rt && rt.healthCheck ? rt.healthCheck(options || {}) : null;
    };

    global.dlRuntimeSnapshot = function(label, options) {
        const rt = parentWin[runtimeKey];
        return rt && rt.takeSnapshot ? rt.takeSnapshot(label || "snapshot", options || {}) : null;
    };

    global.dlRuntimeSnapshotDiff = function(fromRef, toRef) {
        const rt = parentWin[runtimeKey];
        return rt && rt.getSnapshotDiff ? rt.getSnapshotDiff(fromRef, toRef) : null;
    };

    global.dlRuntimeConfigure = function(options) {
        const rt = parentWin[runtimeKey];
        return rt && rt.configure ? rt.configure(options || {}) : null;
    };

    global.dlRuntimePruneDiagnostics = function(options) {
        const rt = parentWin[runtimeKey];
        return rt && rt.pruneDiagnostics ? rt.pruneDiagnostics(options || {}) : null;
    };

    global.dlRuntimeClearDiagnostics = function() {
        const rt = parentWin[runtimeKey];
        return rt && rt.clearDiagnostics ? rt.clearDiagnostics() : null;
    };
})(window);
"""


def build_runtime_js() -> str:
    """Return shared cleanup/runtime instrumentation JavaScript for iframe injection."""
    return dedent(DICT_LOOKUP_RUNTIME_JS).strip()


# -----------------------------------------------------------------------------
# Shared DOM / popup helper JavaScript
# -----------------------------------------------------------------------------

from dict_lookup_popup_assets import ENGLISH_POPUP_JS

DICT_LOOKUP_DOM_HELPERS_JS = ENGLISH_POPUP_JS + r"""
(function(global) {
    if (global.__dictLookupDomHelpersReady) {
        return;
    }

    global.__dictLookupDomHelpersReady = true;

    global.dlClosest = function(target, selector) {
        if (!target || !selector) {
            return null;
        }

        if (target.closest) {
            return target.closest(selector);
        }

        let node = target;
        while (node && node.nodeType === 1) {
            if (node.matches && node.matches(selector)) {
                return node;
            }
            node = node.parentElement;
        }
        return null;
    };

    global.dlBindEnglishLookupHover = function(root, selector, handler, options) {
        if (!root || !selector || typeof handler !== "function") {
            return function() {};
        }

        const opts = options || {};
        const capture = !!opts.capture;
        const accept = typeof opts.accept === "function" ? opts.accept : null;
        const leave = typeof opts.leave === "function" ? opts.leave : null;

        function getTarget(e) {
            const target = global.dlClosest(e.target, selector);
            if (!target) {
                return null;
            }

            if (root.nodeType === 1 && root.contains && !root.contains(target)) {
                return null;
            }

            if (accept && !accept(target, e)) {
                return null;
            }

            return target;
        }

        const overListener = function(e) {
            const target = getTarget(e);
            if (!target) {
                return;
            }

            const related = e.relatedTarget;
            if (
                related
                && target.contains
                && (related === target || target.contains(related))
            ) {
                return;
            }

            handler(target, e);
        };

        const outListener = function(e) {
            if (!leave) {
                return;
            }

            const target = getTarget(e);
            if (!target) {
                return;
            }

            const related = e.relatedTarget;
            if (
                related
                && target.contains
                && (related === target || target.contains(related))
            ) {
                return;
            }

            leave(target, e);
        };

        root.addEventListener("mouseover", overListener, capture);
        root.addEventListener("mouseout", outListener, capture);

        return function() {
            try {
                root.removeEventListener("mouseover", overListener, capture);
            } catch (err) {}
            try {
                root.removeEventListener("mouseout", outListener, capture);
            } catch (err) {}
        };
    };

    global.dlCreateEnglishHoverPopupLifecycle = function(getPopup, closeHandler, delayMs) {
        const delay = Number.isFinite(Number(delayMs))
            ? Math.max(0, Number(delayMs))
            : 500;
        let closeTimer = null;
        let popup = null;
        let popupEnterHandler = null;
        let popupLeaveHandler = null;

        function cancelClose() {
            if (closeTimer) {
                try { clearTimeout(closeTimer); } catch (err) {}
                closeTimer = null;
            }
        }

        function scheduleClose() {
            cancelClose();
            closeTimer = setTimeout(function() {
                closeTimer = null;
                if (typeof closeHandler === "function") {
                    closeHandler();
                }
            }, delay);
        }

        function detachPopup() {
            if (!popup) {
                return;
            }
            try {
                if (popupEnterHandler) {
                    popup.removeEventListener("mouseenter", popupEnterHandler);
                }
                if (popupLeaveHandler) {
                    popup.removeEventListener("mouseleave", popupLeaveHandler);
                }
            } catch (err) {}
            popup = null;
            popupEnterHandler = null;
            popupLeaveHandler = null;
        }

        function attachPopup() {
            const nextPopup = typeof getPopup === "function" ? getPopup() : null;
            if (!nextPopup) {
                return null;
            }
            if (popup === nextPopup) {
                return popup;
            }

            detachPopup();
            popup = nextPopup;
            popup.style.pointerEvents = "auto";
            popupEnterHandler = function() { cancelClose(); };
            popupLeaveHandler = function() { scheduleClose(); };
            popup.addEventListener("mouseenter", popupEnterHandler);
            popup.addEventListener("mouseleave", popupLeaveHandler);
            return popup;
        }

        function cleanup() {
            cancelClose();
            detachPopup();
        }

        return {
            cancelClose: cancelClose,
            scheduleClose: scheduleClose,
            attachPopup: attachPopup,
            cleanup: cleanup
        };
    };

    global.dlRemoveElementById = function(doc, id) {
        try {
            if (!doc || !id) {
                return;
            }
            const el = doc.getElementById(id);
            if (el) {
                try {
                    el.innerHTML = "";
                } catch (err) {}
            }
            if (el && el.parentNode) {
                el.parentNode.removeChild(el);
            }
        } catch (err) {}
    };

    global.dlSetHtmlById = function(doc, id, html) {
        if (!doc || !id) {
            return false;
        }
        const target = doc.getElementById(id);
        if (!target) {
            return false;
        }
        target.innerHTML = html;
        return true;
    };

    global.dlIsInsideAnyId = function(doc, target, ids) {
        if (!doc || !target || !ids) {
            return false;
        }
        for (const id of ids) {
            const root = doc.getElementById(id);
            if (root && root.contains(target)) {
                return true;
            }
        }
        return false;
    };

    global.dlGetDataWord = function(target) {
        if (!target || !target.getAttribute) {
            return "";
        }
        return (target.getAttribute("data-word") || "").toLowerCase();
    };

    global.dlWrapEnglishWordsInRoot = function(root, enDictionary, options) {
        if (!root) {
            return;
        }

        const dictionary = enDictionary || {};
        const opts = options || {};
        const lookupClass = opts.lookupClass || opts.className || "eng-sub-word";
        const skipSelector = opts.skipSelector || ("script, style, ." + lookupClass);
        const wordPattern = opts.wordPattern || /\b([a-zA-Z]+)\b/g;

        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    const parent = node.parentElement;

                    if (!parent) {
                        return NodeFilter.FILTER_REJECT;
                    }

                    if (skipSelector && parent.closest && parent.closest(skipSelector)) {
                        return NodeFilter.FILTER_REJECT;
                    }

                    if (!/[a-zA-Z]/.test(node.nodeValue)) {
                        return NodeFilter.FILTER_REJECT;
                    }

                    return NodeFilter.FILTER_ACCEPT;
                }
            },
            false
        );

        const nodes = [];
        let node;

        while ((node = walker.nextNode())) {
            nodes.push(node);
        }

        nodes.forEach(function(textNode) {
            const text = textNode.nodeValue;
            wordPattern.lastIndex = 0;

            const replaced = text.replace(wordPattern, function(full, word) {
                const clean = (word || "").toLowerCase();

                if (!dictionary[clean]) {
                    return full;
                }

                return "<span class='" + lookupClass + "' data-word='" + clean + "'>" + full + "</span>";
            });

            if (replaced !== text) {
                const span = document.createElement("span");
                span.innerHTML = replaced;
                if (textNode.parentNode) {
                    textNode.parentNode.replaceChild(span, textNode);
                }
            }
        });
    };

    global.dlWrapEnglishWords = function(htmlContent, enDictionary, className) {
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = htmlContent || "";
        global.dlWrapEnglishWordsInRoot(tempDiv, enDictionary || {}, {
            lookupClass: className || "eng-sub-word"
        });
        return tempDiv.innerHTML;
    };

    global.dlEnsurePopupInDoc = function(doc, config, cssText) {
        if (!doc || !config) {
            return { popup: null, content: null };
        }

        const popupId = config.popupId;
        const contentId = config.contentId;
        const styleId = config.styleId;
        const popupClass = config.popupClass || "en-popup";

        if (styleId && cssText && !doc.getElementById(styleId)) {
            const style = doc.createElement("style");
            style.id = styleId;
            style.textContent = cssText;
            doc.head.appendChild(style);
        }

        let popup = doc.getElementById(popupId);
        if (!popup) {
            popup = doc.createElement("div");
            popup.id = popupId;
            popup.className = popupClass;
            popup.innerHTML = `<div id="${contentId}"></div>`;
            doc.body.appendChild(popup);
        }

        return {
            popup: popup,
            content: doc.getElementById(contentId)
        };
    };

    global.dlHidePopup = function(doc, popupId) {
        if (!doc || !popupId) {
            return;
        }
        const popup = doc.getElementById(popupId);
        if (popup) {
            popup.classList.remove("visible");
        }
    };

    global.dlShowPopup = function(finalContent, targetEl, options) {
        if (!targetEl || !options || !options.popupFactory) {
            return;
        }

        const targetDoc = targetEl.ownerDocument || document;
        const popupParts = options.popupFactory(targetDoc);
        const popup = popupParts && popupParts.popup;
        const popupContent = popupParts && popupParts.content;

        if (!popup || !popupContent) {
            return;
        }

        popupContent.innerHTML = finalContent;
        popup.classList.add("visible");

        scappEnglishPopup.place(popup, targetEl, {width: options.defaultPopupWidth || 320});
        return popup;
    };

    global.dlShowParentPopupFromIframe = function(finalContent, targetEl, options) {
        if (!targetEl || !options) {
            return;
        }

        const popup = options.popup;
        const popupContent = options.content;

        if (!popup || !popupContent) {
            return;
        }

        popupContent.innerHTML = finalContent;
        popup.classList.add("visible");

        scappEnglishPopup.place(popup, targetEl, {width: options.defaultPopupWidth || 320});
    };

    global.dlClearActive = function(doc, selector, className) {
        if (!doc || !selector || !className) {
            return;
        }
        doc.querySelectorAll(selector).forEach(function(el) {
            el.classList.remove(className);
        });
    };
})(window);
"""


def build_dom_helpers_js() -> str:
    """Return shared DOM/popup helper JavaScript for iframe injection."""
    return dedent(DICT_LOOKUP_DOM_HELPERS_JS).strip()


__all__ = [
    "CSS_PROFILE_READER",
    "CSS_PROFILE_LOOKUP",
    "CSS_PROFILE_POPUP",
    "DL_READER_FONT_FAMILY",
    "DL_READER_MONO_FONT_FAMILY",
    "DL_READER_FONT_SIZE",
    "DL_READER_LINE_HEIGHT",
    "DL_READER_CODE_FONT_SIZE",
    "DL_READER_CODE_BACKGROUND",
    "DL_READER_TEXT_COLOR",
    "DICT_LOOKUP_TOKENS_CSS",
    "DICT_LOOKUP_BASE_CSS",
    "DICT_LOOKUP_READER_LAYOUT_CSS",
    "DICT_LOOKUP_TABLE_CSS",
    "DICT_LOOKUP_WORD_CSS",
    "DICT_LOOKUP_POPUP_CSS",
    "DICT_LOOKUP_SMALL_VIEW_CSS",
    "DICT_LOOKUP_SCROLLBAR_CSS",
    "DICT_LOOKUP_RUNTIME_JS",
    "DICT_LOOKUP_DOM_HELPERS_JS",
    "build_runtime_js",
    "build_typography_css",
    "build_reader_surface_vars",
    "normalize_reader_surface_position",
    "build_lookup_surface_html",
    "build_lookup_surface_vars",
    "normalize_lookup_surface_position",
    "normalize_pali_text_base",
    "normalize_pali_token_key",
    "extract_pali_tokens",
    "normalize_pali_phrase_key",
    "is_pali_phrase_key",
    "build_pali_glossary_map",
    "pali_term_to_regex",
    "compile_pali_phrase_glossary_pattern",
    "filter_active_pali_glossary",
    "build_pali_glossary_html_block",
    "merge_pali_glossary_into_lookup_dict",
    "wrap_pali_token_for_lookup",
    "wrap_pali_text_token_mode",
    "wrap_pali_text_phrase_mode",
    "build_pali_glossary_css",
    "wrap_pali_chanting_text",
    "build_sidebar_dict_target_html",
    "build_chanting_sidebar_target_html",
    "build_dict_lookup_css",
    "build_reader_css",
    "build_lookup_css",
    "build_popup_css",
    "build_dom_helpers_js",
    "as_style_tag",
]
