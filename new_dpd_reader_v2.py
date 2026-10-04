# Presentation extraction for the independent fixture app. See reports/REUSE_MANIFEST.json.
"""Focused full-DPD Components v2 display using the existing dictionary runtime."""


from __future__ import annotations


import hashlib


from html import escape


from html.parser import HTMLParser


import json


from pathlib import Path


import re


from assets_style import build_reader_typography_reset_css


from dict_lookup_assets import build_typography_css


from new_component_v2_support import get_v2_component


from new_components_v2_config import v2_enabled, v2_strict, record_v2_mount, record_v2_route


from new_dictionary_view_v2 import (
    CSS as DICTIONARY_CSS,
    JS as DICTIONARY_JS,
    dictionary_instance_identity,
)


from new_reader_v2_primitives import reader_css_for_host


from st_style import (STREAMLIT_WIDGET_FONT_FAMILY, STREAMLIT_WIDGET_FONT_SIZE,
                      STREAMLIT_WIDGET_CONTROL_HEIGHT)


FEATURE = 'dpdict_view'


_ASSETS = Path(__file__).parent / 'v2_assets' / 'dpd_v2_assets'


JS = DICTIONARY_JS.split('export default function(component)', 1)[0] + (_ASSETS / 'dpd.js').read_text(encoding='utf-8')


CSS = (reader_css_for_host(build_typography_css()) + DICTIONARY_CSS +
       build_reader_typography_reset_css('[data-dpd-root]', inherit_selectors=[
           '[data-dpd-root] table', '[data-dpd-root] td', '[data-dpd-root] th']) +
       (_ASSETS / 'dpd.css').read_text(encoding='utf-8')
       .replace('UI_FONT_FAMILY', STREAMLIT_WIDGET_FONT_FAMILY)
       .replace('UI_FONT_SIZE', str(STREAMLIT_WIDGET_FONT_SIZE) + 'px')
       .replace('UI_CONTROL_HEIGHT', str(STREAMLIT_WIDGET_CONTROL_HEIGHT) + 'px'))


def _region(body, language):
    return '<span data-dpd-language="' + language + '">' + body + '</span>'


def _html_slot(body, language, fragments, *, block=False):
    key = str(len(fragments))
    fragments[key] = {'html': body, 'language': language}
    tag = 'div' if block else 'span'
    return '<' + tag + ' data-dpd-language="' + language + '" data-dpd-html="' + key + '"></' + tag + '>'


def _header(entry, fragments):
    case = ' (' + escape(entry['plus_case']) + ')' if entry['plus_case'] else ''
    construction = (' [' + _region(escape(entry['construction_summary']), 'pi') + ']'
                    if entry['construction_summary'] else '')
    return ('<strong>' + _region(escape(entry['lemma']), 'pi') + '</strong> ' +
            '<i data-dpd-no-lookup>' + escape(entry['pos']) + '.</i>' +
            '<span data-dpd-no-lookup>' + case + '</span> ' + _html_slot(entry['meaning_html'], 'en', fragments) +
            construction + ' <span data-dpd-no-lookup>' + escape(entry['completion']) + '</span>')


def _section_body(section):
    parts = [section['html']]
    for item in section['items']:
        count = '<span data-dpd-no-lookup>' + str(item['count']) + ' </span>' if item['count'] is not None else ''
        parts.append('<p>' + count + '<strong>' + _region(escape(item['name']), 'pi') + '</strong></p>' + item['html'])
    return '<div data-dpd-language="' + section['language'] + '">' + ''.join(parts) + '</div>'


