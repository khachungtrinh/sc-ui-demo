"""Components v2 renderer for prepared standalone dictionary entry results.

This is the remaining non-media dictionary display boundary.  Python keeps the
canonical query/formatting code; the component owns only the prepared result
surface, optional English hover/click overlay, and browser-local popup/sidebar
state.  No browser API fetch is introduced.
"""
from __future__ import annotations

import hashlib
import json

from new_component_v2_support import SAFE_HTML_JS, get_v2_component
from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route
from new_dictionary_surface_v2 import (
    dictionary_surface_event_js,
    make_dictionary_surface_channel,
    render_dictionary_sidebar_surface,
)
from new_reader_v2_primitives import reader_css_for_host

FEATURE = "dictionary_entry_results"
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_PAYLOAD_BYTES = 12 * 1024 * 1024


class DictionaryEntryUnsupported(ValueError):
    pass


def prepare_dictionary_entry_payload(
    *,
    kind: str,
    body_html: str,
    css: str = "",
    en_lookup: dict[str, object] | None = None,
    english_mode: str = "none",
    height: int | None = None,
    sidebar_channel: str = "",
) -> dict:
    kind = str(kind or "").strip().lower()
    if kind not in {"dpd", "pts", "buddhist", "english", "pali_viet", "proper_names", "viet_pali"}:
        raise DictionaryEntryUnsupported("unsupported_shape")
    english_mode = str(english_mode or "none").strip().lower()
    if english_mode not in {"none", "popup", "sidebar"}:
        raise DictionaryEntryUnsupported("unsupported_shape")
    body_html = str(body_html or "")
    if len(body_html.encode("utf-8", errors="replace")) > MAX_SOURCE_BYTES:
        raise DictionaryEntryUnsupported("source_text_limit")
    data = {
        "version": 1,
        "kind": kind,
        "body_html": body_html,
        "css": reader_css_for_host(str(css or "")),
        "en_lookup": dict(en_lookup or {}),
        "english_mode": english_mode,
        "height": int(height) if isinstance(height, int) and height > 0 else 0,
        "sidebar_channel": str(sidebar_channel or ""),
    }
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise DictionaryEntryUnsupported("payload_limit")
    data["resource_id"] = hashlib.sha256(raw).hexdigest()
    return data


_HTML = '<section class="panel-reader-v2 dictionary-entry-v2" data-dictionary-entry-v2></section>'
_CSS = r'''
.dictionary-entry-v2 {width:100%;box-sizing:border-box;position:relative;overflow:auto;}
.dictionary-entry-v2 .dictionary-entry-en {cursor:pointer;border-bottom:1px dashed transparent;transition:.15s;}
.dictionary-entry-v2 .dictionary-entry-en:hover,.dictionary-entry-v2 .dictionary-entry-en.active-en {color:#5d7367;border-bottom-color:#5d7367;}
.dictionary-entry-v2 .dictionary-entry-popup {position:fixed;z-index:999999;display:none;width:min(510px,calc(100vw - 24px));max-height:calc(100vh - 24px);overflow:auto;background:var(--dl-popup-bg,var(--dl-bg,#ecebe3));border:1px solid var(--dl-border,#d3d2ca);box-shadow:0 4px 18px rgba(0,0,0,.22);padding:12px;box-sizing:border-box;color:var(--dl-text,#3d3a2a);font-family:var(--dl-font-ui,inherit);line-height:1.6;}
.dictionary-entry-v2 .dictionary-entry-popup.visible {display:block;}
'''

