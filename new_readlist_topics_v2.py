"""R6-3 selection transport; the caller retains the ordered UID projection."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import streamlit as st
from new_component_v2_support import get_v2_component
from new_components_v2_style import build_components_v2_style_css

_ROOT='[data-readlist-topics-v2]'
_BASE=Path(__file__).resolve().parent
_ASSETS=_BASE/'v2_assets'/'readlist_topics_v2_assets'
_GRID=_BASE/'v2_assets'/'functional_grid_v2_assets'
_HTML='<section data-readlist-topics-v2></section>'
_CSS=build_components_v2_style_css(_ROOT,content=False,tables=False,dataframe=True)+'\n'+(_GRID/'grid.css').read_text(encoding='utf-8')
_JS=(_GRID/'grid.js').read_text(encoding='utf-8')+'\n'+(_ASSETS/'topics.js').read_text(encoding='utf-8')

def selected_topics(event,data):
    if not isinstance(event,dict) or event.get('revision')!=data['resource_id']:return []
    topics=event.get('topics')
    allowed={row['id'] for row in data['rows']}
    if not isinstance(topics,list) or any(not isinstance(topic,str) or topic not in allowed for topic in topics):return []
    chosen=set(topics)
    return [row['id'] for row in data['rows'] if row['id'] in chosen]

def render_readlist_topics_v2(df, *,key):
    rows=[{'id':topic,'values':[False,topic,suttas]} for topic,suttas in zip(df['Topics'],df['Suttas'])]
    data={'version':1,'rows':rows,'resource_id':hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True).encode()).hexdigest()}
    instance_key=f'readlist-topics-{key}'
    state=st.session_state.get(instance_key,{})
    data['selected']=selected_topics(state.get('selection') if isinstance(state,dict) else None,data)
    get_v2_component('scapp_readlist_topics_v2',_HTML,_CSS,_JS)(data=data,key=instance_key,height='content',
        default={'selection':None},on_selection_change=lambda:None)
    edited=df.copy()
    edited['Select']=edited['Topics'].isin(data['selected'])
    return edited
