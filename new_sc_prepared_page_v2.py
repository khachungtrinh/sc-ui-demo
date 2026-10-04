"""SC prepared-page presentation. Cache/search/fetch remain owned by callers.

A compact display tree records the same current-page UI operations for v2 or
legacy replay. No corpus/query/cache/backend work lives here; only immutable
component assets are read from local files.
"""
import hashlib
import json
import re
from pathlib import Path

from new_component_v2_support import get_v2_component, SAFE_HTML_JS
from new_components_v2_config import v2_enabled, v2_strict, record_v2_route, record_v2_mount
from new_dt_v2_reader import DT_READER_JS

MAX_PAYLOAD_BYTES = 16 * 1024 * 1024
MAX_NODES = 30000
_ASSETS = Path(__file__).parent / 'v2_assets' / 'sc_v2_assets'
_ISOLATED_HTML = re.compile(r'<\s*(?:script|style|iframe|object|embed|audio|video|source|img|svg|math)\b', re.I)


def _digest(value):
    def canonical_default(item):
        # Offline groups contain seen_segs sets. Cache deserialization can change
        # their iteration order without changing the canonical search resource.
        if isinstance(item, (set, frozenset)):
            return sorted(item, key=lambda x: json.dumps(x, sort_keys=True, default=str))
        return str(item)
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=canonical_default).encode('utf-8')).hexdigest()


def page_context(feature, identity, revision):
    return dict(mode=feature, resource_id=_digest([feature, identity]), revision=_digest(revision))


def _key(feature):
    return 'scapp_prepared_page_v2:' + feature


def _meta_key(feature):
    return _key(feature) + ':view'


def validate_page_request(event, context, previous, total_pages):
    """Validate the current server context AND last displayed page generation."""
    if not isinstance(event, dict) or not isinstance(previous, dict):
        return None
    for field in ('resource_id', 'revision', 'mode'):
        if event.get(field) != context[field] or previous.get(field) != context[field]:
            return None
    page = event.get('page')
    if type(page) is not int or not 1 <= page <= total_pages or page == previous.get('page'):
        return None
    if not isinstance(event.get('view_id'), str) or len(event['view_id']) != 64 or event.get('view_id') != previous.get('view_id') or type(event.get('from_page')) is not int or event['from_page'] != previous.get('page'):
        return None
    return page


def consume_page_request(state, context, total_pages, widget_key, scroll_key):
    """Called before slicing/fetching. Streamlit exposes trigger state by key.

    An accepted event retires the displayed generation immediately. Replayed or
    delayed events cannot cause an extra fetch even before the next mount.
    """
    feature = context['mode']
    if not v2_enabled(feature):
        return None
    value = state.get(_key(feature), {})
    event = value.get('page_request') if isinstance(value, dict) else None
    previous = state.get(_meta_key(feature))
    if (isinstance(previous, dict) and all(previous.get(k) == context[k] for k in context)
            and widget_key not in state and type(previous.get('page')) is int
            and 1 <= previous['page'] <= total_pages):
        state[widget_key] = previous['page']
    page = validate_page_request(event, context, previous, total_pages)
    if page is not None:
        state[widget_key] = page
        state[scroll_key] = state.get(scroll_key, 0) + 1
        state[_meta_key(feature)] = {**previous, 'view_id': None}
    return page


class _Group:
    def __init__(self, surface, children):
        self.surface, self.children = surface, children
    def __enter__(self):
        self.surface._stack.append(self.children)
        return self.surface
    def __exit__(self, *args):
        self.surface._stack.pop()
    def link_button(self, *args, **kwargs):
        with self:
            self.surface.link_button(*args, **kwargs)


class PreparedPage:
    """Only the display operations actually used by the two SC page renderers."""
    def __init__(self):
        self.nodes = []
        self._stack = [self.nodes]
        self.count = 0
    def _add(self, kind, **fields):
        node = dict(kind=kind, **fields)
        self._stack[-1].append(node)
        self.count += 1
        return node
    def markdown(self, body, **kwargs):
        self._add('markdown', text=str(body), kwargs=kwargs)
    def caption(self, body, **kwargs):
        self._add('caption', text=str(body), kwargs=kwargs)
    def info(self, body, **kwargs):
        self._add('info', text=str(body), kwargs=kwargs)
    def code(self, body, **kwargs):
        self._add('code', text=str(body), kwargs=kwargs)
    def columns(self, spec, **kwargs):
        widths = [1] * spec if isinstance(spec, int) else list(spec)
        children = [[] for _ in widths]
        self._add('columns', widths=widths, children=children, kwargs=kwargs)
        return [_Group(self, child) for child in children]
    def container(self, **kwargs):
        children = []
        self._add('container', children=children, kwargs=kwargs)
        return _Group(self, children)
    def link_button(self, label, url, **kwargs):
        self._add('link', label=str(label), url=str(url), kwargs=kwargs)
    def replay(self, ui):
        """Fallback uses prepared operations: no second cache/query invocation."""
        def visit(nodes):
            for node in nodes:
                kind, kw = node['kind'], node.get('kwargs', {})
                if kind == 'columns':
                    for col, child in zip(ui.columns(node['widths'], **kw), node['children']):
                        with col:
                            visit(child)
                elif kind == 'container':
                    with ui.container(**kw):
                        visit(node['children'])
                elif kind == 'link':
                    ui.link_button(node['label'], node['url'], **kw)
                else:
                    getattr(ui, kind)(node['text'], **kw)
        visit(self.nodes)


