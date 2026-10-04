# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Prepared dictionary surface shared by canonical JS and existing API readers."""


import hashlib


from html.parser import HTMLParser


import inspect


import json


from pathlib import Path


import re


from new_component_v2_support import SAFE_HTML_JS, get_v2_component


from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route


from new_reader_v2_primitives import KEYWORD_JS, KEYWORD_CSS, reader_css_for_host


from new_dictionary_surface_style import english_dictionary_surface_css


from new_component_v2_theme import native_dictionary_theme_css


ASSETS = Path(__file__).parent / 'v2_assets' / 'r14_assets'


_vendor = (Path(__file__).parent / 'v2_assets' / 'sc_v2_assets' / 'marked-17.0.5.umd.js').read_text(encoding='utf-8')


_PARSER = 'const dictionaryMarkdown = (() => { const exports = {}; const module = {exports};\n' + _vendor + '\nreturn module.exports.marked; })();\n'


from dict_lookup_popup_assets import ENGLISH_POPUP_JS


JS = _PARSER + SAFE_HTML_JS + KEYWORD_JS + ENGLISH_POPUP_JS + (ASSETS / 'dictionary.js').read_text(encoding='utf-8')


CSS = '''
[data-dictionary-root]{color:var(--dl-text,#3d3a2a);font-family:var(--dl-font-reader,"Source Sans Pro",sans-serif);font-size:var(--dl-reader-font-size,1rem);line-height:var(--dl-reader-line-height,1.6);}
.dict-layout{height:100%;display:flex;gap:12px;min-width:0}.dict-content{flex:1;min-width:0;overflow:auto}.dict-content table{width:100%;border-collapse:collapse}.dict-content td{padding:8px;vertical-align:top;border:1px solid var(--dl-border,#eaeae3)}
[data-dict-panel]{flex:1;overflow:auto;min-width:0}.dict-left{display:flex;flex-direction:column;flex:0 0 var(--dl-dict-width,300px);max-width:40%;min-width:0;overflow:hidden}.dict-entry{padding:8px;border-bottom:1px solid var(--dl-border,#d3d2ca)}.dict-word,.pali-word,.eng-word,.eng-sub-word{cursor:pointer}.dict-active{background:var(--dl-bg-hover,#ecebe3)}.dict-popup{position:fixed;z-index:999999;padding:12px;overflow:auto;box-sizing:border-box;background:var(--dl-popup-bg,#ecebe3);color:var(--dl-text,#3d3a2a);border:1px solid var(--dl-border,#d3d2ca);box-shadow:0 4px 18px #0003}.dict-popup-pali{font-family:var(--dl-font-reader,"Source Sans","Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif);margin:0;border-radius:var(--dl-radius,3px);font-size:var(--dl-reader-font-size,1rem);line-height:var(--dl-reader-line-height,1.6);font-weight:400;font-style:normal;text-decoration:none;text-align:left;min-width:min(20em,calc(100vw - 24px));max-width:min(550px,calc(100vw - 24px));max-height:calc(100vh - 24px);height:auto;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;pointer-events:auto}.dict-popup-english{max-height:400px}.dict-popup[hidden]{display:none}
*{scrollbar-width:thin;scrollbar-color:#ccc transparent}::-webkit-scrollbar{width:6px}::-webkit-scrollbar-thumb{background:#ccc}
'''


CSS += native_dictionary_theme_css()


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
    def handle_data(self, data):
        self.text.append(data)


def visible_words(body_html):
    parser = _Text(); parser.feed(str(body_html))
    text = ' '.join(parser.text)
    return set(re.findall(r'[^\s,.–—:;?!“‘-]+', text)), set(re.findall(r"[^\W\d_]+(?:[’'][^\W\d_]+)*(?:-[^\W\d_]+)*", text, re.UNICODE))


def prepare_dictionary_view(body_html, *, css='', pali_lookup=None, en_lookup=None,
                            height=850, pali_position='popup', english_position='popup',
                            canonical=False, history=False, hover_popup=True,
                            english_hover_only=False, meaning_english=False,
                            highlight_word='', channel='dictionary', **extra):
    data = dict(version=1, role='content', body_html=body_html,
                css=reader_css_for_host(css) + CSS + KEYWORD_CSS,
                pali_lookup=pali_lookup or {}, en_lookup=en_lookup or {}, height=int(height),
                pali_position=pali_position, english_position=english_position,
                canonical=canonical, history=history, hover_popup=hover_popup,
                english_hover_only=english_hover_only, meaning_english=meaning_english,
                highlight_word=highlight_word, channel=channel, **extra)
    if 'left' in (pali_position, english_position):
        data['css'] += english_dictionary_surface_css('left')
    data['resource_id'] = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return data


