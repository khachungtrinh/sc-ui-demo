"""Explicit fixture-to-presentation boundaries; no provider/repository emulation."""
import streamlit as st
from new_component_v2_support import get_v2_component
from fixtures import *
from dict_lookup_assets import build_reader_css,build_typography_css,wrap_pali_text_token_mode,wrap_pali_chanting_text
from dict_lookup_eng_assets import build_basic_reader_css,wrap_english_text_for_lookup
from new_dictionary_view_v2 import prepare_dictionary_view,_mount


def choose(options,default=None):
    """Reference-only scenario picker, outside the production content layout."""
    return st.sidebar.selectbox('Trạng thái tham chiếu',options,index=options.index(default) if default else 0,key='reference_scenario_'+str(options[0]))

def english_resource(position='left'):
    # new_reading_view_service.prepare_english: exact row/container/CSS contract.
    rows=''.join("<tr><td class='content-col' style='border-left:none;'>"+wrap_english_text_for_lookup(v)+'</td></tr>' for v in EN.values())
    container='english-reader-main-text'
    css=build_basic_reader_css(container_id=container,grid_template='33% 1fr' if position=='left' else '1fr',border_table='1px solid #d3d2ca',extra_vars=None)
    data=prepare_dictionary_view('<div id="'+container+'" class="text-col english-reader-basic-root"><table>'+rows+'</table></div>',css=css,en_lookup=EN_LOOKUP,height=850,pali_position='none',english_position=position,hover_popup=False,channel='ref-reading')
    return {'type':'reader','dictionary':data}

def dictionary_view(position='popup',key='reference-dict'):
    _mount(prepare_dictionary_view(HTML+'<p>'+EN['ref:1']+'</p>',css=build_typography_css(),pali_lookup=PI_LOOKUP,en_lookup=EN_LOOKUP,height=850,pali_position=position,english_position=position,channel=key),key)

def lcdp_reader(kind='lcdp_html'):
    import new_lcdp_reader_v2 as m
    body='<div class="pali">'+HTML+'</div>'
    lookup={k:{'headwords':[[k,v]],'deconstructor':'dhamma + ṃ'} for k,v in PI_LOOKUP.items()}
    data=dict(version=1,kind=kind,content_html=body,lookup=lookup,highlight_word='dhamma',height=850,sidebar_channel='')
    data['resource_id']=digest(data)
    get_v2_component('scapp_lcdp_reader_v2',m._HTML,m._CSS,m._JS)(data=data,key='reference-lcdp')

def full_dictionary(kind='sujato'):
    import new_full_dictionary_reader_v2 as m
    from new_dictionary_surface_v2 import render_dictionary_sidebar_surface
    channel='ref-full-dictionary'
    data=dict(version=1,feature='sujato_json_reader',kind=kind,body_html='<div class="sujato-reader">'+HTML+'<p>'+EN['ref:1']+'</p></div>',css=m.build_sujato_v2_css(),height=850,pali_lookup={k:{'headwords':[[k,v]],'deconstructor':''} for k,v in PI_LOOKUP.items()},english_lookup=EN_LOOKUP,history_target_id='',sidebar_channel=channel,english_sidebar=False,counts={'pali_words':len(PI_LOOKUP),'english_words':len(EN_LOOKUP)})
    data['resource_id']=digest(data)
    render_dictionary_sidebar_surface('full_dictionary',channel=channel,resource_id=data['resource_id'],placeholder='Chạm từ Pāli để tra cứu...')
    get_v2_component('scapp_full_dictionary_reader_v2',m._HTML,m._CSS,m._JS)(data=data,key='reference-full-dictionary')

def pali_reader(chant=True):
    import new_pali_reader_v2 as m
    rows=m._prepare_rows(PI,active_glossary_map={},allow_glossary_phrases=False)
    data=dict(rows=rows,pali_lookup=PI_LOOKUP,en_lookup=EN_LOOKUP,mode='chant' if chant else 'read',dual_dict=True,show_id=True,dict_width='300px',height=700,font_size='1.6rem' if chant else '1rem',line_height='1.6',typography_vars={})
    data['content_id']=m._reader_fingerprint(data)
    m._pali_reader_v2_component(data=data,key='reference-pali')

