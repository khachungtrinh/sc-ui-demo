# Representative actual clusters from tl.py 345–455,1097–1110,1669+.
import streamlit as st
import pandas as pd
from presentation import choose
from fixtures import READLISTS
state=choose(['Danh sách đọc','Quản lý tệp','Ghi chú','Hướng dẫn'])
if state=='Danh sách đọc':
 left,right=st.columns([2,1])
 with right:
  st.subheader('Công cụ chuẩn hóa')
  mode=st.pills('Hãy chọn công cụ:',['tạo danh sách','tạo từ điển'],default='tạo danh sách',label_visibility='collapsed')
  raw=st.text_area('Nhập mã thô:',height=200,placeholder='mn3, MN4, sn12:3')
  converted=st.button('Chuyển đổi',icon=':material/transform:',use_container_width=True)
  st.code('["mn3", "mn4", "sn12.3"]' if converted else 'Hãy nhập liệu..',language='json',height=330)
 with left:
  edit,create=st.tabs(['✎ Chỉnh sửa & Quản lý','✚ Tạo danh sách mới'])
  with edit:
   a,b=st.columns([3,1],vertical_alignment='bottom')
   a.selectbox('Chọn file để chỉnh sửa:',['reference_readlist.json'],label_visibility='collapsed')
   b.button('Khôi phục mặc định',icon=':material/settings_backup_restore:',use_container_width=True)
   st.text_area('Nội dung chỉnh sửa (Định dạng JSON):',value='{"Nhóm minh họa": ["mn1", "mn2"]}',height=600)
   if st.button('Lưu thay đổi',type='primary',icon=':material/playlist_add:',use_container_width=True):st.success('Đã nhận thay đổi trong phiên tham chiếu.')
  with create:
   st.text_input('Tên danh sách:');st.text_area('Nội dung danh sách:',height=600);st.button('Tạo danh sách',icon=':material/add:')
elif state=='Quản lý tệp':
 cols=st.columns([2,2,2,1,1],vertical_alignment='bottom')
 cols[0].selectbox('Thư mục:',['minh-hoa']);cols[1].selectbox('Tệp:',['reference.txt']);cols[2].text_input('Đổi tên:',value='reference.txt');cols[3].button('Đổi tên')
 with cols[4].popover('Xóa tệp',use_container_width=True,icon=':material/delete:'):
  st.markdown('**⚠️ Chú ý**');st.markdown('Xóa vĩnh viễn: `reference.txt`?')
  if st.button('Xác nhận xóa',type='primary',use_container_width=True):st.success('Mô phỏng xóa trong phiên.')
 st.dataframe(pd.DataFrame({'Tên':['reference.txt','sample.json'],'Loại':['txt','json'],'Kích thước':['1 KB','2 KB']}),hide_index=True)
 st.button('Tải xuống',disabled=True,icon=':material/download:')
elif state=='Ghi chú':
 a,b=st.columns(2)
 with a:st.subheader('Nội dung đang đọc');st.text_area('Nội dung:',height=600)
 with b:
  st.subheader(':material/draw: Ghi chú lại');x,y=st.columns([1,1],vertical_alignment='center')
  x.pills('Chế độ làm việc:',['Ghi lại','Viết bài'],default='Ghi lại',label_visibility='collapsed')
  with st.container(height=200,border=False):
   note=st.chat_input('Gõ ghi chú tổng hợp đã hoàn thiện...',key='synth_input')
  if note:
   with st.chat_message('user'):st.write(note)
else:
 for title in ['Hướng dẫn sử dụng','Tạo danh sách đọc','Quản lý dữ liệu']:
  with st.expander(title):st.markdown('Dữ liệu và thao tác trên trang tham chiếu chỉ dùng để xem giao diện.')
