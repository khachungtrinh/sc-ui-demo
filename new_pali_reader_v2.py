# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Components v2 Pāli reader functional island.

This module is intentionally isolated from ``new_dict_lookup_pli.py``.  It is
not a replacement for the mature legacy reader yet; it is a reference reader
for moving high-frequency reader interaction into the browser while keeping
Streamlit/Python responsible for data preparation and backend dictionary reads.

Current reader boundary
----------------------
Supported intentionally:
* ``dict_pos='left'`` (dictionary panels live inside the component);
* browser-local Pāli word selection;
* browser-local English cross-dictionary lookup when ``dual_dict=True``;
* browser-local active/highlight state and scrolling;
* legacy-compatible Pāli glossary wrapping;
* no ``setStateValue`` / ``setTriggerValue`` calls back to Python.

Not supported intentionally in this reader:
* ``dict_pos='sidebar'``;
* parent-document popup/bridge behavior;
* ``popup_en_vi=True``.

Unsupported combinations must remain on ``render_pali_reader``.  The controlled
SS call-site performs that fallback.

Configuration
-------------
Enable/strict/metrics configuration lives in new_components_v2_config.py.

Security
--------
Components v2 are not iframe-sandboxed.  Reader and dictionary HTML is therefore
sanitized in the browser before insertion.  This reader is intended for the
application-owned corpus and dictionary payloads already used by the legacy
reader, not arbitrary uploaded HTML.
"""


from __future__ import annotations


import hashlib


import json


import logging


from typing import Any


from new_component_v2_support import get_v2_component, SAFE_HTML_JS


from new_components_v2_config import v2_metrics_enabled, record_v2_route


from new_reader_v2_primitives import LOOKUP_DOM_JS


from dict_lookup_assets import (
    DL_READER_FONT_SIZE, DL_READER_LINE_HEIGHT,
    build_reader_css, build_reader_surface_vars, build_pali_glossary_css,
    build_pali_glossary_map, filter_active_pali_glossary,
    merge_pali_glossary_into_lookup_dict,
    wrap_pali_text_phrase_mode, wrap_pali_text_token_mode,
)


LOGGER = logging.getLogger(__name__)


def pali_reader_v2_supported(*, dict_pos: str, popup_en_vi: bool) -> bool:
    """Return whether this intentionally narrow reader supports the call shape."""
    return str(dict_pos or "left").strip().lower() == "left" and not bool(popup_en_vi)


_COMPONENT_HTML = '<div class="pali-reader-v2-host" data-pali-reader-v2-root></div>'


_COMPONENT_CSS = build_reader_css(
    dict_width="300px",
    extra_vars=build_reader_surface_vars("left"),
    extra_css=r"""
.pali-reader-v2-host { width:100%; box-sizing:border-box; }
.main-wrapper { height:100%; gap:var(--dl-reader-gap); padding:0 0 5px 0; }
.text-col { min-width:0; }
.text-col > table { table-layout:auto; }
.text-col > table td { padding:var(--dl-cell-padding); vertical-align:middle; }
.id-col { font-family:var(--dl-font-mono), monospace; font-size:var(--dl-code-font-size);
          width:1%; white-space:nowrap; text-align:center; color:inherit; }
.content-col { font-size:var(--pr-content-font-size, var(--dl-reader-font-size));
               line-height:var(--pr-content-line-height, var(--dl-reader-line-height)); }
.pali-word { border-radius:3px; padding:0 1px; display:inline; transition:0.15s; }
""" + build_pali_glossary_css() + r"""
.eng-sub-word:hover { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--dl-scrollbar-thumb); border-radius:var(--dl-scrollbar-radius); }
""",
).replace(":root", ".pali-reader-v2-host").replace("html,\nbody", ".pali-reader-v2-host").replace("body {", ".pali-reader-v2-host {")


_COMPONENT_JS = SAFE_HTML_JS + LOOKUP_DOM_JS + r"""
function showEnglishMeaning(root, target) {
  const state = root.__paliReaderState || {enDict:{}};
  const box = root.querySelector("[data-pr-en-dict]");
  if (!target || !box) return;
  root.querySelectorAll(".eng-sub-word.active-en").forEach(el => el.classList.remove("active-en"));
  target.classList.add("active-en");
  const word = target.getAttribute("data-word") || target.textContent || "";
  const meaning = getEnglishMeaning(state.enDict, word);
  const body = meaning ? sanitizeHtml(meaning)
    : "<div style='color:var(--dl-en);margin-top:10px;'>Không tìm thấy nghĩa Anh-Việt.</div>";
  box.innerHTML = `
    <div style="font-size:1.2rem;color:var(--dl-en);font-weight:600;border-bottom:2px solid var(--dl-border);margin-bottom:10px;padding-bottom:5px;display:flex;align-items:center;">
      <span style="font-size:.65rem;background:var(--dl-en);color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">En</span>
      ${escapeHtml(word)}
    </div>
    ${body}`;
}

