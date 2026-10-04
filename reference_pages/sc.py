# SC layout: sc.py 67–131,248–281. Prepared nodes replace results acquisition.
import streamlit as st
from fixtures import PI,VI,EN,PI_LOOKUP,EN_LOOKUP
from reference_native import _render_offline_sutta_title,_show_sutta_blurb,_show_muti_lang,_draw_line_mini
from presentation import choose,dictionary_view,full_dictionary,lcdp_reader
from new_sc_prepared_page_v2 import PreparedPage,page_context,prepare_page_payload,_definition,consume_page_request,_meta_key
state=choose(['Local Data','API SC','Từ điển','Sujato','LCDP','Không có kết quả'])
a,b=st.sidebar.columns([1,1],gap='xsmall');a.toggle('API SC',value=state=='API SC',disabled=True);b.toggle('Local Data',value=state!='API SC',disabled=True)
c=st.columns([3,1,1,1,1,1],vertical_alignment='bottom')
c[0].text_input(':material/search: search 1',value='dhamma')
if state=='API SC':
 c[1].selectbox('boundary',['all','mn','dn']);c[2].selectbox('match partial',['true','false']);c[3].selectbox('more result',['false','true']);c[4].selectbox('page size',['20','50','100'],index=1)
else:
 c[1].selectbox('Giới hạn',['Tất cả','Trung Bộ','Trường Bộ'],label_visibility='collapsed');c[2].selectbox('Chế độ tìm',['Từ','Cụm từ'],label_visibility='collapsed');c[3].selectbox('Thêm kết quả',['Mặc định','Toàn văn'],label_visibility='collapsed');c[4].selectbox('Lượng trang',['20','50','100'],index=2,label_visibility='collapsed')
c[5].selectbox('Bộ dữ liệu',['SuttaCentral','LCDP'],disabled=state=='API SC',label_visibility='collapsed')
if state=='Từ điển':dictionary_view()
elif state=='Sujato':full_dictionary()
elif state=='LCDP':lcdp_reader()
elif state=='Không có kết quả':st.info('Không tìm thấy kết quả.')
else:
 feature='sc_online' if state=='API SC' else 'sc_offline_default'
 context=page_context(feature,'fixture-sc','v1')
 consume_page_request(st.session_state,context,3,'sc_ref_page','sc_ref_scroll')
 page=st.session_state.get('sc_ref_page',1)
 surface=PreparedPage()
 for i in range((page-1)*2+1,page*2+1):
  uid=f'mn{i}'
  if state=='API SC':_show_sutta_blurb(uid,'Kinh minh họa',VI['ref:1'],_surface=surface)
  else:_render_offline_sutta_title(uid,2,1,{uid:{'title_pali':'Dhammaṃ'}},_surface=surface)
  _show_muti_lang(PI['ref:1'],EN['ref:1'],VI['ref:1'],show_col3=state=='API SC',_surface=surface)
  _draw_line_mini(_surface=surface)
 data,meta=prepare_page_payload(surface,context,page,3,st.session_state.get(_meta_key(feature)))
 data['dictionary']={'canonical':False,'pali_lookup':PI_LOOKUP,'en_lookup':EN_LOOKUP,'pali_position':'popup','english_position':'popup','hover_popup':True}
 _definition()(data=data,key='scapp_prepared_page_v2:'+feature,on_page_request_change=lambda:None)
 st.session_state[_meta_key(feature)]=meta
