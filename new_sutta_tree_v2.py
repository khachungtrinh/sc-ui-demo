"""R6-1 control transport; traversal, validation and saved-path writes stay in Python."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import streamlit as st
from new_component_v2_support import get_v2_component
from new_components_v2_style import build_components_v2_style_css

_ROOT='[data-sutta-tree-v2]'
_ASSETS=Path(__file__).resolve().parent/'v2_assets'/'sutta_tree_v2_assets'
_HTML='<section data-sutta-tree-v2></section>'
_CSS=build_components_v2_style_css(_ROOT,content=False,tables=False)+'\n'+(_ASSETS/'tree.css').read_text(encoding='utf-8')
_JS=(_ASSETS/'tree.js').read_text(encoding='utf-8')

def validate_tree_selection(event,data):
    if not isinstance(event,dict) or event.get('revision')!=data['resource_id']:return None
    index=event.get('level')
    if type(index) is not int or not 0<=index<len(data['levels']):return None
    level=data['levels'][index];value=event.get('value')
    if not isinstance(value,str) or value not in level['options']:return None
    return level['key'],value

def render_sutta_tree_v2(levels, *,nikaya_code):
    data=dict(version=1,levels=levels,resource_id=hashlib.sha256(json.dumps(levels,ensure_ascii=False,sort_keys=True).encode()).hexdigest())
    key=f'sutta-tree-{nikaya_code}'
    def receive_selection():
        state=st.session_state.get(key,{})
        pair=validate_tree_selection(state.get('selection') if isinstance(state,dict) else None,data)
        if pair is not None:st.session_state[pair[0]]=pair[1]
    return get_v2_component('scapp_sutta_tree_v2',_HTML,_CSS,_JS)(data=data,key=key,height='content',
        default={'selection':None},on_selection_change=receive_selection)