export default function(component) {
  const { data, parentElement } = component;
  const root = parentElement.querySelector("[data-pali-reader-v2-root]");
  if (!root) return;

  const contentId = String(data?.content_id || "");
  const previousId = root.dataset.contentId || "";
  const sameContent = previousId === contentId;
  const oldText = root.querySelector("[data-pr-text]");
  const previousScrollTop = oldText ? oldText.scrollTop : 0;

  root.style.height = `${Number(data?.height || 700)}px`;
  root.style.setProperty("--dl-panel-width", String(data?.dict_width || "300px"));
  root.style.setProperty("--pr-content-font-size", String(data?.font_size || "1rem"));
  root.style.setProperty("--pr-content-line-height", String(data?.line_height || "1.6"));

  const typography = data?.typography_vars || {};
  for (const [key, value] of Object.entries(typography)) {
    if (String(key).startsWith("--dl-") || String(key).startsWith("--pr-")) {
      root.style.setProperty(String(key), String(value));
    }
  }

  if (!sameContent) {
    root.innerHTML = `
      <div class="pali-reader-v2-layout main-wrapper">
        <div class="pali-reader-v2-dict-col dict-col-container" data-pr-dict-col>
          <div class="pali-reader-v2-dict-box sub-dict-box ${data?.dual_dict ? "top-box" : "single-box"}" data-pr-pali-dict>
            <i style="color:#888;"></i>
          </div>
          ${data?.dual_dict ? `
            <div class="pali-reader-v2-dict-box sub-dict-box bottom-box" data-pr-en-dict>
              <i style="color:#888;"></i>
            </div>` : ""}
        </div>
        <div class="pali-reader-v2-text text-col" data-pr-text>
          <table class="pali-reader-v2-table"><tbody data-pr-rows></tbody></table>
        </div>
      </div>`;

    const tbody = root.querySelector("[data-pr-rows]");
    for (const row of (data?.rows || [])) {
      const tr = document.createElement("tr");
      if (data?.show_id) {
        const idCell = document.createElement("td");
        idCell.className = "pali-reader-v2-id id-col";
        idCell.textContent = String(row?.id || "");
        tr.appendChild(idCell);
      }
      const contentCell = document.createElement("td");
      contentCell.className = "pali-reader-v2-content content-col";
      contentCell.innerHTML = sanitizeHtml(row?.html || "");
      tr.appendChild(contentCell);
      tbody.appendChild(tr);
    }

    root.dataset.contentId = contentId;
  }

  const textArea = root.querySelector("[data-pr-text]");

  // Keep the latest payload on the stable root. Event listeners are bound only
  // once, but read this object dynamically so document/lookup changes never use
  // stale dictionaries or stale DOM references.
  root.__paliReaderState = {
    paliDict: data?.pali_lookup || {},
    enDict: data?.en_lookup || {},
    dualDict: Boolean(data?.dual_dict)
  };

  if (!root.dataset.listenersBound) {
    root.addEventListener("click", (event) => {
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;

      const state = root.__paliReaderState || { paliDict: {}, enDict: {}, dualDict: false };
      const paliBox = root.querySelector("[data-pr-pali-dict]");
      const enBox = root.querySelector("[data-pr-en-dict]");

      const paliTarget = target.closest(".pali-word");
      if (paliTarget && root.contains(paliTarget)) {
        root.querySelectorAll(".pali-word.active").forEach((el) => el.classList.remove("active"));
        root.querySelectorAll(".eng-sub-word.active-en").forEach((el) => el.classList.remove("active-en"));
        paliTarget.classList.add("active");

        const rawWord = paliTarget.getAttribute("data-word") || paliTarget.textContent || "";
        const clean = normalizePali(rawWord);
        const meaning = getPaliMeaning(state.paliDict, rawWord, clean);
        const safeClean = encodeURIComponent(clean);

        if (paliBox) {
          const body = meaning
            ? sanitizeHtml(meaning)
            : "<div style='color:#d63031;'>Không tìm thấy dữ liệu.</div>";
          paliBox.innerHTML = `
            <div style="font-size:1.2rem;color:#d63031;font-weight:600;border-bottom:2px solid #d3d2ca;margin-bottom:10px;padding-bottom:5px;display:flex;align-items:center;">
              <span style="font-size:.65rem;background:#d63031;color:white;padding:2px 6px;border-radius:4px;margin-right:8px;text-transform:uppercase;">Pali</span>
              <a href="/sc?q=${safeClean}" target="_blank" rel="noopener noreferrer" style="color:var(--dl-pali);text-decoration:underline;">${escapeHtml(clean)}</a>
            </div>
            <div data-pr-pali-meaning>${body}</div>`;
          if (state.dualDict) decorateEnglishWords(paliBox.querySelector("[data-pr-pali-meaning]"), state.enDict);
        }
        return;
      }

      const enTarget = target.closest(".eng-sub-word");
      if (enTarget && root.contains(enTarget) && enBox) {
        showEnglishMeaning(root, enTarget);
      }
    });

    root.addEventListener("mouseover", (event) => {
      const target = event.target instanceof Element ? event.target.closest(".eng-sub-word") : null;
      if (!target || !root.contains(target)) return;
      showEnglishMeaning(root, target);
    });

    root.dataset.listenersBound = "1";
  }

  if (sameContent && textArea) textArea.scrollTop = previousScrollTop;
}
"""


def _pali_reader_v2_component(**kwargs):
    renderer = get_v2_component('scapp_pali_reader_v2', _COMPONENT_HTML, _COMPONENT_CSS, _COMPONENT_JS)
    return renderer(**kwargs)


def _reader_fingerprint(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:20]


def _prepare_rows(
    pali_dict: dict[Any, Any],
    *,
    active_glossary_map: dict[str, dict[str, str]],
    allow_glossary_phrases: bool,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_id, raw_text in pali_dict.items():
        row_id = str(raw_id)
        display_id = row_id.split(":")[-1] if ":" in row_id else row_id
        text = str(raw_text)
        if allow_glossary_phrases:
            wrapped = wrap_pali_text_phrase_mode(text, active_glossary_map)
        else:
            wrapped = wrap_pali_text_token_mode(text, active_glossary_map)
        rows.append({"id": display_id, "html": wrapped})
    return rows

