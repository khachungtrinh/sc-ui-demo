"""Presentation-only policy for English/Vietnamese left/sidebar dictionary panels.

Consumers select this CSS using existing position/role/language metadata. No
dictionary lookup, HTML mutation, popup, scroll or component-channel behavior.
"""
from assets_style import DL_READER_BG_MAIN, DL_READER_BG_SIDEBAR


def english_dictionary_surface_css(position: str) -> str:
    if position not in ('left', 'sidebar'):
        return ''
    background = DL_READER_BG_SIDEBAR if position == 'sidebar' else DL_READER_BG_MAIN
    # App-owned metadata marks only the terminal block-wrapper chain. Internal
    # hr/table/heading/entry separators and semantic glossary surfaces stay intact.
    css = f'''
[data-dictionary-root] {{
    --dict-main-surface: {DL_READER_BG_MAIN};
    --dict-panel-surface: {background};
}}
[data-dictionary-root] [data-dict-panel] > .dict-entry:last-child {{
    border-bottom: 0;
}}
[data-dictionary-root] [data-dict-panel] > .dict-entry:last-child [data-dict-terminal-wrapper] {{
    border-bottom: 0 !important;
}}
[data-dictionary-root] [data-dict-panel] > .dict-entry:last-child [data-dict-terminal-rule] {{
    display: none;
}}
'''
    if position == 'sidebar':
        css += f'''
[data-dictionary-root] {{
    --eng-bg-main: {DL_READER_BG_SIDEBAR};
    --eng-dict-bg: {DL_READER_BG_SIDEBAR};
    --eng-dict-inner-bg: {DL_READER_BG_SIDEBAR};
    background-color: var(--eng-bg-sidebar, {DL_READER_BG_SIDEBAR});
}}
[data-dictionary-root] [data-dict-panel],
[data-dictionary-root] .dict-col {{
    background-color: var(--eng-bg-sidebar, {DL_READER_BG_SIDEBAR});
}}
[data-dictionary-root] [data-dict-neutral-surface] {{
    background-color: var(--dict-panel-surface) !important;
}}
'''
    return css
