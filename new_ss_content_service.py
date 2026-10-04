"""
Content-formatting helpers for `new_ss.py`.

This module does not import Streamlit. It only prepares HTML strings used by
the Streamlit page.
"""

from __future__ import annotations

import html
import re

from dict_lookup_assets import build_typography_css
from assets_style import build_reader_typography_reset_css


HTML_DETECTION_PATTERN = re.compile(
    r"<(p|div|article|html|body|h[1-6]|ul|li)[^>]*>",
    re.IGNORECASE,
)


def is_html_content(raw_data: str) -> bool:
    """
    Detect whether raw text looks like HTML content.
    """
    return bool(HTML_DETECTION_PATTERN.search(raw_data))


def extract_main_html_content(raw_html: str) -> str:
    """
    Extract article/body content when present; otherwise return the original HTML.
    """
    main_content = raw_html
    match = re.search(r"<(article|body)[^>]*>(.*?)</\1>", raw_html, re.IGNORECASE | re.DOTALL)
    if match:
        main_content = match.group(2)
    return main_content


def remove_internal_anchor_links(raw_html: str) -> str:
    """
    Remove internal anchor links such as href="#...".
    """
    return re.sub(
        r"<a[^>]*href=[\'\"]#.*?[\'\"][^>]*>.*?</a>",
        "",
        raw_html,
        flags=re.IGNORECASE,
    )


def trim_trailing_html_whitespace(raw_html: str) -> str:
    """
    Remove trailing blank HTML fragments and whitespace.
    """
    return re.sub(
        r"(?:<br\s*/?>|<p>\s*(?:&nbsp;)?\s*</p>|\s)+$",
        "",
        raw_html,
        flags=re.IGNORECASE,
    )


def text_to_html_paragraphs(raw_text: str, header_html: str | None = None) -> str:
    """
    Convert plain text into simple HTML paragraphs.
    """
    raw_text = raw_text.replace("\r\n", "\n")
    paragraphs = re.split(r"\n{2,}", raw_text)

    html_paragraphs: list[str] = []

    if header_html:
        html_paragraphs.append(header_html)

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            p_html = paragraph.replace("\n", "<br>")
            html_paragraphs.append(f"<p>{p_html}</p>")

    return "".join(html_paragraphs)


def normalize_inline_html(content_to_render: str) -> str:
    """
    Flatten newlines for the current Streamlit markdown rendering strategy.
    """
    flat_lines = [line.strip() for line in content_to_render.split("\n")]
    return "".join(flat_lines)


def prepare_content_html(raw_data, header_html: str | None = None) -> str:
    """
    Prepare raw sutta content as inner HTML for the scrollable content container.
    """
    raw_data = str(raw_data).strip()

    if is_html_content(raw_data):
        main_content = extract_main_html_content(raw_data)
        content_to_render = remove_internal_anchor_links(main_content)
        content_to_render = trim_trailing_html_whitespace(content_to_render)
    else:
        content_to_render = text_to_html_paragraphs(raw_data, header_html=header_html)

    return normalize_inline_html(content_to_render)


# def build_scrollable_content_html(raw_data, header_html: str | None = None, height=700) -> str:
#     """
#     Build full scrollable HTML block for text/HTML content.
#     """
#     clean_content = prepare_content_html(raw_data, header_html=header_html)
#
#     return (
#         f'<div style="max-height:{height}px;overflow-y:auto;overflow-x:hidden;width:100%;padding-right:15px;">'
#         f"<style>"
#         f".custom-scroll-content p {{margin-top:0;margin-bottom:1rem;line-height:1.6;text-align:justify;}}"
#         f".custom-scroll-content h1, .custom-scroll-content h2, .custom-scroll-content h3 {{margin-top:0;padding-top:5px;}}"
#         f".custom-scroll-content ul, .custom-scroll-content li {{margin-bottom:0.5rem;}}"
#         f".custom-scroll-content::-webkit-scrollbar {{width:6px;}}"
#         f".custom-scroll-content::-webkit-scrollbar-thumb {{background:#ccc;border-radius:4px;}}"
#         f"</style>"
#         f'<div class="custom-scroll-content">'
#         f"{clean_content}"
#         f"</div>"
#         f"</div>"
#     )
#
#
# def build_scrollable_table_html(raw_html_table: str, height=700) -> str:
#     """
#     Build full scrollable HTML block for a table.
#     """
#     return f"""
#     <div style="max-height: {height}px; overflow-y: auto; overflow-x: hidden; width: 100%;">
#         <style>
#             .custom-scroll-table table {{ width: 100%; border-collapse: collapse; }}
#             .custom-scroll-table td {{ padding: 8px; vertical-align: top; }}
#         </style>
#         <div class="custom-scroll-table">
#             {raw_html_table}
#         </div>
#     </div>
#     """


