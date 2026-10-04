"""Pure preparation of the shared, read-only SS all-collections resource.

No Streamlit/Pandas, paths or user/session data at this boundary. Links come
from the application's existing formatter, not a second destination policy.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Callable
from urllib.parse import urlsplit

COLLECTION_TABLE_CACHE_VERSION = 2
RESOURCE_ID = 'ss:parallel-collection-table'
DISPLAY_MODES = (('text', 'Bảng văn bản'), ('online', 'Gắn hyperlink online'),
                 ('offline', 'Gắn hyperlink offline'))
COLUMNS = ('Mã Kinh', 'Tên Kinh', 'Mô tả ngắn', 'IRFF Tag', 'Các Kinh Song Song')


def resolve_irff_tag(sutta_id: str, topics: dict) -> str:
    """Preserve exact ordering/duplicates and sorted uppercase-prefix fallback."""
    upper = sutta_id.upper()
    exact = topics.get(upper) or topics.get(sutta_id)
    if isinstance(exact, list) and exact:
        return ' | '.join(exact)
    matched = set()
    for key, values in topics.items():
        if key.startswith(upper + ':') and isinstance(values, list):
            matched.update(values)
    return ' | '.join(sorted(matched))


def safe_collection_href(href: str | None) -> bool:
    if not href or any(ord(char) < 32 for char in href) or '\\' in href:
        return False
    parsed = urlsplit(href)
    if href.startswith('/ss?uid='):
        return not parsed.scheme and not parsed.netloc and parsed.path == '/ss'
    return parsed.scheme == 'https' and parsed.netloc == 'suttacentral.net' and parsed.path.startswith('/')


def _formatted_href(uid: str, formatter: Callable, *, online: bool) -> str | None:
    # The exact uncoloured label is known. Identity/IRFF never come from Markdown.
    formatted = formatter(uid, mode_online=online)
    prefix = '[' + uid + ']('
    if formatted == uid:
        return None  # Unsupported online prefixes intentionally remain text.
    if not isinstance(formatted, str) or not formatted.startswith(prefix) or not formatted.endswith(')'):
        raise ValueError('Unexpected collection link formatter shape')
    href = formatted[len(prefix):-1]
    if not safe_collection_href(href):
        raise ValueError('Unsafe collection link destination')
    return href


def resource_revision(resource: dict[str, Any]) -> str:
    body = {key: value for key, value in resource.items() if key != 'revision'}
    encoded = json.dumps(body, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def build_all_collection_table_resource(
    *, collection_map: dict[str, list[str]], parallels_list: list[list[str]],
    book_count_by_code: dict[str, int], load_sutta_titles_func: Callable,
    clean_sutra_id_func: Callable, natural_sort_key_func: Callable,
    get_blurb_func: Callable, format_link_markdown_func: Callable,
    sutta_to_topics: dict, cache_version: int = COLLECTION_TABLE_CACHE_VERSION,
) -> dict[str, Any]:
    """One canonical row per target; shared links, no mode-row copies.

    Current sc7.2 has Pāli titles and no PTS column. Prefix/merge/sort/count
    behavior follows that baseline, including singleton groups and overlap.
    """
    titles = load_sutta_titles_func() or {}
    if not isinstance(titles, dict):
        titles = {}
    topics = sutta_to_topics if isinstance(sutta_to_topics, dict) else {}
    prefix_records = sorted(
        ((str(prefix).strip(), name) for name, prefixes in collection_map.items()
         for prefix in prefixes if str(prefix).strip()),
        key=lambda item: len(item[0]), reverse=True)
    tables: dict[str, dict[str, set[str]]] = {name: {} for name in collection_map}
    for group in parallels_list:
        cleaned = {uid for item in group if (uid := clean_sutra_id_func(item))}
        for uid in cleaned:
            for prefix, name in prefix_records:
                if uid.startswith(prefix) and (len(uid) == len(prefix) or uid[len(prefix)].isdigit()):
                    tables[name].setdefault(uid, set()).update(cleaned - {uid})
    links: dict[str, dict[str, Any]] = {}

    def prepare_link(uid: str) -> None:
        if uid not in links:
            links[uid] = {'label': uid,
                          'online_href': _formatted_href(uid, format_link_markdown_func, online=True),
                          'offline_href': _formatted_href(uid, format_link_markdown_func, online=False)}

    collections = {}
    for name, prefixes in collection_map.items():
        table = tables[name]
        total = sum(book_count_by_code.get(prefix, 0) or 0 for prefix in prefixes)
        count = len(table)
        rows = []
        # The baseline natural key defines the order but leaves equal-key set
        # iteration unspecified. UID only breaks such ties for stable revisions.
        for uid in sorted(table, key=lambda key: (natural_sort_key_func(key, prefixes), key)):
            parallel_ids = sorted(table[uid], key=lambda key: (natural_sort_key_func(key), key))
            title_data = titles.get(uid, {})
            title = str(title_data.get('title_pali', '') or '').strip() if isinstance(title_data, dict) else ''
            rows.append({'sutta_id': uid, 'title_pali': title, 'description': get_blurb_func(uid) or '',
                         'irff_tag': resolve_irff_tag(uid, topics), 'parallels': parallel_ids})
            prepare_link(uid)
            for parallel_id in parallel_ids:
                prepare_link(parallel_id)
        collections[name] = {'label': name, 'statistics': {'count_with_parallels': count,
                             'total_in_collection': total, 'percentage': count / total * 100 if total > 0 else 0},
                             'rows': rows}
    resource = {'schema_version': 1, 'resource_id': RESOURCE_ID, 'cache_version': cache_version,
                'heading': 'Bảng dữ liệu song song toàn tập', 'columns': list(COLUMNS),
                'default_collection': next(iter(collection_map), ''), 'default_display_mode': 'offline',
                'display_modes': [{'id': key, 'label': label} for key, label in DISPLAY_MODES],
                'collection_order': list(collection_map), 'collections': collections,
                'links': links, 'link_target': '_blank'}
    resource['revision'] = resource_revision(resource)
    return resource


def native_collection_rows(resource: dict, collection: str, mode: str) -> list[dict]:
    """Presentation-only fallback; consumes the SAME canonical resource."""
    def label(uid, violet=False):
        item = resource['links'][uid]
        text = f":violet[{item['label']}]" if violet else item['label']
        href = item.get(mode + '_href') if mode in ('online', 'offline') else None
        return f'[{text}]({href})' if href else text
    return [dict(zip(COLUMNS, (label(row['sutta_id'], True), row['title_pali'], row['description'],
                              row['irff_tag'], ', '.join(label(uid) for uid in row['parallels']))))
            for row in resource['collections'][collection]['rows']]
