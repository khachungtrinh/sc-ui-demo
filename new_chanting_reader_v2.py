"""Components v2 reader for prepared Pāli chanting/IPA content.

Python keeps the canonical chanting paragraph grouping and IPA/English dictionary
queries.  The component owns only browser-local reading interaction: compact IPA
hover, click-to-sidebar IPA result, English popup inside that sidebar, scrolling,
and optional auto-scroll.  No backend fetch or Python interaction is introduced.
"""
from __future__ import annotations

import hashlib
import json

from new_component_v2_support import SAFE_HTML_JS, get_v2_component
from new_components_v2_config import (
    record_v2_mount,
    record_v2_route,
    v2_enabled,
    v2_strict,
)
from new_dictionary_surface_v2 import (
    dictionary_surface_event_js,
    make_dictionary_surface_channel,
    render_dictionary_sidebar_surface,
)
from new_reader_v2_primitives import LOOKUP_DOM_JS, reader_css_for_host

FEATURE = "chanting_reader"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PAYLOAD_BYTES = 20 * 1024 * 1024
MAX_LOOKUP_ITEMS = 60_000


class ChantingReaderUnsupported(ValueError):
    pass


def prepare_chanting_payload(
    *,
    body_html: str,
    css: str,
    ipa_lookup: dict[str, object] | None,
    ipa_popup_lookup: dict[str, object] | None,
    en_lookup: dict[str, object] | None,
    auto_scroll_speed: float = 0.0,
    height: int | None = None,
    sidebar_channel: str = "",
    dark_mode: bool = False,
) -> dict:
    body_html = str(body_html or "")
    source_bytes = len(body_html.encode("utf-8", errors="replace"))
    if source_bytes > MAX_SOURCE_BYTES:
        raise ChantingReaderUnsupported("source_text_limit")

    ipa_lookup = dict(ipa_lookup or {})
    ipa_popup_lookup = dict(ipa_popup_lookup or {})
    en_lookup = dict(en_lookup or {})
    if len(ipa_lookup) + len(ipa_popup_lookup) + len(en_lookup) > MAX_LOOKUP_ITEMS:
        raise ChantingReaderUnsupported("item_limit")

    try:
        speed = max(0.0, float(auto_scroll_speed or 0.0))
    except (TypeError, ValueError):
        raise ChantingReaderUnsupported("unsupported_shape") from None

    data = {
        "version": 1,
        "body_html": body_html,
        "css": reader_css_for_host(str(css or "")),
        "ipa_lookup": ipa_lookup,
        "ipa_popup_lookup": ipa_popup_lookup,
        "en_lookup": en_lookup,
        "auto_scroll_speed": speed,
        "height": int(height) if isinstance(height, int) and height > 0 else 0,
        "sidebar_channel": str(sidebar_channel or ""),
        "dark_mode": bool(dark_mode),
    }
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise ChantingReaderUnsupported("payload_limit")
    data["resource_id"] = hashlib.sha256(raw).hexdigest()
    return data


_HTML = '<section class="panel-reader-v2 chanting-reader-v2" data-chanting-reader-v2></section>'
_CSS = r'''
.chanting-reader-v2 { width:100%; box-sizing:border-box; position:relative; overflow:hidden; }
.chanting-reader-v2 .chanting-scroll { height:100%; overflow-y:auto; box-sizing:border-box; }
.chanting-reader-v2 .chanting-ipa-popup {
  position:fixed; z-index:999999; display:none; width:min(320px,calc(100vw - 24px));
  max-height:55vh; overflow-y:auto; background:var(--dl-popup-bg,var(--dl-bg,#ecebe3));
  border:1px solid var(--dl-border,#d3d2ca); box-shadow:0 4px 18px rgba(0,0,0,.18);
  padding:10px 12px; box-sizing:border-box; color:var(--dl-text,#3d3a2a); line-height:1.55;
}
.chanting-reader-v2 .chanting-ipa-popup.visible { display:block; }
.chanting-reader-v2[data-dark="1"] .chanting-ipa-popup { background:#1e1e1e; color:#f0f0f0; border-color:#444; box-shadow:0 4px 18px rgba(0,0,0,.55); }
'''

