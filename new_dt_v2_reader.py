"""Canonical range preparation and DOM primitives used by both DT L2 readers.
No application state/cache or browser/Python bridge is owned here.
"""
from bisect import bisect_left
import re
from new_dt_search_service import _keyword_regex, _normalize_search_text


def prepare_ranges(content, offsets, queries, *, max_matches, error_type):
    if any(len(value) > 4096 for value in queries):
        raise error_type("keyword_limit")
    patterns = [_keyword_regex(value) if _normalize_search_text(value) else None for value in queries]
    marks = []
    examined = 0
    for start, end in offsets:
        first = []
        for priority, pattern in enumerate(patterns):
            if pattern is None:
                continue
            # pos/endpos gives exactly the legacy per-page matching boundary,
            # including matches that would be missed by matching the whole text.
            first_starts = [a for a, _ in first] if priority else []
            for match in pattern.finditer(content, start, end):
                examined += 1
                if examined > max_matches:
                    raise error_type("match_limit")
                a, b = match.span()
                if priority:
                    at = bisect_left(first_starts, a)
                    if (at > 0 and first[at-1][1] > a) or (at < len(first) and first[at][0] < b):
                        continue
                else:
                    first.append((a, b))
                marks.append((a, b, priority))
    marks.sort(key=lambda item: item[0])
    # Python indexes code points; JS String.slice indexes UTF-16 code units.
    astral = [match.start() for match in re.finditer(r'[\U00010000-\U0010ffff]', content)]
    def units(index):
        return index + bisect_left(astral, index)
    pages = [[units(a), units(b)] for a, b in offsets]
    spans = [[units(a), units(b), color] for a, b, color in marks]
    return pages, spans

DT_READER_JS = r"""
function clampPage(page, count) {
  const value = Number.isInteger(page) ? page : 1;
  return Math.max(1, Math.min(value, count));
}
function composedParent(node) {
  return node?.parentElement || node?.getRootNode?.().host || null;
}
function scrollReaderTop(root) {
  let parent = composedParent(root);
  while (parent && parent !== document.body) {
    const style = window.getComputedStyle(parent);
    if (["auto", "scroll"].includes(style.overflowY) && parent.scrollHeight > parent.clientHeight) {
      const top = parent.scrollTop + root.getBoundingClientRect().top - parent.getBoundingClientRect().top;
      parent.scrollTo({top:Math.max(0, top), left:0, behavior:"auto"});
      return;
    }
    parent = composedParent(parent);
  }
  root.scrollIntoView({behavior:"auto", block:"start", inline:"nearest"});
}
function fillMarkedRange(container, data, start, end) {
  const fragment = document.createDocumentFragment();
  let cursor = start;
  // Only visit relevant spans. The payload is sorted and non-overlapping.
  let low = 0, high = data.marks.length;
  while (low < high) {
    const mid = Math.floor((low + high)/2);
    if (data.marks[mid][1] <= start) low = mid + 1;
    else high = mid;
  }
  for (let i = low; i < data.marks.length && data.marks[i][0] < end; i++) {
    const [a, b, color] = data.marks[i];
    if (a < start || b > end) continue;
    fragment.appendChild(document.createTextNode(data.text.slice(cursor, a)));
    const mark = document.createElement("mark");
    mark.style.backgroundColor = color === 0 ? "#ffcf33" : "#00ffcc";
    mark.textContent = data.text.slice(a, b);
    fragment.appendChild(mark);
    cursor = b;
  }
  fragment.appendChild(document.createTextNode(data.text.slice(cursor, end)));
  container.replaceChildren(fragment);
}
function renderPager(nav, currentPage, count) {
  nav.replaceChildren();
  nav.hidden = count <= 1;
  function button(label, page, disabled, current=false) {
    const control = document.createElement("button");
    control.type = "button";
    control.textContent = label;
    control.dataset.page = String(page);
    control.disabled = disabled;
    control.setAttribute("aria-label", /^\d+$/.test(label) ? `Trang ${label}` : label);
    if (current) control.setAttribute("aria-current", "page");
    nav.appendChild(control);
  }
  if (count > 1) {
    button("Trang Trước", currentPage-1, currentPage === 1);
    const visible = new Set([1, count]);
    for (let page = Math.max(1, currentPage-2); page <= Math.min(count, currentPage+2); page++) visible.add(page);
    let previous = 0;
    for (const page of Array.from(visible).sort((a,b) => a-b)) {
      if (previous && page-previous > 1) {
        const gap = document.createElement("span"); gap.textContent = "…"; nav.appendChild(gap);
      }
      button(String(page), page, false, page === currentPage);
      previous = page;
    }
    button("Trang Sau", currentPage+1, currentPage === count);
  }
}
"""
