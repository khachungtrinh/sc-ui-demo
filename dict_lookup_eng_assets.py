"""
Shared frontend/runtime helpers for English dictionary reader components.

This module is intentionally independent from the Pali lookup module so it can be
reused in an English-learning app without importing Pali-specific code.
"""

from __future__ import annotations

import html as html_lib
import re
from typing import Iterable, Literal


PALI_DIACRITIC_WORD_RE = re.compile(
    r"\b[a-zA-ZāīūṅñṭḍṇḷṃṁĀĪŪṄÑṬḌṆḶṂṀ]*[āīūṅñṭḍṇḷṃṁĀĪŪṄÑṬḌṆḶṂṀ][a-zA-ZāīūṅñṭḍṇḷṃṁĀĪŪṄÑṬḌṆḶṂṀ]*\b",
    flags=re.IGNORECASE,
)

EN_WORD_RE = re.compile(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b")

COMMON_IGNORE_WORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "by", "for",
    "from", "with", "without", "as", "is", "are", "be", "was", "were",
    "been", "being", "this", "that", "these", "those", "it", "its",
    "not", "no", "yes", "do", "does", "did", "done", "can", "could",
    "should", "would", "may", "might", "must", "will", "shall",
}

TEXT_IGNORE_WORDS = COMMON_IGNORE_WORDS | {
    "i", "you", "he", "she", "we", "they", "me", "him", "her", "them",
    "my", "your", "his", "their", "our", "lit", "root", "family", "words",
}

TABLE_IGNORE_WORDS = COMMON_IGNORE_WORDS | {
    "masc", "fem", "nt", "adj", "adv", "pp", "prp", "abs", "aor", "pr",
    "lit", "root", "family", "words",
}


# ---------------------------------------------------------------------------
# Streamlit typography tokens
# ---------------------------------------------------------------------------

# These values intentionally mirror the user's Streamlit theme defaults.
# They are defined here rather than imported from the Pali assets so this module
# remains reusable in an English-only application.
ENG_READER_FONT_FAMILY = "'Source Sans', 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
ENG_READER_MONO_FONT_FAMILY = "'SpaceMono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
ENG_READER_FONT_SIZE = "1rem"
ENG_READER_LINE_HEIGHT = "1.6"
ENG_READER_CODE_FONT_SIZE = ".75rem"
ENG_READER_CODE_BACKGROUND = "#ecebe4"
ENG_READER_BG_MAIN = "#fdfdf8"
ENG_READER_BG_SEC = "#ecebe3"
ENG_READER_BG_SEC_SOFT = "#f1f0e9"
ENG_READER_BG_SIDEBAR = "#f0f0ec"
# Dictionary surface colors. Keep lookup/sidebar/popup panels aligned with
# Streamlit secondaryBackgroundColor by default.
ENG_DICT_BACKGROUND = ENG_READER_BG_SEC
ENG_DICT_INNER_BACKGROUND = ENG_READER_BG_SEC
ENG_SIDEBAR_DICT_BACKGROUND = ENG_READER_BG_SIDEBAR
ENG_POPUP_BACKGROUND = ENG_READER_BG_SEC
ENG_READER_BORDER_COLOR = "#d3d2ca"
ENG_READER_PRIMARY_COLOR = "#3d3a2a"
ENG_READER_TEXT_COLOR = "#3d3a2a"
ENG_READER_MUTED_TEXT_COLOR = "rgba(61, 58, 42, 0.7)"
ENG_READER_CELL_PADDING = "8px"
ENG_READER_CELL_PADDING_COMPACT = "8px"
ENG_READER_ID_CELL_PADDING = "8px"
ENG_READER_PANEL_PADDING = "15px"
ENG_READER_GAP = "20px"
ENG_READER_WORD_PADDING = "0 1px"
ENG_READER_GLOSSARY_WORD_PADDING = "0 2px"
ENG_READER_LOOKUP_TITLE_FONT_SIZE = "1.2rem"
ENG_READER_LOOKUP_BADGE_FONT_SIZE = "0.65rem"
# Thin, low-contrast component scrollbar tokens. These are intentionally lighter
# than the page scrollbar so dictionary iframes/popups do not visually dominate.
ENG_SCROLLBAR_WIDTH = "3px"
ENG_SCROLLBAR_THUMB_COLOR = "rgba(61, 58, 42, 0.10)"
ENG_SCROLLBAR_THUMB_HOVER_COLOR = "rgba(61, 58, 42, 0.18)"
ENG_SCROLLBAR_TRACK_COLOR = "transparent"
ENG_SCROLLBAR_RADIUS = "999px"

ENG_READER_TYPOGRAPHY_CSS = f"""
:root {{
    font-size: 16px;
    --eng-bg-main: {ENG_READER_BG_MAIN};
    --eng-bg-sec: {ENG_READER_BG_SEC};
    --eng-bg-sec-soft: {ENG_READER_BG_SEC_SOFT};
    --eng-bg-sidebar: {ENG_READER_BG_SIDEBAR};
    --eng-dict-bg: {ENG_DICT_BACKGROUND};
    --eng-dict-inner-bg: {ENG_DICT_INNER_BACKGROUND};
    --eng-sidebar-dict-bg: {ENG_SIDEBAR_DICT_BACKGROUND};
    --eng-popup-bg: {ENG_POPUP_BACKGROUND};
    --eng-border: {ENG_READER_BORDER_COLOR};
    --eng-primary: {ENG_READER_PRIMARY_COLOR};
    --eng-reader-font: {ENG_READER_FONT_FAMILY};
    --eng-reader-mono-font: {ENG_READER_MONO_FONT_FAMILY};
    --eng-reader-font-size: {ENG_READER_FONT_SIZE};
    --eng-reader-line-height: {ENG_READER_LINE_HEIGHT};
    --eng-reader-code-font-size: {ENG_READER_CODE_FONT_SIZE};
    --eng-reader-code-bg: {ENG_READER_CODE_BACKGROUND};
    --eng-reader-text: {ENG_READER_TEXT_COLOR};
    --eng-reader-muted: {ENG_READER_MUTED_TEXT_COLOR};
    --eng-reader-cell-padding: {ENG_READER_CELL_PADDING};
    --eng-reader-cell-padding-compact: {ENG_READER_CELL_PADDING_COMPACT};
    --eng-reader-id-cell-padding: {ENG_READER_ID_CELL_PADDING};
    --eng-reader-panel-padding: {ENG_READER_PANEL_PADDING};
    --eng-reader-gap: {ENG_READER_GAP};
    --eng-reader-word-padding: {ENG_READER_WORD_PADDING};
    --eng-reader-glossary-word-padding: {ENG_READER_GLOSSARY_WORD_PADDING};
    --eng-reader-lookup-title-font-size: {ENG_READER_LOOKUP_TITLE_FONT_SIZE};
    --eng-reader-lookup-badge-font-size: {ENG_READER_LOOKUP_BADGE_FONT_SIZE};
    --eng-scrollbar-width: {ENG_SCROLLBAR_WIDTH};
    --eng-scrollbar-thumb: {ENG_SCROLLBAR_THUMB_COLOR};
    --eng-scrollbar-thumb-hover: {ENG_SCROLLBAR_THUMB_HOVER_COLOR};
    --eng-scrollbar-track: {ENG_SCROLLBAR_TRACK_COLOR};
    --eng-scrollbar-radius: {ENG_SCROLLBAR_RADIUS};
}}
"""


def build_typography_css(extra_vars: dict[str, str] | None = None) -> str:
    """Return CSS variables mirroring the Streamlit typography baseline.

    ``extra_vars`` may override ``--eng-reader-*`` CSS custom properties for
    controlled experiments without editing individual CSS builders.
    """
    if not extra_vars:
        return ENG_READER_TYPOGRAPHY_CSS

    lines = [ENG_READER_TYPOGRAPHY_CSS.strip(), ":root {"]
    for key, value in extra_vars.items():
        if not (str(key).startswith("--eng-reader-") or str(key).startswith("--eng-scrollbar-")):
            raise ValueError(f"English reader CSS variable must start with '--eng-reader-' or '--eng-scrollbar-': {key!r}")
        lines.append(f"    {key}: {value};")
    lines.append("}")
    return "\n".join(lines)




def build_scrollbar_css(selector: str = "*") -> str:
    """Return shared thin scrollbar CSS for English reader surfaces."""
    selector = (selector or "*").strip()
    webkit_selector = "" if selector == "*" else selector
    return f"""
        {selector} {{
            scrollbar-width: thin;
            scrollbar-color: var(--eng-scrollbar-thumb, rgba(61, 58, 42, 0.10)) var(--eng-scrollbar-track, transparent);
        }}

        {webkit_selector}::-webkit-scrollbar {{
            width: var(--eng-scrollbar-width, 3px);
            height: var(--eng-scrollbar-width, 3px);
        }}

        {webkit_selector}::-webkit-scrollbar-track {{
            background: var(--eng-scrollbar-track, transparent);
        }}

        {webkit_selector}::-webkit-scrollbar-thumb {{
            background: var(--eng-scrollbar-thumb, rgba(61, 58, 42, 0.10));
            border-radius: var(--eng-scrollbar-radius, 999px);
        }}

        {webkit_selector}::-webkit-scrollbar-thumb:hover {{
            background: var(--eng-scrollbar-thumb-hover, rgba(61, 58, 42, 0.18));
        }}

        {webkit_selector}::-webkit-scrollbar-corner {{
            background: transparent;
        }}
    """


def normalize_lookup_surface_position(position: str | None = "sidebar") -> str:
    """Normalize lookup card placement for English dictionary surfaces."""
    value = str(position or "sidebar").strip().lower()
    if value in {"main", "page", "content", "body"}:
        return "main"
    return "sidebar"


def build_lookup_surface_html(
    html_content: object,
    *,
    position: str | None = "sidebar",
    class_name: str = "eng-lookup-surface-card",
) -> str:
    """Wrap direct ``st.markdown`` English lookup HTML in a placement-aware surface."""
    normalized = normalize_lookup_surface_position(position)
    background = ENG_READER_BG_MAIN if normalized == "main" else ENG_READER_BG_SIDEBAR
    safe_class = html_lib.escape(str(class_name), quote=True)
    content = "" if html_content is None else str(html_content)
    return (
        f'<div class="{safe_class}" style="'
        f'background:{background}; color:{ENG_READER_TEXT_COLOR}; '
        f'border:1px solid {ENG_READER_BORDER_COLOR}; padding:12px 14px; '
        f'box-sizing:border-box; font-family:{ENG_READER_FONT_FAMILY}; '
        f'font-size:{ENG_READER_FONT_SIZE}; line-height:{ENG_READER_LINE_HEIGHT};'
        f'">{content}</div>'
    )


# ---------------------------------------------------------------------------
# Python-side HTML/text helpers
# ---------------------------------------------------------------------------

