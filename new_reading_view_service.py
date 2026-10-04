# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Reading presentation only: accepted Anh–Việt helpers, no writes/translation/OCR."""


from __future__ import annotations


from html import escape


import re


import time


from new_reading_v2_contracts import digest, SECTION_BYTES, serialized_bytes, CommandError


def table_resource(values, height=850):
    if not isinstance(values, dict):
        raise CommandError('table_shape')
    # st.table(dict, border=False) displays index and one value column in order.
    return {'type': 'table', 'rows': [[str(k), str(v)] for k, v in values.items()], 'height': height, 'border': False}


def text_resource(text, height=850, *, label='Nội dung gốc:'):
    return {'type': 'text_preview', 'value': str(text or ''), 'height': height, 'label': label}


def json_resource(value, *, expanded=True):
    return {'type': 'json', 'value': value, 'expanded': bool(expanded)}


def cached_presentation(state, variant, dependencies, prepare):
    """Bounded per-session presentation cache. Keys contain digests, no paths."""
    key = digest([variant, dependencies])
    index = state.s.setdefault('prepared_index', {})
    record = index.get(key, {})
    resource_id = record.get('resource_id')
    if resource_id not in state.s['resources'] or time.monotonic()-record.get('created',0)>300:
        value = prepare()
        resource_id = state.put_resource(value)
        index[key] = {'resource_id':resource_id,'created':time.monotonic()}
        if len(index) > 24:
            for old in list(index)[:-16]:
                index.pop(old, None)
    return resource_id