def _mount(data, key, legacy=False):
    # All panel callers, including ReadingUI's prepared-resource path, cross
    # this boundary. A caller-specific helper missed the actual Reading sidebar.
    if data.get('role') == 'panel':
        data = {**data, 'css': data['css'] + english_dictionary_surface_css('sidebar')}
    if legacy:
        import streamlit.components.v1 as components
        # Legacy optional sidebar: same-origin BroadcastChannel between the two
        # isolated iframes. Sidebar panel frames start collapsed and expand only
        # after a real dictionary entry arrives.
        if data.get('role') == 'panel':
            data = {**data, 'legacy_panel_frame': True}
        bridge = """const localBus = new EventTarget();
const channel = new BroadcastChannel(DATA.channel);
localBus.addEventListener('scapp-dictionary-r14', e => { if (!e.detail.relayed) channel.postMessage(e.detail); });
channel.addEventListener('message', e => localBus.dispatchEvent(new CustomEvent('scapp-dictionary-r14',{detail:{...e.data,relayed:true}})));
window.addEventListener('pagehide', () => channel.close(), {once:true});"""
        script = JS.replace('export default function(component)', 'function mount(component)').replace('return dictInstall(root,data);', 'return dictInstall(root,data,localBus);')
        raw = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
        initial_height = 0 if data.get('role') == 'panel' else data['height']
        components.html('<section data-dictionary-root></section><script type="module">' + 'const DATA=' + raw + ';' + bridge + script + '\nmount({parentElement:document,data:DATA});</script>', height=initial_height, scrolling=False)
    else:
        get_v2_component('scapp_dictionary_r14', '<section class="panel-reader-v2 container sujato-reader" data-dictionary-root></section>', CSS, JS)(data=data, key=key)


def dictionary_instance_identity(feature, instance_key):
    """Return a stable SCAPP-owned channel/key pair for one logical reader.

    The identity deliberately depends only on application semantics, never on
    Streamlit's private positional delta-path API.  The readable feature prefix
    helps diagnostics while the digest keeps Streamlit element keys compact and
    safe even when callers use long document/query identifiers.
    """
    feature_text = str(feature or 'dictionary').strip() or 'dictionary'
    instance_text = str(instance_key or '').strip()
    if not instance_text:
        raise ValueError('dictionary instance_key must not be empty')
    safe_feature = re.sub(r'[^a-zA-Z0-9_-]+', '_', feature_text).strip('_') or 'dictionary'
    digest = hashlib.sha256((feature_text + '\0' + instance_text).encode('utf-8', errors='ignore')).hexdigest()[:16]
    return f'scapp-dict:{safe_feature}:{digest}', f'scapp_dict_{safe_feature}_{digest}'


def _automatic_instance_key(feature, body_html):
    """Compatibility identity for existing callers without an explicit key.

    A Python call-site plus a content digest is stable across ordinary Streamlit
    reruns and independent of layout position.  Callers with a natural semantic
    identity can pass ``instance_key=...`` directly; DPD v2 does so.
    """
    frame = None
    caller = None
    try:
        frame = inspect.currentframe()
        caller = frame.f_back.f_back if frame and frame.f_back else None
        call_site = (
            f'{Path(caller.f_code.co_filename).name}:{caller.f_lineno}'
            if caller is not None else 'unknown'
        )
    except Exception:
        call_site = 'unknown'
    finally:
        # Avoid keeping frame locals alive through a reference cycle.
        del caller
        del frame
    body_digest = hashlib.sha256(str(body_html).encode('utf-8', errors='ignore')).hexdigest()[:16]
    return f'auto:{feature}:{call_site}:{body_digest}'


def mount_dictionary_view(feature, *, body_html, instance_key, legacy=False, **kwargs):
    import streamlit as st
    if not legacy:
        get_v2_component('scapp_dictionary_r14', '<section class="panel-reader-v2 container sujato-reader" data-dictionary-root></section>', CSS, JS)
    channel, key_base = dictionary_instance_identity(feature, instance_key)
    # ``key`` is Streamlit's public stable-identity mechanism.  The container
    # and component use distinct keys while sharing the same application-owned
    # BroadcastChannel name for content/sidebar communication.
    slot = st.container(key=key_base + '_slot')
    data = prepare_dictionary_view(body_html, channel=channel, **kwargs)
    for lang, position in [('pi',data['pali_position']),('en',data['english_position'])]:
        if position == 'sidebar':
            with st.sidebar:
                panel = {**data,'role':'panel','body_html':'','height':350,'panel_language':lang,
                         'pali_lookup':{}, 'en_lookup':data['en_lookup'] if lang == 'pi' else {}}
                _mount(panel, key_base + '_panel_' + lang, legacy=legacy)
    with slot:
        _mount(data, key_base + '_content', legacy=legacy)
    if not legacy:
        record_v2_mount(feature,data)
    return True

