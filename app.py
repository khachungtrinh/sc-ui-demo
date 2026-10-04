"""Independent public UI reference. All data is synthetic and session-local."""
import streamlit as st
from st_style import *
import new_components_v2_config as v2_policy

st.set_page_config(page_title='SCAPP — UI Reference',page_icon=':material/moon_stars:',layout='wide')
config_layout()
app_layout_style()
checkbox_as_button_style()
sidebar_widget_font_size(14)
sidebar_collapse_style()
main_page_style()
# Reference must surface a v2 mount failure instead of silently using legacy UI.
v2_policy.V2_STRICT=True
pages=[
 st.Page('reference_pages/controls.py',title='UI Controls',icon=':material/tune:',default=True,url_path='controls'),
 st.Page('reference_pages/dt.py',title='Đại Tạng',icon=':material/collections_bookmark:',url_path='dt'),
 st.Page('reference_pages/sc.py',title='Tam Tạng',icon=':material/clarify:',url_path='sc'),
 st.Page('reference_pages/ss.py',title='Đối Chiếu',icon=':material/library_books:',url_path='ss'),
 st.Page('reference_pages/td.py',title='Tụng Đọc',icon=':material/dialogs:',url_path='td'),
 st.Page('reference_pages/reading.py',title='Văn Bản',icon=':material/library_add:',url_path='reading'),
 st.Page('reference_pages/tools.py',title='Công Cụ',icon=':material/cards_star:',url_path='tools')]
st.navigation(pages).run()