def sanitize_html(raw_html: object) -> str:
    """Remove scripts, embedded objects, inline event handlers, and javascript: URLs."""
    raw_html = "" if raw_html is None else str(raw_html)

    raw_html = re.sub(
        r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
        "",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    raw_html = re.sub(
        r"<\s*(iframe|object|embed)\b[^>]*>.*?<\s*\/\s*\1\s*>",
        "",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    raw_html = re.sub(
        r"<\s*(iframe|object|embed)\b[^>]*\/?>",
        "",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    raw_html = re.sub(
        r"\s+on\w+\s*=\s*(['\"]).*?\1",
        "",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    raw_html = re.sub(
        r"\s+on\w+\s*=\s*[^\s>]+",
        "",
        raw_html,
        flags=re.IGNORECASE,
    )

    raw_html = re.sub(r"javascript\s*:", "", raw_html, flags=re.IGNORECASE)
    return raw_html


def compact_html(
    raw_html: object,
    *,
    preserve_intertag_whitespace: bool = False,
) -> str:
    """Compact generated HTML without accidentally joining inline words.

    ``preserve_intertag_whitespace=True`` must be used when the HTML already
    contains inline lookup spans separated by meaningful spaces. Removing the
    whitespace between ``</span>`` and ``<span>`` would concatenate words and
    prevent normal line wrapping.
    """
    raw_html = "" if raw_html is None else str(raw_html)
    raw_html = raw_html.strip()

    if preserve_intertag_whitespace:
        return raw_html

    return re.sub(r">\s+<", "><", raw_html)


def estimate_table_iframe_height(raw_html: object) -> int:
    raw_html = "" if raw_html is None else str(raw_html)

    row_count = len(re.findall(r"<tr\b", raw_html, flags=re.IGNORECASE))
    table_count = len(re.findall(r"<table\b", raw_html, flags=re.IGNORECASE))
    paragraph_count = len(re.findall(r"<p\b", raw_html, flags=re.IGNORECASE))
    br_count = len(re.findall(r"<br\b", raw_html, flags=re.IGNORECASE))

    estimated = 32 + row_count * 30 + table_count * 10 + paragraph_count * 30 + br_count * 20
    return max(90, min(8000, estimated))


def strip_html_for_lookup(raw_html: object, *, mode: Literal["text", "table"] = "text") -> str:
    """Return plain text used for collecting English lookup words."""
    extract_html = "" if raw_html is None else str(raw_html)

    for tag in ("script", "style"):
        extract_html = re.sub(
            rf"<{tag}\b[^<]*(?:(?!<\/{tag}>)<[^<]*)*<\/{tag}>",
            " ",
            extract_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

    if mode == "table":
        # Avoid headword/header and compact POS-only cells.
        extract_html = re.sub(r"<th\b[^>]*>.*?</th>", " ", extract_html, flags=re.IGNORECASE | re.DOTALL)
        extract_html = re.sub(
            r"<td\b[^>]*>\s*<b\b[^>]*>.*?</b>\s*</td>",
            " ",
            extract_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        extract_html = re.sub(
            r"<td\b[^>]*>\s*<strong\b[^>]*>.*?</strong>\s*</td>",
            " ",
            extract_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

    for tag in ("code", "pre"):
        extract_html = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            " ",
            extract_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

    plain_text = re.sub(r"<[^>]+>", " ", extract_html)
    plain_text = html_lib.unescape(plain_text)
    plain_text = PALI_DIACRITIC_WORD_RE.sub(" ", plain_text)
    return plain_text


def extract_english_lookup_words(
    raw_html: object,
    *,
    mode: Literal["text", "table"] = "text",
    extra_ignore_words: Iterable[str] | None = None,
) -> set[str]:
    ignore_words = set(TEXT_IGNORE_WORDS if mode == "text" else TABLE_IGNORE_WORDS)

    if extra_ignore_words:
        ignore_words.update(str(w).lower() for w in extra_ignore_words)

    plain_text = strip_html_for_lookup(raw_html, mode=mode)
    words: set[str] = set()

    for word in EN_WORD_RE.findall(plain_text.lower()):
        if len(word) <= 1:
            continue
        if word in ignore_words:
            continue
        words.add(word)

    return words


# ---------------------------------------------------------------------------
# CSS builders
# ---------------------------------------------------------------------------

def build_sidebar_target_html(
    target_id: str,
    placeholder: str = "Chạm từ tiếng Anh...",
    *,
    position: str | None = "sidebar",
    height: int | str | None = None,
    border: bool = True,
) -> str:
    """Build a position-aware English lookup target.

    ``height`` creates an independently scrollable result surface. Main-page
    targets normally receive the height of the adjacent dictionary iframe;
    sidebar targets normally use a compact height such as ``350``.
    """
    normalized = normalize_lookup_surface_position(position)
    background = ENG_READER_BG_MAIN if normalized == "main" else ENG_READER_BG_SIDEBAR
    safe_target_id = html_lib.escape(str(target_id), quote=True)
    safe_position = html_lib.escape(normalized, quote=True)

    height_css = ""
    if height is not None:
        if isinstance(height, (int, float)):
            height_value = f"{max(1, int(height))}px"
        else:
            height_value = str(height).strip()
        if height_value:
            safe_height = html_lib.escape(height_value, quote=True)
            height_css = f"height:{safe_height}; max-height:{safe_height}; overflow-y:auto; overflow-x:hidden;"

    border_css = f"1px solid {ENG_READER_BORDER_COLOR}" if border else "none"

    return (
        "<style>"
        ".eng-lookup-target:empty{display:none;}"
        ".eng-lookup-target{scrollbar-width:thin;scrollbar-color:rgba(61,58,42,.10) transparent;}"
        ".eng-lookup-target::-webkit-scrollbar{width:3px;height:3px;}"
        ".eng-lookup-target::-webkit-scrollbar-track{background:transparent;}"
        ".eng-lookup-target::-webkit-scrollbar-thumb{background:rgba(61,58,42,.10);border-radius:999px;}"
        ".eng-lookup-target::-webkit-scrollbar-thumb:hover{background:rgba(61,58,42,.18);}"
        "</style>"
        f"<div id='{safe_target_id}' class='eng-lookup-target' "
        f"data-eng-surface-position='{safe_position}' "
        f"style=\"background:{background}; border:{border_css}; "
        f"padding:12px; box-sizing:border-box; color:{ENG_READER_TEXT_COLOR}; "
        f"font-family:{ENG_READER_FONT_FAMILY}; font-size:{ENG_READER_FONT_SIZE}; "
        f"line-height:{ENG_READER_LINE_HEIGHT}; {height_css}\">"
        "</div>"
    )


def build_table_root_css(container_id: str, *, extra_vars: dict[str, str] | None = None) -> str:
    return f"""
        {build_typography_css(extra_vars)}
        {build_scrollbar_css()}

        html,
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow-x: hidden;
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            color: var(--eng-reader-text, #3d3a2a);
            font-weight: 400;
            text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
            -webkit-font-smoothing: auto;
        }}

        #{container_id} table.family th {{
            text-align: left;
        }}

        #{container_id} {{
            width: 100%;
            display: block;
            box-sizing: border-box;
            color: var(--eng-reader-text, #3d3a2a);
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            margin: 0;
            padding: 0;
        }}

        #{container_id} .erd-block {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            border: none;
        }}

        #{container_id} .erd-block + .erd-block {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #d3d2ca;
        }}

        #{container_id} .erd-block-no-id {{ border: none; }}

        #{container_id} .erd-block-id {{
            font-family: var(--eng-reader-mono-font);
            font-size: var(--eng-reader-code-font-size);
            color: #777;
            margin: 0 0 4px 0;
            padding: 0;
            line-height: 1.35;
        }}

        #{container_id} .erd-block-content {{ margin: 0; padding: 0; }}
        #{container_id} .erd-block-content > :first-child {{ margin-top: 0 !important; }}
        #{container_id} .erd-block-content > :last-child {{ margin-bottom: 0 !important; }}

        #{container_id} .erd-block-content p {{
            margin: 0 0 0.45rem 0;
            padding: 0;
        }}

        #{container_id} .erd-block-content p:last-child {{ margin-bottom: 0 !important; }}
        #{container_id} .erd-block-content strong,
        #{container_id} .erd-block-content b {{ font-weight: 700; }}
        #{container_id} .erd-block-content em {{ font-style: italic; }}

        #{container_id} .erd-block-content .heading {{
            margin: 0 0 6px 0 !important;
            padding-top: 0;
        }}

        #{container_id} .erd-block-content .underlined {{
            border-bottom: 1px solid #d3d2ca;
            padding-bottom: 4px;
        }}

        #{container_id} .erd-block-content .gray {{ color: #888; }}

        #{container_id} table.dataframe-table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            background: transparent;
        }}

        #{container_id} table.dataframe-table th,
        #{container_id} table.dataframe-table td {{
            border: 1px solid var(--eng-border);
            padding: var(--eng-reader-cell-padding-compact);
            vertical-align: top;
            line-height: var(--eng-reader-line-height);
            word-break: normal;
            overflow-wrap: anywhere;
        }}

        #{container_id} table.dataframe-table th {{
            background: var(--eng-popup-bg, var(--eng-bg-sec));
            font-weight: 700;
            text-align: left;
            white-space: nowrap;
        }}

        #{container_id}.english-reader-table-root .eng-word {{
            cursor: pointer;
            transition: 0.15s;
            color: inherit;
            background: transparent;
            border: none;
            border-bottom: 1px solid transparent;
            padding: 0;
            border-radius: 0;
            font-weight: inherit;
        }}

        #{container_id}.english-reader-table-root .eng-word:hover,
        #{container_id}.english-reader-table-root .eng-word.active-en {{
            color: #5d7367;
            background: transparent;
            border-bottom: 1px solid #5d7367;
            padding: 0;
            border-radius: 0;
            font-weight: inherit;
        }}
    """


def build_text_root_css(container_id: str, *, extra_vars: dict[str, str] | None = None) -> str:
    return f"""
        {build_typography_css(extra_vars)}
        {build_scrollbar_css()}

        #{container_id} {{
            width: 100%;
            box-sizing: border-box;
            color: var(--eng-reader-text, #3d3a2a);
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            margin: 0;
            padding: 0;
        }}

        #{container_id} p {{ margin: 0 0 0.65rem 0; padding: 0; }}
        #{container_id} p:last-child {{ margin-bottom: 0; }}
        #{container_id} .ert-line {{ margin: 0 0 0.35rem 0; padding: 0; }}
        #{container_id} .ert-line:last-child {{ margin-bottom: 0; }}
        #{container_id} .ert-blank-line {{ height: 0.65rem; }}

        #{container_id} ul,
        #{container_id} ol {{
            margin-top: 0.35rem;
            margin-bottom: 0.65rem;
        }}

        #{container_id} blockquote {{
            margin: 0.5rem 0;
            padding-left: 0.8rem;
            border-left: 3px solid #d3d2ca;
            color: #5f5b48;
        }}

        #{container_id} code {{
            background: var(--eng-reader-code-bg);
            padding: 1px 4px;
            border-radius: 3px;
            font-family: var(--eng-reader-mono-font);
            font-size: var(--eng-reader-code-font-size);
        }}
    """


def build_text_word_style_css(container_id: str, *, extra_vars: dict[str, str] | None = None) -> str:
    return f"""
        #{container_id}.english-reader-text-root .eng-word {{
            cursor: pointer;
            transition: 0.15s;
            color: inherit;
            background: transparent;
            border: none;
            border-bottom: 1px solid transparent;
            padding: 0;
            border-radius: 0;
            font-weight: inherit;
        }}

        #{container_id}.english-reader-text-root .eng-word:hover,
        #{container_id}.english-reader-text-root .eng-word.active-en {{
            color: #5d7367;
            background: transparent;
            border-bottom: 1px solid #5d7367;
            padding: 0;
            border-radius: 0;
            font-weight: inherit;
        }}
    """


def build_popup_css(
    popup_class: str,
    close_class: str = "",
    *,
    extra_vars: dict[str, str] | None = None,
) -> str:
    """Build shared popup CSS.

    ``close_class`` is retained only for backward-compatible callers. Hover
    popups no longer render a close button, so no close-button CSS is emitted.
    """
    return f"""
        {build_typography_css(extra_vars)}
        {build_scrollbar_css('.' + popup_class)}

        .{popup_class} {{
            display: none;
            position: fixed;
            z-index: 999999;
            width: 510px;
            max-width: calc(100vw - 16px);
            max-height: 400px;
            overflow-y: auto;
            background: var(--eng-popup-bg, var(--eng-bg-sec));
            border: 1px solid var(--eng-border);
            box-shadow: 0 4px 18px rgba(0,0,0,0.22);
            padding: 12px;
            box-sizing: border-box;
            color: var(--eng-reader-text, #3d3a2a);
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
        }}

        .{popup_class}.visible {{ display: block; }}
    """



def wrap_english_text_for_lookup(text: object, *, word_class: str = "eng-word") -> str:
    """Escape plain text and wrap English tokens with lookup spans.

    This is intended for controlled reader text, not raw dictionary HTML.
    It preserves whitespace and punctuation while storing a clean lowercase lookup key.
    """
    text = "" if text is None else str(text)
    parts = re.split(r"(\s+)", text)
    out: list[str] = []

    for part in parts:
        if not part:
            continue
        if part.isspace():
            out.append(part)
            continue

        match = EN_WORD_RE.search(part)
        if not match:
            out.append(html_lib.escape(part))
            continue

        clean_word = match.group(0).lower()
        safe_text = html_lib.escape(part)
        safe_word = html_lib.escape(clean_word, quote=True)
        safe_class = html_lib.escape(word_class, quote=True)
        out.append(f"<span class='{safe_class}' data-word='{safe_word}'>{safe_text}</span>")

    return "".join(out)


# ---------------------------------------------------------------------------
# Glossary helpers for controlled English reader text
# ---------------------------------------------------------------------------

def normalize_glossary_key(term: object) -> str:
    """Normalize glossary keys for stable Python-side matching."""
    return re.sub(r"\s+", " ", str(term).strip()).casefold()


def normalize_lookup_key(term: object) -> str:
    """Normalize keys used by JS lookup dictionaries."""
    return re.sub(r"\s+", " ", str(term).strip()).lower()


def is_english_glossary_phrase(norm_key: object) -> bool:
    """Return True when a normalized glossary key is a phrase."""
    return " " in str(norm_key).strip()


def build_glossary_map(
    glossary: dict[str, str] | None,
    *,
    allow_phrases: bool = True,
) -> dict[str, dict[str, object]]:
    """Normalize user glossary data for controlled English readers.

    Output shape:
        {
            normalized_key: {
                "term": original_term,
                "lookup_key": normalized_lookup_key,
                "meaning": meaning,
                "is_phrase": bool,
            }
        }
    """
    if not glossary:
        return {}

    result: dict[str, dict[str, object]] = {}

    for term, meaning in glossary.items():
        raw_term = str(term).strip()
        raw_meaning = "" if meaning is None else str(meaning).strip()

        # Empty meanings are intentionally kept. This allows users to
        # pre-mark glossary terms for highlight first, then fill meanings later.
        # Merge helpers decide whether a glossary meaning should be displayed.
        if not raw_term:
            continue

        norm_key = normalize_glossary_key(raw_term)
        is_phrase = is_english_glossary_phrase(norm_key)

        if is_phrase and not allow_phrases:
            continue

        result[norm_key] = {
            "term": raw_term,
            "lookup_key": normalize_lookup_key(raw_term),
            "meaning": raw_meaning,
            "has_meaning": bool(raw_meaning),
            "is_phrase": is_phrase,
        }

    return result


def compile_glossary_pattern(glossary_map: dict[str, dict[str, object]]):
    """Compile a phrase-aware glossary matching pattern.

    Longer terms are matched first so that phrases such as "present mind" are
    not partially consumed by shorter terms such as "mind".
    """
    if not glossary_map:
        return None

    terms = sorted(
        [str(item.get("term", "")).strip() for item in glossary_map.values()],
        key=len,
        reverse=True,
    )

    escaped_terms: list[str] = []

    for term in terms:
        if not term:
            continue
        escaped = re.escape(term)
        escaped = re.sub(r"\\\s+", r"\\s+", escaped)
        escaped = escaped.replace(r"\ ", r"\s+")
        escaped_terms.append(escaped)

    if not escaped_terms:
        return None

    return re.compile(
        r"(?<![A-Za-z])(" + "|".join(escaped_terms) + r")(?![A-Za-z])",
        flags=re.IGNORECASE,
    )


def format_glossary_meaning_html(term: object, meaning: object, *, label: str = "In Glossary") -> str:
    """Return safe HTML for a user glossary meaning block.

    Empty meanings return an empty string; the term may still be highlighted,
    but no glossary block is merged into the dictionary payload.
    """
    safe_term = html_lib.escape(str(term).strip())
    safe_label = html_lib.escape(str(label).strip() or "In Glossary")
    raw_meaning = "" if meaning is None else str(meaning).strip()

    if not raw_meaning:
        return ""

    safe_meaning = html_lib.escape(raw_meaning).replace("\n", "<br>")

    return (
        "<div class='eng-glossary-block'>"
        f"<div class='eng-glossary-label'>{safe_label}</div>"
        f"<div class='eng-glossary-term'>{safe_term}</div>"
        f"<div class='eng-glossary-meaning'>{safe_meaning}</div>"
        "</div>"
    )


def merge_glossary_into_lookup_dict(
    lookup_dict: dict[str, str] | None,
    glossary_map: dict[str, dict[str, object]],
    *,
    matched_keys: set[str] | None = None,
) -> dict[str, str]:
    """Merge glossary meanings into an English→Vietnamese lookup dictionary.

    Only matched glossary keys are merged when matched_keys is provided. This
    keeps the JS payload bounded when the user glossary is large.
    """
    result = dict(lookup_dict or {})

    if not glossary_map:
        return result

    keys = set(glossary_map.keys()) if matched_keys is None else set(matched_keys)

    for norm_key in keys:
        item = glossary_map.get(norm_key)
        if not item:
            continue

        lookup_key = str(item.get("lookup_key") or normalize_lookup_key(item.get("term", "")))
        if not lookup_key:
            continue

        glossary_html = format_glossary_meaning_html(
            item.get("term", lookup_key),
            item.get("meaning", ""),
        )

        # Empty glossary meanings should not override or expand the lookup data.
        # The term is still highlighted because it remains in glossary_map.
        if not glossary_html:
            continue

        old_meaning = str(result.get(lookup_key, "")).strip()

        if old_meaning:
            result[lookup_key] = f"{glossary_html}<div class='eng-glossary-dict-divider'></div>{old_meaning}"
        else:
            result[lookup_key] = glossary_html

    return result


def wrap_english_text_for_lookup_with_glossary(
    text: object,
    glossary_map: dict[str, dict[str, object]],
    *,
    word_class: str = "eng-word",
    glossary_class: str = "eng-word glossary-hit",
) -> tuple[str, set[str]]:
    """Wrap controlled English text while prioritizing glossary terms.

    Returns:
        (html, matched_glossary_keys)
    """
    if not glossary_map:
        return wrap_english_text_for_lookup(text, word_class=word_class), set()

    pattern = compile_glossary_pattern(glossary_map)
    if pattern is None:
        return wrap_english_text_for_lookup(text, word_class=word_class), set()

    raw_text = "" if text is None else str(text)
    html_parts: list[str] = []
    matched_keys: set[str] = set()
    last_pos = 0

    for match in pattern.finditer(raw_text):
        start, end = match.span()

        if start > last_pos:
            html_parts.append(wrap_english_text_for_lookup(raw_text[last_pos:start], word_class=word_class))

        matched_text = match.group(0)
        norm_key = normalize_glossary_key(matched_text)
        item = glossary_map.get(norm_key)

        if item:
            matched_keys.add(norm_key)
            lookup_key = str(item.get("lookup_key") or normalize_lookup_key(item.get("term", matched_text)))
            safe_text = html_lib.escape(matched_text)
            safe_lookup_key = html_lib.escape(lookup_key, quote=True)
            safe_class = html_lib.escape(glossary_class, quote=True)
            html_parts.append(
                f"<span class='{safe_class}' data-word='{safe_lookup_key}' "
                f"data-glossary='1' title='In Glossary'>{safe_text}</span>"
            )
        else:
            html_parts.append(wrap_english_text_for_lookup(matched_text, word_class=word_class))

        last_pos = end

    if last_pos < len(raw_text):
        html_parts.append(wrap_english_text_for_lookup(raw_text[last_pos:], word_class=word_class))

    return "".join(html_parts), matched_keys


def build_glossary_css(container_id: str) -> str:
    """CSS for glossary highlights and merged glossary meaning blocks."""
    return f"""
        #{container_id} .glossary-hit {{
            background-color: rgba(255, 218, 80, 0.35) !important;
            border-bottom: 1.5px solid rgba(120, 90, 0, 0.55);
            border-radius: 3px;
            padding: var(--eng-reader-glossary-word-padding);
            cursor: pointer;
        }}

        #{container_id} .glossary-hit:hover,
        #{container_id} .glossary-hit.active,
        #{container_id} .glossary-hit.active-en {{
            background-color: rgba(255, 218, 80, 0.58) !important;
            border-bottom: 2px solid rgba(120, 90, 0, 0.7);
            color: var(--eng-reader-text, #3d3a2a);
        }}

        .eng-glossary-block {{
            background: rgba(255, 218, 80, 0.22);
            border-left: 3px solid rgba(120, 90, 0, 0.55);
            padding: 8px 10px;
            margin: 0 0 10px 0;
            box-sizing: border-box;
        }}

        .eng-glossary-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: #6f5200;
            margin-bottom: 2px;
        }}

        .eng-glossary-term {{
            font-weight: 700;
            color: var(--eng-reader-text, #3d3a2a);
            margin-bottom: 4px;
        }}

        .eng-glossary-meaning {{
            color: var(--eng-reader-text, #3d3a2a);
            line-height: 1.5;
        }}

        .eng-glossary-dict-divider {{
            height: 1px;
            background: #d3d2ca;
            margin: 10px 0;
        }}
    """


def build_basic_reader_css(
    *,
    container_id: str,
    grid_template: str,
    border_table: str,
    extra_vars: dict[str, str] | None = None,
) -> str:
    """CSS profile for render_english_reader's simple En→Vi reader."""
    return f"""
        {build_typography_css(extra_vars)}
        {build_scrollbar_css()}

        html,
        body {{
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            background-color: var(--eng-bg-main, #fdfdf8);
            color: var(--eng-reader-text, #3d3a2a);
            margin: 0;
            height: 100vh;
            overflow: hidden;
            font-weight: 400;
            text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
            -webkit-font-smoothing: auto;
        }}

        .main-grid {{
            display: grid;
            grid-template-columns: {grid_template};
            height: 100%;
            gap: var(--eng-reader-gap);
            align-items: start;
            box-sizing: border-box;
        }}

        .text-col {{
            padding: 0;
            overflow-y: auto;
            overflow-x: hidden;
            min-width: 0;
            height: 100%;
            box-sizing: border-box;
        }}

        .dict-col {{
            /* Local En→Vi result panel lives on the main page surface. */
            background: var(--eng-bg-main, #fdfdf8);
            border: {border_table};
            padding: var(--eng-reader-panel-padding);
            overflow-y: auto;
            border-radius: 0;
            box-sizing: border-box;
            height: 100vh;
        }}

        #{container_id} table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            border: {border_table};
            margin-top: 0;
        }}

        #{container_id} td {{
            padding: var(--eng-reader-cell-padding);
            border: {border_table};
            vertical-align: middle;
        }}

        #{container_id} .id-col {{
            font-family: var(--eng-reader-mono-font);
            font-size: var(--eng-reader-code-font-size);
            width: 1%;
            min-width: max-content;
            white-space: nowrap;
            text-align: center;
            padding: var(--eng-reader-id-cell-padding);
            color: inherit;
            box-sizing: border-box;
        }}

        #{container_id} .content-col {{
            width: auto;
            min-width: 0;
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            white-space: normal;
            word-break: normal;
            overflow-wrap: break-word;
        }}

        #{container_id} .eng-word {{
            cursor: pointer;
            border-radius: 3px;
            transition: 0.15s;
            padding: var(--eng-reader-word-padding);
            display: inline;
            color: inherit;
        }}

        #{container_id} .eng-word:hover,
        #{container_id} .eng-word.active,
        #{container_id} .eng-word.active-en {{
            background: var(--eng-bg-sec);
            border-bottom: 2px solid #5d7367;
            font-weight: 600;
            color: #5d7367;
        }}

        /* English→Vietnamese overlay inside Longman/Oxford result HTML.
           Hover/active states intentionally do not change geometry. */
        .dict-col .eng-sub-word {{
            cursor: pointer;
            color: inherit;
            background: transparent;
            border: none;
            padding: 0;
            margin: 0;
            border-radius: 0;
            font-weight: inherit;
            transition: color 0.15s, background-color 0.15s;
        }}

        .dict-col .eng-sub-word:hover,
        .dict-col .eng-sub-word.active-en {{
            color: #5d7367;
            background: rgba(93, 115, 103, 0.10);
            border: none;
            padding: 0;
            margin: 0;
            font-weight: inherit;
        }}
    """


from dict_lookup_popup_assets import ENGLISH_POPUP_JS

ENG_READER_HOVER_LOOKUP_HELPER_JS = ENGLISH_POPUP_JS + r"""
function bindEnglishLookupHover(root, selector, handler, leaveHandler) {
    if (!root || !selector || typeof handler !== 'function') {
        return function() {};
    }

    const overListener = function(e) {
        const target = e.target && e.target.closest ? e.target.closest(selector) : null;
        if (!target) return;

        if (root.nodeType === 1 && root.contains && !root.contains(target)) return;

        const related = e.relatedTarget;
        if (related && target.contains && (related === target || target.contains(related))) return;

        handler(target, e);
    };

    const outListener = typeof leaveHandler === 'function'
        ? function(e) {
            const target = e.target && e.target.closest ? e.target.closest(selector) : null;
            if (!target) return;

            if (root.nodeType === 1 && root.contains && !root.contains(target)) return;

            const related = e.relatedTarget;
            if (related && target.contains && (related === target || target.contains(related))) return;

            leaveHandler(target, e);
        }
        : null;

    root.addEventListener('mouseover', overListener, true);
    if (outListener) root.addEventListener('mouseout', outListener, true);

    return function() {
        try { root.removeEventListener('mouseover', overListener, true); } catch (err) {}
        try { if (outListener) root.removeEventListener('mouseout', outListener, true); } catch (err) {}
    };
}

/*
 * Shared lifecycle for interactive hover popups.
 *
 * The word and its popup are treated as one logical hover region:
 * - leaving a word schedules close after a short grace period;
 * - entering the popup cancels that close so the user can scroll/copy;
 * - leaving the popup schedules close again;
 * - entering another word cancels the pending close immediately.
 */
function createEnglishHoverPopupLifecycle(getPopup, closeHandler, delayMs) {
    const delay = Number.isFinite(Number(delayMs)) ? Math.max(0, Number(delayMs)) : 500;
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
            if (typeof closeHandler === 'function') closeHandler();
        }, delay);
    }

    function detachPopup() {
        if (!popup) return;
        try {
            if (popupEnterHandler) popup.removeEventListener('mouseenter', popupEnterHandler);
            if (popupLeaveHandler) popup.removeEventListener('mouseleave', popupLeaveHandler);
        } catch (err) {}
        popup = null;
        popupEnterHandler = null;
        popupLeaveHandler = null;
    }

    function attachPopup() {
        const nextPopup = typeof getPopup === 'function' ? getPopup() : null;
        if (!nextPopup) return null;
        if (popup === nextPopup) return popup;

        detachPopup();
        popup = nextPopup;
        popup.style.pointerEvents = 'auto';
        popupEnterHandler = function() { cancelClose(); };
        popupLeaveHandler = function() { scheduleClose(); };
        popup.addEventListener('mouseenter', popupEnterHandler);
        popup.addEventListener('mouseleave', popupLeaveHandler);
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
}
"""


BASIC_READER_JS_TEMPLATE = r"""
<script>
(function() {
    __HOVER_LOOKUP_HELPER_JS__

    let dictState = {
        enVi: __EN_VI_JSON__
    };

    const isSidebar = __IS_SIDEBAR__;
    const isPopup = __IS_POPUP__;
    const containerId = "__CONTAINER_ID__";
    const targetId = "__TARGET_ID__";
    const cleanupKey = "__CLEANUP_KEY__";
    const popupId = "__POPUP_ID__";
    const popupContentId = "__POPUP_CONTENT_ID__";
    const popupStyleId = "__POPUP_STYLE_ID__";
    const popupClass = "__POPUP_CLASS__";
    const popupCss = decodeURIComponent("__POPUP_CSS_ENCODED__");

    const parentDoc = window.parent.document;
    const parentWin = window.parent;

    if (parentWin[cleanupKey]) {
        try { parentWin[cleanupKey](); } catch (err) {}
    }

    let container = null;
    let clickHandler = null;
    let hoverCleanup = null;
    let parentClickHandler = null;
    let keyHandler = null;
    let beforeUnloadHandler = null;
    let parentPopup = null;
    let popupLifecycle = null;

    function removeElementById(id) {
        if (!id) return;
        try {
            const el = parentDoc.getElementById(id);
            if (el && el.parentNode) {
                try { el.innerHTML = ""; } catch (err) {}
                el.parentNode.removeChild(el);
            }
        } catch (err) {}
    }

    function removePopupArtifacts() {
        removeElementById(popupId);
        removeElementById(popupStyleId);
    }

    function ensurePopupStyle() {
        if (!isPopup) return;
        if (parentDoc.getElementById(popupStyleId)) return;
        const style = parentDoc.createElement("style");
        style.id = popupStyleId;
        style.textContent = popupCss;
        parentDoc.head.appendChild(style);
    }

    function createPopup() {
        if (!isPopup) return null;
        ensurePopupStyle();
        let popup = parentDoc.getElementById(popupId);
        if (!popup) {
            popup = parentDoc.createElement("div");
            popup.id = popupId;
            popup.className = popupClass;
            popup.innerHTML = `<div id="${popupContentId}"></div>`;
            parentDoc.body.appendChild(popup);
        }
        return popup;
    }

    function hidePopup() {
        if (popupLifecycle) popupLifecycle.cancelClose();
        if (parentPopup) parentPopup.classList.remove("visible");
        if (isPopup) clearActive();
    }

    function buildContent(cleanWord) {
        const enViDictionary = dictState ? dictState.enVi : {};
        const meaning = Object.prototype.hasOwnProperty.call(enViDictionary, cleanWord)
            ? enViDictionary[cleanWord]
            : "<div style='color:#5d7367; padding:10px; background:var(--eng-bg-sec); border-radius:4px;'>Không tìm thấy trong từ điển.</div>";

        return meaning || "<div style='color:#5d7367; padding:10px; background:var(--eng-bg-sec); border-radius:4px;'>Không tìm thấy trong từ điển.</div>";
    }

    function setTargetHtml(html) {
        const target = isSidebar ? parentDoc.getElementById(targetId) : document.getElementById(targetId);
        if (target) target.innerHTML = html;
    }

    function showPopup(content, targetEl) {
        if (!parentPopup) return;
        const contentEl = parentDoc.getElementById(popupContentId);
        if (!contentEl) return;

        contentEl.innerHTML = content;
        parentPopup.classList.add("visible");

        scappEnglishPopup.place(parentPopup, targetEl, {width: 510});
    }

    function clearActive() {
        if (!container) return;
        container.querySelectorAll('.eng-word').forEach(function(el) {
            el.classList.remove('active');
            el.classList.remove('active-en');
        });
    }

    function handleLookup(target) {
        if (popupLifecycle) popupLifecycle.cancelClose();
        clearActive();
        target.classList.add('active-en');

        const cleanWord = (target.getAttribute('data-word') || target.textContent || '').trim().toLowerCase();
        if (!cleanWord) return;
        const content = buildContent(cleanWord);

        if (isSidebar) {
            hidePopup();
            setTargetHtml(content);
        } else if (isPopup) {
            showPopup(content, target);
        } else {
            hidePopup();
            setTargetHtml(content);
        }
    }

    function setup() {
        container = document.getElementById(containerId);
        if (!container) return;

        removePopupArtifacts();
        if (isPopup) {
            parentPopup = createPopup();
            popupLifecycle = createEnglishHoverPopupLifecycle(
                function() { return parentPopup; },
                hidePopup
            );
            popupLifecycle.attachPopup();
        }

        clickHandler = function(e) {
            const target = e.target && e.target.closest ? e.target.closest('.eng-word') : null;
            if (!target || !container.contains(target)) {
                if (isPopup) hidePopup();
                return;
            }

            e.preventDefault();
            e.stopPropagation();
            handleLookup(target);
        };

        container.addEventListener('click', clickHandler, true);
        hoverCleanup = bindEnglishLookupHover(
            container,
            '.eng-word',
            function(target, e) {
                if (popupLifecycle) popupLifecycle.cancelClose();
                handleLookup(target, e);
            },
            isPopup
                ? function() { if (popupLifecycle) popupLifecycle.scheduleClose(); }
                : null
        );

        if (isPopup) {
            parentClickHandler = function(e) {
                if (
                    parentPopup
                    && parentPopup.classList.contains("visible")
                    && !parentPopup.contains(e.target)
                ) {
                    hidePopup();
                }
            };
            parentDoc.addEventListener("click", parentClickHandler, true);
        }

        keyHandler = function(e) {
            if (e.key === "Escape") hidePopup();
        };
        document.addEventListener("keydown", keyHandler);
        parentDoc.addEventListener("keydown", keyHandler);

        beforeUnloadHandler = function() {
            try { if (parentWin[cleanupKey]) parentWin[cleanupKey](); } catch (err) {}
        };
        window.addEventListener('beforeunload', beforeUnloadHandler);
    }

    function cleanup() {
        try { if (container && clickHandler) container.removeEventListener('click', clickHandler, true); } catch (err) {}
        try { if (hoverCleanup) hoverCleanup(); } catch (err) {}
        try { if (popupLifecycle) popupLifecycle.cleanup(); } catch (err) {}
        try { if (parentClickHandler) parentDoc.removeEventListener("click", parentClickHandler, true); } catch (err) {}
        try {
            if (keyHandler) {
                document.removeEventListener("keydown", keyHandler);
                parentDoc.removeEventListener("keydown", keyHandler);
            }
        } catch (err) {}
        try { if (beforeUnloadHandler) window.removeEventListener('beforeunload', beforeUnloadHandler); } catch (err) {}
        try {
            if (dictState) {
                dictState.enVi = null;
                dictState = null;
            }
        } catch (err) {}
        removePopupArtifacts();
        container = null;
        clickHandler = null;
        hoverCleanup = null;
        parentClickHandler = null;
        keyHandler = null;
        parentPopup = null;
        popupLifecycle = null;
        try { delete parentWin[cleanupKey]; } catch (err) {
            try { parentWin[cleanupKey] = null; } catch (err2) {}
        }
    }

    setup();
    parentWin[cleanupKey] = cleanup;
})();
</script>
"""


def build_basic_reader_js(
    *,
    en_vi_json: str,
    is_sidebar: bool,
    container_id: str,
    target_id: str,
    cleanup_key: str,
    is_popup: bool = False,
    typography_vars: dict[str, str] | None = None,
    popup_id: str | None = None,
    popup_content_id: str | None = None,
    popup_style_id: str | None = None,
    popup_class: str = "english-reader-parent-popup",
    popup_close_class: str = "english-reader-parent-popup-close",
) -> str:
    """Build JS for render_english_reader.

    Modes:
    - left/default: show lookup in the in-iframe dictionary column.
    - sidebar: show lookup in the Streamlit sidebar target.
    - popup: show lookup in a parent-document popup to avoid iframe clipping.
    """
    from urllib.parse import quote

    popup_id = popup_id or f"{container_id}-popup"
    popup_content_id = popup_content_id or f"{popup_id}-content"
    popup_style_id = popup_style_id or f"{popup_id}-style"
    popup_css = build_popup_css(popup_class, popup_close_class, extra_vars=typography_vars)

    replacements = {
        "__EN_VI_JSON__": en_vi_json,
        "__IS_SIDEBAR__": _js_bool(is_sidebar),
        "__IS_POPUP__": _js_bool(is_popup),
        "__CONTAINER_ID__": str(container_id),
        "__TARGET_ID__": str(target_id),
        "__CLEANUP_KEY__": str(cleanup_key),
        "__POPUP_ID__": str(popup_id),
        "__POPUP_CONTENT_ID__": str(popup_content_id),
        "__POPUP_STYLE_ID__": str(popup_style_id),
        "__POPUP_CLASS__": str(popup_class),
        "__POPUP_CSS_ENCODED__": quote(popup_css or ""),
        "__HOVER_LOOKUP_HELPER_JS__": ENG_READER_HOVER_LOOKUP_HELPER_JS,
    }
    out = BASIC_READER_JS_TEMPLATE
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


SOURCE_LOOKUP_READER_JS_TEMPLATE = r"""
<script>
(function() {
    __HOVER_LOOKUP_HELPER_JS__

    let dictState = {
        source: __SOURCE_JSON__,
        enVi: __ENVI_JSON__
    };

    const textRootId = "__TEXT_ROOT_ID__";
    const targetId = "__TARGET_ID__";
    const cleanupKey = "__CLEANUP_KEY__";
    const sourceLabel = "__SOURCE_LABEL__";
    const popupId = "__POPUP_ID__";
    const popupContentId = "__POPUP_CONTENT_ID__";
    const popupStyleId = "__POPUP_STYLE_ID__";
    const popupClass = "__POPUP_CLASS__";
    const popupCss = decodeURIComponent("__POPUP_CSS_ENCODED__");

    const parentDoc = window.parent.document;
    const parentWin = window.parent;

    __ENTRY_DECORATOR_JS__

    if (parentWin[cleanupKey]) {
        try { parentWin[cleanupKey](); } catch (err) {}
    }

    let textRoot = null;
    let sourceTarget = null;
    let bodyClickHandler = null;
    let subWordHoverCleanup = null;
    let beforeUnloadHandler = null;
    let parentPopup = null;
    let popupLifecycle = null;

    window.toggle = function(expandable) {
        if (!expandable) return;
        const expParent = expandable.parentNode;
        const target = expParent ? expParent.querySelector('.content') : null;
        const arrow = expParent ? expParent.querySelector('span.arrow') : null;
        if (target) {
            const isExpanded = target.style.display === 'block';
            target.style.display = isExpanded ? 'none' : 'block';
            if (arrow) arrow.innerHTML = isExpanded ? '\u25BA' : '\u25BC';
        }
    };

    window.showAtLink = function(ele) {
        if (!ele) return;
        const target = ele.nextElementSibling;
        if (target) target.style.display = target.style.display === 'block' ? 'none' : 'block';
    };

    window.toggleImg = function(ele) {
        if (!ele) return;
        ele.style.maxHeight = (ele.style.maxHeight === 'none') ? '4em' : 'none';
    };

    function removeElementById(id) {
        if (!id) return;
        try {
            const el = parentDoc.getElementById(id);
            if (el && el.parentNode) el.parentNode.removeChild(el);
        } catch (err) {}
    }

    function removePopupArtifacts() {
        removeElementById(popupId);
        removeElementById(popupStyleId);
    }

    function ensurePopupStyle() {
        if (parentDoc.getElementById(popupStyleId)) return;
        const style = parentDoc.createElement('style');
        style.id = popupStyleId;
        style.textContent = popupCss;
        parentDoc.head.appendChild(style);
    }

    function createPopup() {
        ensurePopupStyle();
        let popup = parentDoc.getElementById(popupId);
        if (!popup) {
            popup = parentDoc.createElement('div');
            popup.id = popupId;
            popup.className = popupClass;
            popup.innerHTML = `<div id="${popupContentId}"></div>`;
            popup.style.pointerEvents = 'auto';
            parentDoc.body.appendChild(popup);
        }
        return popup;
    }

    function clearActive() {
        if (!textRoot) return;
        textRoot.querySelectorAll('.eng-word').forEach(function(el) {
            el.classList.remove('active');
            el.classList.remove('active-en');
        });
    }

    function clearSubActive() {
        if (!sourceTarget) return;
        sourceTarget.querySelectorAll('.eng-sub-word').forEach(function(el) {
            el.classList.remove('active-en');
        });
    }

    function buildEnViContent(enWord) {
        const enViDictionary = dictState ? dictState.enVi : {};
        const meaning = Object.prototype.hasOwnProperty.call(enViDictionary, enWord)
            ? enViDictionary[enWord]
            : "<div style='color:#5d7367; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";

        return meaning || "<div style='color:#5d7367; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";
    }

    function positionPopup(targetEl) {
        if (!parentPopup || !targetEl) return;

        scappEnglishPopup.place(parentPopup, targetEl, {width: 510});
    }

    function showEnViPopup(target) {
        if (!target) return;
        if (popupLifecycle) popupLifecycle.cancelClose();
        const enWord = (target.getAttribute('data-word') || target.textContent || '').trim().toLowerCase();
        if (!enWord) return;

        clearSubActive();
        target.classList.add('active-en');

        if (!parentPopup) parentPopup = createPopup();
        const contentEl = parentDoc.getElementById(popupContentId);
        if (!parentPopup || !contentEl) return;

        contentEl.innerHTML = buildEnViContent(enWord);
        parentPopup.classList.add('visible');
        positionPopup(target);
    }

    function hideEnViPopup() {
        if (popupLifecycle) popupLifecycle.cancelClose();
        clearSubActive();
        if (parentPopup) parentPopup.classList.remove('visible');
    }

    function wrapEnglishWords(htmlContent) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent || '';
        const enViDictionary = dictState ? dictState.enVi : {};
        const walker = document.createTreeWalker(
            tempDiv,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    if (
                        parent.closest(
                            'script, style, audio, video, button, a, code, pre, .eng-sub-word, .no-en-lookup'
                        )
                    ) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    if (!/[a-zA-Z]/.test(node.nodeValue || '')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            },
            false
        );

        const nodes = [];
        let n;
        while ((n = walker.nextNode())) nodes.push(n);

        nodes.forEach(function(node) {
            const rawText = node.nodeValue || '';
            const regex = /\b([a-zA-Z]+(?:'[a-zA-Z]+)?)\b/g;
            const fragment = document.createDocumentFragment();
            let match;
            let lastIndex = 0;
            let changed = false;

            while ((match = regex.exec(rawText)) !== null) {
                const full = match[0];
                const key = String(match[1] || '').toLowerCase();

                if (!Object.prototype.hasOwnProperty.call(enViDictionary, key)) {
                    continue;
                }
                if (!enViDictionary[key]) {
                    continue;
                }

                if (match.index > lastIndex) {
                    fragment.appendChild(
                        document.createTextNode(rawText.slice(lastIndex, match.index))
                    );
                }

                const span = document.createElement('span');
                span.className = 'eng-sub-word';
                span.setAttribute('data-word', key);
                span.textContent = full;
                fragment.appendChild(span);

                lastIndex = match.index + full.length;
                changed = true;
            }

            if (!changed) return;

            if (lastIndex < rawText.length) {
                fragment.appendChild(document.createTextNode(rawText.slice(lastIndex)));
            }

            if (node.parentNode) {
                node.parentNode.replaceChild(fragment, node);
            }
        });

        return tempDiv.innerHTML;
    }

    function showLookup(target) {
        clearActive();
        hideEnViPopup();
        target.classList.add('active');

        const cleanWord = (target.getAttribute('data-word') || target.textContent || '').trim().toLowerCase();
        if (!cleanWord) return;

        const dictionary = dictState ? dictState.source : {};
        const rawMeaning = Object.prototype.hasOwnProperty.call(dictionary, cleanWord)
            ? dictionary[cleanWord]
            : `<div style="color:#d63031; padding:10px;">Không tìm thấy trong ${sourceLabel}.</div>`;
        const meaning = wrapEnglishWords(rawMeaning);

        if (!sourceTarget) return;
        sourceTarget.innerHTML = meaning || `<div style="color:#d63031; padding:10px;">Không tìm thấy trong ${sourceLabel}.</div>`;
        if (typeof decorateLongmanEntryHeaders === 'function') {
            decorateLongmanEntryHeaders(sourceTarget);
        }
    }

    function handleLinkClick(e) {
        const aTag = e.target && e.target.closest ? e.target.closest('a') : null;
        if (!aTag) return false;

        const href = aTag.getAttribute('href');
        const target = aTag.getAttribute('target');
        if (!href) return false;

        if (href.startsWith('#')) {
            e.preventDefault();
            const targetIdLocal = href.substring(1);
            const targetEl = document.getElementById(targetIdLocal) || document.getElementsByName(targetIdLocal)[0];
            if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return true;
        }

        if (target === '_blank') {
            e.preventDefault();
            parentWin.open(href, '_blank');
            return true;
        }

        if (target === '_parent') {
            e.preventDefault();
            parentWin.location.href = href;
            return true;
        }

        return false;
    }

    function setup() {
        textRoot = document.getElementById(textRootId);
        sourceTarget = document.getElementById(targetId);
        if (!textRoot || !sourceTarget) return;

        removePopupArtifacts();
        parentPopup = createPopup();
        popupLifecycle = createEnglishHoverPopupLifecycle(
            function() { return parentPopup; },
            hideEnViPopup
        );
        popupLifecycle.attachPopup();

        bodyClickHandler = function(e) {
            const mainWord = e.target && e.target.closest ? e.target.closest('.eng-word') : null;
            if (mainWord && textRoot.contains(mainWord)) {
                e.preventDefault();
                e.stopPropagation();
                showLookup(mainWord);
                return;
            }

            if (handleLinkClick(e)) return;
        };

        document.body.addEventListener('click', bodyClickHandler, true);
        subWordHoverCleanup = bindEnglishLookupHover(
            sourceTarget,
            '.eng-sub-word',
            function(target, e) {
                if (popupLifecycle) popupLifecycle.cancelClose();
                showEnViPopup(target, e);
            },
            function() {
                if (popupLifecycle) popupLifecycle.scheduleClose();
            }
        );

        beforeUnloadHandler = function() {
            try { if (parentWin[cleanupKey]) parentWin[cleanupKey](); } catch (err) {}
        };
        window.addEventListener('beforeunload', beforeUnloadHandler);
    }

    function cleanup() {
        try { if (bodyClickHandler) document.body.removeEventListener('click', bodyClickHandler, true); } catch (err) {}
        try { if (subWordHoverCleanup) subWordHoverCleanup(); } catch (err) {}
        try { if (popupLifecycle) popupLifecycle.cleanup(); } catch (err) {}
        try { if (beforeUnloadHandler) window.removeEventListener('beforeunload', beforeUnloadHandler); } catch (err) {}
        removePopupArtifacts();
        try {
            if (dictState) {
                dictState.source = null;
                dictState.enVi = null;
                dictState = null;
            }
        } catch (err) {}
        textRoot = null;
        sourceTarget = null;
        parentPopup = null;
        popupLifecycle = null;
        bodyClickHandler = null;
        subWordHoverCleanup = null;
        beforeUnloadHandler = null;
        try { delete parentWin[cleanupKey]; } catch (err) {
            try { parentWin[cleanupKey] = null; } catch (err2) {}
        }
    }

    setup();
    parentWin[cleanupKey] = cleanup;
})();
</script>
"""


def build_source_lookup_reader_js(
    *,
    source_json: str,
    en_vi_json: str,
    text_root_id: str,
    target_id: str,
    cleanup_key: str,
    source_label: str,
    decorate_longman_headers: bool = False,
    typography_vars: dict[str, str] | None = None,
) -> str:
    """Build Longman/Oxford lookup JS with an En→Vi hover overlay on entry HTML."""
    from urllib.parse import quote

    popup_id = f"{text_root_id}-source-envi-popup"
    popup_content_id = f"{popup_id}-content"
    popup_style_id = f"{popup_id}-style"
    popup_class = "english-reader-source-envi-popup"
    popup_css = build_popup_css(
        popup_class,
        extra_vars=typography_vars,
    )

    replacements = {
        "__SOURCE_JSON__": source_json,
        "__ENVI_JSON__": en_vi_json,
        "__TEXT_ROOT_ID__": str(text_root_id),
        "__TARGET_ID__": str(target_id),
        "__CLEANUP_KEY__": str(cleanup_key),
        "__SOURCE_LABEL__": str(source_label),
        "__POPUP_ID__": popup_id,
        "__POPUP_CONTENT_ID__": popup_content_id,
        "__POPUP_STYLE_ID__": popup_style_id,
        "__POPUP_CLASS__": popup_class,
        "__POPUP_CSS_ENCODED__": quote(popup_css),
        "__ENTRY_DECORATOR_JS__": (
            LONGMAN_ENTRY_HEADER_DECORATOR_JS if decorate_longman_headers else ""
        ),
        "__HOVER_LOOKUP_HELPER_JS__": ENG_READER_HOVER_LOOKUP_HELPER_JS,
    }
    out = SOURCE_LOOKUP_READER_JS_TEMPLATE
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


LONGMAN_ENTRY_HEADER_DECORATOR_JS = r'''
function decorateLongmanEntryHeaders(root) {
    const scope = root || document;
    const entries = scope.querySelectorAll ? scope.querySelectorAll('.entry') : [];

    entries.forEach(function(entry) {
        if (entry.querySelector(':scope > .longman-entry-head')) return;

        const headword = entry.querySelector('.hyphenation');
        if (!headword) return;

        let startNode = headword;
        while (startNode.parentNode && startNode.parentNode !== entry) {
            startNode = startNode.parentNode;
        }
        if (!startNode || startNode.parentNode !== entry) return;

        const boundarySelector = [
            '.buttons', '.sense', '.runon', '.collobox', '.thesbox',
            '.usagebox', '.grambox', '.f2nbox', '.phrvbentry',
            '.etymbox', 'spoken', '.spokensect', '.phrvbs'
        ].join(',');

        const nodes = [];
        let current = startNode;
        while (current) {
            if (current.nodeType === Node.ELEMENT_NODE
                && current.matches
                && current.matches(boundarySelector)) {
                break;
            }
            nodes.push(current);
            current = current.nextSibling;
        }

        if (!nodes.length) return;

        const wrapper = document.createElement('span');
        wrapper.className = 'longman-entry-head';
        entry.insertBefore(wrapper, nodes[0]);
        nodes.forEach(function(node) { wrapper.appendChild(node); });
    });
}
''';


def build_longman_entry_header_decorator_js(*, auto_run: bool = False) -> str:
    """Return the Longman lexical-header DOM decorator.

    The decorator starts at the direct child containing `.hyphenation` and stops
    before menu buttons, senses, or structural dictionary boxes. This prevents
    the header surface from covering unrelated chips or entry-menu controls.
    """
    js = LONGMAN_ENTRY_HEADER_DECORATOR_JS
    if auto_run:
        js += r'''
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        decorateLongmanEntryHeaders(document);
    }, { once: true });
} else {
    decorateLongmanEntryHeaders(document);
}
'''
    return js


# ---------------------------------------------------------------------------
# Source-dictionary visual theme overrides
# ---------------------------------------------------------------------------

def build_longman_theme_css(
    *,
    content_background: str = "var(--eng-bg-main, #fdfdf8)",
    header_background: str = "rgba(69, 119, 191, 0.14)",
    nested_header_background: str = "rgba(199, 110, 6, 0.14)",
    entry_header_background: str = "#ede29a",
    border_color: str = "rgba(69, 119, 191, 0.42)",
    header_color: str = "var(--eng-reader-text, #3d3a2a)",
) -> str:
    """Return the application Longman theme layered after ``LDOCE6.css``.

    Longman is visually aligned with Oxford while preserving Longman's semantic
    headword/meta colours. The lexical header is wrapped dynamically and receives
    a warm yellow surface across the available row width, without any fixed height.
    Major box headers and outer borders use Oxford's pale blue; nested headings use
    Oxford's pale amber.
    """
    content_background = str(content_background or "var(--eng-bg-main, #fdfdf8)")
    header_background = str(header_background or "rgba(69, 119, 191, 0.14)")
    nested_header_background = str(nested_header_background or "rgba(199, 110, 6, 0.14)")
    entry_header_background = str(entry_header_background or "#ede29a")
    border_color = str(border_color or "rgba(69, 119, 191, 0.42)")
    header_color = str(header_color or "var(--eng-reader-text, #3d3a2a)")

    return f"""
        /* Longman lexical header: full row width, automatic height, no fixed band. */
        .longman-entry-head {{
            display: flex !important;
            flex-wrap: wrap !important;
            align-items: center !important;
            gap: 0.1rem 0.25rem !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
            background-color: {entry_header_background} !important;
            padding: 2px 6px !important;
            margin: 0 0 4px 0 !important;
            border: 0 !important;
            border-radius: 0 !important;
            line-height: inherit !important;
        }}

        /* Keep Longman's native semantic colours for headword and metadata. */
        .longman-entry-head .hyphenation,
        .longman-entry-head .pos,
        .longman-entry-head .gram,
        .longman-entry-head .freq,
        .longman-entry-head .frequent,
        .longman-entry-head .level,
        .longman-entry-head .homnum,
        .longman-entry-head .pronstrong {{
            -webkit-text-fill-color: currentColor !important;
        }}

        /* Audio controls inside the lexical header stay neutral and square. */
        .longman-entry-head .native-play-btn {{
            background: var(--eng-bg-sec, #ecebe3) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
            border: 1px solid var(--eng-border, #d3d2ca) !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}

        .longman-entry-head .native-play-btn:hover,
        .longman-entry-head .native-play-btn:focus {{
            background: var(--eng-border, #d3d2ca) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
        }}

        /* Longman: square the large structural boxes and unify their border. */
        .collobox,
        .thesbox,
        .usagebox,
        .grambox,
        spoken,
        .f2nbox {{
            border-radius: 0 !important;
            background-color: {header_background} !important;
            border-color: {border_color} !important;
        }}

        /* LDOCE6.css rounds the final inner section separately. */
        .collobox .last,
        .thesbox .last,
        .usagebox .last,
        .grambox .last,
        spoken .last,
        .f2nbox .last {{
            border-bottom-left-radius: 0 !important;
            border-bottom-right-radius: 0 !important;
        }}

        /* Major heading surfaces use Oxford's pale blue. */
        .collobox > .heading,
        .thesbox > .heading,
        .usagebox > .heading,
        .grambox > .heading,
        spoken > .heading,
        .f2nbox > .heading,
        .grambox .heading.newline {{
            background-color: {header_background} !important;
            color: {header_color} !important;
            -webkit-text-fill-color: {header_color} !important;
            border-radius: 0 !important;
        }}

        /* Some source markup colours child spans independently. */
        .collobox > .heading *,
        .thesbox > .heading *,
        .usagebox > .heading *,
        .grambox > .heading *,
        spoken > .heading *,
        .f2nbox > .heading *,
        .grambox .heading.newline * {{
            color: {header_color} !important;
            -webkit-text-fill-color: {header_color} !important;
        }}

        /* Nested section headings are softer: Oxford's pale amber. */
        .collobox .secheading,
        .thesbox .secheading,
        .usagebox .secheading,
        .grambox .secheading,
        spoken .secheading,
        .f2nbox .secheading,
        .collobox .subheading,
        .thesbox .subheading,
        .usagebox .subheading,
        .grambox .subheading,
        spoken .subheading,
        .f2nbox .subheading {{
            background-color: {nested_header_background} !important;
            color: {header_color} !important;
            -webkit-text-fill-color: {header_color} !important;
            border-radius: 0 !important;
        }}

        .collobox .secheading *,
        .thesbox .secheading *,
        .usagebox .secheading *,
        .grambox .secheading *,
        spoken .secheading *,
        .f2nbox .secheading *,
        .collobox .subheading *,
        .thesbox .subheading *,
        .usagebox .subheading *,
        .grambox .subheading *,
        spoken .subheading *,
        .f2nbox .subheading * {{
            color: {header_color} !important;
            -webkit-text-fill-color: {header_color} !important;
        }}

        /* Align only the content surfaces with the main page. */
        .thesbox .section,
        .collobox .section,
        .usagebox .expl,
        .grambox .expl,
        .grambox .compareword,
        spoken .section,
        spoken .expl,
        .f2nbox .section,
        .f2nbox .expl {{
            background-color: {content_background} !important;
            border-radius: 0 !important;
        }}

        /* Application-generated pronunciation controls outside the lexical header. */
        .native-play-btn {{
            background: var(--eng-bg-sec, #ecebe3) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
            border: 1px solid var(--eng-border, #d3d2ca) !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}

        .native-play-btn:hover,
        .native-play-btn:focus {{
            background: var(--eng-border, #d3d2ca) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
        }}
    """

def build_oxford_theme_css(
    *,
    content_background: str = "var(--eng-bg-main, #fdfdf8)",
    collapsed_heading_background: str = "rgba(199, 110, 6, 0.14)",
    collapsed_heading_hover_background: str = "rgba(199, 110, 6, 0.20)",
    top_heading_background: str = "rgba(69, 119, 191, 0.14)",
    top_heading_hover_background: str = "rgba(69, 119, 191, 0.20)",
) -> str:
    """Return a controlled OALD9 override layered after ``OALD9.css``.

    Oxford's accent borders, icons, audio controls, and semantic colours remain
    intact. Large panels are squared and their body surfaces use the main page
    background. Collapsed headings keep a visible resting background so users
    can recognise them before hover or activation.
    """
    content_background = str(content_background or "var(--eng-bg-main, #fdfdf8)")

    return f"""
        /* Oxford sketch panels: retain accent borders, remove rounding. */
        .ColloPanel,
        .ThesPanel {{
            border-radius: 0 !important;
            background-color: {content_background} !important;
        }}

        .CorpusHeader,
        .ColloHeader {{
            border-radius: 0 !important;
        }}

        /* Main entry header content: retain the blue webtop header only. */
        .top-container {{
            background-color: {content_background} !important;
        }}

        /* Usage, grammar, wordfinder and expandable content boxes. */
        .entry-box-style,
        .un,
        .collapse,
        .res-g > .unbox {{
            border-radius: 0 !important;
            background-color: {content_background} !important;
        }}

        .top-container .entry-box-style,
        .top-container .un,
        .top-container .collapse {{
            background-color: {content_background} !important;
        }}

        .res-g > .unbox > .body {{
            background-color: {content_background} !important;
        }}

        /* Idiom, phrasal-verb and word-family boxes. */
        .idm-gs,
        .pv-gs,
        .wf-g {{
            border-radius: 0 !important;
            background-color: {content_background} !important;
        }}

        /* Square major box headings. */
        .entry-box-style-heading,
        .collapse .heading,
        .collapse pnc.heading,
        .res-g > .unbox > .heading,
        .idm-gs > .heading,
        .pv-gs > .heading,
        .wf-g > .heading {{
            border-radius: 0 !important;
        }}

        /* Keep collapsed boxes visually discoverable before hover. */
        .entry-box-style-heading,
        .collapse .heading,
        .collapse pnc.heading,
        .res-g > .unbox > .heading {{
            background-color: {collapsed_heading_background} !important;
        }}

        .entry-box-style-heading:hover,
        .entry-box-style-heading:focus,
        .entry-box-style-heading:active,
        .collapse .heading:hover,
        .collapse .heading:focus,
        .collapse .heading:active,
        .collapse pnc.heading:hover,
        .collapse pnc.heading:focus,
        .collapse pnc.heading:active,
        .unbox.is-active .heading,
        .unbox.is-active pnc.heading {{
            background-color: {collapsed_heading_hover_background} !important;
        }}

        /* Top-entry collapsible headings retain Oxford's blue family. */
        .top-container .entry-box-style-heading,
        .top-container .collapse .heading,
        .collapse .top-container .heading,
        .top-container .res-g > .unbox > .heading {{
            background-color: {top_heading_background} !important;
        }}

        .top-container .entry-box-style-heading:hover,
        .top-container .entry-box-style-heading:focus,
        .top-container .entry-box-style-heading:active,
        .top-container .collapse .heading:hover,
        .top-container .collapse .heading:focus,
        .top-container .collapse .heading:active,
        .collapse .top-container .heading:hover,
        .collapse .top-container .heading:focus,
        .collapse .top-container .heading:active,
        .top-container .unbox.is-active .heading {{
            background-color: {top_heading_hover_background} !important;
        }}

        /* Match Oxford application-generated audio controls to Longman. */
        .native-play-btn {{
            background: var(--eng-bg-sec, #ecebe3) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
            border: 1px solid var(--eng-border, #d3d2ca) !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}

        .native-play-btn:hover,
        .native-play-btn:focus {{
            background: var(--eng-border, #d3d2ca) !important;
            color: var(--eng-reader-text, #3d3a2a) !important;
        }}
    """

# ---------------------------------------------------------------------------
# JS builder
# ---------------------------------------------------------------------------

ENG_READER_LOOKUP_JS_TEMPLATE = r'''
<script>
(function() {
    __HOVER_LOOKUP_HELPER_JS__

    let dictState = {
        enVi: __EN_VI_JSON__
    };

    const useSidebar = __USE_SIDEBAR__;
    const useParentContainer = __USE_PARENT_CONTAINER__;
    const useFrameOffset = __USE_FRAME_OFFSET__;
    const sidebarTargetId = "__SIDEBAR_TARGET_ID__";
    const containerId = "__CONTAINER_ID__";
    const tableLookupPolicy = "__TABLE_LOOKUP_POLICY__";
    const rootType = "__ROOT_TYPE__";

    const parentDoc = window.parent.document;
    const parentWin = window.parent;
    const doc = useParentContainer ? parentDoc : document;
    const hostWin = useParentContainer ? parentWin : window;
    const NF = hostWin.NodeFilter || window.NodeFilter;

    const cleanupKey = "__CLEANUP_KEY__";
    const legacyCleanupKeys = __LEGACY_CLEANUP_KEYS_JSON__;
    const legacyArtifactIds = __LEGACY_ARTIFACT_IDS_JSON__;

    const popupId = "__POPUP_ID__";
    const popupContentId = "__POPUP_CONTENT_ID__";
    const popupStyleId = "__POPUP_STYLE_ID__";
    const wordStyleId = "__WORD_STYLE_ID__";
    const popupClass = "__POPUP_CLASS__";
    const wordStyleCss = decodeURIComponent("__WORD_STYLE_CSS_ENCODED__");
    const popupCss = decodeURIComponent("__POPUP_CSS_ENCODED__");

    legacyCleanupKeys.forEach(function(key) {
        if (key && key !== cleanupKey && parentWin[key]) {
            try { parentWin[key](); } catch (err) {}
            try { delete parentWin[key]; } catch (err) {
                try { parentWin[key] = null; } catch (err2) {}
            }
        }
    });

    if (parentWin[cleanupKey]) {
        try { parentWin[cleanupKey](); } catch (err) {}
    }

    let container = null;
    let containerClickHandler = null;
    let hoverCleanup = null;
    let parentClickHandler = null;
    let parentKeyHandler = null;
    let beforeUnloadHandler = null;
    let parentPopup = null;
    let popupLifecycle = null;
    let initTimer = null;
    let attempts = 0;

    function removeElementById(id) {
        if (!id) return;
        try {
            const el = parentDoc.getElementById(id);
            if (el && el.parentNode) {
                try { el.innerHTML = ""; } catch (err) {}
                el.parentNode.removeChild(el);
            }
        } catch (err) {}
    }

    function removeArtifacts() {
        removeElementById(popupId);
        removeElementById(popupStyleId);
        removeElementById(wordStyleId);
        legacyArtifactIds.forEach(function(id) { removeElementById(id); });
    }

    function ensureWordStyle() {
        if (!wordStyleId || !wordStyleCss) return;
        if (parentDoc.getElementById(wordStyleId)) return;
        const style = parentDoc.createElement("style");
        style.id = wordStyleId;
        style.textContent = wordStyleCss;
        parentDoc.head.appendChild(style);
    }

    function ensurePopupStyle() {
        if (useSidebar) return;
        if (parentDoc.getElementById(popupStyleId)) return;
        const style = parentDoc.createElement("style");
        style.id = popupStyleId;
        style.textContent = popupCss;
        parentDoc.head.appendChild(style);
    }

    function hidePopup() {
        if (popupLifecycle) popupLifecycle.cancelClose();
        if (parentPopup) parentPopup.classList.remove("visible");
        if (!useSidebar) clearEnglishActive();
    }

    function createPopup() {
        if (useSidebar) return null;
        ensurePopupStyle();
        let popup = parentDoc.getElementById(popupId);
        if (!popup) {
            popup = parentDoc.createElement("div");
            popup.id = popupId;
            popup.className = popupClass;
            popup.innerHTML = `<div id="${popupContentId}"></div>`;
            parentDoc.body.appendChild(popup);
        }
        return popup;
    }

    function clearEnglishActive() {
        if (!container) return;
        container.querySelectorAll(".eng-word").forEach(function(el) {
            el.classList.remove("active-en");
        });
    }

    function buildEnContent(enWord) {
        const enViDictionary = dictState ? dictState.enVi : {};
        const hasMeaning = Object.prototype.hasOwnProperty.call(enViDictionary, enWord);
        const enMeaning = hasMeaning
            ? enViDictionary[enWord]
            : "<div style='color:#5d7367; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";

        return enMeaning || "<div style='color:#5d7367; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";
    }

    function showPopup(finalContent, targetEl) {
        if (!parentPopup) return;
        const contentEl = parentDoc.getElementById(popupContentId);
        if (!contentEl) return;

        contentEl.innerHTML = finalContent;
        parentPopup.classList.add("visible");

        scappEnglishPopup.place(parentPopup, targetEl, {width: 510});
    }

    function showSidebar(finalContent) {
        const target = parentDoc.getElementById(sidebarTargetId);
        if (target) target.innerHTML = finalContent;
    }

    function handleEnglishLookup(targetEl) {
        if (popupLifecycle) popupLifecycle.cancelClose();
        clearEnglishActive();
        targetEl.classList.add("active-en");
        const rawWord = targetEl.getAttribute("data-word") || "";
        const enWord = rawWord.toLowerCase();
        if (!enWord) return;
        const finalContent = buildEnContent(enWord);
        if (useSidebar) {
            hidePopup();
            showSidebar(finalContent);
        } else {
            showPopup(finalContent, targetEl);
        }
    }

    function shouldSkipTextNode(node) {
        const parent = node.parentElement;
        if (!parent) return true;

        if (rootType === "text") {
            if (parent.closest("script, style, a, code, pre, table, th, td, .eng-word, .no-en-lookup")) return true;
            return false;
        }

        if (parent.closest("script, style, a, code, pre, th, .heading, .eng-word, .no-en-lookup")) return true;

        const table = parent.closest("table");
        if (!table) return false;
        if (tableLookupPolicy === "none") return true;
        const td = parent.closest("td");
        if (!td) return true;
        if (tableLookupPolicy === "all_td") return false;
        if (table.classList.contains("family")) return !td.matches("td:nth-of-type(2)");
        if (tableLookupPolicy === "meaning_only") return true;
        return false;
    }

    function makeWordSpan(wordText, cleanWord) {
        const span = doc.createElement("span");
        span.className = "eng-word";
        span.setAttribute("data-word", cleanWord);
        span.textContent = wordText;
        return span;
    }

    function replaceTextNodeWithLookupSpans(node) {
        const enViDictionary = dictState ? dictState.enVi : {};
        const text = node.nodeValue;
        const regex = /\b([a-zA-Z]+(?:'[a-zA-Z]+)?)\b/g;
        let match;
        let lastIndex = 0;
        let changed = false;
        const fragment = doc.createDocumentFragment();

        while ((match = regex.exec(text)) !== null) {
            const wordText = match[0];
            const cleanWord = wordText.toLowerCase();

            if (!Object.prototype.hasOwnProperty.call(enViDictionary, cleanWord)) continue;
            if (!enViDictionary[cleanWord]) continue;

            if (match.index > lastIndex) {
                fragment.appendChild(doc.createTextNode(text.slice(lastIndex, match.index)));
            }

            fragment.appendChild(makeWordSpan(wordText, cleanWord));
            lastIndex = match.index + wordText.length;
            changed = true;
        }

        if (!changed) return;
        if (lastIndex < text.length) fragment.appendChild(doc.createTextNode(text.slice(lastIndex)));
        node.parentNode.replaceChild(fragment, node);
    }

    function wrapEnglishWords(root) {
        if (!root || !NF) return;
        const walker = doc.createTreeWalker(
            root,
            NF.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    if (shouldSkipTextNode(node)) return NF.FILTER_REJECT;
                    if (!/[a-zA-Z]/.test(node.nodeValue)) return NF.FILTER_REJECT;
                    return NF.FILTER_ACCEPT;
                }
            },
            false
        );

        const nodes = [];
        let n;
        while ((n = walker.nextNode())) nodes.push(n);
        nodes.forEach(function(node) { replaceTextNodeWithLookupSpans(node); });
    }

    function setup() {
        container = doc.getElementById(containerId);
        if (!container) return false;

        removeArtifacts();
        ensureWordStyle();
        wrapEnglishWords(container);

        containerClickHandler = function(e) {
            const target = e.target && e.target.closest ? e.target.closest(".eng-word") : null;
            if (target && container.contains(target)) {
                e.preventDefault();
                e.stopPropagation();
                handleEnglishLookup(target);
                return;
            }
            if (!useSidebar) hidePopup();
        };
        container.addEventListener("click", containerClickHandler, true);

        if (!useSidebar) {
            parentPopup = createPopup();
            popupLifecycle = createEnglishHoverPopupLifecycle(
                function() { return parentPopup; },
                hidePopup
            );
            popupLifecycle.attachPopup();
        }

        hoverCleanup = bindEnglishLookupHover(
            container,
            ".eng-word",
            function(target, e) {
                if (popupLifecycle) popupLifecycle.cancelClose();
                handleEnglishLookup(target, e);
            },
            !useSidebar
                ? function() { if (popupLifecycle) popupLifecycle.scheduleClose(); }
                : null
        );

        if (!useSidebar) {
            parentClickHandler = function(e) {
                if (parentPopup && parentPopup.classList.contains("visible") && !parentPopup.contains(e.target)) {
                    hidePopup();
                }
            };
            parentDoc.addEventListener("click", parentClickHandler, true);
        }

        parentKeyHandler = function(e) {
            if (e.key === "Escape") hidePopup();
        };
        parentDoc.addEventListener("keydown", parentKeyHandler);

        beforeUnloadHandler = function() {
            try { if (parentWin[cleanupKey]) parentWin[cleanupKey](); } catch (err) {}
        };
        window.addEventListener("beforeunload", beforeUnloadHandler);
        return true;
    }

    function setupWithRetry() {
        attempts += 1;
        if (setup()) return;
        if (__ENABLE_RETRY__ && attempts < 20) initTimer = setTimeout(setupWithRetry, 100);
    }

    function cleanup() {
        try { if (initTimer) clearTimeout(initTimer); } catch (err) {}
        try { if (container && containerClickHandler) container.removeEventListener("click", containerClickHandler, true); } catch (err) {}
        try { if (hoverCleanup) hoverCleanup(); } catch (err) {}
        try { if (popupLifecycle) popupLifecycle.cleanup(); } catch (err) {}
        try { if (parentClickHandler) parentDoc.removeEventListener("click", parentClickHandler, true); } catch (err) {}
        try { if (parentKeyHandler) parentDoc.removeEventListener("keydown", parentKeyHandler); } catch (err) {}
        try { if (beforeUnloadHandler) window.removeEventListener("beforeunload", beforeUnloadHandler); } catch (err) {}
        try {
            if (dictState) {
                dictState.enVi = null;
                dictState = null;
            }
        } catch (err) {}
        removeArtifacts();
        container = null;
        containerClickHandler = null;
        hoverCleanup = null;
        parentClickHandler = null;
        parentKeyHandler = null;
        parentPopup = null;
        popupLifecycle = null;
        try { delete parentWin[cleanupKey]; } catch (err) {
            try { parentWin[cleanupKey] = null; } catch (err2) {}
        }
    }

    setupWithRetry();
    parentWin[cleanupKey] = cleanup;
})();
</script>
'''


def _js_bool(value: bool) -> str:
    return "true" if bool(value) else "false"


def build_lookup_js(
    *,
    en_vi_json: str,
    use_sidebar: bool,
    use_parent_container: bool,
    use_frame_offset: bool,
    sidebar_target_id: str,
    container_id: str,
    cleanup_key: str,
    popup_id: str,
    popup_content_id: str,
    popup_style_id: str,
    root_type: Literal["text", "table"],
    table_lookup_policy: str = "auto",
    popup_class: str = "english-reader-popup",
    popup_close_class: str = "english-reader-popup-close",
    word_style_id: str = "",
    word_style_css: str = "",
    legacy_cleanup_keys_json: str = "[]",
    legacy_artifact_ids_json: str = "[]",
    typography_vars: dict[str, str] | None = None,
    enable_retry: bool = False,
) -> str:
    from urllib.parse import quote

    popup_css = build_popup_css(popup_class, popup_close_class, extra_vars=typography_vars)

    replacements = {
        "__EN_VI_JSON__": en_vi_json,
        "__USE_SIDEBAR__": _js_bool(use_sidebar),
        "__USE_PARENT_CONTAINER__": _js_bool(use_parent_container),
        "__USE_FRAME_OFFSET__": _js_bool(use_frame_offset),
        "__SIDEBAR_TARGET_ID__": str(sidebar_target_id),
        "__CONTAINER_ID__": str(container_id),
        "__TABLE_LOOKUP_POLICY__": str(table_lookup_policy),
        "__ROOT_TYPE__": str(root_type),
        "__CLEANUP_KEY__": str(cleanup_key),
        "__LEGACY_CLEANUP_KEYS_JSON__": legacy_cleanup_keys_json or "[]",
        "__LEGACY_ARTIFACT_IDS_JSON__": legacy_artifact_ids_json or "[]",
        "__POPUP_ID__": str(popup_id),
        "__POPUP_CONTENT_ID__": str(popup_content_id),
        "__POPUP_STYLE_ID__": str(popup_style_id),
        "__WORD_STYLE_ID__": str(word_style_id or ""),
        "__POPUP_CLASS__": str(popup_class),
        "__WORD_STYLE_CSS_ENCODED__": quote(word_style_css or ""),
        "__POPUP_CSS_ENCODED__": quote(popup_css),
        "__ENABLE_RETRY__": _js_bool(enable_retry),
        "__HOVER_LOOKUP_HELPER_JS__": ENG_READER_HOVER_LOOKUP_HELPER_JS,
    }

    out = ENG_READER_LOOKUP_JS_TEMPLATE
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out

# ---------------------------------------------------------------------------
# Dictionary-backed English reader builders (Longman / Oxford)
# ---------------------------------------------------------------------------

def build_dictionary_reader_css(
    *,
    dict_width: str,
    accent_color: str,
    scrollbar_bg: str = "#ecebe3",
    is_sidebar: bool = False,
) -> str:
    """CSS profile for dictionary-backed readers such as Longman/Oxford.

    External dictionary CSS should be injected before this CSS so the layout shell can
    normalize iframe/sidebar behavior without rewriting dictionary-specific styles.
    """
    if is_sidebar:
        box_css = """
            .sub-dict-box {
                height: 100%;
                overflow-y: auto;
                padding: var(--eng-reader-panel-padding);
                box-sizing: border-box;
                background: var(--eng-dict-inner-bg, var(--eng-bg-sec));
            }
        """
    else:
        box_css = """
            .sub-dict-box {
                overflow-y: auto;
                padding: var(--eng-reader-panel-padding);
                box-sizing: border-box;
                background: var(--eng-dict-inner-bg, var(--eng-bg-sec));
            }
            .top-box { flex: 2; height: 66.66%; }
            .bottom-box {
                flex: 1;
                height: 33.33%;
                border-top: 3px solid #d3d2ca;
                /* The Anh–Việt result is placed on the main-page surface. */
                background: var(--eng-bg-main, #fdfdf8);
            }
        """

    return f"""
        {ENG_READER_TYPOGRAPHY_CSS}
        {build_scrollbar_css()}

        html,
        body {{
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: var(--eng-reader-font);
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
            background-color: transparent;
            color: var(--eng-reader-text, #3d3a2a);
        }}

        .main-wrapper {{
            display: flex;
            height: 100vh;
            gap: var(--eng-reader-gap);
            box-sizing: border-box;
            padding-bottom: 5px;
        }}

        .dict-col-container {{
            flex: 0 0 {dict_width};
            display: flex;
            flex-direction: column;
            background: var(--eng-dict-bg, var(--eng-bg-sec));
            border: 1px solid var(--eng-border);
            border-radius: 0;
            overflow: hidden;
        }}

        {box_css}

        .text-col {{
            flex-grow: 1;
            overflow-y: auto;
            height: 100%;
            padding-right: 5px;
            box-sizing: border-box;
        }}

        .text-col table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid var(--eng-border);
            margin: 0;
        }}

        .text-col td {{
            padding: var(--eng-reader-cell-padding);
            border: 1px solid var(--eng-border);
            vertical-align: middle;
        }}

        .id-col {{
            font-family: var(--eng-reader-mono-font);
            font-size: var(--eng-reader-code-font-size);
            width: 1%;
            white-space: nowrap;
            text-align: center;
            color: #888;
            background: #f4f4f0;
        }}

        .content-col {{
            font-size: var(--eng-reader-font-size);
            line-height: var(--eng-reader-line-height);
        }}

        .eng-word {{
            cursor: pointer;
            border-radius: 3px;
            padding: 0 1px;
            transition: 0.15s;
            display: inline;
        }}

        .eng-word:hover,
        .eng-word.active {{
            background: #d3d2ca;
            border-bottom: 2px solid {accent_color};
            font-weight: 600;
            color: {accent_color};
        }}

        .eng-sub-word {{
            cursor: pointer;
            border-bottom: none;
            transition: 0.15s;
            color: #2d3436;
        }}

        .eng-sub-word:hover {{
            color: #d63031;
            border-bottom: none;
        }}

        .eng-sub-word.active-en {{
            background: #d63031;
            color: white;
            border: none;
            padding: var(--eng-reader-glossary-word-padding);
            border-radius: 2px;
        }}

        /* Scrollbar styling is provided by build_scrollbar_css(). */
    """


DICTIONARY_READER_JS_TEMPLATE = r'''
<script>
(function() {
    __HOVER_LOOKUP_HELPER_JS__

    let dictState = {
        entry: __ENTRY_JSON__,
        enVi: __ENVI_JSON__
    };

    const isSidebar = __IS_SIDEBAR__;
    const entryTargetId = "__ENTRY_TARGET_ID__";
    const enviTargetId = "__ENVI_TARGET_ID__";
    const textRootId = "__TEXT_ROOT_ID__";
    const cleanupKey = "__CLEANUP_KEY__";
    const entryLabel = "__ENTRY_LABEL__";
    const accentColor = "__ACCENT_COLOR__";
    const parentDoc = window.parent.document;
    const parentWin = window.parent;

    __ENTRY_DECORATOR_JS__

    if (parentWin[cleanupKey]) {
        try { parentWin[cleanupKey](); } catch (err) {}
    }

    let bodyClickHandler = null;
    let subWordHoverCleanup = null;
    let beforeUnloadHandler = null;
    let textRoot = null;

    window.toggle = function(expandable) {
        if (!expandable) return;
        const expParent = expandable.parentNode;
        const target = expParent ? expParent.querySelector('.content') : null;
        const arrow = expParent ? expParent.querySelector('span.arrow') : null;
        if (target) {
            const isExp = target.style.display === 'block';
            target.style.display = isExp ? 'none' : 'block';
            if (arrow) arrow.innerHTML = isExp ? '\u25BA' : '\u25BC';
        }
    };

    window.showAtLink = function(ele) {
        if (!ele) return;
        const target = ele.nextElementSibling;
        if (target) target.style.display = target.style.display === 'block' ? 'none' : 'block';
    };

    window.toggleImg = function(ele) {
        if (!ele) return;
        ele.style.maxHeight = (ele.style.maxHeight === 'none') ? '4em' : 'none';
    };

    function buildEntryContent(word, meaning) {
        return `
            <div style='font-size:1.2rem; color:${accentColor}; font-weight:600; border-bottom:2px solid #d3d2ca; margin-bottom:10px; padding-bottom:5px; display:flex; align-items:center;'>
                <span style='font-size:0.65rem; background:${accentColor}; color:white; padding:2px 6px; border-radius:4px; margin-right:8px;'>${entryLabel}</span>
                ${(word || '').toUpperCase()}
            </div>
            ${meaning}
        `;
    }

    function buildEnViContent(enWord) {
        const enViDict = dictState ? dictState.enVi : {};
        const enMeaning = Object.prototype.hasOwnProperty.call(enViDict, enWord)
            ? enViDict[enWord]
            : "<div style='color:#d63031; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";

        return `
            <div style='font-size:1.2rem; color:#d63031; font-weight:600; border-bottom:2px solid #d3d2ca; margin-bottom:10px; padding-bottom:5px; display:flex; align-items:center;'>
                <span style='font-size:0.65rem; background:#d63031; color:white; padding:2px 6px; border-radius:4px; margin-right:8px;'>VIỆT</span>
                ${enWord}
            </div>
            ${enMeaning || "<div style='color:#d63031; margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>"}
        `;
    }

    function wrapEnglishWords(htmlContent) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent || '';
        const walker = document.createTreeWalker(tempDiv, NodeFilter.SHOW_TEXT, null, false);
        const nodes = [];
        let n;
        while ((n = walker.nextNode())) {
            const parentTag = n.parentNode && n.parentNode.tagName ? n.parentNode.tagName.toLowerCase() : '';
            if (!['script', 'style', 'audio', 'video', 'button'].includes(parentTag)) nodes.push(n);
        }

        nodes.forEach(function(node) {
            const text = node.nodeValue;
            if (!/[a-zA-Z]/.test(text)) return;
            const replaced = text.replace(/\b([a-zA-Z]+)\b/g, "<span class='eng-sub-word' data-word='$1'>$1</span>");
            if (replaced !== text) {
                const span = document.createElement('span');
                span.innerHTML = replaced;
                node.parentNode.replaceChild(span, node);
            }
        });
        return tempDiv.innerHTML;
    }

    function clearMainActive() {
        if (!textRoot) return;
        textRoot.querySelectorAll('.eng-word').forEach(function(el) { el.classList.remove('active'); });
    }

    function clearSubActive() {
        document.querySelectorAll('.eng-sub-word').forEach(function(el) { el.classList.remove('active-en'); });
    }

    function showEntryLookup(target) {
        clearMainActive();
        target.classList.add('active');
        const word = (target.getAttribute('data-word') || '').toLowerCase();
        if (!word) return;
        const entryDict = dictState ? dictState.entry : {};
        let meaning = Object.prototype.hasOwnProperty.call(entryDict, word)
            ? entryDict[word]
            : "<div style='color:#d63031; padding:10px;'>Không tìm thấy.</div>";
        meaning = wrapEnglishWords(meaning);
        const targetBox = document.getElementById(entryTargetId);
        if (targetBox) {
            targetBox.innerHTML = buildEntryContent(word, meaning);
            if (typeof decorateLongmanEntryHeaders === 'function') {
                decorateLongmanEntryHeaders(targetBox);
            }
        }
    }

    function showEnViLookup(target) {
        clearSubActive();
        target.classList.add('active-en');
        const enWord = (target.getAttribute('data-word') || '').toLowerCase();
        if (!enWord) return;
        const content = buildEnViContent(enWord);
        if (isSidebar) {
            const sbEnvi = parentDoc.getElementById(enviTargetId);
            if (sbEnvi) sbEnvi.innerHTML = content;
        } else {
            const localEnvi = document.getElementById(enviTargetId);
            if (localEnvi) localEnvi.innerHTML = content;
        }
    }

    function handleLinkClick(e) {
        const aTag = e.target && e.target.closest ? e.target.closest('a') : null;
        if (!aTag) return false;
        const href = aTag.getAttribute('href');
        const target = aTag.getAttribute('target');
        if (!href) return false;

        if (href.startsWith('#')) {
            e.preventDefault();
            const targetId = href.substring(1);
            const targetEl = document.getElementById(targetId) || document.getElementsByName(targetId)[0];
            if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return true;
        }

        if (target === '_blank') {
            e.preventDefault();
            parentWin.open(href, '_blank');
            return true;
        }

        if (target === '_parent') {
            e.preventDefault();
            parentWin.location.href = href;
            return true;
        }

        return false;
    }

    function setup() {
        textRoot = document.getElementById(textRootId);
        bodyClickHandler = function(e) {
            const mainWord = e.target && e.target.closest ? e.target.closest('.eng-word') : null;
            if (mainWord && textRoot && textRoot.contains(mainWord)) {
                e.preventDefault();
                e.stopPropagation();
                showEntryLookup(mainWord);
                return;
            }

            const subWord = e.target && e.target.closest ? e.target.closest('.eng-sub-word') : null;
            if (subWord) {
                e.preventDefault();
                e.stopPropagation();
                showEnViLookup(subWord);
                return;
            }

            if (handleLinkClick(e)) return;

            if ((e.target && e.target.closest && e.target.closest('.content')) || (e.target && e.target.tagName && e.target.tagName.toLowerCase() === 'img')) {
                e.stopPropagation();
            }
        };
        document.body.addEventListener('click', bodyClickHandler, true);
        subWordHoverCleanup = bindEnglishLookupHover(document.body, '.eng-sub-word', showEnViLookup);

        beforeUnloadHandler = function() {
            try { if (parentWin[cleanupKey]) parentWin[cleanupKey](); } catch (err) {}
        };
        window.addEventListener('beforeunload', beforeUnloadHandler);
    }

    function cleanup() {
        try { if (bodyClickHandler) document.body.removeEventListener('click', bodyClickHandler, true); } catch (err) {}
        try { if (subWordHoverCleanup) subWordHoverCleanup(); } catch (err) {}
        try { if (beforeUnloadHandler) window.removeEventListener('beforeunload', beforeUnloadHandler); } catch (err) {}
        try {
            if (dictState) {
                dictState.entry = null;
                dictState.enVi = null;
                dictState = null;
            }
        } catch (err) {}
        textRoot = null;
        bodyClickHandler = null;
        subWordHoverCleanup = null;
        beforeUnloadHandler = null;
        try { delete parentWin[cleanupKey]; } catch (err) {
            try { parentWin[cleanupKey] = null; } catch (err2) {}
        }
    }

    setup();
    parentWin[cleanupKey] = cleanup;
})();
</script>
'''


def build_dictionary_reader_js(
    *,
    entry_json: str,
    en_vi_json: str,
    is_sidebar: bool,
    entry_target_id: str,
    envi_target_id: str,
    text_root_id: str,
    cleanup_key: str,
    entry_label: str,
    accent_color: str,
    decorate_longman_headers: bool = False,
) -> str:
    replacements = {
        "__ENTRY_JSON__": entry_json,
        "__ENVI_JSON__": en_vi_json,
        "__IS_SIDEBAR__": _js_bool(is_sidebar),
        "__ENTRY_TARGET_ID__": str(entry_target_id),
        "__ENVI_TARGET_ID__": str(envi_target_id),
        "__TEXT_ROOT_ID__": str(text_root_id),
        "__CLEANUP_KEY__": str(cleanup_key),
        "__ENTRY_LABEL__": str(entry_label),
        "__ACCENT_COLOR__": str(accent_color),
        "__ENTRY_DECORATOR_JS__": (
            LONGMAN_ENTRY_HEADER_DECORATOR_JS if decorate_longman_headers else ""
        ),
        "__HOVER_LOOKUP_HELPER_JS__": ENG_READER_HOVER_LOOKUP_HELPER_JS,
    }
    out = DICTIONARY_READER_JS_TEMPLATE
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out
