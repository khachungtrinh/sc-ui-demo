"""Prepared left-panel readers: bilingual Pāli/English and English–Vietnamese.

The legacy functions retain canonical row/glossary/dictionary/CSS preparation.
Only sanitized DOM, active words, local lookup and scroll move to Components v2.
Sidebar, popup and source-dictionary shapes retain their existing renderers.
"""
import hashlib
import json

from new_component_v2_support import get_v2_component, SAFE_HTML_JS
from new_components_v2_config import v2_enabled, v2_strict, record_v2_route, record_v2_mount
from new_reader_v2_primitives import LOOKUP_DOM_JS, KEYWORD_JS, KEYWORD_CSS, reader_css_for_host

MAX_PAYLOAD_BYTES = 24 * 1024 * 1024


class PanelReaderUnsupported(ValueError):
    pass


def prepare_panel_payload(feature, *, body_html, css, en_lookup, height,
                          pali_lookup=None, highlight_word=""):
    if feature not in {"bilingual_reader", "english_reader"}:
        raise PanelReaderUnsupported("unsupported_shape")
    data = dict(version=1, kind=feature, body_html=body_html,
                css=reader_css_for_host(css) + KEYWORD_CSS,
                en_lookup=en_lookup or {}, pali_lookup=pali_lookup or {},
                height=int(height), highlight_word=str(highlight_word or ""))
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True).encode('utf-8')
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise PanelReaderUnsupported("payload_limit")
    data['resource_id'] = hashlib.sha256(raw).hexdigest()
    if len(json.dumps(data).encode('utf-8')) > MAX_PAYLOAD_BYTES:
        raise PanelReaderUnsupported("payload_limit")
    return data


_HTML = '<section class="panel-reader-v2" data-panel-reader-v2></section>'
_CSS = '''
.panel-reader-v2 {width:100%;box-sizing:border-box;}
.panel-reader-v2 > [data-panel-body] {height:100%;}
''' 
_JS = SAFE_HTML_JS + LOOKUP_DOM_JS + KEYWORD_JS + r"""
function clearPanelEnglish(root) {
  root.querySelectorAll('.eng-word.active-en, .eng-sub-word.active-en').forEach(el => el.classList.remove('active-en'));
}
function panelEnglish(root, target) {
  const state = root.__panelState;
  if (!state) return;
  const word = (target.getAttribute('data-word') || target.textContent || '').trim().toLowerCase();
  if (!word) return;
  clearPanelEnglish(root);
  target.classList.add('active-en');
  const meaning = getEnglishMeaning(state.en_lookup, word);
  if (state.kind === 'english_reader') {
    const box = root.querySelector('#eng-dict-target');
    if (box) box.innerHTML = meaning ? sanitizeHtml(meaning)
      : "<div style='color:#5d7367;padding:10px;background:var(--eng-bg-sec);border-radius:4px;'>Không tìm thấy trong từ điển.</div>";
  } else {
    const box = root.querySelector('#en-target');
    if (box) box.innerHTML = `<div style='color:#5d7367;font-weight:bold;border-bottom:1px solid #ccc;margin-bottom:10px;'>EN: ${escapeHtml(word)}</div>`
      + (meaning ? sanitizeHtml(meaning) : 'Không tìm thấy.');
  }
}
function panelPali(root, target) {
  const state = root.__panelState;
  root.querySelectorAll('.pali-word.active').forEach(el => el.classList.remove('active'));
  clearPanelEnglish(root);
  target.classList.add('active');
  const raw = target.getAttribute('data-word') || '';
  // Exact bilingual legacy normalization; no JS search/highlight rewrite.
  const clean = raw.replace(/[^a-zA-Zāīūṅñṭḍṇḷṃṁ]/gi, '').toLowerCase();
  const meaning = state.pali_lookup[clean] || state.pali_lookup[raw];
  const box = root.querySelector('#pali-target');
  if (!box) return;
  box.innerHTML = `<div style='color:#d63031;font-weight:bold;border-bottom:1px solid #ccc;margin-bottom:10px;'>PALI: <a href="/sc?q=${encodeURIComponent(clean)}" target="_blank" rel="noopener noreferrer" style="color:#d63031;text-decoration:underline;">${escapeHtml(clean)}</a></div><div data-panel-meaning></div>`;
  const body = box.querySelector('[data-panel-meaning]');
  body.innerHTML = meaning ? sanitizeHtml(meaning) : 'Không tìm thấy.';
  decorateEnglishWords(body, state.en_lookup, "bilingual");
}
export default function(component) {
  const {data, parentElement} = component;
  const root = parentElement.querySelector('[data-panel-reader-v2]');
  if (!root || data?.version !== 1) return;
  const previous = root.__panelState;
  root.__panelState = data;
  root.style.height = `${data.height}px`;
  if (previous?.resource_id !== data.resource_id) {
    const style = document.createElement('style');
    // CSS is assembled from app-owned canonical helpers, never corpus markup.
    style.textContent = data.css;
    const body = document.createElement('div'); body.setAttribute('data-panel-body', '');
    body.innerHTML = sanitizeHtml(data.body_html);
    root.replaceChildren(style, body);
    if (data.highlight_word) applyReaderKeywordHighlight(root);
  }
  if (!root.__panelListeners) {
    root.addEventListener('click', event => {
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;
      const pali = target.closest('.pali-word');
      if (pali && root.contains(pali)) panelPali(root, pali);
      const en = target.closest('.eng-word, .eng-sub-word');
      if (en && root.contains(en)) {
        if (root.__panelState.kind === "english_reader") event.preventDefault();
        panelEnglish(root, en);
      }
    });
    root.addEventListener('mouseover', event => {
      const en = event.target instanceof Element ? event.target.closest('.eng-word, .eng-sub-word') : null;
      if (!en || !root.contains(en) || (event.relatedTarget instanceof Node && en.contains(event.relatedTarget))) return;
      panelEnglish(root, en);
    });
    root.__panelListeners = true;
  }
}
"""


def try_render_panel_reader(feature, *, supported, **prepared):
    """Return True only after mounting; do not repeat Python lookup on fallback."""
    if not v2_enabled(feature):
        record_v2_route(feature, "legacy_disabled")
        return False
    if not supported:
        record_v2_route(feature, "legacy_unsupported_shape")
        return False
    try:
        data = prepare_panel_payload(feature, **prepared)
        renderer = get_v2_component('scapp_panel_reader_v2', _HTML, _CSS, _JS)
        renderer(data=data, key='scapp_panel_reader_v2:' + feature)
    except PanelReaderUnsupported as exc:
        record_v2_route(feature, 'legacy_' + str(exc))
        return False
    except Exception:
        record_v2_route(feature, 'legacy_setup_error')
        if v2_strict(feature):
            raise
        return False
    record_v2_mount(feature, data)
    return True
