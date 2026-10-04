"""Synthetic public fixtures only. Shapes follow the accepted presentation contracts.
These are UI samples, not excerpts from a private corpus or dictionary.
"""
from copy import deepcopy
from html import escape
import hashlib,json

PI={'ref:1':'Dhammaṃ passati. Sabbe saṅkhārā aniccā.', 'ref:2':'Sati paññā mettā karuṇā — ā ī ū ṅ ñ ṭ ḍ ṇ ḷ ṃ.', 'ref:3':'Dhammaṃ passati. '*24}
EN={'ref:1':'Mindfulness and wisdom bring peace.', 'ref:2':'A reader can compare this short sentence with a longer example. '*12}
VI={'ref:1':'Đây là dữ liệu minh họa giao diện, không phải bản dịch kinh.', 'ref:2':'Một đoạn tiếng Việt dài để kiểm tra xuống dòng, dấu câu và bố cục. '*14}
EN_LOOKUP={word:f'<p><strong>{word}</strong> — nghĩa minh họa tiếng Việt.</p>' for word in ['mindfulness','wisdom','peace','reader','example','teaching','dhamma']}
PI_LOOKUP={word:'<p><b>'+word+'</b> — teaching; nghĩa minh họa.</p>' for word in ['dhammaṃ','dhamma','passati','sabbe','saṅkhārā','aniccā','sati','paññā','mettā','karuṇā']}
CANON_PI={k:{'dppn_html':v,'pts_html':v,'cepd_html':v,'html':v,'meaning':v} for k,v in PI_LOOKUP.items()}
TEXT='\n\n'.join(VI.values())+'\n\n'+ '\n'.join(PI.values())
HTML='<h3>Nội dung minh họa</h3>'+''.join('<p>'+escape(v)+'</p>' for v in PI.values())
TABLE='<table><thead><tr><th>ID</th><th>Pāli</th><th>Tiếng Việt</th></tr></thead><tbody>'+''.join(f'<tr><td>{k}</td><td>{escape(v)}</td><td>{escape(VI.get(k,VI["ref:1"]))}</td></tr>' for k,v in PI.items())+'</tbody></table>'
HITS=[{'hit':{'title':f'Kinh minh họa {i} — Việt / Pāli / 漢字','snippet':'Đoạn văn minh họa có chánh niệm và trí tuệ. '+('Nội dung dài. '*i),'path':f'fixture-{i}'},'count':i,'count_q2':1} for i in range(1,8)]
TAISHO={'version':1,'resource_id':'reference-taisho','revision':'fixture-v1','sections':[{'breadcrumb':['Đại Tạng minh họa','Quyển 1',f'Mục {i}'],'overview':False,'content':f'第{i}章 — Văn bản minh họa\n\n'+TEXT} for i in range(1,4)]}
READLISTS={'Tuyển tập minh họa':{'Nhóm ngắn':['mn1','mn2'],'Nhóm dài':['mn3','sn1.1','dn1']}}

def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def collection_resource(empty=False):
 from new_ss_collection_service import COLUMNS,DISPLAY_MODES,resource_revision
 collections={}
 for name,count in [('Trung Bộ',4),('Tương Ưng',3),('Bộ rỗng',0)]:
  rows=[] if empty else [{'sutta_id':f'mn{i}','title_pali':'Dhammaṃ — tên kinh minh họa dài '+str(i),'description':'Mô tả minh họa có Unicode, khoảng trắng và xuống dòng. '*i,'irff_tag':'niệm | tuệ','parallels':['dn1','sn1.1']} for i in range(1,count+1)]
  collections[name]={'label':name,'statistics':{'count_with_parallels':len(rows),'total_in_collection':8,'percentage':len(rows)/8*100},'rows':rows}
 links={uid:{'label':uid,'online_href':None,'offline_href':None} for uid in ['mn1','mn2','mn3','mn4','dn1','sn1.1']}
 data={'schema_version':1,'resource_id':'ss:reference-collection','cache_version':2,'heading':'Bảng dữ liệu song song toàn tập','columns':list(COLUMNS),'default_collection':'Trung Bộ','default_display_mode':'text','display_modes':[{'id':k,'label':v} for k,v in DISPLAY_MODES],'collection_order':list(collections),'collections':collections,'links':links,'link_target':'_blank'}
 data['revision']=resource_revision(data);return data

def dpd_result():
 return {'display_version':1,'entries':[{'lemma':lemma,'plus_case':'','construction_summary':'dhamma','pos':'noun','meaning_html':'<p>teaching; wisdom</p>','completion':'✓','sections':{'grammar':{'label':'grammar','language':'en','html':'<p>Reference grammar example.</p>','items':[]},'examples':{'label':'examples','language':'pi','html':'<p>Dhammaṃ passati.</p>','items':[]}}} for lemma in ['dhamma','dhamma 2']],'meta':{'deconstructor':['dhamma + ṃ']}}
