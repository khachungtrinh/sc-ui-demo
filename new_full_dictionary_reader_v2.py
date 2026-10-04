# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Components v2 runtime for prepared Search/AIFast/Sujato dictionary viewers.

Canonical dictionary storage is intentionally absent from this module. Python
prepares only entries reachable from the current view through
``new_dictionary_data``; browser state owns hover popup/history/scroll.
"""


from __future__ import annotations


import hashlib


import json


from assets_style import build_reader_typography_reset_css


from dict_lookup_assets import build_popup_css


from new_component_v2_support import SAFE_HTML_JS, get_v2_component


from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route


from new_dictionary_surface_v2 import (
    dictionary_surface_event_js, make_dictionary_surface_channel,
    render_dictionary_sidebar_surface,
)


from new_reader_v2_primitives import reader_css_for_host


MAX_SOURCE_BYTES = 8 * 1024 * 1024


MAX_PAYLOAD_BYTES = 24 * 1024 * 1024


MAX_PALI_WORDS = 20_000


MAX_ENGLISH_WORDS = 20_000


class FullDictionaryReaderUnsupported(ValueError):
    pass


def build_sujato_v2_css() -> str:
    """Canonical Sujato visual profile without loading full dictionary JS."""
    shared_popup_css = build_popup_css(include_scrollbar=True)
    typography = build_reader_typography_reset_css(
        ".panel-reader-v2",
        inherit_selectors=(
            ".panel-reader-v2 #content",
            ".panel-reader-v2 #content .sujato-english-table",
            ".panel-reader-v2 #content .sujato-english-table td",
            ".panel-reader-v2 #content .sujato-english-text",
            ".panel-reader-v2 #content .sujato-english-text p",
            ".panel-reader-v2 #content .sujato-english-text div",
            ".panel-reader-v2 #content .sujato-english-text span",
            ".panel-reader-v2 #content .sujato-english-text li",
            ".panel-reader-v2 #content .sujato-english-text a",
            ".panel-reader-v2 #content .sujato-english-text em",
            ".panel-reader-v2 #content .sujato-english-text strong",
            ".panel-reader-v2 #content .sujato-english-text b",
            ".panel-reader-v2 #content .sujato-english-text i",
            ".panel-reader-v2 #content .sujato-english-text font",
            ".panel-reader-v2 #content .sujato-english-text small",
            ".panel-reader-v2 #content .sujato-english-text label",
        ),
        id_selector=".panel-reader-v2 #content .sujato-segment",
    )
    reader_css = r'''
.panel-reader-v2 {margin:0;padding:0;background:var(--dl-bg-main,#fdfdf8);color:var(--dl-text,#3d3a2a);box-sizing:border-box;}
.panel-reader-v2 #content {width:100%;box-sizing:border-box;padding-right:15px;}
.panel-reader-v2 #content .sujato-english-table {width:100%;border-collapse:collapse;border:1px solid #eaeae3;}
.panel-reader-v2 #content .sujato-english-table td {padding:8px;vertical-align:top;border:1px solid #eaeae3;line-height:var(--dl-reader-line-height,1.6);}
'''
    return reader_css + "\n" + reader_css_for_host(shared_popup_css) + "\n" + typography


_HTML = '<section class="panel-reader-v2 dictionary-reader-v2" data-dictionary-reader-v2></section>'


_CSS = r'''
.dictionary-reader-v2 {width:100%;box-sizing:border-box;overflow:auto;position:relative;}
.dictionary-v2-popup {position:fixed;z-index:999999;min-width:min(20em,calc(100vw - 24px));width:min(550px,calc(100vw - 24px));max-width:calc(100vw - 24px);max-height:calc(100vh - 24px);overflow:auto;box-sizing:border-box;background:var(--dl-popup-bg,var(--dl-bg,#ecebe3));border:1px solid var(--dl-border,#d3d2ca);box-shadow:0 4px 18px rgba(0,0,0,.18);color:var(--dl-text,#3d3a2a);border-radius:var(--dl-radius,3px);font-size:var(--dl-reader-font-size,1rem);line-height:var(--dl-reader-line-height,1.6);font-weight:400;font-style:normal;text-decoration:none;text-align:left;padding:12px;overscroll-behavior:contain;}
.dictionary-v2-english, .pali-word {cursor:pointer;}
'''


_JS = SAFE_HTML_JS + dictionary_surface_event_js() + r'''
function dictEscape(text) { const d=document.createElement('div'); d.textContent=String(text||''); return d.innerHTML; }
function normalizeDictPali(raw) {
  return String(raw||'').replace(/[^a-zA-Zāīūṅñṭḍṇḷṃṁ]/gi,'').toLowerCase().replace(/ṁ/g,'ṃ');
}
function normalizeDictEnglish(raw) {
  return String(raw||'').toLowerCase().trim().replace(/[‘’]/g,"'").replace(/^["'“”]+|["'“”]+$/g,'');
}
function formatDictHeadword(headword) {
  const value=String(headword||''); const m=value.match(/^(.+?)\s(\d[\d.]*)$/);
  if(!m) return dictEscape(value);
  return `${dictEscape(m[1].trim())}<sub style="font-size:60%;font-weight:bold;">${dictEscape(m[2])}</sub>`;
}
function paliMeaning(state, rawWord) {
  const original=String(rawWord||'').trim(); const clean=normalizeDictPali(original); const item=state.pali_lookup?.[clean]; if(!item) return '';
  let out='';
  if(Array.isArray(item.headwords)&&item.headwords.length){
    out += `<strong>${dictEscape(original)}</strong><br><ul style="line-height:1.4em;padding-left:15px;margin-top:4px;">`;
    for(const row of item.headwords){if(!Array.isArray(row)||row.length<2)continue;out += `<li>${formatDictHeadword(row[0])}: ${sanitizeHtml(row[1])}</li>`;}
    out += '</ul>';
  }
  if(item.deconstructor){out += `<strong>${dictEscape(original)}</strong><br><ul style="line-height:1.4em;padding-left:15px;margin-top:4px;"><li>${sanitizeHtml(item.deconstructor)}</li></ul>`;}
  out += '</ul>';
  return out.replace(/ṁ/g,'ṃ');
}
function englishMeaning(state, rawWord) {
  const original=String(rawWord||'').trim(); const clean=normalizeDictEnglish(original); const meaning=state.english_lookup?.[clean];
  if(!meaning) return '';
  return `<strong>${dictEscape(original)}</strong><br>${sanitizeHtml(meaning)}`;
}
function showEnglishDictionaryResult(root, anchor) {
  const html=englishMeaning(root.__dictState,anchor.textContent||'');
  if(root.__dictState?.english_sidebar){
    hideDictPopup(root);
    if(html) emitDictionarySurface(root,html,false);
    return;
  }
  showDictPopup(root,anchor,html);
}
function decorateDictionaryPali(root) {
  const roots=Array.from(root.querySelectorAll('[lang="pi"], [lang="pli"], [lang="pali"]'))
    .filter(el=>!el.parentElement?.closest('[lang="pi"], [lang="pli"], [lang="pali"]'));
  const splitter=/([^ \u00a0,. – —:;?!“‘-]+)/;
  for(const langRoot of roots){
    if(langRoot.querySelector('.pali-word')) continue;
    const walker=document.createTreeWalker(langRoot,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
    for(const node of nodes){
      const parent=node.parentElement;if(!parent||parent.closest('script,style,textarea,.pali-word,.dictionary-v2-popup'))continue;
      const parts=(node.nodeValue||'').split(splitter);if(parts.length<2)continue;const frag=document.createDocumentFragment();
      for(let i=0;i<parts.length;i++){const part=parts[i];if(!part)continue;if(i%2===1){const span=document.createElement('span');span.className='pali-word';span.dataset.word=part;span.textContent=part;frag.appendChild(span);}else frag.appendChild(document.createTextNode(part));}
      node.replaceWith(frag);
    }
  }
}
function decorateDictionaryEnglish(root) {
  const pattern = (()=>{try{return new RegExp("\\p{L}+(?:[’']\\p{L}+)*(?:-\\p{L}+(?:[’']\\p{L}+)*)*","gu");}catch(_){return /[A-Za-z]+(?:[’'][A-Za-z]+)*(?:-[A-Za-z]+(?:[’'][A-Za-z]+)*)*/g;}})();
  for(const lookupRoot of root.querySelectorAll('.sujato-english-text[lang="en"]')){
    const walker=document.createTreeWalker(lookupRoot,NodeFilter.SHOW_TEXT); const nodes=[]; while(walker.nextNode())nodes.push(walker.currentNode);
    for(const node of nodes){
      const parent=node.parentElement; if(!parent||parent.closest('a,script,style,textarea,.dictionary-v2-english,.dictionary-v2-popup'))continue;
      const text=node.nodeValue||''; pattern.lastIndex=0; let match,last=0,found=false; const frag=document.createDocumentFragment();
      while((match=pattern.exec(text))!==null){found=true;if(match.index>last)frag.appendChild(document.createTextNode(text.slice(last,match.index)));const span=document.createElement('span');span.className='dictionary-v2-english';span.textContent=match[0];frag.appendChild(span);last=pattern.lastIndex;}
      if(found){if(last<text.length)frag.appendChild(document.createTextNode(text.slice(last)));node.replaceWith(frag);}
    }
  }
}
function ensureDictPopup(root) {
  let p=root.querySelector('[data-dictionary-popup]'); if(p)return p;
  p=document.createElement('span');p.className='dictionary-v2-popup';p.dataset.dictionaryPopup='1';p.hidden=true;p.setAttribute('role','tooltip');root.appendChild(p);return p;
}
function hideDictPopup(root){const p=root.querySelector('[data-dictionary-popup]');if(p){p.hidden=true;p.innerHTML='';}root.__dictAnchor=null;}
function positionDictPopup(root,anchor){const p=root.querySelector('[data-dictionary-popup]');if(!p||p.hidden||!anchor)return;const M=12,G=8,vw=document.documentElement.clientWidth||window.innerWidth,vh=document.documentElement.clientHeight||window.innerHeight;p.style.left='0px';p.style.top='0px';p.style.maxHeight=Math.max(80,vh-M*2)+'px';const ar=anchor.getBoundingClientRect(),pr=p.getBoundingClientRect(),pw=Math.min(pr.width,Math.max(0,vw-M*2)),ph=Math.min(pr.height,Math.max(0,vh-M*2));const below=vh-ar.bottom-G-M,above=ar.top-G-M,placeBelow=ph<=below?true:ph<=above?false:below>=above;const clamp=(v,min,max)=>max<min?min:Math.min(Math.max(v,min),max);p.style.left=Math.round(clamp(ar.left,M,vw-M-pw))+'px';p.style.top=Math.round(clamp(placeBelow?ar.bottom+G:ar.top-G-ph,M,vh-M-ph))+'px';}
function showDictPopup(root,anchor,html){const p=ensureDictPopup(root);if(!html){hideDictPopup(root);return;}p.innerHTML=html;p.hidden=false;root.__dictAnchor=anchor;positionDictPopup(root,anchor);}
function historyTarget(root){const id=root.__dictState?.history_target_id;if(!id)return null;return root.querySelector(`#${CSS.escape(id)}`);}
function appendPaliHistory(root,target){const state=root.__dictState;const raw=target.getAttribute('data-word')||target.textContent||'';const clean=normalizeDictPali(raw);const meaning=paliMeaning(state,raw);const entryHtml=`<div style="box-sizing:border-box;"><div style="font-size:1.2rem;color:#d63031;font-weight:600;border-bottom:2px solid #d3d2ca;margin-bottom:10px;padding-bottom:5px;display:flex;align-items:center;"><span style="font-size:0.65rem;background:#d63031;color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">Pali</span>${dictEscape(clean||raw)}</div><div>${meaning||"<div style='color:#d63031;'>Không tìm thấy dữ liệu.</div>"}</div></div>`;if(emitDictionarySurface(root,entryHtml,true))return;const box=historyTarget(root);if(!box)return;const placeholder=box.querySelector('i');if(placeholder&&box.querySelectorAll('.stored-pali-entry').length===0)placeholder.remove();const entry=document.createElement('div');entry.className='stored-pali-entry';entry.innerHTML=entryHtml;box.appendChild(entry);try{box.scrollTop=box.scrollHeight;}catch(_){}}
export default function(component){
  const {data,parentElement}=component;const root=parentElement.querySelector('[data-dictionary-reader-v2]');if(!root||data?.version!==1)return;
  const previous=root.__dictState;const same=previous?.resource_id===data.resource_id;const oldScroll=root.scrollTop||0;root.__dictState=data;root.style.height=`${Number(data.height||850)}px`;
  if(!same){const style=document.createElement('style');style.textContent=data.css||'';const body=document.createElement('div');body.dataset.dictionaryBody='1';body.innerHTML=sanitizeHtml(data.body_html||'');root.replaceChildren(style,body);decorateDictionaryPali(root);decorateDictionaryEnglish(root);ensureDictPopup(root);root.scrollTop=0;}else{root.scrollTop=oldScroll;}
  if(!root.__dictListeners){let hideTimer=null;const cancel=()=>{if(hideTimer!==null){clearTimeout(hideTimer);hideTimer=null;}};const schedule=()=>{cancel();hideTimer=setTimeout(()=>hideDictPopup(root),140);};
    root.addEventListener('mouseover',event=>{const t=event.target instanceof Element?event.target:null;if(!t)return;const pali=t.closest('.pali-word');if(pali&&root.contains(pali)&&!(event.relatedTarget instanceof Node&&pali.contains(event.relatedTarget))){cancel();showDictPopup(root,pali,paliMeaning(root.__dictState,pali.getAttribute('data-word')||pali.textContent||''));return;}const en=t.closest('.dictionary-v2-english');if(en&&root.contains(en)&&!(event.relatedTarget instanceof Node&&en.contains(event.relatedTarget))){cancel();showEnglishDictionaryResult(root,en);return;}if(t.closest('[data-dictionary-popup]'))cancel();});
    root.addEventListener('mouseout',event=>{const t=event.target instanceof Element?event.target:null;if(!t)return;if(t.closest('.pali-word,.dictionary-v2-english,[data-dictionary-popup]'))schedule();});
    root.addEventListener('click',event=>{const t=event.target instanceof Element?event.target:null;if(!t)return;const pali=t.closest('.pali-word');if(pali&&root.contains(pali)){root.querySelectorAll('.pali-word.active').forEach(el=>el.classList.remove('active'));pali.classList.add('active');appendPaliHistory(root,pali);return;}const en=t.closest('.dictionary-v2-english');if(en&&root.contains(en)){event.stopPropagation();cancel();showEnglishDictionaryResult(root,en);return;}if(!t.closest('[data-dictionary-popup]'))hideDictPopup(root);});
    root.addEventListener('scroll',()=>{if(root.__dictAnchor)positionDictPopup(root,root.__dictAnchor);},true);root.__dictResizeObserver=new ResizeObserver(()=>{if(root.__dictAnchor)positionDictPopup(root,root.__dictAnchor);});root.__dictResizeObserver.observe(root);root.__dictListeners=true;}
}
'''