def _meta_body(meta):
    parts = []
    variants = meta.get('variant')
    if variants:
        rows = []
        if isinstance(variants, dict):
            for source, files in variants.items():
                if not isinstance(files, dict):
                    continue
                for filename, pairs in files.items():
                    if not isinstance(pairs, list):
                        continue
                    for pair in pairs:
                        if isinstance(pair, list) and len(pair) >= 2:
                            rows.append('<tr><td data-dpd-no-lookup>' + escape(str(source)) + '</td>' +
                                        '<td data-dpd-no-lookup>' + escape(str(filename)) + '</td><td>' +
                                        _region(escape(str(pair[0])), 'pi') + '</td><td>' +
                                        _region(escape(str(pair[1])), 'pi') + '</td></tr>')
        body = ('<table><thead><tr data-dpd-no-lookup><th>source</th><th>filename</th><th>context</th><th>variant</th></tr></thead><tbody>' +
                ''.join(rows) + '</tbody></table>') if rows else _region(escape(json.dumps(variants, ensure_ascii=False)), 'pi')
        parts.append('<h4 data-dpd-no-lookup>variants</h4>' + body)
    if meta.get('deconstructor'):
        decon = meta['deconstructor']
        values = decon if isinstance(decon, list) else [decon]
        parts.append('<h4 data-dpd-no-lookup>deconstructor</h4>' + ''.join(
            '<p>' + _region(escape(str(value)), 'pi') + '</p>' for value in values))
    return ''.join(parts)


def build_dpd_html(result):
    entries = result['entries']
    fragments = {}
    parts = []
    if entries:
        parts.append('<h4 data-dpd-no-lookup>summary</h4>')
        for i, entry in enumerate(entries):
            jump = (' <button type="button" data-dpd-select="' + str(i) + '" aria-label="' +
                    escape('Show ' + entry['lemma'], quote=True) + '">►</button>') if len(entries) > 1 else ''
            parts.append('<p class="dpd-summary">' + _header(entry, fragments) + jump + '</p>')
        if len(entries) > 1:
            parts.append('<nav class="dpd-controls" data-dpd-no-lookup aria-label="Lựa chọn biến thể">' + ''.join(
                '<button type="button" data-dpd-select="' + str(i) + '" aria-pressed="' +
                ('true' if i == 0 else 'false') + '">' + escape(entry['lemma']) + '</button>'
                for i, entry in enumerate(entries)) + '</nav>')
        for i, entry in enumerate(entries):
            parts.append('<article data-dpd-entry="' + str(i) + '"' + (' hidden' if i else '') + '>')
            if len(entries) > 1:
                parts.append('<p>' + _header(entry, fragments) + '</p>')
            parts.append('<nav class="dpd-controls" data-dpd-no-lookup aria-label="DPD sections">')
            for key, section in entry['sections'].items():
                target = 'dpd-' + str(i) + '-' + key
                parts.append('<button type="button" data-dpd-toggle="' + escape(target, quote=True) +
                             '" aria-controls="' + escape(target, quote=True) + '" aria-expanded="false">' +
                             escape(section['label']) + '</button>')
            parts.append('</nav>')
            for key, section in entry['sections'].items():
                target = 'dpd-' + str(i) + '-' + key
                parts.append('<section data-dpd-section="' + escape(target, quote=True) + '" id="' +
                             escape(target, quote=True) + '" hidden>' +
                             _html_slot(_section_body(section), section['language'], fragments, block=True) + '</section>')
            parts.append('</article>')
    parts.append(_meta_body(result['meta']))
    return ''.join(parts), fragments


class _LookupText(HTMLParser):
    """Same lexical boundary as shared subsets, scoped to semantic content."""
    VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'wbr', 'source', 'area', 'embed', 'col'}
    SKIP = {'a', 'button', 'script', 'style', 'code', 'pre', 'select', 'option', 'textarea'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.pi, self.en = [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent_lang, parent_skip = self.stack[-1][1:] if self.stack else ('mixed', False)
        lang = attrs.get('data-dpd-language', attrs.get('lang', parent_lang))
        skip = parent_skip or tag in self.SKIP or 'data-dpd-no-lookup' in attrs or lang == 'none'
        if tag not in self.VOID:
            self.stack.append((tag, lang, skip))

    def handle_startendtag(self, tag, attrs):
        if tag not in self.VOID:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, value):
        lang, skip = self.stack[-1][1:] if self.stack else ('mixed', False)
        if skip or not re.search(r'[^\W\d_]', value):
            return
        if lang in ('pi', 'pli', 'pali', 'mixed'):
            self.pi.append(value)
        if lang in ('en', 'mixed'):
            self.en.append(value)

