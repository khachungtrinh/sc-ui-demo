# Extracted cluster boundaries: page_reading.py 890–1015,1555–1640,2215–2490.
# ReadingUI retains original browser assets / local command protocol.
import streamlit as st
import pandas as pd
from fixtures import *
from presentation import choose,english_resource
from new_reading_workspace_v2 import ReadingUI
from new_reading_view_service import text_resource,table_resource
state=choose(['Nhập dữ liệu','Đọc tài liệu','AI workspace','Glossary'])
ui=ReadingUI(identity='reference-'+state)
if state=='Nhập dữ liệu':
 left,right=st.columns([1,1])
 with left:
  st.subheader(':material/system_update_alt: Nhập dữ liệu')
  a,b=st.columns([1,1],vertical_alignment='bottom')
  text=ui.text_area('Nội dung văn bản:',height=600,placeholder='Dán đoạn văn bản cần đọc/dịch...',label_visibility='collapsed',section='reading_intake',v2_role='intake_text',value=TEXT)
  with a:ui.text_input('Tên tài liệu (Tùy chọn):',placeholder='Nhập tên để lưu dự án, để trống sẽ không được lưu.',label_visibility='collapsed',section='reading_intake')
  with b:
   if ui.button('Xử lý văn bản',icon=':material/content_paste_go:',width='stretch',section='reading_intake',command_kind='submit_paste'):st.success('Đã nhận văn bản trong phiên tham chiếu.')
 with right:
  st.subheader(':material/cases: Quản lý dự án cũ')
  a,b,c=st.columns([2,1,1],vertical_alignment='bottom')
  a.selectbox('Danh sách dự án:',['Dự án minh họa'],index=None,placeholder='Chọn dự án đang làm dở...')
  b.button('Mở dự án');c.button('Xóa',disabled=True)
  ui.display(text_resource(TEXT,600),role='project_preview')
elif state=='Đọc tài liệu':
 # Native page skeleton and original v2 read_workspace root; input already prepared.
 role='read_workspace';ui.state.root(role,kind='request_view',options=['processed','original'])
 active=st.session_state.get('reference_read_view','processed')
 event=ui.state.consume(role,'request_view')
 if event:
  active=event.get('payload',{}).get('choice','processed');st.session_state['reference_read_view']=active;ui.state.finish()
 resource=english_resource() if active=='processed' else text_resource(TEXT,850)
 rid=ui.state.put_resource(resource)
 ui._emit(role,type='read_workspace',current_view=active,view_revisions={'processed':digest(EN),'original':digest(TEXT)},tabs=[{'id':'processed','label':':material/order_approve: **Đọc tài liệu**'},{'id':'original','label':':material/raw_on: Văn bản gốc'}],views={active:ui.state.transport(rid)})
elif state=='AI workspace':
 left,right=st.columns([1,1]);left2,right2=st.columns([1,1])
 with left:
  st.caption('**1. Thiết kế ngữ cảnh và tạo prompt phù hợp**')
  ui.text_input('Chuỗi phân bổ ID (PAST | TARGET | FUTURE):',value='ref:1 | ref:2 | ref:3',label_visibility='collapsed',section='reading_ai_workspace')
  a,b,c,d=st.columns([2,1,1,1],vertical_alignment='bottom')
  with a:ui.selectbox('Lĩnh vực dịch thuật:',['Phật học','Ngôn ngữ'],label_visibility='collapsed',section='reading_ai_workspace')
  with b:ui.selectbox('Gói tài khoản:',['Gemini Free','Gemini Pro'],label_visibility='collapsed',section='reading_ai_workspace')
  with c:
   if ui.button('Cấu hình',icon=':material/rule_settings:',section='reading_ai_workspace'):st.session_state['ref_config']=not st.session_state.get('ref_config',False)
  with d:ui.button('Gợi ý',icon=':material/filter_center_focus:',section='reading_ai_workspace')
  if st.session_state.get('ref_config'):
   with st.container(border=True):ui.number_input('Giới hạn số từ an toàn (Base Limit):',value=2000,min_value=500,max_value=10000,step=500,section='reading_ai_workspace')
  ui.code('Đây là prompt minh họa. Không gọi dịch vụ AI.\n'+TEXT,height=655)
 with right:
  ui.text_area('Dán dữ liệu JSON:',value=json.dumps(VI,ensure_ascii=False,indent=2),height=655,v2_role='ai_json',section='reading_ai_workspace')
  ui.button('Cập nhật bản dịch',section='reading_ai_workspace')
 with left2:ui.display(english_resource(),role='english_preview')
 with right2:ui.table(VI,height=850)
else:
 tabs=st.tabs(['Glossary','Văn bản gốc'])
 with tabs[0]:
  st.data_editor(pd.DataFrame({'Từ':['dhamma','sati'],'Nghĩa':['pháp','niệm']}),num_rows='dynamic',hide_index=True)
  st.button('Lưu Glossary')
 with tabs[1]:ui.json(PI)
ui.finish()
