# Native navigation pattern from td.py 247–300; actual v2 reader surfaces below.
import streamlit as st
from presentation import *
from new_result_list_v2 import try_tdk_results
state=choose(['Pāli','Tụng / IPA','Anh–Việt','Từ điển','DPD','Mục từ','Bảng Anh','Văn bản Anh','LCDP','Sujato','Kết quả từ điển'])
a,b=st.sidebar.columns([1,1],gap='xsmall');a.toggle('Tuyển Tập');b.toggle('Xem lại')
st.sidebar.text_input('uid',value='mn1',placeholder='⌕ uid',label_visibility='collapsed')
a,b=st.sidebar.columns([1,1],gap='xsmall');a.button('Kinh Trước',disabled=True);b.button('Kinh Tiếp')
st.sidebar.selectbox('Chọn kinh:',['Kinh minh họa 1','Kinh minh họa 2'],label_visibility='collapsed')
if state=='Pāli':pali_reader()
elif state=='Tụng / IPA':chanting()
elif state=='Anh–Việt':panel()
elif state=='Từ điển':dictionary_view('left')
elif state=='DPD':dpd()
elif state=='Mục từ':dictionary_entry()
elif state=='Bảng Anh':english_data('table')
elif state=='Văn bản Anh':english_data('text')
elif state=='LCDP':lcdp_reader('pali_json')
elif state=='Sujato':full_dictionary()
else:assert try_tdk_results([('Từ điển minh họa','**dhamma**','teaching; wisdom'),('Pāli–Việt','sati','niệm'),('Anh–Việt','peace','an bình')],'reference',page_size=2)
