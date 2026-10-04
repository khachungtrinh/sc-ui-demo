"""Local DOM helpers shared by prepared dictionary reader components."""
import re
from new_reader_highlight import build_keyword_highlight_assets


def reader_css_for_host(css):
    """Retarget canonical iframe roots; styles remain inside the ShadowRoot."""
    return re.sub(r"(?<![\w-])(?:html|body|:root)(?![\w-])", ".panel-reader-v2", css).replace("100vh", "100%")


# Adapt the existing literal highlight implementation, not its matching rules.
_assets = build_keyword_highlight_assets("__v2_keyword__", root_selector=".text-container", auto_run=False)
KEYWORD_CSS, _script = _assets.split("</style><script>", 1)
KEYWORD_CSS = KEYWORD_CSS.removeprefix("<style>")
KEYWORD_JS = (_script.removesuffix("</script>")
    .replace("function applyReaderKeywordHighlight()", "function applyReaderKeywordHighlight(host)")
    .replace('document.querySelector(".text-container")', 'host.querySelector(".text-container")')
    .replace('fold("__v2_keyword__")', 'fold(host.__panelState.highlight_word)'))

LOOKUP_DOM_JS = r"""
function normalizePali(raw) {
  return String(raw || "")
    .replace(/ṁ/g, "ṃ")
    .replace(/[^a-zA-Zāīūṅñṭḍṇḷṃ\s]/gi, "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, " ");
}

function getPaliMeaning(dict, rawWord, cleanWord) {
  if (!dict) return null;
  return dict[rawWord] || dict[String(rawWord || "").toLowerCase()] || dict[cleanWord] || null;
}

function getEnglishMeaning(dict, word) {
  if (!dict) return null;
  const clean = String(word || "").toLowerCase();
  return dict[clean] || null;
}

function decorateEnglishWords(container, enDict, profile="pali") {
  if (!container || !enDict) return;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);

  const wordPattern = profile === 'bilingual' ? /\b[A-Za-z]+\b/g : /[A-Za-z]+(?:'[A-Za-z]+)?/g;
  for (const textNode of nodes) {
    const parent = textNode.parentElement;
    if (!parent || parent.closest(profile === "bilingual" ? "script, style, .eng-sub-word" : "a, code, pre, .eng-sub-word")) continue;

    const text = textNode.nodeValue || "";
    let last = 0;
    let changed = false;
    const fragment = document.createDocumentFragment();

    text.replace(wordPattern, (match, offset) => {
      const clean = match.toLowerCase();
      if (profile === "bilingual" ? !enDict[clean] : !Object.prototype.hasOwnProperty.call(enDict, clean)) return match;

      changed = true;
      if (offset > last) fragment.appendChild(document.createTextNode(text.slice(last, offset)));
      const span = document.createElement("span");
      span.className = "eng-sub-word";
      span.dataset.word = clean;
      span.textContent = match;
      fragment.appendChild(span);
      last = offset + match.length;
      return match;
    });

    if (changed) {
      if (last < text.length) fragment.appendChild(document.createTextNode(text.slice(last)));
      textNode.replaceWith(fragment);
    }
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text || "");
  return div.innerHTML;
}

"""