def _wrap_ss_reader_html(
    content_html: str,
    *,
    height,
    container_id,
    scroll_to_top=False,
    table_mode=False,
) -> str:
    """A self-contained SS iframe; one scroll surface for text and tables."""
    # CSS variables must be defined inside the iframe, not on Streamlit's body.
    typography_css = build_typography_css()
    reader_typography_css = build_reader_typography_reset_css(
        ".ss-reader",
        inherit_selectors=(
            ".ss-reader table",
            ".ss-reader td",
            ".ss-reader th",
            ".ss-reader p",
            ".ss-reader div",
            ".ss-reader span",
            ".ss-reader li",
            ".ss-reader a",
            ".ss-reader em",
            ".ss-reader strong",
            ".ss-reader b",
            ".ss-reader i",
            ".ss-reader font",
            ".ss-reader small",
            ".ss-reader label",
        ),
        id_selector=(
            ".ss-reader table td:first-child"
            if table_mode
            else None
        ),
    )
    reset_script = (
        '<script>document.querySelector(".ss-reader").scrollTop = 0;</script>'
        if scroll_to_top else ""
    )
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {typography_css}
        html, body {{
            margin: 0; padding: 0; overflow: hidden;
            background: var(--dl-bg-main, #fdfdf8);
            color: var(--dl-text, #3d3a2a);
        }}
        .ss-reader {{
            height: {height}px; width: 100%; box-sizing: border-box;
            overflow-y: auto; overflow-x: hidden; padding-right: 15px;
            color: var(--dl-text, #3d3a2a);
            text-size-adjust: 100%; -webkit-text-size-adjust: 100%;
            -webkit-font-smoothing: auto;
            scrollbar-width: thin; scrollbar-color: #ccc transparent;
        }}
        /* Firefox uses the standard rule; Chromium/WebKit use the 6px thumb. */
        @supports selector(::-webkit-scrollbar) {{
            .ss-reader {{ scrollbar-width: auto; scrollbar-color: auto; }}
        }}
        .ss-reader::-webkit-scrollbar {{ width: 6px; }}
        .ss-reader::-webkit-scrollbar-track {{ background: transparent; }}
        .ss-reader::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
        .ss-reader p {{
            margin-top: 0; margin-bottom: 1rem;
            line-height: var(--dl-reader-line-height, 1.6); text-align: justify;
        }}
        .ss-reader h1, .ss-reader h2, .ss-reader h3,
        .ss-reader h4, .ss-reader h5, .ss-reader h6 {{
            margin-top: 0; padding-top: 5px; line-height: 1.2;
            font-weight: 600; color: var(--dl-primary, #3d3a2a);
        }}
        .ss-reader ul, .ss-reader li {{ margin-bottom: 0.5rem; }}
        .ss-reader table {{ width: 100%; border-collapse: collapse; border: 1px solid #eaeae3; }}
        .ss-reader td, .ss-reader th {{ padding: 8px; vertical-align: top; border: 1px solid #eaeae3; }}
        {reader_typography_css}
    </style>
</head>
<body>
    <div id="{html.escape(container_id, quote=True)}" class="ss-reader">{content_html}</div>
    {reset_script}
</body>
</html>"""


def build_scrollable_content_html(
    raw_data, header_html: str | None = None, height=700, container_id="",
    *, scroll_to_top=False,
) -> str:
    """Build the SS content iframe without changing source formatting."""
    return _wrap_ss_reader_html(
        prepare_content_html(raw_data, header_html=header_html),
        height=height,
        container_id=container_id,
        scroll_to_top=scroll_to_top,
        table_mode=False,
    )


def build_scrollable_table_html(
    raw_html_table: str, height=700, container_id="", *, scroll_to_top=False,
) -> str:
    """Build the SS table iframe with the same reader surface as text."""
    return _wrap_ss_reader_html(
        raw_html_table,
        height=height,
        container_id=container_id,
        scroll_to_top=scroll_to_top,
        table_mode=True,
    )

