# Presentation call sites: dt.py 597–646, 1035–1132; fixture routing replaces search.
import streamlit as st
from fixtures import HITS,TEXT
from reference_native import draw_line_dt
from presentation import choose,taisho
from new_result_list_v2 import try_dt_results
from new_dt_full_text_v2 import render_dt_full_text_v2
from new_dt_snippets_v2 import render_dt_snippets_v2
state=choose(['Kết quả / toàn văn','Trích đoạn','Không có kết quả','Lỗi tìm kiếm','Taisho'])
with st.sidebar:
 st.selectbox('Chọn bộ tra cứu:',['Đại Chánh Tạng','Đại Tạng','Thư viện minh họa'],label_visibility='collapsed')
 a,b=st.columns([1,1]);a.toggle('Dữ liệu');b.toggle('Chọn kinh')
if state=='Taisho':
 taisho()
else:
 left,right=st.columns([1,1.25],border=True,gap='xxsmall')
 with left:
  st.subheader(':material/quick_reference_all: Đại Chánh Tạng')
  f1,f2=st.columns([1,3]);f1.selectbox('Lọc:',['Loại bỏ tiêu đề','Chỉ chọn tiêu đề','Chọn nhiều kinh'])
  f2.multiselect('Thẻ:',['A Hàm','Kinh','Luận','Yếu','Tán','Tụng'],default=['Kinh'],accept_new_options=True,wrap=False)
  draw_line_dt()
  a,b=st.columns([1,3]);mode=a.selectbox('Tìm theo:',['Nội dung','Tên kinh']);q=b.text_input(':material/search: từ khóa chính:',value='minh họa')
  draw_line_dt()
  a,b=st.columns([1,3]);a.selectbox('Ngữ cảnh gần:',['Không giới hạn','Khoảng 15 từ','Khoảng 50 từ'],disabled=mode!='Nội dung');q2=b.text_input(':material/search: từ khóa phụ:',value='trí tuệ')
  draw_line_dt()
  if state=='Lỗi tìm kiếm':
   st.error('Không thể nhận kết quả — trạng thái minh họa.');st.button('Thử lại tìm kiếm')
  elif state=='Không có kết quả':st.info('Không tìm thấy kết quả.')
  else:
   def selected(hit,view):st.session_state['dt_selected_title']=hit['title'];st.session_state['dt_selected_view']=view
   assert try_dt_results(HITS,q,q2,mode,3,'reference-dt',on_select=selected)[0]
 with right:
  title=st.session_state.get('dt_selected_title','Kinh minh họa 1')
  if state=='Trích đoạn' or st.session_state.get('dt_selected_view')=='snippets':
   render_dt_snippets_v2(TEXT,'minh họa','Pāli',title,'ref',snippets_per_page=2)
  else:
   cut=len(TEXT)//2
   render_dt_full_text_v2(TEXT,[(0,cut),(cut,len(TEXT))],'ref',title,q,q2,mode)
