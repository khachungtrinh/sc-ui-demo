"""Optional keyword highlighting for reader iframes; no dictionary/data access."""

import json


def build_keyword_highlight_assets(word, *, root_selector, auto_run=True):
    """Highlight a literal word/phrase, ignoring case/diacritics.

    Only text nodes change. Lookup attributes/listeners remain on their original
    elements. Empty input emits nothing, preserving the existing reader HTML.
    LCDP runs the function after its lookup spans have been created.
    """
    word = str(word or "").strip()
    if not word:
        return ""

    def script_json(value):
        return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    script = r"""
function applyReaderKeywordHighlight() {
    const root = document.querySelector(__ROOT__);
    if (!root) return;
    function fold(text) {
        let value = "", starts = [], ends = [], offset = 0;
        for (const char of text) {
            const start = offset;
            offset += char.length;
            const plain = char.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replace(/đ/g, "d");
            if (!plain && ends.length) ends[ends.length - 1] = offset;
            for (const part of plain) {
                const normalized = /\s/u.test(part) ? " " : part;
                if (normalized === " " && value.endsWith(" ")) {
                    ends[ends.length - 1] = offset;
                    continue;
                }
                value += normalized;
                for (let i = 0; i < normalized.length; i++) {
                    starts.push(start); ends.push(offset);
                }
            }
        }
        return {value, starts, ends};
    }
    const keyword = fold(__WORD__).value.trim();
    if (!keyword) return;
    const groups = [];
    let group = null;
    const walker = document.createTreeWalker(root, 4); // SHOW_TEXT
    let node;
    while ((node = walker.nextNode())) {
        const parent = node.parentElement;
        if (!parent || parent.closest("mark.reader-keyword-highlight")) {
            group = null;
            continue;
        }
        if (parent.closest("script,style,noscript,textarea,button,select,.meaning,.dl-hover-popup,.id-col")) continue;
        const block = parent.closest("p,li,td,th,h1,h2,h3,h4,h5,h6,blockquote,div") || root;
        if (!group || group.block !== block) {
            group = {block, text: "", nodes: []}; groups.push(group);
        }
        group.nodes.push({node, start: group.text.length, end: group.text.length + node.data.length});
        group.text += node.data;
    }
    for (const item of groups) {
        const folded = fold(item.text), matches = [];
        let position = 0;
        while ((position = folded.value.indexOf(keyword, position)) !== -1) {
            matches.push([folded.starts[position], folded.ends[position + keyword.length - 1]]);
            position += keyword.length;
        }
        if (!matches.length) continue;
        let matchIndex = 0;
        for (const entry of item.nodes) {
            while (matchIndex < matches.length && matches[matchIndex][1] <= entry.start) matchIndex++;
            const overlaps = [];
            for (let i = matchIndex; i < matches.length && matches[i][0] < entry.end; i++) {
                overlaps.push([Math.max(0, matches[i][0] - entry.start), Math.min(entry.end, matches[i][1]) - entry.start]);
            }
            if (!overlaps.length) continue;
            const fragment = document.createDocumentFragment();
            let cursor = 0;
            for (const [start, end] of overlaps) {
                fragment.appendChild(document.createTextNode(entry.node.data.slice(cursor, start)));
                const mark = document.createElement("mark");
                mark.className = "reader-keyword-highlight";
                mark.textContent = entry.node.data.slice(start, end);
                fragment.appendChild(mark);
                cursor = end;
            }
            fragment.appendChild(document.createTextNode(entry.node.data.slice(cursor)));
            entry.node.parentNode.replaceChild(fragment, entry.node);
        }
    }
}
"""
    script = script.replace("__ROOT__", script_json(root_selector)).replace("__WORD__", script_json(word))
    if auto_run:
        script += """
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyReaderKeywordHighlight, {once: true});
} else {
    applyReaderKeywordHighlight();
}
"""
    return """<style>
.reader-keyword-highlight {
    background-color: #ffe066; color: inherit; font: inherit;
    padding: 0; border-radius: 2px; pointer-events: none;
}
</style><script>""" + script + "</script>"