_JS = SAFE_HTML_JS + dictionary_surface_event_js() + r'''
function entryEscape(text){const d=document.createElement('div');d.textContent=String(text||'');return d.innerHTML;}
function deWord(raw){return String(raw||'').trim().toLowerCase();}
function clearEntryEnglish(root){root.querySelectorAll('.dictionary-entry-en.active-en').forEach(el=>el.classList.remove('active-en'));}
function entryPopup(root){let p=root.querySelector('[data-entry-popup]');if(!p){p=document.createElement('div');p.className='dictionary-entry-popup';p.dataset.entryPopup='1';root.appendChild(p);}return p;}
function hideEntryPopup(root){const p=root.querySelector('[data-entry-popup]');if(p){p.classList.remove('visible');p.innerHTML='';}root.__entryAnchor=null;}
function positionEntryPopup(root,anchor){const p=root.querySelector('[data-entry-popup]');if(!p||!p.classList.contains('visible')||!anchor)return;const M=12,G=8,vw=document.documentElement.clientWidth||window.innerWidth,vh=document.documentElement.clientHeight||window.innerHeight;p.style.left='0px';p.style.top='0px';const ar=anchor.getBoundingClientRect(),pr=p.getBoundingClientRect(),pw=Math.min(pr.width,Math.max(0,vw-M*2)),ph=Math.min(pr.height,Math.max(0,vh-M*2));const below=vh-ar.bottom-G-M,above=ar.top-G-M,down=ph<=below?true:ph<=above?false:below>=above;const clamp=(v,min,max)=>max<min?min:Math.min(Math.max(v,min),max);p.style.left=Math.round(clamp(ar.left,M,vw-M-pw))+'px';p.style.top=Math.round(clamp(down?ar.bottom+G:ar.top-G-ph,M,vh-M-ph))+'px';}
function entryEnglishContent(word,meaning,withHeader){const body=meaning?sanitizeHtml(String(meaning)):"<div style='color:#5d7367;margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";if(!withHeader)return body;return `<div style="font-size:1.2rem;color:#5d7367;font-weight:600;border-bottom:2px solid #d3d2ca;margin-bottom:10px;padding-bottom:5px;display:flex;align-items:center;"><span style="font-size:.65rem;background:#5d7367;color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">En</span>${entryEscape(word)}</div>${body}`;}
function showEntryEnglish(root,target){const state=root.__entryState||{};const word=deWord(target.getAttribute('data-word')||target.textContent||'');if(!word)return;clearEntryEnglish(root);target.classList.add('active-en');const meaning=state.en_lookup?.[word];if(state.english_mode==='sidebar'){hideEntryPopup(root);emitDictionarySurface(root,entryEnglishContent(word,meaning,true),false);return;}const p=entryPopup(root);p.innerHTML=entryEnglishContent(word,meaning,false);p.classList.add('visible');root.__entryAnchor=target;positionEntryPopup(root,target);}
function entrySkipNode(state,node){const parent=node.parentElement;if(!parent)return true;if(state.kind==='pts'){return Boolean(parent.closest('a,dfn,sup,script,style,.ref,.term,.square,.dictionary-entry-en'));}return Boolean(parent.closest('script,style,.dictionary-entry-en'));}
function decorateEntryEnglish(root){const state=root.__entryState||{};if(state.english_mode==='none'||!state.en_lookup)return;const body=root.querySelector('[data-entry-body]');if(!body)return;const walker=document.createTreeWalker(body,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);for(const node of nodes){if(entrySkipNode(state,node)||!/[A-Za-z]/.test(node.nodeValue||''))continue;const text=node.nodeValue||'';const regex=/\b([A-Za-z]+(?:'[A-Za-z]+)?)\b/g;let match,last=0,changed=false;const frag=document.createDocumentFragment();while((match=regex.exec(text))!==null){const word=match[0],clean=word.toLowerCase();if(!state.en_lookup?.[clean])continue;if(match.index>last)frag.appendChild(document.createTextNode(text.slice(last,match.index)));const span=document.createElement('span');span.className='dictionary-entry-en';span.dataset.word=clean;span.textContent=word;frag.appendChild(span);last=match.index+word.length;changed=true;}if(changed){if(last<text.length)frag.appendChild(document.createTextNode(text.slice(last)));node.replaceWith(frag);}}}
export default function(component){const {data,parentElement}=component;const root=parentElement.querySelector('[data-dictionary-entry-v2]');if(!root||data?.version!==1)return;const previous=root.__entryState;const same=previous?.resource_id===data.resource_id;const oldScroll=root.scrollTop||0;root.__entryState=data;root.__dictState=data;if(data.height){root.style.height=`${Number(data.height)}px`;root.style.overflowY='auto';}else{root.style.height='';root.style.overflowY='visible';}if(!same){const style=document.createElement('style');style.textContent=data.css||'';const body=document.createElement('div');body.dataset.entryBody='1';body.innerHTML=sanitizeHtml(data.body_html||'');root.replaceChildren(style,body);decorateEntryEnglish(root);root.scrollTop=0;}else root.scrollTop=oldScroll;if(!root.__entryListeners){let timer=null;const cancel=()=>{if(timer!==null){clearTimeout(timer);timer=null;}};const schedule=()=>{cancel();timer=setTimeout(()=>hideEntryPopup(root),140);};root.addEventListener('mouseover',event=>{const t=event.target instanceof Element?event.target.closest('.dictionary-entry-en'):null;if(!t||!root.contains(t)||(event.relatedTarget instanceof Node&&t.contains(event.relatedTarget)))return;cancel();showEntryEnglish(root,t);});root.addEventListener('mouseout',event=>{const t=event.target instanceof Element?event.target:null;if(t?.closest('.dictionary-entry-en,[data-entry-popup]'))schedule();});root.addEventListener('click',event=>{const t=event.target instanceof Element?event.target:null;if(!t)return;const en=t.closest('.dictionary-entry-en');if(en&&root.contains(en)){event.stopPropagation();cancel();showEntryEnglish(root,en);return;}if(!t.closest('[data-entry-popup]'))hideEntryPopup(root);});root.addEventListener('scroll',()=>{if(root.__entryAnchor)positionEntryPopup(root,root.__entryAnchor);},true);root.__entryListeners=true;}}
'''


