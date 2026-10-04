# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Components v2 LCDP reader using prepared per-document canonical DPD data."""


from __future__ import annotations


import hashlib


import json


from assets_style import build_reader_typography_reset_css


from dict_lookup_assets import build_popup_css


from new_component_v2_support import SAFE_HTML_JS, get_v2_component


from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route


from new_dictionary_surface_v2 import dictionary_surface_event_js, make_dictionary_surface_channel, render_dictionary_sidebar_surface


from new_reader_highlight import build_keyword_highlight_assets


from new_reader_v2_primitives import reader_css_for_host


MAX_SOURCE_BYTES = 8 * 1024 * 1024


MAX_PAYLOAD_BYTES = 12 * 1024 * 1024


MAX_LOOKUP_WORDS = 12000


class LCDPReaderUnsupported(ValueError):
    pass


def _highlight_js() -> tuple[str, str]:
    assets = build_keyword_highlight_assets("__lcdp_keyword__", root_selector=".lcdp-v2-content", auto_run=False)
    if not assets:
        return "", ""
    css, script = assets.split("</style><script>", 1)
    css = css.removeprefix("<style>")
    script = script.removesuffix("</script>")
    script = script.replace("function applyReaderKeywordHighlight()", "function applyLCDPKeywordHighlight(host)")
    script = script.replace('document.querySelector(".lcdp-v2-content")', 'host.querySelector(".lcdp-v2-content")')
    script = script.replace('fold("__lcdp_keyword__")', 'fold(host.__lcdpState.highlight_word)')
    return css, script


_HIGHLIGHT_CSS, _HIGHLIGHT_JS = _highlight_js()


_READER_CSS = reader_css_for_host(build_popup_css(include_scrollbar=True) + "\n" + build_reader_typography_reset_css(
    ".lcdp-v2-reader",
    inherit_selectors=(
        ".lcdp-v2-content",
        ".lcdp-v2-content p",
        ".lcdp-v2-content .p",
        ".lcdp-v2-content .pali",
        ".lcdp-v2-content .speaker",
        ".lcdp-v2-content .verse",
        ".lcdp-v2-content .lcdp-pali-table",
        ".lcdp-v2-content .lcdp-pali-table td",
        ".lcdp-v2-content .lcdp-pali-text",
        '.lcdp-v2-content .lcdp-pali-text span[lang="pi"].lcdp-json-pali',
    ),
    id_selector=".lcdp-v2-content .lcdp-pali-segment",
)).replace(".panel-reader-v2", ".lcdp-v2-reader")


_HTML = '<section class="lcdp-v2-reader" data-lcdp-v2-root><div class="lcdp-v2-scroll" data-lcdp-scroll><div class="lcdp-v2-content" data-lcdp-content></div><div class="lcdp-v2-popup" data-lcdp-popup hidden></div></div></section>'


_CSS = _READER_CSS + "\n" + _HIGHLIGHT_CSS + r'''
.lcdp-v2-reader {
  width: 100%; box-sizing: border-box; color: var(--dl-text, #3d3a2a);
  background: var(--dl-bg-main, #fdfdf8); position: relative;
}
.lcdp-v2-scroll {height:100%; overflow:auto; padding-right:15px; box-sizing:border-box; scrollbar-width:thin; scrollbar-color:#ccc transparent;}
.lcdp-v2-scroll::-webkit-scrollbar {width:6px;}
.lcdp-v2-scroll::-webkit-scrollbar-thumb {background:#ccc;border-radius:4px;}
.lcdp-v2-content {width:100%;box-sizing:border-box;}
.lcdp-v2-content p, .lcdp-v2-content .p {margin-top:0!important;margin-bottom:1rem!important;line-height:var(--dl-reader-line-height,1.6);text-align:justify;}
.lcdp-v2-content h1,.lcdp-v2-content h2,.lcdp-v2-content h3,.lcdp-v2-content h4,.lcdp-v2-content h5,.lcdp-v2-content h6 {margin-top:0;padding-top:5px;line-height:1.2;font-weight:600;color:var(--dl-primary,#3d3a2a);}
.lcdp-v2-content ul,.lcdp-v2-content li {margin-bottom:.5rem;}
.lcdp-v2-content p.vi {text-align:justify;}
.lcdp-v2-content .pali {color:var(--dl-muted,rgba(61,58,42,.7));}
.lcdp-v2-content .speaker {font-weight:600;color:var(--dl-primary,#3d3a2a);}
.lcdp-v2-content .verse {margin-left:1.5em!important;text-align:left;}
.lcdp-v2-content .pts_pn,.lcdp-v2-content .msdiv,.lcdp-v2-content .ms,.lcdp-v2-content .pts-cs,.lcdp-v2-content q {display:none;}
.lcdp-v2-content .lcdp-pali-table {width:100%;border-collapse:collapse;border:1px solid #eaeae3;}
.lcdp-v2-content .lcdp-pali-table td {padding:8px;vertical-align:top;border:1px solid #eaeae3;}
.lcdp-v2-content .lcdp-pali-table span[lang="pi"].lcdp-json-pali {color:var(--dl-text,#3d3a2a);}
.lcdp-v2-content .lcdp-source-note {text-align:right;font-style:italic;margin-top:40px;color:var(--dl-muted,rgba(61,58,42,.7));}
.lcdp-v2-content .lcdp-source-note a {color:var(--dl-primary,#3d3a2a);text-decoration:none;border-bottom:1px dotted var(--dl-border,#d3d2ca);}
.lcdp-v2-content .lcdp-source-note a:hover {border-bottom-style:solid;}
.lcdp-v2-lookup {cursor:default;}
.lcdp-v2-popup {position:fixed;z-index:999999;min-width:min(20em,calc(100vw - 24px));max-width:min(550px,calc(100vw - 24px));max-height:calc(100vh - 24px);overflow:auto;box-sizing:border-box;background:var(--dl-popup-bg,var(--dl-bg,#ecebe3));border:1px solid var(--dl-border,#d3d2ca);box-shadow:0 4px 18px rgba(0,0,0,.18);border-radius:var(--dl-radius,3px);padding:12px;color:var(--dl-text,#3d3a2a);font:inherit;text-align:left;}
'''


