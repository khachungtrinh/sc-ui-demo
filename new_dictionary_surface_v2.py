"""Cross-root Components v2 surfaces for prepared dictionary readers.

The surface is a browser-local companion for reader components.  It owns only
presentation/lifecycle state; canonical lookup data is still prepared by Python.
Reader and sidebar components communicate through a same-document CustomEvent,
so ordinary dictionary interaction does not trigger a Streamlit rerun.
"""
from __future__ import annotations

import hashlib
from typing import Any

from new_component_v2_support import SAFE_HTML_JS, get_v2_component
from new_reader_v2_primitives import LOOKUP_DOM_JS

_EVENT_NAME = "scapp-dictionary-v2-surface"


def make_dictionary_surface_channel(feature: str, resource_id: str, role: str = "sidebar") -> str:
    raw = f"{feature}|{resource_id}|{role}".encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:24]


_HTML = '<section class="dictionary-sidebar-v2" data-dictionary-sidebar-v2></section>'
_CSS = r'''
.dictionary-sidebar-v2 {
  width:100%; box-sizing:border-box; min-height:2.8rem; position:relative;
  background:var(--dl-bg-sidebar,#f4f3ec); color:var(--dl-text,#3d3a2a);
  border:1px solid var(--dl-border,#d3d2ca); padding:12px 14px;
  font-family:"Source Sans","Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:1rem; line-height:1.6; overflow-wrap:anywhere;
  scrollbar-width:thin; scrollbar-color:rgba(61,58,42,.10) transparent;
}
.dictionary-sidebar-v2[data-profile="english"] { background:var(--eng-bg-main,#fdfdf8); }
.dictionary-sidebar-v2[data-dark="1"] { background:#1e1e1e; color:#f0f0f0; border-color:#444; }
.dictionary-sidebar-v2[data-dark="1"] .dictionary-surface-popup { background:#1e1e1e; color:#f0f0f0; border-color:#444; box-shadow:0 4px 18px rgba(0,0,0,.55); }
.dictionary-sidebar-v2::-webkit-scrollbar {width:3px;height:3px;}
.dictionary-sidebar-v2::-webkit-scrollbar-track {background:transparent;}
.dictionary-sidebar-v2::-webkit-scrollbar-thumb {background:rgba(61,58,42,.10);border-radius:999px;}
.dictionary-sidebar-v2 .stored-pali-entry + .stored-pali-entry {
  margin-top:12px; padding-top:12px; border-top:1px solid var(--dl-border,#d3d2ca);
}
.dictionary-sidebar-v2 .eng-sub-word { cursor:pointer; border-bottom:1px dashed #b2bec3; transition:.15s; }
.dictionary-sidebar-v2 .eng-sub-word:hover { color:#5d7367; border-bottom-color:#5d7367; }
.dictionary-sidebar-v2 .eng-sub-word.active-en { background:#5d7367; color:white; border:none; padding:0 2px; border-radius:2px; }
.dictionary-sidebar-v2 code,.dictionary-sidebar-v2 pre {
  font-family:"SpaceMono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.75rem; background:var(--dl-code-bg,#ecebe4);
}
.dictionary-sidebar-v2 .dictionary-surface-popup {
  position:fixed; z-index:999999; display:none;
  min-width:min(20em,calc(100vw - 24px)); width:min(500px,calc(100vw - 24px));
  max-height:calc(100vh - 24px); overflow:auto;
  background:var(--dl-popup-bg,var(--dl-bg,#ecebe3)); color:var(--dl-text,#3d3a2a);
  border:1px solid var(--dl-border,#d3d2ca); box-shadow:0 4px 18px rgba(0,0,0,.18);
  padding:12px; box-sizing:border-box;
}
.dictionary-sidebar-v2 .dictionary-surface-popup.visible { display:block; }
'''
_JS = SAFE_HTML_JS + LOOKUP_DOM_JS + rf'''
const EVENT_NAME = {repr(_EVENT_NAME)};

function setDictionarySurfacePlaceholder(root, text) {{
  const node = document.createElement("i");
  node.style.color = "#888";
  node.textContent = String(text || "");
  root.replaceChildren(node);
}}

function clearDictionarySurfaceEnglish(root) {{
  root.querySelectorAll(".eng-sub-word.active-en").forEach(el => el.classList.remove("active-en"));
}}

function hideDictionarySurfacePopup(root) {{
  const popup = root.querySelector("[data-dictionary-surface-popup]");
  if (popup) {{ popup.classList.remove("visible"); popup.innerHTML = ""; }}
  root.__dictionarySurfacePopupAnchor = null;
}}

function positionDictionarySurfacePopup(root, anchor) {{
  const popup = root.querySelector("[data-dictionary-surface-popup]");
  if (!popup || !popup.classList.contains("visible") || !anchor) return;
  const margin = 12, gap = 8;
  const vw = document.documentElement.clientWidth || window.innerWidth;
  const vh = document.documentElement.clientHeight || window.innerHeight;
  popup.style.left = "0px"; popup.style.top = "0px";
  const ar = anchor.getBoundingClientRect();
  const pr = popup.getBoundingClientRect();
  const pw = Math.min(pr.width, Math.max(0, vw - margin * 2));
  const ph = Math.min(pr.height, Math.max(0, vh - margin * 2));
  const below = vh - ar.bottom - gap - margin;
  const above = ar.top - gap - margin;
  const down = ph <= below ? true : ph <= above ? false : below >= above;
  const clamp = (v, min, max) => max < min ? min : Math.min(Math.max(v, min), max);
  popup.style.left = Math.round(clamp(ar.left, margin, vw - margin - pw)) + "px";
  popup.style.top = Math.round(clamp(down ? ar.bottom + gap : ar.top - gap - ph, margin, vh - margin - ph)) + "px";
}}

function showDictionarySurfacePopup(root, anchor, html) {{
  let popup = root.querySelector("[data-dictionary-surface-popup]");
  if (!popup) {{
    popup = document.createElement("div");
    popup.className = "dictionary-surface-popup";
    popup.dataset.dictionarySurfacePopup = "1";
    root.appendChild(popup);
  }}
  popup.innerHTML = sanitizeHtml(String(html || ""));
  popup.classList.add("visible");
  root.__dictionarySurfacePopupAnchor = anchor;
  positionDictionarySurfacePopup(root, anchor);
}}

function dictionarySurfaceEnglishContent(word, meaning) {{
  const body = meaning
    ? sanitizeHtml(meaning)
    : "<div style='color:#5d7367;margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";
  return `<div style="font-size:1.2rem;color:#5d7367;font-weight:600;border-bottom:2px solid #d3d2ca;margin-bottom:10px;padding-bottom:5px;display:flex;align-items:center;"><span style="font-size:.65rem;background:#5d7367;color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">En</span>${{escapeHtml(word)}}</div>${{body}}`;
}}

function dispatchDictionarySurface(channel, resourceId, html, append=false) {{
  if (!channel || !resourceId) return false;
  window.dispatchEvent(new CustomEvent(EVENT_NAME, {{detail:{{
    channel:String(channel), resource_id:String(resourceId), html:String(html || ""), append:Boolean(append)
  }}}}));
  return true;
}}

function decorateDictionarySurfaceEnglish(root, state) {{
  if (!state?.decorate_english || !state?.en_lookup) return;
  const targets = root.querySelectorAll("[data-pr-pali-meaning], [data-dictionary-pali-meaning]");
  if (targets.length) targets.forEach(el => decorateEnglishWords(el, state.en_lookup, "pali"));
}}

function handleDictionarySurfaceEnglish(root, target) {{
  const state = root.__dictionarySurfaceData || {{}};
  if (!state.en_lookup) return;
  const word = String(target.getAttribute("data-word") || target.textContent || "").trim().toLowerCase();
  if (!word) return;
  clearDictionarySurfaceEnglish(root);
  target.classList.add("active-en");
  const meaning = getEnglishMeaning(state.en_lookup, word);
  const content = dictionarySurfaceEnglishContent(word, meaning);
  if (state.popup_en_vi) {{
    showDictionarySurfacePopup(root, target, content);
  }} else if (state.english_channel) {{
    hideDictionarySurfacePopup(root);
    dispatchDictionarySurface(state.english_channel, state.resource_id, content, false);
  }}
}}

function applyDictionarySurfaceHtml(root, detail, state) {{
  const safe = sanitizeHtml(String(detail.html || ""));
  if (detail.append) {{
    const placeholder = root.querySelector("i");
    if (placeholder && !root.querySelector(".stored-pali-entry")) placeholder.remove();
    const item = document.createElement("div");
    item.className = "stored-pali-entry";
    item.innerHTML = safe;
    root.appendChild(item);
  }} else if (safe) {{
    root.innerHTML = safe;
  }} else {{
    setDictionarySurfacePlaceholder(root, state.placeholder || "");
  }}
  decorateDictionarySurfaceEnglish(root, state);
}}

function resetDictionarySurface(root, data) {{
  root.dataset.profile = String(data?.profile || "pali");
  root.dataset.dark = data?.dark_mode ? "1" : "0";
  root.style.maxHeight = data?.height ? `${{Number(data.height)}}px` : "";
  root.style.overflowY = data?.height ? "auto" : "";
  setDictionarySurfacePlaceholder(root, data?.placeholder || "");
  root.dataset.resourceId = String(data?.resource_id || "");
  hideDictionarySurfacePopup(root);
}}

function ensureDictionarySurfaceBus() {{
  if (window.__scappDictionarySurfaceBus) return window.__scappDictionarySurfaceBus;
  const bus = {{targets:new Map()}};
  window.addEventListener(EVENT_NAME, event => {{
    const detail = event?.detail || {{}};
    const channel = String(detail.channel || "");
    const ref = bus.targets.get(channel);
    const root = ref && typeof ref.deref === "function" ? ref.deref() : null;
    if (!root) {{ if (ref) bus.targets.delete(channel); return; }}
    const current = root.__dictionarySurfaceData || {{}};
    if (String(detail.resource_id || "") !== String(current.resource_id || "")) return;
    applyDictionarySurfaceHtml(root, detail, current);
  }});
  window.__scappDictionarySurfaceBus = bus;
  return bus;
}}

export default function(component) {{
  const {{data,parentElement}} = component;
  const root = parentElement.querySelector("[data-dictionary-sidebar-v2]");
  if (!root || data?.version !== 1) return;
  const previousResource = root.dataset.resourceId || "";
  if (previousResource !== String(data.resource_id || "")) resetDictionarySurface(root, data);
  const bus = ensureDictionarySurfaceBus();
  const previousChannel = String(root.dataset.channel || "");
  const nextChannel = String(data.channel || "");
  if (previousChannel && previousChannel !== nextChannel) bus.targets.delete(previousChannel);
  root.__dictionarySurfaceData = data;
  root.dataset.channel = nextChannel;
  if (typeof WeakRef === "function") bus.targets.set(nextChannel, new WeakRef(root));
  else bus.targets.set(nextChannel, {{deref:()=>root}});

  if (!root.dataset.listenersBound) {{
    root.addEventListener("click", event => {{
      const target = event.target instanceof Element ? event.target.closest(".eng-sub-word") : null;
      if (target && root.contains(target)) {{ event.preventDefault(); handleDictionarySurfaceEnglish(root, target); return; }}
      if (!(event.target instanceof Element && event.target.closest("[data-dictionary-surface-popup]"))) hideDictionarySurfacePopup(root);
    }});
    root.addEventListener("mouseover", event => {{
      const target = event.target instanceof Element ? event.target.closest(".eng-sub-word") : null;
      if (!target || !root.contains(target)) return;
      if (event.relatedTarget instanceof Node && target.contains(event.relatedTarget)) return;
      handleDictionarySurfaceEnglish(root, target);
    }});
    root.addEventListener("scroll", () => {{
      if (root.__dictionarySurfacePopupAnchor) positionDictionarySurfacePopup(root, root.__dictionarySurfacePopupAnchor);
    }}, true);
    root.dataset.listenersBound = "1";
  }}
}}
'''