_JS = SAFE_HTML_JS + LOOKUP_DOM_JS + dictionary_surface_event_js() + r'''
function chantingLookup(dict, rawWord, cleanWord) {
  if (!dict) return null;
  return dict[rawWord] || dict[cleanWord] || dict[String(rawWord || '').toLowerCase()] || dict[String(cleanWord || '').toLowerCase()] || null;
}
function chantingClearActive(root) {
  root.querySelectorAll('.chanting-pali-word.active').forEach(el => el.classList.remove('active'));
}
function chantingPopup(root) {
  let popup = root.querySelector('[data-chanting-ipa-popup]');
  if (!popup) {
    popup = document.createElement('div');
    popup.className = 'chanting-ipa-popup';
    popup.dataset.chantingIpaPopup = '1';
    root.appendChild(popup);
  }
  return popup;
}
function chantingHidePopup(root) {
  const popup = root.querySelector('[data-chanting-ipa-popup]');
  if (popup) { popup.classList.remove('visible'); popup.innerHTML = ''; }
  root.__chantingPopupAnchor = null;
}
function chantingPositionPopup(root, anchor) {
  const popup = root.querySelector('[data-chanting-ipa-popup]');
  if (!popup || !popup.classList.contains('visible') || !anchor) return;
  const M=12,G=8,vw=document.documentElement.clientWidth||window.innerWidth,vh=document.documentElement.clientHeight||window.innerHeight;
  popup.style.left='0px'; popup.style.top='0px';
  const ar=anchor.getBoundingClientRect(),pr=popup.getBoundingClientRect();
  const pw=Math.min(pr.width,Math.max(0,vw-M*2)),ph=Math.min(pr.height,Math.max(0,vh-M*2));
  const below=vh-ar.bottom-G-M,above=ar.top-G-M,down=ph<=below?true:ph<=above?false:below>=above;
  const clamp=(v,min,max)=>max<min?min:Math.min(Math.max(v,min),max);
  popup.style.left=Math.round(clamp(ar.left,M,vw-M-pw))+'px';
  popup.style.top=Math.round(clamp(down?ar.bottom+G:ar.top-G-ph,M,vh-M-ph))+'px';
}
function chantingShowCompact(root, target) {
  const state=root.__chantState||{};
  const raw=target.getAttribute('data-word')||'';
  const clean=target.getAttribute('data-clean')||raw;
  const html=chantingLookup(state.ipa_popup_lookup,raw,clean);
  if (!html) { chantingHidePopup(root); return; }
  const popup=chantingPopup(root);
  popup.innerHTML=sanitizeHtml(String(html));
  popup.classList.add('visible');
  root.__chantingPopupAnchor=target;
  chantingPositionPopup(root,target);
}
function chantingSidebarHtml(root,target) {
  const state=root.__chantState||{};
  const raw=target.getAttribute('data-word')||'';
  const clean=target.getAttribute('data-clean')||raw;
  const meaning=chantingLookup(state.ipa_lookup,raw,clean);
  if (!meaning) return `<div style="color:#5d7367;margin-top:10px;">Không có dữ liệu IPA cho <b>${escapeHtml(clean||'từ này')}</b>.</div>`;
  const temp=document.createElement('div');
  temp.innerHTML=sanitizeHtml(String(meaning));
  decorateEnglishWords(temp,state.en_lookup||{},'pali');
  return temp.innerHTML;
}
function stopChantingAutoScroll(root) {
  if (root.__chantFrame!=null) { cancelAnimationFrame(root.__chantFrame); root.__chantFrame=null; }
  if (root.__chantResumeTimer!=null) { clearTimeout(root.__chantResumeTimer); root.__chantResumeTimer=null; }
  root.__chantLast=null; root.__chantPaused=false; root.__chantFinished=false;
}
function holdChantingAutoScroll(root) {
  const state=root.__chantState||{};
  if (!(Number(state.auto_scroll_speed)>0) || root.__chantFinished) return;
  root.__chantPaused=true; root.__chantLast=null;
  const scroller=root.querySelector('[data-chanting-scroll]');
  if (scroller) root.__chantPosition=Number(scroller.scrollTop||0);
  if (root.__chantResumeTimer!=null) { clearTimeout(root.__chantResumeTimer); root.__chantResumeTimer=null; }
}
function scheduleChantingResume(root, delay=1500) {
  const state=root.__chantState||{};
  if (!(Number(state.auto_scroll_speed)>0) || root.__chantFinished) return;
  holdChantingAutoScroll(root);
  root.__chantResumeTimer=setTimeout(()=>{
    root.__chantResumeTimer=null;
    const scroller=root.querySelector('[data-chanting-scroll]');
    if (scroller) root.__chantPosition=Number(scroller.scrollTop||0);
    root.__chantPaused=false; root.__chantLast=null;
  },delay);
}
function startChantingAutoScroll(root) {
  stopChantingAutoScroll(root);
  const state=root.__chantState||{},scroller=root.querySelector('[data-chanting-scroll]');
  const speed=Number(state.auto_scroll_speed)||0;
  if (!(speed>0) || !scroller) return;
  root.__chantPosition=Number(scroller.scrollTop||0); root.__chantFinished=false;
  const step=(timestamp)=>{
    const current=root.__chantState||{};
    const activeSpeed=Number(current.auto_scroll_speed)||0;
    const currentScroller=root.querySelector('[data-chanting-scroll]');
    if (!(activeSpeed>0) || !currentScroller || root.__chantFinished) { root.__chantFrame=null; return; }
    if (root.__chantPaused) {
      root.__chantLast=timestamp; root.__chantPosition=Number(currentScroller.scrollTop||0);
      root.__chantFrame=requestAnimationFrame(step); return;
    }
    if (root.__chantLast==null) root.__chantLast=timestamp;
    else {
      const elapsed=Math.min(timestamp-root.__chantLast,100); root.__chantLast=timestamp;
      const maxScroll=Math.max(0,currentScroller.scrollHeight-currentScroller.clientHeight);
      if (maxScroll<=0 || currentScroller.scrollTop>=maxScroll-.5) {
        currentScroller.scrollTop=maxScroll; root.__chantFinished=true; root.__chantFrame=null; return;
      }
      root.__chantPosition=Math.min(maxScroll,Number(root.__chantPosition||0)+activeSpeed*elapsed/1000);
      currentScroller.scrollTop=root.__chantPosition;
    }
    root.__chantFrame=requestAnimationFrame(step);
  };
  root.__chantFrame=requestAnimationFrame(step);
}
function bindChantingListeners(root) {
  if (root.__chantListeners) return;
  let closeTimer=null,drag=false;
  const cancelClose=()=>{if(closeTimer!=null){clearTimeout(closeTimer);closeTimer=null;}};
  const scheduleClose=()=>{cancelClose();closeTimer=setTimeout(()=>chantingHidePopup(root),500);};
  root.addEventListener('mouseover',event=>{
    const target=event.target instanceof Element?event.target.closest('.chanting-pali-word'):null;
    if (!target||!root.contains(target)||(event.relatedTarget instanceof Node&&target.contains(event.relatedTarget))) return;
    cancelClose(); chantingShowCompact(root,target);
  });
  root.addEventListener('mouseout',event=>{
    const target=event.target instanceof Element?event.target.closest('.chanting-pali-word'):null;
    if (!target||!root.contains(target)||(event.relatedTarget instanceof Node&&target.contains(event.relatedTarget))) return;
    scheduleClose();
  });
  root.addEventListener('click',event=>{
    const target=event.target instanceof Element?event.target.closest('.chanting-pali-word'):null;
    if (!target||!root.contains(target)) return;
    event.preventDefault(); event.stopPropagation(); chantingClearActive(root); target.classList.add('active');
    emitDictionarySurface(root,chantingSidebarHtml(root,target),false);
  });
  root.addEventListener('wheel',()=>scheduleChantingResume(root),{passive:true});
  root.addEventListener('touchstart',()=>holdChantingAutoScroll(root),{passive:true});
  root.addEventListener('touchmove',()=>scheduleChantingResume(root),{passive:true});
  root.addEventListener('touchend',()=>scheduleChantingResume(root),{passive:true});
  root.addEventListener('keydown',event=>{
    if (['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' ','Spacebar'].includes(event.key)) scheduleChantingResume(root);
  });
  root.addEventListener('pointerdown',event=>{
    const scroller=root.querySelector('[data-chanting-scroll]'); if(!scroller)return;
    const rect=scroller.getBoundingClientRect();
    if ((rect.right-event.clientX)<=20 && scroller.scrollHeight>scroller.clientHeight+1) { drag=true; holdChantingAutoScroll(root); }
  });
  root.addEventListener('pointermove',()=>{if(drag)holdChantingAutoScroll(root);});
  root.addEventListener('pointerup',()=>{if(drag){drag=false;scheduleChantingResume(root);}});
  root.addEventListener('scroll',()=>{if(root.__chantingPopupAnchor)chantingPositionPopup(root,root.__chantingPopupAnchor);},true);
  root.__chantListeners=true;
}
export default function(component) {
  const {data,parentElement}=component;
  const root=parentElement.querySelector('[data-chanting-reader-v2]');
  if (!root||data?.version!==1) return;
  const previous=root.__chantState,same=previous?.resource_id===data.resource_id,oldScroll=root.querySelector('[data-chanting-scroll]')?.scrollTop||0;
  stopChantingAutoScroll(root); root.__chantState=data; root.__dictState=data;
  root.dataset.dark=data.dark_mode?'1':'0';
  root.style.height=data.height?`${Number(data.height)}px`:'';
  if (!same) {
    const style=document.createElement('style'); style.textContent=data.css||'';
    const scroll=document.createElement('div'); scroll.className='chanting-scroll chanting-text-col'; scroll.dataset.chantingScroll='1'; scroll.tabIndex=0;
    scroll.innerHTML=sanitizeHtml(`<table><tbody>${String(data.body_html||'')}</tbody></table>`);
    root.replaceChildren(style,scroll); root.scrollTop=0;
  } else {
    const scroll=root.querySelector('[data-chanting-scroll]'); if(scroll)scroll.scrollTop=oldScroll;
  }
  bindChantingListeners(root); startChantingAutoScroll(root);
}
'''