def chanting():
    from new_chanting_reader_v2 import try_render_chanting_reader_v2
    body=''.join('<p>'+wrap_pali_chanting_text(v)[0]+'</p>' for v in PI.values())
    assert try_render_chanting_reader_v2(body_html=body,css=build_reader_css(),ipa_lookup={k:'<p>'+k+' — IPA minh họa /aː/</p>' for k in PI_LOOKUP},ipa_popup_lookup={k:'/aː/' for k in PI_LOOKUP},en_lookup=EN_LOOKUP,height=850)

def panel():
    from new_panel_reader_v2 import try_render_panel_reader
    r=english_resource()['dictionary']
    body='<div class="main-grid"><div class="dict-col"><div id="eng-dict-target"><i>Click an English word on the right...</i></div></div>'+r['body_html']+'</div>'
    assert try_render_panel_reader('english_reader',supported=True,body_html=body,css=r['css'],en_lookup=EN_LOOKUP,height=850)

def dpd():
    import new_dpd_reader_v2 as m
    body,fragments=m.build_dpd_html(dpd_result())
    data=dict(version=1,role='content',body_html=body,fragments=fragments,css=m.CSS,pali_lookup=PI_LOOKUP,en_lookup=EN_LOOKUP,canonical=True,predecorated=True,pali_position='popup',english_position='popup',hover_popup=True,meaning_english=True,history=False,channel='ref-dpd')
    data['resource_id']=digest(data)
    get_v2_component('scapp_dpd_full_v2','<section class="panel-reader-v2" data-dictionary-root data-dpd-root></section>',m.CSS,m.JS)(data=data,key='reference-dpd')

def dictionary_entry():
    import new_dictionary_entry_v2 as m
    data=m.prepare_dictionary_entry_payload(kind='pts',body_html='<h3>Dhamma</h3><p>teaching; wisdom; example</p>',css=build_typography_css(),en_lookup=EN_LOOKUP,english_mode='popup',height=850)
    get_v2_component('scapp_dictionary_entry_v2',m._HTML,m._CSS,m._JS)(data=data,key='reference-entry')

def english_data(mode='table'):
    import new_english_data_reader_v2 as m
    body='<table><tr><th>Word</th><th>Meaning</th></tr><tr><td>mindfulness</td><td>peace and wisdom</td></tr></table>' if mode=='table' else '<p>'+EN['ref:1']+'</p>'
    data=m.prepare_english_data_payload(body_html=body,css=build_typography_css(),en_lookup=EN_LOOKUP,mode=mode,height=850)
    get_v2_component('scapp_english_data_reader_v2',m._HTML,m._CSS,m._JS)(data=data,key='reference-english-data')

def taisho():
    from new_taisho_reader_v2 import render_taisho_v2
    render_taisho_v2(TAISHO,st.sidebar,st.container(),height=950)

def readlist_topics(df):
    """Original topic grid with export disabled at the reference integration edge."""
    import new_readlist_topics_v2 as m
    rows=[{'id':topic,'values':[False,topic,suttas]} for topic,suttas in zip(df['Topics'],df['Suttas'])]
    data={'version':1,'rows':rows,'resource_id':digest(rows)}
    key='reference-readlist-topics'
    event=st.session_state.get(key,{})
    data['selected']=m.selected_topics(event.get('selection') if isinstance(event,dict) else None,data)
    # Preserve source asset bytes. Only suppress the production download action.
    js=m._JS.replace('export default function(component)', 'function mountOriginalTopics(component)')+'''
export default function(component) {
 const cleanup=mountOriginalTopics(component);
 const button=component.parentElement.querySelector('[data-tool="download"]');
 if(button){button.disabled=true;button.setAttribute('aria-disabled','true');}
 return cleanup;
}
'''
    get_v2_component('reference_readlist_topics',m._HTML,m._CSS,js)(data=data,key=key,height='content',default={'selection':None},on_selection_change=lambda:None)
    return data['selected']
