# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
from __future__ import annotations


import html


import re


from bisect import bisect_left, bisect_right


from pathlib import Path


from typing import Any


def _normalize_search_text(value: str | None) -> str:
    """Normalize user-entered whitespace without changing searchable letters."""

    return re.sub(r"\s+", " ", value or "").strip()


def _keyword_regex(keyword: str) -> re.Pattern[str]:
    """Create a literal phrase regex that tolerates varying whitespace."""

    parts = _normalize_search_text(keyword).split(" ")
    pattern = r"\s+".join(re.escape(part) for part in parts if part)
    return re.compile(pattern, re.IGNORECASE)


def find_keyword_matches(text: str, keyword: str) -> list[re.Match[str]]:
    """Return literal phrase matches using the canonical whitespace semantics."""

    if not text or not _normalize_search_text(keyword):
        return []
    return list(_keyword_regex(keyword).finditer(text))


def highlight_keywords(
    text: str,
    keyword_styles: list[tuple[str, str]],
) -> str:
    """Escape raw text and highlight canonical, non-overlapping phrase matches.

    Keywords earlier in ``keyword_styles`` have priority when matches overlap.
    The function always expects raw text and returns safe HTML.
    """

    if not text:
        return ""

    selected: list[tuple[int, int, str]] = []

    for keyword, color in keyword_styles:
        if not _normalize_search_text(keyword):
            continue

        for match in find_keyword_matches(text, keyword):
            start, end = match.span()
            overlaps_existing = any(
                start < existing_end and end > existing_start
                for existing_start, existing_end, _ in selected
            )
            if overlaps_existing:
                continue
            selected.append((start, end, color))

    if not selected:
        return html.escape(text).replace("~", "&#126;")

    selected.sort(key=lambda item: item[0])
    output: list[str] = []
    cursor = 0

    for start, end, color in selected:
        output.append(html.escape(text[cursor:start]).replace("~", "&#126;"))
        matched_text = html.escape(text[start:end]).replace("~", "&#126;")
        safe_color = html.escape(color, quote=True)
        output.append(
            '<mark style="background-color: '
            f'{safe_color}; color: black; padding: 0 2px; border-radius: 2px;">'
            f'{matched_text}</mark>'
        )
        cursor = end

    output.append(html.escape(text[cursor:]).replace("~", "&#126;"))
    return "".join(output)


def highlight_text(text: str, keyword: str, color: str = "#ffcf33") -> str:
    """Backward-compatible single-keyword wrapper around ``highlight_keywords``."""

    return highlight_keywords(text, [(keyword, color)])


def extract_all_snippets(text: str, keyword: str, window: int = 350) -> list[str]:
    """Extract all non-overlapping snippets around literal keyword matches."""

    if not text or not keyword:
        return []

    matches = find_keyword_matches(text, keyword)
    snippets: list[dict[str, Any]] = []
    last_end = -1

    for match in matches:
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)

        if start <= last_end and snippets:
            snippets[-1]["content"] += text[snippets[-1]["end_idx"]:end]
            snippets[-1]["end_idx"] = end
        else:
            snippets.append({"content": text[start:end], "start_idx": start, "end_idx": end})

        last_end = end

    return [snippet["content"] for snippet in snippets]