_JS = SAFE_HTML_JS + dictionary_surface_event_js() + "\n" + _HIGHLIGHT_JS + r'''
function escapeLCDP(text) { const d=document.createElement('div'); d.textContent=String(text||''); return d.innerHTML; }
function normalizeLCDPWord(raw) {
  return String(raw || '').toLowerCase().trim().replace(/\u00ad/g,'').replace(/ṁg/g,'ṅg').replace(/ṁk/g,'ṅk').replace(/[’”'"]/g,'').replace(/ṁ/g,'ṃ');
}
function formatHeadword(headword) {
  const value=String(headword||''); const m=value.match(/^(.+?)\s(\d[\d.]*)$/);
  if (!m) return escapeLCDP(value);
  return `${escapeLCDP(m[1].trim())}<sub style="font-size:60%; font-weight:bold;">${escapeLCDP(m[2])}</sub>`;
}
function lookupLCDP(state, rawWord) {
  const clean=normalizeLCDPWord(rawWord); const item=state.lookup?.[clean]; if (!item) return '';
  let out='';
  if (Array.isArray(item.headwords) && item.headwords.length) {
    out += `<strong>${escapeLCDP(rawWord)}</strong><br><ul style="line-height: 1.4em; padding-left: 15px; margin-top: 4px;">`;
    for (const row of item.headwords) {
      if (!Array.isArray(row) || row.length < 2) continue;
      out += `<li>${formatHeadword(row[0])}: ${sanitizeHtml(row[1])}</li>`;
    }
    out += '</ul>';
  }
  if (item.deconstructor) {
    out += `<strong>${escapeLCDP(rawWord)}</strong><br><ul style="line-height: 1.4em; padding-left: 15px; margin-top: 4px;"><li>${sanitizeHtml(item.deconstructor)}</li></ul>`;
  }
  out += '</ul>';
  return out.replace(/ṁ/g,'ṃ');
}
function shouldSkipTextNode(node) {
  const parent=node.parentElement; if (!parent) return true;
  if (parent.closest('script,style,noscript,textarea,button,select,.lcdp-v2-popup,.reader-keyword-highlight')) return true;
  if (parent.tagName === 'A') {
    const gp=parent.parentElement; if (!gp || !/^H[1-6]$/.test(gp.tagName)) return true;
  }
  return false;
}
function decoratePaliRoot(container) {
  const roots=Array.from(container.querySelectorAll('[lang="pi"], [lang="pli"], [lang="pali"]'))
    .filter(el => !el.parentElement?.closest('[lang="pi"], [lang="pli"], [lang="pali"]'));
  const splitter=/([^ \u00a0,. – —:;?!“‘-]+)/;
  for (const langRoot of roots) {
    const walker=document.createTreeWalker(langRoot, NodeFilter.SHOW_TEXT); const nodes=[];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      if (shouldSkipTextNode(node) || !node.nodeValue) continue;
      const parts=node.nodeValue.split(splitter); if (parts.length < 2) continue;
      const frag=document.createDocumentFragment();
      for (let i=0;i<parts.length;i++) {
        const part=parts[i]; if (!part) continue;
        if (i % 2 === 1) { const span=document.createElement('span'); span.className='lcdp-v2-lookup'; span.textContent=part; frag.appendChild(span); }
        else frag.appendChild(document.createTextNode(part));
      }
      node.replaceWith(frag);
    }
  }
}
function hideLCDPPopup(root) { const p=root.querySelector('[data-lcdp-popup]'); if(p){p.hidden=true;p.innerHTML='';} root.__lcdpAnchor=null; }
function positionLCDPPopup(root, anchor) {
  const p=root.querySelector('[data-lcdp-popup]'); if(!p || p.hidden || !anchor) return;
  const M=12,G=8,vw=document.documentElement.clientWidth||window.innerWidth,vh=document.documentElement.clientHeight||window.innerHeight;
  p.style.left='0px';p.style.top='0px';p.style.maxHeight=Math.max(80,vh-M*2)+'px';
  const ar=anchor.getBoundingClientRect(), pr=p.getBoundingClientRect();
  const pw=Math.min(pr.width,Math.max(0,vw-M*2)), ph=Math.min(pr.height,Math.max(0,vh-M*2));
  const below=vh-ar.bottom-G-M, above=ar.top-G-M;
  const placeBelow=ph<=below ? true : ph<=above ? false : below>=above;
  const clamp=(v,min,max)=>max<min?min:Math.min(Math.max(v,min),max);
  const left=clamp(ar.left,M,vw-M-pw); let top=placeBelow?ar.bottom+G:ar.top-G-ph; top=clamp(top,M,vh-M-ph);
  p.style.left=Math.round(left)+'px'; p.style.top=Math.round(top)+'px';
}
function showLCDPPopup(root, anchor) {
  const state=root.__lcdpState; const html=lookupLCDP(state, anchor.textContent||''); const p=root.querySelector('[data-lcdp-popup]');
  if (state?.sidebar_channel) {
    hideLCDPPopup(root);
    if (html) emitDictionarySurface(root, html, false);
    return;
  }
  if (!html || !p) { hideLCDPPopup(root); return; }
  p.innerHTML=html; p.hidden=false; root.__lcdpAnchor=anchor; positionLCDPPopup(root,anchor);
}
export default function(component) {
  const {data,parentElement}=component; const root=parentElement.querySelector('[data-lcdp-v2-root]'); if(!root||data?.version!==1)return;
  const scroll=root.querySelector('[data-lcdp-scroll]'), content=root.querySelector('[data-lcdp-content]');
  const previous=root.__lcdpState; const same=previous?.resource_id===data.resource_id; const oldScroll=scroll?.scrollTop||0;
  root.__lcdpState=data; root.style.height=`${Number(data.height||850)}px`;
  if (!same) {
    content.innerHTML=sanitizeHtml(data.content_html||''); decoratePaliRoot(content);
    if (data.highlight_word) applyLCDPKeywordHighlight(root);
    if (scroll) scroll.scrollTop=0;
  } else if (scroll) scroll.scrollTop=oldScroll;
  if (!root.__lcdpListeners) {
    let hideTimer=null; const cancel=()=>{if(hideTimer!==null){clearTimeout(hideTimer);hideTimer=null;}};
    root.addEventListener('mouseover',e=>{const a=e.target instanceof Element?e.target.closest('.lcdp-v2-lookup'):null;if(!a||!root.contains(a))return; if(e.relatedTarget instanceof Node&&a.contains(e.relatedTarget))return; cancel();showLCDPPopup(root,a);});
    root.addEventListener('mouseout',e=>{const a=e.target instanceof Element?e.target.closest('.lcdp-v2-lookup'):null;if(!a)return; cancel();hideTimer=setTimeout(()=>hideLCDPPopup(root),140);});
    root.addEventListener('mouseover',e=>{if(e.target instanceof Element&&e.target.closest('[data-lcdp-popup]'))cancel();});
    root.addEventListener('mouseout',e=>{if(e.target instanceof Element&&e.target.closest('[data-lcdp-popup]')){cancel();hideTimer=setTimeout(()=>hideLCDPPopup(root),140);}});
    root.addEventListener('scroll',()=>{if(root.__lcdpAnchor)positionLCDPPopup(root,root.__lcdpAnchor);},true);
    root.__lcdpResizeObserver=new ResizeObserver(()=>{if(root.__lcdpAnchor)positionLCDPPopup(root,root.__lcdpAnchor);}); root.__lcdpResizeObserver.observe(root);
    root.__lcdpListeners=true;
  }
}
'''

