"""One public-key Components v2 surface for the SS all-collections table."""
from __future__ import annotations
from pathlib import Path
import streamlit as st
from new_component_v2_support import get_v2_component
from new_components_v2_config import v2_enabled, v2_strict, record_v2_route, record_v2_mount
from new_ss_collection_service import COLLECTION_TABLE_CACHE_VERSION, build_all_collection_table_resource, native_collection_rows
from new_components_v2_style import build_components_v2_style_css
from new_component_v2_theme import native_selectbox_theme_css

_ASSETS = Path(__file__).parent / "v2_assets" / "ss_collection_v2_assets"
HTML = '<section data-ss-collection-root></section>'
JS = (_ASSETS / "collection_table.js").read_text(encoding="utf-8")
CSS = (build_components_v2_style_css('[data-ss-collection-root]', content=False, dataframe=False) + '\n'
       + (_ASSETS / "collection_table.css").read_text(encoding="utf-8")
       + native_selectbox_theme_css('[data-ss-collection-root]'))




def _native_fallback(resource, key):
    """Feature-off/runtime fallback; browser-local switching is the v2 guarantee."""
    st.subheader(":material/table_view: " + resource["heading"])
    first, second = st.columns([1, 2])
    modes = resource["display_modes"]
    with first:
        mode = st.selectbox("Chế độ hiển thị:", [item["id"] for item in modes], index=2,
                            format_func=lambda value: next(item["label"] for item in modes if item["id"] == value),
                            key=key + "_fallback_mode")
    with second:
        collection = st.selectbox("Chọn bộ kinh:", resource["collection_order"], key=key + "_fallback_collection")
    selected = resource["collections"].get(collection)
    if not selected:
        st.warning("Không tìm thấy dữ liệu cho bộ kinh này.")
        return
    stats = selected["statistics"]
    text = f"Có song song: {stats['count_with_parallels']} | Tổng số: {stats['total_in_collection']}"
    if stats["total_in_collection"] > 0:
        text += f" | Tỷ lệ: {stats['percentage']:.2f}%"
    st.caption(text)
    if not selected["rows"]:
        st.warning("Không tìm thấy dữ liệu cho bộ kinh này.")
        return
    import pandas as pd
    st.table(pd.DataFrame(native_collection_rows(resource, collection, mode)))


def render_ss_collection_table_v2(resource, *, key="ss_collection_table_all"):
    """No callbacks/state/triggers for read-only local interaction."""
    if not v2_enabled("ss_table"):
        record_v2_route("ss_table", "legacy_disabled")
        return _native_fallback(resource, key)
    try:
        renderer = get_v2_component("scapp_ss_collection_table_v2", HTML, CSS, JS)
        result = renderer(key=key, data=resource, height="content")
    except Exception:
        if v2_strict("ss_table"):
            raise
        record_v2_route("ss_table", "legacy_setup_error")
        return _native_fallback(resource, key)
    record_v2_mount("ss_table", resource, items=sum(len(item["rows"]) for item in resource["collections"].values()))
    return result
