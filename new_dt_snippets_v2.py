# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Bounded DT selected-document snippets L2 island.

Python remains authoritative for extraction/matching and resource/query identity.
Only pagination/DOM/scroll/focus stay local; never fetch or emit bridge state.
Enable/strict policy belongs to new_components_v2_config and the caller.
"""


import hashlib


import json


from new_component_v2_support import get_v2_component


from new_dt_search_service import extract_all_snippets, _keyword_regex, _normalize_search_text


from new_dt_v2_reader import prepare_ranges, DT_READER_JS


from new_components_v2_config import record_v2_route, record_v2_mount


MAX_SOURCE_BYTES = 8 * 1024 * 1024


MAX_EXTRACTION_MATCHES = 20000


MAX_SNIPPETS = 1000


MAX_TEXT_BYTES = 768 * 1024


MAX_PAYLOAD_BYTES = 2 * 1024 * 1024


MAX_MATCH_CANDIDATES = 12000


MAX_PAGES = 128


MAX_PAGE_SIZE = 100


class DTSnippetsV2Unsupported(ValueError):
    """Use the existing snippet fragment for this input."""


def prepare_dt_snippets_payload(selected_content, selected_query, q2, clean_title, identity,
                                *, snippets_per_page=100, key_prefix=""):
    if not isinstance(selected_content, str) or len(selected_content) > MAX_SOURCE_BYTES:
        raise DTSnippetsV2Unsupported("source_text_limit")
    raw_source = selected_content.encode('utf-8', errors='replace')
    if len(raw_source) > MAX_SOURCE_BYTES:
        raise DTSnippetsV2Unsupported("source_text_limit")
    if type(snippets_per_page) is not int or not 1 <= snippets_per_page <= MAX_PAGE_SIZE:
        raise DTSnippetsV2Unsupported("page_size_limit")
    queries = (selected_query or '', q2 or '')
    if any(len(query) > 4096 for query in queries):
        raise DTSnippetsV2Unsupported("keyword_limit")
    # Canonical extraction materializes matches. Bound that allocation before
    # calling the unchanged helper; eligibility scanning does not alter semantics.
    if _normalize_search_text(queries[0]):
        for count, _ in enumerate(_keyword_regex(queries[0]).finditer(selected_content), 1):
            if count > MAX_EXTRACTION_MATCHES:
                raise DTSnippetsV2Unsupported("extraction_match_limit")
    snippets = extract_all_snippets(selected_content, queries[0])
    if len(snippets) > MAX_SNIPPETS:
        raise DTSnippetsV2Unsupported("snippet_limit")
    pages = [[start, min(start + snippets_per_page, len(snippets))]
             for start in range(0, len(snippets), snippets_per_page)] or [[0, 0]]
    if len(pages) > MAX_PAGES:
        raise DTSnippetsV2Unsupported("page_limit")
    text = ''.join(snippets)
    if len(text) > MAX_TEXT_BYTES or len(text.encode('utf-8', errors='replace')) > MAX_TEXT_BYTES:
        raise DTSnippetsV2Unsupported("snippet_text_limit")
    cursor = 0
    offsets = []
    for snippet in snippets:
        offsets.append((cursor, cursor + len(snippet)))
        cursor += len(snippet)
    items, marks = prepare_ranges(text, offsets, queries,
                                 max_matches=MAX_MATCH_CANDIDATES, error_type=DTSnippetsV2Unsupported)
    # Queries are included even when they happen to yield the same snippets:
    # legacy resets its page on either query change. Canonical identity adds
    # URL/dataset/revision isolation without exposing these fields in the payload.
    identity_bytes = json.dumps([identity, queries, snippets_per_page, str(clean_title)], ensure_ascii=False,
                                default=str, separators=(',', ':')).encode('utf-8', errors='replace')
    resource_id = hashlib.sha256(identity_bytes + b'\0' + raw_source).hexdigest()
    view_id = hashlib.sha256(json.dumps([items, marks, str(clean_title)], ensure_ascii=False,
                                      separators=(',', ':')).encode('utf-8', errors='replace')).hexdigest()
    payload = dict(version=1, text=text, items=items, marks=marks, pages=pages,
                   count=len(snippets), title=str(clean_title), resource_id=resource_id, view_id=view_id,
                   instance_key='scapp_dt_snippets_v2:' + str(key_prefix))
    # Match Streamlit's default JSON serialization, including Unicode escapes.
    if len(json.dumps(payload).encode('utf-8')) > MAX_PAYLOAD_BYTES:
        raise DTSnippetsV2Unsupported("payload_limit")
    return payload


_COMPONENT_HTML = '<section class="dt-snippets-v2" data-dt-snippets-v2-root></section>'


_COMPONENT_CSS = r"""
.dt-snippets-v2 { width:100%; box-sizing:border-box; font-family:inherit; color:inherit; }
.dt-snippets-v2 h3 { margin:0 0 .5rem; font-size:1.35rem; font-weight:600; line-height:1.4; }
.dt-snippets-v2 [data-snippet-icon] { font-family:'Material Symbols Rounded'; font-size:1.35rem; vertical-align:middle; font-weight:400; }
.dt-snippets-v2 hr { margin:.5rem 0; opacity:.65; }
.dt-snippets-v2 [data-snippet-count] { margin:0 0 1rem; }
.dt-snippets-v2 article { background:mintCream; color:#31333f; padding:15px; border-radius:5px; margin-bottom:15px; border-left:4px solid #ffcf33; font-size:15px; overflow-wrap:anywhere; }
.dt-snippets-v2 mark { color:black; padding:0 2px; border-radius:2px; }
.dt-snippets-v2 nav { display:flex; flex-wrap:wrap; gap:.35rem; align-items:center; margin-top:1rem; }
.dt-snippets-v2 button { font:inherit; color:inherit; background:transparent; border:1px solid #9996; border-radius:.4rem; padding:.3rem .6rem; cursor:pointer; }
.dt-snippets-v2 button[aria-current="page"] { background:#f0f2f6; border-color:#777; }
.dt-snippets-v2 button:disabled { opacity:.45; cursor:default; }
.dt-snippets-v2 button:focus-visible { outline:2px solid #1678cb; outline-offset:2px; }
"""


_COMPONENT_JS = DT_READER_JS + r"""
const PAGE_STORE = Symbol.for("scapp.dt-snippets-v2.pages");
function pageStore() {
  if (!window[PAGE_STORE]) window[PAGE_STORE] = new Map();
  return window[PAGE_STORE];
}
function renderPage(root, scroll) {
  const state = root.__dtSnippetsV2, data = state.data;
  state.page = clampPage(state.page, data.pages.length);
  pageStore().set(data.instance_key, {resource_id:data.resource_id, page:state.page});
  const [start, end] = data.pages[state.page-1];
  const cards = document.createDocumentFragment();
  for (let i = start; i < end; i++) {
    const card = document.createElement("article");
    card.setAttribute("data-snippet-index", String(i));
    const content = document.createElement("span");
    fillMarkedRange(content, data, ...data.items[i]);
    card.appendChild(document.createTextNode("... "));
    card.appendChild(content);
    card.appendChild(document.createTextNode(" ..."));
    cards.appendChild(card);
  }
  root.querySelector("[data-snippet-items]").replaceChildren(cards);
  renderPager(root.querySelector("nav"), state.page, data.pages.length);
  if (scroll) requestAnimationFrame(() => scrollReaderTop(root));
}
export default function(component) {
  const {data, parentElement} = component;
  const root = parentElement.querySelector("[data-dt-snippets-v2-root]");
  if (!root || data?.version !== 1 || !data.pages?.length) return;
  const previous = root.__dtSnippetsV2;
  if (!previous) {
    const heading = document.createElement("h3");
    const icon = document.createElement("span");
    icon.setAttribute("data-snippet-icon", ""); icon.setAttribute("aria-hidden", "true"); icon.textContent = "action_key";
    const title = document.createElement("span"); title.setAttribute("data-snippet-title", "");
    heading.appendChild(icon); heading.appendChild(title);
    const divider = document.createElement("hr");
    const count = document.createElement("p"); count.setAttribute("data-snippet-count", "");
    const total = document.createElement("strong"); total.setAttribute("data-snippet-total", "");
    count.appendChild(document.createTextNode("Tìm thấy ")); count.appendChild(total); count.appendChild(document.createTextNode(" phân đoạn."));
    const items = document.createElement("div"); items.setAttribute("data-snippet-items", "");
    const nav = document.createElement("nav"); nav.setAttribute("aria-label", "Phân trang phân đoạn");
    root.replaceChildren(heading, divider, count, items, nav);
    root.addEventListener("click", event => {
      const target = event.target instanceof Element ? event.target.closest("button[data-page]") : null;
      if (!target || !root.contains(target) || target.disabled) return;
      const state = root.__dtSnippetsV2;
      const next = clampPage(Number(target.dataset.page), state.data.pages.length);
      if (next === state.page) return;
      const label = target.getAttribute("aria-label");
      state.page = next;
      renderPage(root, true);
      const controls = Array.from(root.querySelector("nav").querySelectorAll("button"));
      const focus = controls.find(button => !button.disabled && button.getAttribute("aria-label") === label)
        || controls.find(button => button.getAttribute("aria-current") === "page");
      focus?.focus({preventScroll:true});
    });
  }
  const remembered = pageStore().get(data.instance_key);
  const sameResource = previous?.data.resource_id === data.resource_id;
  const page = sameResource ? previous.page : remembered?.resource_id === data.resource_id ? remembered.page : 1;
  const unchanged = sameResource && previous.data.view_id === data.view_id;
  root.__dtSnippetsV2 = {data, page:clampPage(page, data.pages.length)};
  root.querySelector("[data-snippet-title]").textContent = ` Chi tiết: ${data.title}`;
  root.querySelector("[data-snippet-total]").textContent = String(data.count);
  if (!unchanged) renderPage(root, Boolean(previous && !sameResource));
}
"""


def render_dt_snippets_v2(selected_content, selected_query, q2, clean_title, identity,
                          *, snippets_per_page=100, key_prefix=""):
    payload = prepare_dt_snippets_payload(selected_content, selected_query, q2, clean_title, identity,
                                         snippets_per_page=snippets_per_page, key_prefix=key_prefix)
    renderer = get_v2_component('scapp_dt_snippets_v2', _COMPONENT_HTML, _COMPONENT_CSS, _COMPONENT_JS)
    result = renderer(data=payload, key='scapp_dt_snippets_v2:' + str(key_prefix))
    record_v2_mount("dt_snippets", payload, items=payload['count'], pages=len(payload['pages']))
    return result

