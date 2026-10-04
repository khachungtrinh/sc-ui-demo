"""Small primitives shared by the application Components v2 readers.

Only immutable component definitions are cached here; never business/user data.
Importing this module does not require Components v2 on a legacy runtime.
"""
from functools import lru_cache


@lru_cache(maxsize=8)
def get_v2_component(name, html, css, js):
    try:
        from streamlit.components.v2 import component
    except ImportError as exc:
        raise RuntimeError("Components v2 is unavailable; use the legacy renderer.") from exc
    return component(name=name, html=html, css=css, js=js, isolate_styles=True)


# Shared HTML policy. DT text readers use text/mark nodes and no HTML sink.
# This is an app-owned corpus/dictionary boundary, not an arbitrary HTML viewer.
SAFE_HTML_JS = r"""
const DROP_TAGS = new Set([
  "script", "style", "noscript", "template", "iframe", "object", "embed",
  "link", "meta", "base", "form", "input", "button", "textarea", "select",
  "option", "svg", "math", "canvas"
]);
const ALLOWED_TAGS = new Set([
  "p", "div", "span", "br", "hr", "a", "strong", "b", "em", "i", "u",
  "s", "small", "sub", "sup", "h1", "h2", "h3", "h4", "h5", "h6",
  "ul", "ol", "li", "dl", "dt", "dd", "blockquote", "pre", "code",
  "section", "article", "center", "font", "table", "thead", "tbody",
  "tfoot", "tr", "th", "td", "caption", "ruby", "rt", "rp", "mark"
]);
const ALLOWED_ATTRS = new Set([
  "class", "id", "title", "lang", "dir", "style", "href", "target", "rel",
  "colspan", "rowspan", "color", "face", "size"
]);
const SAFE_STYLE_PROPERTIES = new Set([
  "color", "background", "background-color", "font-family", "font-size", "font-style",
  "font-weight", "line-height", "letter-spacing", "word-spacing", "text-align",
  "text-decoration", "vertical-align", "white-space", "border", "border-color",
  "border-style", "border-width", "border-radius", "border-bottom", "border-left",
  "border-right", "border-top", "padding", "padding-top", "padding-bottom",
  "padding-left", "padding-right", "margin", "margin-top", "margin-bottom",
  "margin-left", "margin-right"
]);
function isSafeUrl(value) {
  try {
    const url = new URL(String(value || "").trim(), window.location.origin);
    return ["http:", "https:", "mailto:"].includes(url.protocol);
  } catch (_) { return false; }
}
function safeStyle(value) {
  // Reject escapes/comments/control characters rather than trying to decode
  // CSS that could hide a url(), expression(), or an unknown function.
  const raw = String(value || "");
  if (/[\\\x00-\x1f]|\/\*|\*\//.test(raw)) return "";
  const result = [];
  for (const declaration of raw.split(";")) {
    const colon = declaration.indexOf(":");
    if (colon < 0) continue;
    const property = declaration.slice(0, colon).trim().toLowerCase();
    const val = declaration.slice(colon + 1).trim();
    if (!SAFE_STYLE_PROPERTIES.has(property)) continue;
    if (!/^[a-zA-Z0-9\s#.,%()'"!+\/-]+$/.test(val)) continue;
    const functions = Array.from(val.matchAll(/([a-z-]+)\s*\(/gi), match => match[1].toLowerCase());
    if (functions.some(name => !["rgb", "rgba", "hsl", "hsla"].includes(name))) continue;
    result.push(`${property}:${val}`);
  }
  return result.join(";");
}
function sanitizeHtml(rawHtml) {
  const template = document.createElement("template");
  template.innerHTML = String(rawHtml || "");
  for (const element of Array.from(template.content.querySelectorAll("*"))) {
    const tag = element.tagName.toLowerCase();
    if (DROP_TAGS.has(tag)) { element.remove(); continue; }
    if (!ALLOWED_TAGS.has(tag)) {
      const fragment = document.createDocumentFragment();
      while (element.firstChild) fragment.appendChild(element.firstChild);
      element.replaceWith(fragment);
      continue;
    }
    for (const attr of Array.from(element.attributes)) {
      const name = attr.name.toLowerCase();
      if (name.startsWith("on") || (!ALLOWED_ATTRS.has(name) && !name.startsWith("data-") && !name.startsWith("aria-"))) {
        element.removeAttribute(attr.name);
      } else if (name === "href" && !isSafeUrl(attr.value)) {
        element.removeAttribute(attr.name);
      } else if (name === "style") {
        const clean = safeStyle(attr.value);
        if (clean) element.setAttribute("style", clean);
        else element.removeAttribute("style");
      }
    }
    if (tag === "a" && element.getAttribute("target") === "_blank") element.setAttribute("rel", "noopener noreferrer");
  }
  return template.innerHTML;
}
"""
