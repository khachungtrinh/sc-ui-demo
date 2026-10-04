"""Bounded held-result viewers for DT main search and TD dictionary results.

Pagination is local. DT selection emits only a resource digest, ordinal and
view mode; Python resolves them against its current canonical hit list.
"""
import hashlib
import html
import json
import re
from pathlib import Path
import streamlit as st

from new_component_v2_support import get_v2_component, SAFE_HTML_JS
from new_components_v2_config import v2_enabled, v2_strict, record_v2_route, record_v2_mount
from new_dt_search_service import highlight_keywords
from new_dt_v2_reader import DT_READER_JS

MAX_ITEMS = 20000
MAX_TEXT_BYTES = 8 * 1024 * 1024
MAX_PAYLOAD_BYTES = 24 * 1024 * 1024


class ResultListUnsupported(ValueError):
    pass


def _payload(kind, items, identity, page_size, *, allow_snippets=False, key_prefix="main"):
    if type(page_size) is not int or not 1 <= page_size <= 200:
        raise ResultListUnsupported('page_size_limit')
    material = json.dumps([identity, items, page_size, allow_snippets], ensure_ascii=False, default=str)
    resource_id = hashlib.sha256(material.encode('utf-8', errors='replace')).hexdigest()
    payload = dict(version=1, kind=kind, items=items, page_size=page_size,
                   resource_id=resource_id, allow_snippets=allow_snippets,
                   instance_key='scapp_result_list_v2:' + kind + ':' + str(key_prefix))
    if kind != 'tdk_results' and len(json.dumps(payload).encode('utf-8')) > MAX_PAYLOAD_BYTES:
        raise ResultListUnsupported('payload_limit')
    return payload


def prepare_dt_results(all_hits, q1, q2, search_mode, page_size, identity):
    if len(all_hits) > MAX_ITEMS:
        raise ResultListUnsupported('item_limit')
    if any(len(str(value or '')) > 4096 for value in (q1, q2)):
        raise ResultListUnsupported('keyword_limit')
    items, size = [], 0
    for item in all_hits:
        hit = item['hit']
        title, snippet = str(hit['title']), str(hit.get('snippet', '') or '')
        size += len((title + snippet).encode('utf-8', errors='replace'))
        if size > MAX_TEXT_BYTES:
            raise ResultListUnsupported('text_limit')
        body = highlight_keywords(snippet, [(q1, '#ffcf33'), (q2, '#00ffcc')]) if search_mode == 'Nội dung' and snippet else ''
        stats = f"x{item['count']}" + (f" + {item.get('count_q2', 0)}" if q2 else '')
        items.append(dict(title=title, body=body, stats=stats))
    # Paths remain Python-owned; include their digest input to reject stale events
    # when records with identical visible fields refer to different resources.
    owner = [identity, q1, q2, search_mode, [item['hit'].get('path') for item in all_hits]]
    return _payload('dt_results', items, owner, page_size, allow_snippets=search_mode == 'Nội dung')


def prepare_tdk_results(results, identity, page_size=200):
    """Hard v2 contract: visible fields only; ordinary large/Markdown is supported."""
    items = []
    for row in results:
        if not isinstance(row, (tuple, list)) or len(row) != 3:
            raise ResultListUnsupported('TDK v2 requires (source, highlighted_keyword, highlighted_meaning)')
        source, keyword, meaning = row
        items.append(dict(source=str(source), keyword=str(keyword), meaning=str(meaning)))
    return _payload('tdk_results', items, identity, page_size)


def validate_dt_selection(event, payload, all_hits):
    """Reject stale/malformed browser events; never trust a browser path/title."""
    if not isinstance(event, dict) or event.get('resource_id') != payload['resource_id']:
        return None
    index, mode = event.get('index'), event.get('mode')
    if type(index) is not int or not 0 <= index < len(all_hits):
        return None
    if mode not in ({'full', 'snippets'} if payload['allow_snippets'] else {'full'}):
        return None
    return all_hits[index]['hit'], mode