def try_render_dictionary_entry_v2(
    *,
    kind: str,
    body_html: str,
    css: str = "",
    en_lookup: dict[str, object] | None = None,
    english_mode: str = "none",
    height: int | None = None,
    sidebar_placeholder: str = "Chạm từ Anh để tra cứu...",
) -> bool:
    if not v2_enabled(FEATURE):
        record_v2_route(FEATURE, "legacy_disabled")
        return False
    try:
        data = prepare_dictionary_entry_payload(
            kind=kind,
            body_html=body_html,
            css=css,
            en_lookup=en_lookup,
            english_mode=english_mode,
            height=height,
        )
        if data["english_mode"] == "sidebar":
            channel = make_dictionary_surface_channel(FEATURE, data["resource_id"], f"{kind}-english")
            data["sidebar_channel"] = channel
            render_dictionary_sidebar_surface(
                FEATURE,
                channel=channel,
                resource_id=data["resource_id"],
                placeholder=sidebar_placeholder,
                profile="english",
                key_suffix=f"{kind}-english",
            )
        renderer = get_v2_component("scapp_dictionary_entry_v2", _HTML, _CSS, _JS)
        renderer(data=data, key=f"scapp_dictionary_entry_v2:{kind}")
    except DictionaryEntryUnsupported as exc:
        route = {
            "source_text_limit": "legacy_source_text_limit",
            "payload_limit": "legacy_payload_limit",
            "unsupported_shape": "legacy_unsupported_shape",
        }.get(str(exc), "legacy_unsupported_shape")
        record_v2_route(FEATURE, route)
        return False
    except Exception:
        record_v2_route(FEATURE, "legacy_setup_error")
        if v2_strict(FEATURE):
            raise
        return False
    record_v2_mount(FEATURE, data, text_bytes=len(str(body_html).encode("utf-8", errors="replace")))
    return True
