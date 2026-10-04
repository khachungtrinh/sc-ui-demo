"""Components v2 for prepared English text/table data with Anh-Việt overlay.

Used by DPD detailed summary/root/compound/set renderers.  Python preserves the
existing formatting and English query preparation; browser owns local hover,
active word, popup/sidebar display and cleanup.
"""
from __future__ import annotations

import hashlib
import json

from new_component_v2_support import SAFE_HTML_JS, get_v2_component
from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route
from new_dictionary_surface_v2 import dictionary_surface_event_js, make_dictionary_surface_channel, render_dictionary_sidebar_surface

FEATURE = "english_data_reader"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PAYLOAD_BYTES = 24 * 1024 * 1024


class EnglishDataReaderUnsupported(ValueError):
    pass


def prepare_english_data_payload(*, body_html: str, css: str, en_lookup: dict[str, object], mode: str,
                                 table_lookup_policy: str = "auto", height: int | None = None,
                                 scrolling: bool = True, dict_pos_sidebar: bool = False,
                                 sidebar_channel: str = "") -> dict:
    mode = str(mode or "").strip().lower()
    if mode not in {"text", "table"}:
        raise EnglishDataReaderUnsupported("unsupported_shape")
    policy = str(table_lookup_policy or "auto").strip().lower()
    if policy not in {"auto", "meaning_only", "all_td", "none"}:
        raise EnglishDataReaderUnsupported("unsupported_shape")
    body_html = str(body_html or "")
    if len(body_html.encode("utf-8", errors="replace")) > MAX_SOURCE_BYTES:
        raise EnglishDataReaderUnsupported("source_text_limit")
    data = {
        "version": 1,
        "body_html": body_html,
        "css": str(css or ""),
        "en_lookup": dict(en_lookup or {}),
        "mode": mode,
        "table_lookup_policy": policy,
        "height": int(height) if isinstance(height, int) and height > 0 else 0,
        "scrolling": bool(scrolling),
        "dict_pos_sidebar": bool(dict_pos_sidebar),
        "sidebar_channel": str(sidebar_channel or ""),
    }
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise EnglishDataReaderUnsupported("payload_limit")
    data["resource_id"] = hashlib.sha256(raw).hexdigest()
    return data


_HTML = '<section class="english-data-reader-v2" data-english-data-reader-v2></section>'
_CSS = r'''
.english-data-reader-v2 {width:100%;box-sizing:border-box;position:relative;color:#3d3a2a;}
.english-data-reader-v2 .eng-word {cursor:pointer;transition:.15s;color:inherit;background:transparent;border:none;border-bottom:1px solid transparent;padding:0;border-radius:0;font-weight:inherit;}
.english-data-reader-v2 .eng-word:hover,.english-data-reader-v2 .eng-word.active-en {color:#5d7367;border-bottom-color:#5d7367;}
.english-data-reader-v2 .english-data-popup {position:fixed;z-index:999999;display:none;width:min(510px,calc(100vw - 24px));max-height:72vh;overflow:auto;background:var(--eng-popup-bg,#f4f3ec);border:1px solid var(--eng-border,#d3d2ca);box-shadow:0 4px 18px rgba(0,0,0,.22);padding:12px;box-sizing:border-box;color:var(--eng-reader-text,#3d3a2a);font-family:var(--eng-reader-font,inherit);line-height:var(--eng-reader-line-height,1.6);}
.english-data-reader-v2 .english-data-popup.visible {display:block;}
'''

