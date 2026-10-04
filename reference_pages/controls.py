"""Reference-only gallery of controls found in the current source inventory."""
import streamlit as st
import pandas as pd
st.subheader('SCAPP — UI Reference')
st.caption('Dữ liệu minh họa • Chọn một trang và trạng thái ở thanh bên để xem giao diện.')
a,b=st.columns([1,1])
with a:
 st.selectbox('Chọn bộ tra cứu:',['Đại Chánh Tạng','Đại Tạng','Không có dữ liệu'],index=0)
 st.multiselect('Thẻ:',['A Hàm','Kinh','Luận'],default=['Kinh'],accept_new_options=True)
 st.text_input(':material/search: từ khóa chính:',value='Dhamma — chánh niệm')
 st.text_area('Nội dung văn bản:',value='Tiếng Việt / Pāli / 漢字\nā ī ū ṅ ñ ṭ ḍ ṇ ḷ ṃ',height=200)
 st.number_input('Giới hạn số từ an toàn (Base Limit):',value=2000,min_value=500,max_value=10000,step=500)
 st.radio('Công cụ dữ liệu',['Tạo chỉ mục','Lab crop PDF'],horizontal=True)
 c,d=st.columns(2);c.toggle('Dữ liệu');d.checkbox('Chọn kinh')
 st.segmented_control('Chọn chế độ đối chiếu:',['tracuu','tudien'],default='tracuu')
 st.pills('Chế độ làm việc:',['Ghi lại','Viết bài'],default='Ghi lại')
 c,d=st.columns(2);c.button('Nạp danh sách',icon=':material/list_alt_add:',width='stretch');d.button('Về',icon=':material/back_to_tab:',disabled=True,width='stretch')
 st.menu_button('Thao tác',['Sửa','Khôi phục','Xóa'])
with b:
 st.file_uploader('Chọn tài liệu:',type=['txt','json'],disabled=True)
 st.button('Tải xuống',icon=':material/download:',disabled=True)
 st.link_button('Hướng dẫn Streamlit','https://docs.streamlit.io',disabled=True)
 st.badge('Đang xem dữ liệu minh họa',color='gray')
 tabs=st.tabs(['✎ Chỉnh sửa & Quản lý','Văn bản gốc'])
 with tabs[0]:st.data_editor(pd.DataFrame({'Chọn':[True,False],'Từ':['dhamma','sati'],'Nghĩa':['pháp','niệm']}),hide_index=True)
 with tabs[1]:st.json({'ref:1':'Dhammaṃ passati.'})
 with st.popover('Xóa tệp',icon=':material/delete:'):
  st.markdown('**⚠️ Chú ý**');st.button('Xác nhận xóa',type='primary')
 with st.expander('Hướng dẫn sử dụng'):st.markdown('Đây là bộ tham chiếu UI. Các thao tác xử lý dữ liệu được thay bằng fixture hoặc trạng thái trong phiên.')
 st.table(pd.DataFrame({'ID':['ref:1'],'Nội dung':['Một dòng minh họa.']}))
 st.code('{"ref:1": "Dhammaṃ passati."}',language='json')
 st.info('Thông tin minh họa.');st.warning('Cảnh báo minh họa.');st.error('Lỗi minh họa.');st.success('Hoàn tất minh họa.')