_HTML = '<section class="result-list-v2" data-result-list-v2></section>'
_CSS = r"""
.result-list-v2 {width:100%;color:inherit;font:inherit;box-sizing:border-box;}
.result-list-v2 h5 {font:inherit;font-size:1.125rem;font-weight:600;margin:0 0 1rem;}
.result-list-v2 p {margin:0 0 1rem;}
.result-list-v2 hr {margin:.5rem 0;opacity:.65;}
.result-list-v2 [data-result-snippet] {font-size:.90rem;color:#555555;border-left:2px solid #555;padding-left:10px;margin-bottom:10px;overflow-wrap:anywhere;}
.result-list-v2 mark {color:black;padding:0 2px;border-radius:2px;}
.result-list-v2 [data-result-actions] {display:flex;justify-content:space-between;gap:1rem;}
.result-list-v2 [data-result-actions] button:only-child {width:100%;}
.result-list-v2 nav {display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;margin:1rem 0;}
.result-list-v2 button {font:inherit;color:inherit;background:transparent;border:1px solid #9996;border-radius:.4rem;padding:.3rem .6rem;cursor:pointer;}
.result-list-v2 button[aria-current="page"] {background:#f0f2f6;border-color:#777;}
.result-list-v2 button:disabled {opacity:.45;cursor:default;}
.result-list-v2 button:focus-visible {outline:2px solid #1678cb;outline-offset:2px;}
.result-list-v2 [data-icon] {font-family:'Material Symbols Rounded';vertical-align:middle;}
.result-list-v2 [data-tdk-body] {overflow-wrap:anywhere;}
"""
_vendor = (Path(__file__).parent / 'v2_assets' / 'sc_v2_assets' / 'marked-17.0.5.umd.js').read_text(encoding='utf-8')
_PARSER = 'const tdkMarkdown = (() => { const exports = {}; const module = {exports};\n' + _vendor + '\nreturn module.exports.marked; })();\n'
_JS = _PARSER + SAFE_HTML_JS + DT_READER_JS + r"""
const RESULT_PAGES = Symbol.for('scapp.result-list-v2.pages');
function resultPages() { if (!window[RESULT_PAGES]) window[RESULT_PAGES] = new Map(); return window[RESULT_PAGES]; }
function resultIcon(name) {
  const span = document.createElement('span'); span.setAttribute('data-icon', ''); span.setAttribute('aria-hidden', 'true'); span.textContent = name; return span;
}
function drawResults(root, scroll) {
  const state = root.__results, data = state.data;
  const count = Math.max(1, Math.ceil(data.items.length/data.page_size));
  state.page = clampPage(state.page, count);
  resultPages().set(data.instance_key, {resource_id:data.resource_id, page:state.page});
  const fragment = document.createDocumentFragment();
  const start = (state.page-1)*data.page_size;
  for (let i = start; i < Math.min(start + data.page_size, data.items.length); i++) {
    const item = data.items[i], card = document.createElement('article');
    if (data.kind === 'dt_results') {
      const title = document.createElement('h5'); title.textContent = `${i+1}. ${item.title}`; card.appendChild(title);
      if (item.body) {
        const snippet = document.createElement('div'); snippet.setAttribute('data-result-snippet', '');
        snippet.innerHTML = '... ' + sanitizeHtml(item.body) + ' ...'; card.appendChild(snippet);
      }
      const stats = document.createElement('p'); stats.appendChild(resultIcon('equalizer'));
      stats.appendChild(document.createTextNode(' ' + item.stats)); card.appendChild(stats);
      const actions = document.createElement('div'); actions.setAttribute('data-result-actions', '');
      for (const mode of (data.allow_snippets ? ['full','snippets'] : ['full'])) {
        const button = document.createElement('button'); button.type = 'button';
        button.dataset.index = String(i); button.dataset.mode = mode;
        button.appendChild(resultIcon(mode === 'full' ? 'book' : 'list_alt_add'));
        button.appendChild(document.createTextNode(mode === 'full' ? ' Toàn văn' : ' Xem thêm'));
        actions.appendChild(button);
      }
      card.appendChild(actions);
    } else {
      card.setAttribute('data-tdk-body', '');
      const header = document.createElement('strong'); header.innerHTML = sanitizeHtml(item.keyword);
      const source = document.createElement('code'); source.textContent = '[' + item.source + ']';
      const meaning = document.createElement('div'); meaning.innerHTML = sanitizeHtml(tdkMarkdown.parse(item.meaning, {breaks:true}));
      [header, document.createTextNode(' '), source, document.createTextNode(': '), meaning].forEach(child => card.appendChild(child));
    }
    card.appendChild(document.createElement('hr')); fragment.appendChild(card);
  }
  root.querySelector('[data-result-items]').replaceChildren(fragment);
  renderPager(root.querySelector('nav'), state.page, count);
  if (scroll) requestAnimationFrame(() => scrollReaderTop(root));
}
export default function(component) {
  const {data, parentElement, setTriggerValue} = component;
  const root = parentElement.querySelector('[data-result-list-v2]');
  if (!root || data?.version !== 1) return;
  const previous = root.__results;
  if (!previous) {
    const count = document.createElement('p'); count.setAttribute('data-result-count','');
    const items = document.createElement('div'); items.setAttribute('data-result-items','');
    const nav = document.createElement('nav'); nav.setAttribute('aria-label', 'Phân trang kết quả');
    root.replaceChildren(count, items, nav);
    root.addEventListener('click', event => {
      const target = event.target instanceof Element ? event.target.closest('button') : null;
      if (!target || !root.contains(target) || target.disabled) return;
      const state = root.__results;
      if (target.dataset.page !== undefined) {
        const page = clampPage(Number(target.dataset.page), Math.max(1,Math.ceil(state.data.items.length/state.data.page_size)));
        if (page === state.page) return;
        const label = target.getAttribute('aria-label'); state.page = page; drawResults(root, true);
        const controls = Array.from(root.querySelector('nav').querySelectorAll('button'));
        (controls.find(b => !b.disabled && b.getAttribute('aria-label') === label)
          || controls.find(b => b.getAttribute('aria-current') === 'page'))?.focus({preventScroll:true});
      } else if (state.data.kind === 'dt_results' && target.dataset.mode) {
        state.sendSelection('selection', {resource_id:state.data.resource_id, index:Number(target.dataset.index), mode:target.dataset.mode});
      }
    });
  }
  const same = previous?.data.resource_id === data.resource_id;
  const remembered = resultPages().get(data.instance_key);
  root.__results = {data, page:same ? previous.page : remembered?.resource_id === data.resource_id ? remembered.page : 1, sendSelection:setTriggerValue};
  const count = root.querySelector('[data-result-count]'); count.hidden = data.kind === 'tdk_results';
  count.textContent = data.items.length ? `Tìm thấy ${data.items.length} bài.` : 'Không tìm thấy kết quả nào phù hợp.';
  if (!same) drawResults(root, Boolean(previous));
}
"""