def new_page_surface(feature):
    if v2_enabled(feature):
        return PreparedPage()
    record_v2_route(feature, 'legacy_disabled')
    return None


def prepare_page_payload(surface, context, page, total_pages, previous=None):
    if surface.count > MAX_NODES:
        raise ValueError('item_limit')
    if type(page) is not int or type(total_pages) is not int or not 1 <= page <= max(1, total_pages):
        raise ValueError('page_limit')
    def check_shape(nodes):
        for node in nodes:
            if node['kind'] == 'columns':
                for children in node['children']:
                    check_shape(children)
            elif node['kind'] == 'container':
                check_shape(node['children'])
            elif node['kind'] in {'markdown', 'caption', 'info'}:
                # Do not silently strip a source-specific runtime/media surface
                # into a degraded v2 page. Replay the already-prepared legacy UI.
                body = node['text']
                if ((node.get('kwargs', {}).get('unsafe_allow_html') and _ISOLATED_HTML.search(body))
                        or re.search(r'!\[[^\]\n]*\]\s*[\[(]', body)):
                    raise ValueError('unsupported_shape')
    check_shape(surface.nodes)
    body_id = _digest([surface.nodes, bool(getattr(surface, 'dictionary_overlay', False))])
    previous = previous or {}
    same_view = (all(previous.get(k) == context[k] for k in context)
                 and previous.get('page') == page and previous.get('body_id') == body_id
                 and previous.get('view_id') is not None)
    generation = previous.get('generation', 0) + (0 if same_view else 1)
    view_id = previous['view_id'] if same_view else _digest([context, page, body_id, generation])
    data = dict(version=1, **context, page=page, total_pages=max(1, total_pages),
                view_id=view_id, nodes=surface.nodes)
    if len(json.dumps(data).encode('utf-8')) > MAX_PAYLOAD_BYTES:
        raise ValueError('payload_limit')
    meta = dict(**context, page=page, view_id=view_id, body_id=body_id, generation=generation)
    return data, meta


def _definition():
    # Vendored, pinned parser; no runtime CDN/import/fetch or frontend build step.
    vendor = (_ASSETS / 'marked-17.0.5.umd.js').read_text(encoding='utf-8')
    parser = 'const scMarkdown = (() => { const exports = {}; const module = {exports};\n' + vendor + '\nreturn module.exports.marked; })();\n'
    from new_dictionary_view_v2 import ASSETS as DICT_ASSETS, CSS as DICT_CSS
    dictionary_js = (DICT_ASSETS / 'dictionary.js').read_text(encoding='utf-8').split('export default function(component)')[0]
    from dict_lookup_popup_assets import ENGLISH_POPUP_JS
    js = parser + SAFE_HTML_JS + DT_READER_JS + ENGLISH_POPUP_JS + dictionary_js + (_ASSETS / 'prepared_page.js').read_text(encoding='utf-8')
    return get_v2_component('scapp_prepared_page_v2', '<section class="sc-prepared-page" data-sc-page></section>',
                            (_ASSETS / 'prepared_page.css').read_text(encoding='utf-8') + DICT_CSS, js)


def mount_prepared_page(surface, context, page, total_pages, state):
    feature = context['mode']
    try:
        payload, meta = prepare_page_payload(surface, context, page, total_pages, state.get(_meta_key(feature)))
        _definition()(data=payload, key=_key(feature), on_page_request_change=lambda: None)
    except ValueError as exc:
        if feature == "sc_offline_dictionary":
            raise
        reason = str(exc) if str(exc) in {'item_limit', 'page_limit', 'payload_limit', 'unsupported_shape'} else 'setup_error'
        record_v2_route(feature, 'legacy_' + reason)
        if reason == 'setup_error' and v2_strict(feature):
            raise
        return False
    except Exception:
        if feature == "sc_offline_dictionary":
            raise
        record_v2_route(feature, 'legacy_setup_error')
        if v2_strict(feature):
            raise
        return False
    state[_meta_key(feature)] = meta
    record_v2_mount(feature, payload, items=surface.count, pages=total_pages)
    return True