_JS = SAFE_HTML_JS + dictionary_surface_event_js() + r'''
function edEscape(text){const d=document.createElement('div');d.textContent=String(text||'');return d.innerHTML;}
function edClear(root){root.querySelectorAll('.eng-word.active-en').forEach(el=>el.classList.remove('active-en'));}
function edPopup(root){let p=root.querySelector('[data-ed-popup]');if(!p){p=document.createElement('div');p.className='english-data-popup';p.dataset.edPopup='1';root.appendChild(p);}return p;}
function edHide(root){const p=root.querySelector('[data-ed-popup]');if(p){p.classList.remove('visible');p.innerHTML='';}root.__edAnchor=null;}
function edPos(root,anchor){const p=root.querySelector('[data-ed-popup]');if(!p||!p.classList.contains('visible')||!anchor)return;const M=12,G=8,vw=document.documentElement.clientWidth||window.innerWidth,vh=document.documentElement.clientHeight||window.innerHeight;p.style.left='0px';p.style.top='0px';const ar=anchor.getBoundingClientRect(),pr=p.getBoundingClientRect(),pw=Math.min(pr.width,Math.max(0,vw-M*2)),ph=Math.min(pr.height,Math.max(0,vh-M*2));const below=vh-ar.bottom-G-M,above=ar.top-G-M,down=ph<=below?true:ph<=above?false:below>=above;const clamp=(v,min,max)=>max<min?min:Math.min(Math.max(v,min),max);p.style.left=Math.round(clamp(ar.left,M,vw-M-pw))+'px';p.style.top=Math.round(clamp(down?ar.bottom+G:ar.top-G-ph,M,vh-M-ph))+'px';}
function edContent(word,meaning,header){const body=meaning?sanitizeHtml(String(meaning)):"<div style='color:#5d7367;margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";return header?`<div style="font-size:1.2rem;color:#5d7367;font-weight:600;border-bottom:2px solid #d3d2ca;margin-bottom:10px;padding-bottom:5px;"><span style="font-size:.65rem;background:#5d7367;color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">En</span>${edEscape(word)}</div>${body}`:body;}
function edShow(root,target){const state=root.__edState||{};const word=String(target.getAttribute('data-word')||target.textContent||'').trim().toLowerCase();if(!word)return;edClear(root);target.classList.add('active-en');const meaning=state.en_lookup?.[word];if(state.dict_pos_sidebar){edHide(root);emitDictionarySurface(root,edContent(word,meaning,true),false);return;}const p=edPopup(root);p.innerHTML=edContent(word,meaning,false);p.classList.add('visible');root.__edAnchor=target;edPos(root,target);}
function edSkip(state,node){const parent=node.parentElement;if(!parent)return true;if(state.mode==='text')return Boolean(parent.closest('script,style,a,code,pre,table,th,td,.eng-word,.no-en-lookup'));if(parent.closest('script,style,a,code,pre,th,.heading,.eng-word,.no-en-lookup'))return true;const table=parent.closest('table');if(!table)return false;if(state.table_lookup_policy==='none')return true;const td=parent.closest('td');if(!td)return true;if(state.table_lookup_policy==='all_td')return false;if(table.classList.contains('family'))return !td.matches('td:nth-of-type(2)');if(state.table_lookup_policy==='meaning_only')return true;return false;}
function edDecorate(root){const state=root.__edState||{},body=root.querySelector('[data-ed-body]');if(!body)return;const walker=document.createTreeWalker(body,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);for(const node of nodes){if(edSkip(state,node)||!/[A-Za-z]/.test(node.nodeValue||''))continue;const text=node.nodeValue||'',regex=/\b([A-Za-z]+(?:'[A-Za-z]+)?)\b/g;let match,last=0,changed=false;const frag=document.createDocumentFragment();while((match=regex.exec(text))!==null){const word=match[0],clean=word.toLowerCase();if(!state.en_lookup?.[clean])continue;if(match.index>last)frag.appendChild(document.createTextNode(text.slice(last,match.index)));const span=document.createElement('span');span.className='eng-word';span.dataset.word=clean;span.textContent=word;frag.appendChild(span);last=match.index+word.length;changed=true;}if(changed){if(last<text.length)frag.appendChild(document.createTextNode(text.slice(last)));node.replaceWith(frag);}}}
export default function(component){const {data,parentElement}=component;const root=parentElement.querySelector('[data-english-data-reader-v2]');if(!root||data?.version!==1)return;const prev=root.__edState,same=prev?.resource_id===data.resource_id,oldScroll=root.scrollTop||0;root.__edState=data;root.__dictState=data;if(data.height){root.style.height=`${Number(data.height)}px`;root.style.overflowY=data.scrolling?'auto':'visible';}else{root.style.height='';root.style.overflowY='visible';}if(!same){const style=document.createElement('style');style.textContent=data.css||'';const body=document.createElement('div');body.dataset.edBody='1';body.innerHTML=sanitizeHtml(data.body_html||'');root.replaceChildren(style,body);edDecorate(root);root.scrollTop=0;}else root.scrollTop=oldScroll;if(!root.__edListeners){let timer=null;const cancel=()=>{if(timer!==null){clearTimeout(timer);timer=null;}};const schedule=()=>{cancel();timer=setTimeout(()=>edHide(root),140);};root.addEventListener('mouseover',event=>{const t=event.target instanceof Element?event.target.closest('.eng-word'):null;if(!t||!root.contains(t)||(event.relatedTarget instanceof Node&&t.contains(event.relatedTarget)))return;cancel();edShow(root,t);});root.addEventListener('mouseout',event=>{const t=event.target instanceof Element?event.target:null;if(t?.closest('.eng-word,[data-ed-popup]'))schedule();});root.addEventListener('click',event=>{const t=event.target instanceof Element?event.target:null;if(!t)return;const en=t.closest('.eng-word');if(en&&root.contains(en)){event.stopPropagation();cancel();edShow(root,en);return;}if(!t.closest('[data-ed-popup]'))edHide(root);});root.addEventListener('scroll',()=>{if(root.__edAnchor)edPos(root,root.__edAnchor);},true);root.__edListeners=true;}}
'''


def try_render_english_data_reader_v2(*, body_html: str, css: str, en_lookup: dict[str, object], mode: str,
                                      table_lookup_policy: str = "auto", height: int | None = None,
                                      scrolling: bool = True, dict_pos_sidebar: bool = False,
                                      sidebar_placeholder: str = "Chạm từ Anh để tra cứu...",
                                      key_suffix: str = "main") -> bool:
    if not v2_enabled(FEATURE):
        record_v2_route(FEATURE, "legacy_disabled")
        return False
    try:
        data = prepare_english_data_payload(
            body_html=body_html, css=css, en_lookup=en_lookup, mode=mode,
            table_lookup_policy=table_lookup_policy, height=height, scrolling=scrolling,
            dict_pos_sidebar=dict_pos_sidebar,
        )
        if dict_pos_sidebar:
            channel = make_dictionary_surface_channel(FEATURE, data["resource_id"], mode)
            data["sidebar_channel"] = channel
            render_dictionary_sidebar_surface(
                FEATURE, channel=channel, resource_id=data["resource_id"],
                placeholder=sidebar_placeholder, profile="english", key_suffix=f"{mode}:{key_suffix}",
            )
        renderer = get_v2_component("scapp_english_data_reader_v2", _HTML, _CSS, _JS)
        renderer(data=data, key=f"scapp_english_data_reader_v2:{mode}:{key_suffix}")
    except EnglishDataReaderUnsupported as exc:
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
