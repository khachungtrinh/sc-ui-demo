"""Streamlit Components v2 renderer for SS content.

This module is intentionally isolated from ``ss.py`` so it can serve as a
small reference implementation for later Components v2 functional islands.

Reader contract
---------------
* keep the existing ``show_content`` data contract;
* pass prepared content to the browser once per Streamlit render;
* keep scrolling/render-only behavior in the browser;
* send no component state or trigger values back to Python;
* keep the legacy iframe renderer available as the default/fallback path.

Enable/strict/metrics configuration lives in new_components_v2_config.py.

Security note
-------------
Components v2 are not iframe-sandboxed. The dynamic content is therefore sent
through the component ``data`` channel and sanitized in the browser before it
is assigned to ``innerHTML``. This renderer is intended only for application-owned
Sutta/corpus content. It must not be reused for arbitrary uploaded or otherwise
untrusted HTML without a dedicated sanitizer/security review.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from new_component_v2_support import get_v2_component, SAFE_HTML_JS
from new_components_v2_config import v2_metrics_enabled, record_v2_route
from assets_style import build_reader_typography_reset_css

from dict_lookup_assets import (
    DL_READER_BG_MAIN,
    DL_READER_BORDER_COLOR,
    DL_READER_FONT_FAMILY,
    DL_READER_FONT_SIZE,
    DL_READER_LINE_HEIGHT,
    DL_READER_PRIMARY_COLOR,
    DL_READER_TEXT_COLOR,
)
from new_ss_content_service import prepare_content_html


LOGGER = logging.getLogger(__name__)

_COMPONENT_HTML = '<div class="ss-content-v2-host" data-ss-content-v2-root></div>'

_COMPONENT_CSS = f"""
.ss-content-v2-host {{
    width: 100%;
    box-sizing: border-box;
}}

.ss-content-v2-reader {{
    width: 100%;
    box-sizing: border-box;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 15px;
    background: {DL_READER_BG_MAIN};
    color: {DL_READER_TEXT_COLOR};
    font-family: {DL_READER_FONT_FAMILY};
    font-size: {DL_READER_FONT_SIZE};
    line-height: {DL_READER_LINE_HEIGHT};
    font-weight: 400;
    letter-spacing: normal;
    word-spacing: normal;
    text-size-adjust: 100%;
    -webkit-text-size-adjust: 100%;
    -webkit-font-smoothing: auto;
    scrollbar-width: thin;
    scrollbar-color: #ccc transparent;
}}

.ss-content-v2-reader::-webkit-scrollbar {{ width: 6px; }}
.ss-content-v2-reader::-webkit-scrollbar-track {{ background: transparent; }}
.ss-content-v2-reader::-webkit-scrollbar-thumb {{
    background: #ccc;
    border-radius: 4px;
}}

.ss-content-v2-reader p {{
    margin-top: 0;
    margin-bottom: 1rem;
    line-height: {DL_READER_LINE_HEIGHT};
    text-align: justify;
}}

.ss-content-v2-reader h1,
.ss-content-v2-reader h2,
.ss-content-v2-reader h3,
.ss-content-v2-reader h4,
.ss-content-v2-reader h5,
.ss-content-v2-reader h6 {{
    margin-top: 0;
    padding-top: 5px;
    line-height: 1.2;
    font-weight: 600;
    color: {DL_READER_PRIMARY_COLOR};
}}

.ss-content-v2-reader ul,
.ss-content-v2-reader li {{
    margin-bottom: 0.5rem;
}}

.ss-content-v2-reader table {{
    width: 100%;
    border-collapse: collapse;
    border: 1px solid {DL_READER_BORDER_COLOR};
}}

.ss-content-v2-reader td,
.ss-content-v2-reader th {{
    padding: 8px;
    vertical-align: top;
    border: 1px solid #eaeae3;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
}}
"""

# Text and table surfaces share the same local DOM/sanitizer contract.
_COMPONENT_CSS += build_reader_typography_reset_css(
    ".ss-content-v2-host.ss-table", inherit_selectors=(".ss-table td", ".ss-table th", ".ss-table td *"),
    id_selector=".ss-table table td:first-child")
_COMPONENT_CSS += ".ss-table table {border:1px solid #eaeae3;}"
_COMPONENT_JS = SAFE_HTML_JS + r"""
export default function(component) {
  const { data, parentElement } = component;
  const root = parentElement.querySelector("[data-ss-content-v2-root]");
  if (!root) return;

  const previousScrollTop = root.scrollTop || 0;
  const previousContentId = root.dataset.contentId || "";
  const contentId = String(data?.content_id || "");

  root.classList.add("ss-content-v2-reader");
  root.classList.toggle("ss-table", Boolean(data?.table_mode));
  root.style.height = `${Number(data?.height || 700)}px`;

  if (previousContentId !== contentId) {
    root.innerHTML = sanitizeHtml(data?.content_html || "");
    root.dataset.contentId = contentId;
  }

  if (data?.scroll_to_top) {
    root.scrollTop = 0;
  } else if (previousContentId === contentId) {
    root.scrollTop = previousScrollTop;
  }
}
"""


def _ss_content_v2_component(**kwargs):
    renderer = get_v2_component('scapp_ss_content_v2', _COMPONENT_HTML, _COMPONENT_CSS, _COMPONENT_JS)
    return renderer(**kwargs)


def _content_fingerprint(content_html: str) -> str:
    return hashlib.sha256(content_html.encode("utf-8", errors="replace")).hexdigest()[:20]


def render_ss_content_v2(
    raw_data: Any,
    header_html: str | None = None,
    height: int = 700,
    scroll_to_top: bool = True,
):
    """Render SS content through the isolated Components v2 reader.

    The wrapper intentionally mirrors ``ss.show_content`` so a caller can be
    switched between legacy and v2 with a single conditional branch.

    No state/trigger value is sent from the browser to Python. Scroll state is
    browser-local for the lifetime of the mounted component.
    """
    if not raw_data:
        return None

    content_html = prepare_content_html(raw_data, header_html=header_html)
    content_id = _content_fingerprint(content_html)

    if v2_metrics_enabled("ss_content"):
        LOGGER.info(
            "ss_content_v2 mount content_id=%s utf8_bytes=%d height=%s scroll_to_top=%s",
            content_id,
            len(content_html.encode("utf-8", errors="replace")),
            height,
            bool(scroll_to_top),
        )

    result = _ss_content_v2_component(
        data={
            "content_html": content_html,
            "content_id": content_id,
            "height": int(height),
            "scroll_to_top": bool(scroll_to_top),
            "version": 1,
        }
    )
    record_v2_route("ss_content", "v2")
    return result


def render_ss_table_v2(raw_html_table, *, height=700, scroll_to_top=True):
    """Use the canonical prepared table directly; do not reformat as prose."""
    if len(raw_html_table.encode('utf-8', errors='replace')) > 16 * 1024 * 1024:
        raise ValueError("table_text_limit")
    data = {
        "content_html": raw_html_table,
        "content_id": _content_fingerprint("table:" + raw_html_table),
        "height": int(height), "scroll_to_top": bool(scroll_to_top),
        "version": 1, "table_mode": True,
    }
    if len(json.dumps(data).encode("utf-8")) > 32 * 1024 * 1024:
        raise ValueError("table_payload_limit")
    result = _ss_content_v2_component(data=data)
    record_v2_route("ss_table", "v2")
    return result
