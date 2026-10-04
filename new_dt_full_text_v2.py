# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Opt-in DT full-text L2 island. Existing document/search ownership stays Python.

Canonical Python match/page ranges cross the wire once per mount/update. Local
page buttons only slice text and build safe DOM nodes; they send no events/data
back to Python and perform no network reads. Larger inputs retain legacy.
"""


import hashlib


import json


import base64


from new_component_v2_support import get_v2_component


from new_dt_v2_reader import prepare_ranges, DT_READER_JS


from new_components_v2_config import record_v2_route, record_v2_mount


MAX_TEXT_BYTES = 16 * 1024 * 1024


MAX_PAYLOAD_BYTES = 32 * 1024 * 1024


MAX_MATCH_CANDIDATES = 200000


MAX_PAGES = 2048


MAX_PAGE_CHARS = 2 * 1024 * 1024


class DTFullTextV2Unsupported(ValueError):
    """This document should stay on the existing full-text renderer."""


def prepare_dt_full_text_payload(content, offsets, identity, clean_title, query, query2, search_mode,
                                 *, key_prefix="", initial_page=1):
    if not isinstance(content, str) or len(content) > MAX_TEXT_BYTES:
        raise DTFullTextV2Unsupported("text_limit")
    raw = content.encode('utf-8', errors='replace')
    if len(raw) > MAX_TEXT_BYTES:
        raise DTFullTextV2Unsupported("text_limit")
    if not isinstance(offsets, (list, tuple)) or not offsets:
        raise DTFullTextV2Unsupported("invalid_offsets")
    if len(offsets) > MAX_PAGES:
        raise DTFullTextV2Unsupported("page_limit")
    cursor = 0
    for pair in offsets:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise DTFullTextV2Unsupported("invalid_offsets")
        start, end = pair
        if type(start) is not int or type(end) is not int or start != cursor or end < start or end > len(content):
            raise DTFullTextV2Unsupported("invalid_offsets")
        if end - start > MAX_PAGE_CHARS:
            raise DTFullTextV2Unsupported("page_text_limit")
        cursor = end
    if cursor != len(content):
        raise DTFullTextV2Unsupported("invalid_offsets")
    queries = (query or '', query2 or '') if search_mode == 'Nội dung' else ('', '')
    pages, spans = prepare_ranges(content, offsets, queries,
                                  max_matches=MAX_MATCH_CANDIDATES, error_type=DTFullTextV2Unsupported)
    identity_bytes = json.dumps(identity, ensure_ascii=False, default=str, separators=(',', ':')).encode('utf-8', errors='replace')
    resource_id = hashlib.sha256(identity_bytes + b'\0' + raw).hexdigest()
    view = [pages, spans, str(clean_title)]
    view_id = hashlib.sha256(json.dumps(view, ensure_ascii=False, separators=(',', ':')).encode('utf-8', errors='replace')).hexdigest()
    payload = dict(version=1, text=content, pages=pages, marks=spans,
                   resource_id=resource_id, view_id=view_id, title=str(clean_title),
                   instance_key='scapp_dt_full_text_v2:' + str(key_prefix),
                   initial_page=max(1, min(int(initial_page), len(pages))))
    # Large Vietnamese/Pāli strings can grow substantially under JSON ASCII
    # escaping. Use lossless UTF-8/base64 only where it reduces the wire field.
    # No compression runtime, browser fetch or backend contract is involved.
    if len(raw) >= 64 * 1024 and len(json.dumps(content)) > 4 * ((len(raw) + 2) // 3):
        payload.pop('text')
        payload.update(version=2, text_utf8_b64=base64.b64encode(raw).decode('ascii'))
    # Streamlit 1.63 serializes component data with json.dumps defaults, including
    # ASCII escapes. Count that representation, not a smaller compact UTF-8 JSON.
    # This bounds data JSON only, not protocol overhead or browser heap usage.
    if len(json.dumps(payload).encode('utf-8')) > MAX_PAYLOAD_BYTES:
        raise DTFullTextV2Unsupported("payload_limit")
    return payload


_COMPONENT_HTML = '<section class="dt-full-text-v2" data-dt-full-text-v2-root></section>'


_COMPONENT_CSS = r"""
.dt-full-text-v2 { width:100%; box-sizing:border-box; font-family:inherit; color:inherit; }
.dt-full-text-v2 h3 { margin:0 0 .5rem; font-size:1.35rem; font-weight:600; line-height:1.4; }
.dt-full-text-v2 [data-dt-icon] { font-family:'Material Symbols Rounded'; font-size:1.35rem; vertical-align:middle; font-weight:400; }
.dt-full-text-v2 hr { margin:.5rem 0; opacity:.65; }
.dt-full-text-v2 [data-dt-text] { background:mintCream; color:#31333f; white-space:pre-wrap; overflow-wrap:anywhere; line-height:inherit; }
.dt-full-text-v2 mark { color:black; padding:0 2px; border-radius:2px; }
.dt-full-text-v2 nav { display:flex; flex-wrap:wrap; gap:.35rem; align-items:center; margin-top:1rem; }
.dt-full-text-v2 button { font:inherit; color:inherit; background:transparent; border:1px solid #9996; border-radius:.4rem; padding:.3rem .6rem; cursor:pointer; }
.dt-full-text-v2 button[aria-current="page"] { background:#f0f2f6; border-color:#777; }
.dt-full-text-v2 button:disabled { opacity:.45; cursor:default; }
.dt-full-text-v2 button:focus-visible { outline:2px solid #1678cb; outline-offset:2px; }
.dt-full-text-v2 [data-dt-caption] { font-size:.875rem; margin-top:.5rem; color:#666; }
"""


_COMPONENT_JS = DT_READER_JS + r"""
// Per-tab, last resource/page only for each owner. No content, query, URL, or
// history is stored here, and nothing is sent back through the Streamlit bridge.
const PAGE_STORE = Symbol.for("scapp.dt-full-text-v2.pages");
function pageStore() {
  if (!window[PAGE_STORE]) window[PAGE_STORE] = new Map();
  return window[PAGE_STORE];
}
function renderPage(root, scroll) {
  const state = root.__dtFullTextV2;
  const data = state.data;
  state.page = clampPage(state.page, data.pages.length);
  pageStore().set(data.instance_key, {resource_id:data.resource_id, page:state.page});
  fillMarkedRange(root.querySelector("[data-dt-text]"), data, ...data.pages[state.page-1]);
  const nav = root.querySelector("nav");
  renderPager(nav, state.page, data.pages.length);
  const caption = root.querySelector("[data-dt-caption]");
  caption.hidden = data.pages.length <= 1;
  caption.textContent = `Trang ${state.page} / ${data.pages.length}`;
  if (scroll) requestAnimationFrame(() => scrollReaderTop(root));
}
export default function(component) {
  const {parentElement} = component;
  let data = component.data;
  const root = parentElement.querySelector("[data-dt-full-text-v2-root]");
  if (!root || ![1, 2].includes(data?.version) || !data.pages?.length) return;
  const previous = root.__dtFullTextV2;
  if (data.version === 2) {
    const text = previous?.data.resource_id === data.resource_id
      ? previous.data.text
      : new TextDecoder('utf-8', {fatal:true}).decode(Uint8Array.from(atob(data.text_utf8_b64), c => c.charCodeAt(0)));
    // Keep only the decoded representation in our local state.
    const {text_utf8_b64, ...fields} = data;
    data = {...fields, text};
  }
  if (!previous) {
    const heading = document.createElement("h3");
    const icon = document.createElement("span");
    icon.setAttribute("data-dt-icon", ""); icon.setAttribute("aria-hidden", "true"); icon.textContent = "book";
    const title = document.createElement("span"); title.setAttribute("data-dt-title", "");
    heading.appendChild(icon); heading.appendChild(title);
    const divider = document.createElement("hr");
    const text = document.createElement("div"); text.setAttribute("data-dt-text", "");
    const nav = document.createElement("nav"); nav.setAttribute("aria-label", "Phân trang toàn văn");
    const caption = document.createElement("div"); caption.setAttribute("data-dt-caption", ""); caption.setAttribute("aria-live", "polite");
    root.replaceChildren(heading, divider, text, nav, caption);
    root.addEventListener("click", event => {
      const target = event.target instanceof Element ? event.target.closest("button[data-page]") : null;
      if (!target || !root.contains(target) || target.disabled) return;
      const state = root.__dtFullTextV2;
      const next = clampPage(Number(target.dataset.page), state.data.pages.length);
      if (next !== state.page) {
        const label = target.getAttribute("aria-label");
        state.page = next;
        renderPage(root, true);
        // DOM replacement must not discard keyboard focus on each page action.
        const controls = Array.from(root.querySelector("nav").querySelectorAll("button"));
        const focus = controls.find(button => !button.disabled && button.getAttribute("aria-label") === label)
          || controls.find(button => button.getAttribute("aria-current") === "page");
        focus?.focus({preventScroll:true});
      }
    });
  }
  const remembered = pageStore().get(data.instance_key);
  const sameResource = previous?.data.resource_id === data.resource_id;
  const page = sameResource ? previous.page : remembered?.resource_id === data.resource_id ? remembered.page : data.initial_page;
  const unchanged = sameResource && previous.data.view_id === data.view_id;
  root.__dtFullTextV2 = {data, page:clampPage(page, data.pages.length)};
  root.querySelector("[data-dt-title]").textContent = `Toàn văn: ${data.title}`;
  if (!unchanged) renderPage(root, Boolean(previous && !sameResource));
}
"""


def render_dt_full_text_v2(content, offsets, identity, clean_title, query, query2, search_mode,
                           *, key_prefix="", initial_page=1):
    payload = prepare_dt_full_text_payload(content, offsets, identity, clean_title, query, query2, search_mode,
                                           key_prefix=key_prefix, initial_page=initial_page)
    renderer = get_v2_component('scapp_dt_full_text_v2', _COMPONENT_HTML, _COMPONENT_CSS, _COMPONENT_JS)
    result = renderer(data=payload, key='scapp_dt_full_text_v2:' + str(key_prefix))
    record_v2_mount('dt_full_text', payload,
                    pages=len(payload['pages']), marks=len(payload['marks']))
    return result

