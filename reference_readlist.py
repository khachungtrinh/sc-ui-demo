"""Presentation extraction of ss.render_ss_readlist; fixture preparation only.
Columns, labels, table height and callback boundary retained. Disk progress removed.
"""
import streamlit as st
import pandas as pd
from fixtures import READLISTS
from presentation import readlist_topics

def render_ss_readlist(placeholder,on_load):
 with placeholder.container():
  st.subheader(':material/two_pager: Danh sách các tuyển tập')
  a,b,c,d=st.columns([1,2,2,1],vertical_alignment='bottom')
  selected_file=a.selectbox('Bộ tuyển tập:',list(READLISTS),key='key_readlist_loadfile')
  current=READLISTS[selected_file]
  selected_key=b.selectbox('Nhóm tuyển tập:',['DUYỆT NHIỀU DANH SÁCH --']+list(current),key='key_readlist_chapter_'+selected_file)
  if selected_key=='DUYỆT NHIỀU DANH SÁCH --':
   rows=pd.DataFrame({'Topics':list(current),'Suttas':[', '.join(v) for v in current.values()]})
   topics=readlist_topics(rows)
   selected=[uid for key in topics for uid in current[key]]
  else:
   selected=current[selected_key]
   st.table(pd.DataFrame({'Mã Kinh':selected,'Tên Kinh':['Kinh minh họa']*len(selected),'IRFF Tag':['niệm']*len(selected)}),height=850)
  value=c.selectbox('Danh sách kinh:',[selected] if selected else [],key='key_readlist_suttas_reference')
  d.button('Nạp danh sách',icon=':material/list_alt_add:',use_container_width=True,disabled=not selected,on_click=on_load,args=(value,))
