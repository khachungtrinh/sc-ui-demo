# SS native layout 671–714,1057–1118; collection height from accepted follow-up.
import streamlit as st
from fixtures import *
from presentation import choose,dictionary_view,taisho
from new_ss_content_v2 import render_ss_content_v2,render_ss_table_v2
from new_ss_collection_table_v2 import render_ss_collection_table_v2
from reference_readlist import render_ss_readlist
if st.session_state.pop('ref_close_readlist',False):
 st.session_state['reference_scenario_Đối chiếu']='Đối chiếu'
state=choose(['Đối chiếu','Cây kinh','Bảng song song','Tuyển tập','Bảng nội dung','Từ điển','Taisho','Bảng rỗng'])
with st.sidebar:
 a,b=st.columns(2,gap='xsmall')
 def toggle_table():st.session_state.tog_readlist=False
 def toggle_readlist():st.session_state.tog_table=False
 on_table=a.toggle('Song song',key='tog_table',on_change=toggle_table)
 on_readlist=b.toggle('Tuyển tập',key='tog_readlist',on_change=toggle_readlist)
 a.toggle('Đại Tạng',key='ss_taisho')
 b.text_input(':material/search: nhập mã PTS',placeholder='PTS',label_visibility='collapsed',disabled=on_table or on_readlist)
 st.text_input(':material/search: nhập kinh tra cứu',value='mn1',placeholder='UID',label_visibility='collapsed',disabled=on_table or on_readlist)
 a,b=st.columns(2);a.button('Kinh Trước',disabled=True);b.button('Kinh Tiếp')
if state=='Cây kinh':
 from new_sutta_tree_v2 import render_sutta_tree_v2
 value=st.session_state.get('ref_tree_level','Chương 1')
 render_sutta_tree_v2([{'level':0,'key':'ref_tree_level','options':['Chương 1','Chương 2'],'selected':value}],nikaya_code='reference')
 render_ss_content_v2(HTML,height=850)
elif on_readlist or state=='Tuyển tập':
 def on_load(value):
  st.session_state['ref_loaded_uids']=value
  st.session_state.tog_readlist=False
  st.session_state['ref_close_readlist']=True
 render_ss_readlist(st.empty(),on_load)
elif on_table or state in ['Bảng song song','Bảng rỗng']:
 placeholder_table=st.empty()
 with placeholder_table.container(height=1000,border=False):render_ss_collection_table_v2(collection_resource(state=='Bảng rỗng'))
elif state=='Taisho' or st.session_state.ss_taisho:taisho()
elif state=='Từ điển':dictionary_view('left')
else:
 info=st.columns([1,1]);ctrl=st.columns([1,1]);body=st.columns([1,1])
 info[0].segmented_control('Chọn chế độ đối chiếu:',['tracuu','tudien'],default=None,label_visibility='collapsed')
 info[1].segmented_control('Chọn bản song song:',['dn1','sn1.1'],default='dn1',label_visibility='collapsed')
 ctrl[0].segmented_control('Bản dịch cho mn1:',['pali','minhchau','sujato'],default='pali',label_visibility='collapsed')
 ctrl[1].segmented_control('Bản dịch cho dn1:',['pali','minhchau','sujato'],default='minhchau',label_visibility='collapsed')
 with body[0]:render_ss_content_v2(HTML,height=850)
 with body[1]:
  if state=='Bảng nội dung':render_ss_table_v2(TABLE,height=850)
  else:render_ss_content_v2('\n\n'.join(VI.values()),height=850)