def try_render_chanting_reader_v2(
    *,
    body_html: str,
    css: str,
    ipa_lookup: dict[str, object] | None,
    ipa_popup_lookup: dict[str, object] | None,
    en_lookup: dict[str, object] | None,
    auto_scroll_speed: float = 0.0,
    height: int | None = None,
    sidebar_placeholder: str = "Bấm vào một chữ Pāli để xem IPA...",
    dark_mode: bool = False,
) -> bool:
    if not v2_enabled(FEATURE):
        record_v2_route(FEATURE, "legacy_disabled")
        return False
    try:
        preliminary = prepare_chanting_payload(
            body_html=body_html,
            css=css,
            ipa_lookup=ipa_lookup,
            ipa_popup_lookup=ipa_popup_lookup,
            en_lookup=en_lookup,
            auto_scroll_speed=auto_scroll_speed,
            height=height,
            dark_mode=dark_mode,
        )
        channel = make_dictionary_surface_channel(FEATURE, preliminary["resource_id"], "ipa_sidebar")
        data = dict(preliminary)
        data["sidebar_channel"] = channel
        # Resource identity must include the channel-independent content only.
        data["resource_id"] = preliminary["resource_id"]
        render_dictionary_sidebar_surface(
            FEATURE,
            channel=channel,
            resource_id=data["resource_id"],
            placeholder=sidebar_placeholder,
            profile="pali",
            key_suffix="ipa",
            en_lookup=dict(en_lookup or {}),
            decorate_english=False,
            popup_en_vi=True,
            dark_mode=dark_mode,
        )
        renderer = get_v2_component("scapp_chanting_reader_v2", _HTML, _CSS, _JS)
        renderer(data=data, key="scapp_chanting_reader_v2:main")
    except ChantingReaderUnsupported as exc:
        route = {
            "source_text_limit": "legacy_source_text_limit",
            "payload_limit": "legacy_payload_limit",
            "item_limit": "legacy_item_limit",
            "unsupported_shape": "legacy_unsupported_shape",
        }.get(str(exc), "legacy_unsupported_shape")
        record_v2_route(FEATURE, route)
        return False
    except Exception:
        record_v2_route(FEATURE, "legacy_setup_error")
        if v2_strict(FEATURE):
            raise
        return False
    record_v2_mount(
        FEATURE,
        data,
        text_bytes=len(str(body_html).encode("utf-8", errors="replace")),
        items=len(dict(ipa_lookup or {})),
    )
    return True