def _mount(payload, *, on_selection_change=None):
    renderer = get_v2_component('scapp_result_list_v2', _HTML, _CSS, _JS)
    callbacks = {'on_selection_change': on_selection_change or (lambda: None)} if payload['kind'] == 'dt_results' else {}
    result = renderer(data=payload, key=payload['instance_key'], **callbacks)
    record_v2_mount(payload['kind'], payload, items=len(payload['items']))
    return result


def try_dt_results(all_hits, q1, q2, search_mode, page_size, identity, *, on_select=None):
    if not v2_enabled('dt_results'):
        record_v2_route('dt_results', 'legacy_disabled')
        return False, None
    try:
        data = prepare_dt_results(all_hits, q1, q2, search_mode, page_size, identity)
        def receive_selection():
            current = st.session_state.get(data['instance_key'], {})
            event = current.get('selection') if isinstance(current, dict) else None
            selection = validate_dt_selection(event, data, all_hits)
            if selection is not None:
                on_select(*selection)

        result = _mount(data, on_selection_change=receive_selection if on_select is not None else None)
        if on_select is not None:
            return True, None
        return True, validate_dt_selection(result.get('selection'), data, all_hits)
    except ResultListUnsupported as exc:
        record_v2_route('dt_results', 'legacy_' + str(exc))
    except Exception:
        record_v2_route('dt_results', 'legacy_setup_error')
        if v2_strict('dt_results'):
            raise
    return False, None


def try_tdk_results(results, identity, page_size=200):
    if not v2_enabled('tdk_results'):
        record_v2_route('tdk_results', 'legacy_disabled')
        return False
    # An explicitly selected v2 mode never changes renderer after inspecting data.
    _mount(prepare_tdk_results(results, identity, page_size))
    return True
