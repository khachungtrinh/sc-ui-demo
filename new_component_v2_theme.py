"""Native generic theme aliases for the shared r14 Components v2 renderer.

The host provides --st-* in its actual main/sidebar context. :host deliberately
keeps this policy out of legacy iframes. Content metrics and domain colors are
still provided by their existing SCAPP owners.
"""


def native_dictionary_theme_css() -> str:
    # Specificity beats the legacy prepared CSS's one-class/root token blocks.
    # The canonical --dict-main-surface remains a recognition token for legacy
    # neutral provider HTML, never the native component's surface painter.
    return '''
:host [data-dictionary-root] {
    --dl-bg-main: var(--st-background-color);
    --dl-bg-sidebar: var(--st-background-color);
    --dl-dict-bg: var(--st-background-color);
    --dl-dict-inner-bg: var(--st-background-color);
    --dl-sidebar-dict-bg: var(--st-background-color);
    --eng-bg-main: var(--st-background-color);
    --eng-bg-sidebar: var(--st-background-color);
    --eng-dict-bg: var(--st-background-color);
    --eng-dict-inner-bg: var(--st-background-color);
    --dict-panel-surface: var(--st-background-color);
    --dl-bg: var(--st-secondary-background-color);
    --dl-bg-hover: var(--st-secondary-background-color);
    --dl-popup-bg: var(--st-secondary-background-color);
    --dl-lookup-bg: var(--st-secondary-background-color);
    --eng-bg-sec: var(--st-secondary-background-color);
    --eng-bg-hover: var(--st-secondary-background-color);
    --eng-popup-bg: var(--st-secondary-background-color);
    --dl-text: var(--st-text-color);
    --eng-text: var(--st-text-color);
    --dl-primary: var(--st-primary-color);
    --eng-primary: var(--st-primary-color);
    --dl-border: var(--st-border-color);
    --dl-border-main: var(--st-border-color);
    --eng-border: var(--st-border-color);
    --dl-font-reader: var(--st-font);
    --dl-font-ui: var(--st-font);
    --eng-font-reader: var(--st-font);
    --eng-font-ui: var(--st-font);
    --dl-font-mono: var(--st-code-font);
    --eng-font-mono: var(--st-code-font);
    --dl-code-bg: var(--st-code-background-color);
    --eng-code-bg: var(--st-code-background-color);
    --dl-muted: color-mix(in srgb, var(--st-text-color) 70%, transparent);
    --eng-muted: color-mix(in srgb, var(--st-text-color) 70%, transparent);
}
:host [data-dictionary-root] [data-dict-neutral-surface] {
    background-color: var(--st-background-color) !important;
}
'''


def native_selectbox_theme_css(root_selector: str) -> str:
    """Native palette for app-owned menus, with the accepted Taisho fallbacks."""
    root = str(root_selector).strip()
    if not root:
        raise ValueError("root_selector must not be empty")
    return f'''
{root} {{
    --scapp-select-background: var(--st-secondary-background-color, #ecebe3);
    --scapp-select-menu-background: var(--st-background-color, #fdfdf8);
    --scapp-select-text: var(--st-text-color, #3d3a2a);
    --scapp-select-border: var(--st-widget-border-color, var(--st-border-color, #d3d2ca));
    --scapp-select-hover-border: #b8b6ad;
    --scapp-select-active-background: var(--st-secondary-background-color, #ecebe3);
}}
'''