def render_dictionary_sidebar_surface(
    feature: str,
    *,
    channel: str,
    resource_id: str,
    placeholder: str,
    profile: str = "pali",
    height: int | None = None,
    key_suffix: str = "sidebar",
    en_lookup: dict[str, str] | None = None,
    decorate_english: bool = False,
    popup_en_vi: bool = False,
    english_channel: str = "",
    dark_mode: bool = False,
) -> Any:
    """Mount one browser-local sidebar target for a prepared reader.

    ``en_lookup`` is optional.  When supplied for a Pāli surface, English words
    inside marked Pāli meanings can keep the legacy dual-dictionary overlay
    without any Python bridge.  ``english_channel`` targets a second sidebar
    surface; ``popup_en_vi`` keeps the English result as a local popup instead.
    """
    data = {
        "version": 1,
        "channel": str(channel),
        "resource_id": str(resource_id),
        "placeholder": str(placeholder),
        "profile": "english" if str(profile).lower() == "english" else "pali",
        "height": int(height) if height else 0,
        "en_lookup": dict(en_lookup or {}),
        "decorate_english": bool(decorate_english),
        "popup_en_vi": bool(popup_en_vi),
        "english_channel": str(english_channel or ""),
        "dark_mode": bool(dark_mode),
    }
    import streamlit as st
    renderer = get_v2_component("scapp_dictionary_sidebar_surface_v2", _HTML, _CSS, _JS)
    with st.sidebar:
        return renderer(data=data, key=f"scapp_dictionary_sidebar_surface_v2:{feature}:{key_suffix}")


def dictionary_surface_event_js() -> str:
    """JS helper inserted into reader components that publish sidebar updates."""
    return rf'''
const DICTIONARY_SURFACE_EVENT = {repr(_EVENT_NAME)};
function emitDictionarySurface(root, html, append=false) {{
  const state = root.__dictState || root.__panelState || root.__paliReaderState || root.__lcdpState || {{}};
  const channel = String(state.sidebar_channel || "");
  const resourceId = String(state.resource_id || state.content_id || "");
  if (!channel || !resourceId) return false;
  window.dispatchEvent(new CustomEvent(DICTIONARY_SURFACE_EVENT, {{detail:{{
    channel:channel, resource_id:resourceId, html:String(html || ""), append:Boolean(append)
  }}}}));
  return true;
}}
'''
