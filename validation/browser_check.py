"""Real Chromium navigation, rendered v2 roots, DOM snapshots and interactions.
Dev dependency: playwright==1.58.0. Set REFERENCE_CHROMIUM to a local executable.
"""
import os,sys,json,time,subprocess,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'reports/browser';out.mkdir(exist_ok=True)
SCENARIOS={
 'dt':['Kết quả / toàn văn','Trích đoạn','Không có kết quả','Lỗi tìm kiếm','Taisho'],
 'sc':['Local Data','API SC','Từ điển','Sujato','LCDP','Không có kết quả'],
 'ss':['Đối chiếu','Cây kinh','Bảng song song','Tuyển tập','Bảng nội dung','Từ điển','Taisho','Bảng rỗng'],
 'td':['Pāli','Tụng / IPA','Anh–Việt','Từ điển','DPD','Mục từ','Bảng Anh','Văn bản Anh','LCDP','Sujato','Kết quả từ điển'],
 'reading':['Nhập dữ liệu','Đọc tài liệu','AI workspace','Glossary'],
 'tools':['Danh sách đọc','Quản lý tệp','Ghi chú','Hướng dẫn']}
ROOTS='[data-result-list-v2],[data-dt-full-text-v2-root],[data-dt-snippets-v2-root],[data-taisho-root],[data-sc-page],[data-dictionary-root],[data-dictionary-reader-v2],[data-lcdp-reader-v2],[data-ss-content-v2-root],[data-ss-table-v2-root],[data-ss-collection-v2],[data-readlist-topics-v2],[data-sutta-tree-v2],[data-pali-reader-v2-root],[data-chanting-reader-v2],[data-panel-reader-v2],[data-dictionary-entry-v2],[data-english-data-reader-v2],[data-reading-root],[data-dictionary-sidebar-surface-v2]'
# Root selectors are additionally discovered from actual DOM attributes in snapshot().
SNAPSHOT='''() => {const roots=[]; function walk(node){for(const el of node.querySelectorAll('*')){if(el.shadowRoot){const sr=el.shadowRoot;roots.push({host:el.outerHTML.slice(0,500),html:sr.innerHTML,text:sr.textContent,style:{background:getComputedStyle(el).getPropertyValue('--st-background-color'),secondary:getComputedStyle(el).getPropertyValue('--st-secondary-background-color'),text:getComputedStyle(el).getPropertyValue('--st-text-color')}});walk(sr);}}}walk(document);return {url:location.pathname,viewport:[innerWidth,innerHeight],roots,native:document.querySelector('[data-testid="stAppViewContainer"]')?.outerHTML};}'''
log=open(out/'server.log','w');server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address=127.0.0.1','--server.port=8517'],cwd=root,stdout=log,stderr=log)
results=[];interactions=[];errors=[];external=[]
try:
 for _ in range(80):
  try:urllib.request.urlopen('http://127.0.0.1:8517/_stcore/health',timeout=1);break
  except Exception:time.sleep(.25)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('REFERENCE_CHROMIUM','/tmp/scapp-reference-chromium'),headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:external.append(r.url) if not r.url.startswith(('http://127.0.0.1','ws://127.0.0.1','data:','blob:')) else None)
  def select(label):
   page.get_by_test_id('stSelectbox').filter(has_text='Trạng thái tham chiếu').get_by_role('combobox').click()
   page.get_by_role('option',name=label,exact=True).click()
  def capture(key,scenario):
   # Wait until script and browser render settle; no source mount is credited from Python alone.
   page.wait_for_timeout(550)
   data=page.evaluate(SNAPSHOT)
   data['native']=data['native'].replace('http://127.0.0.1:8517','{REFERENCE_ORIGIN}') if data['native'] else ''
   (out/(key+'.dom.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
   page.screenshot(path=str(out/(key+'.png')),full_page=True)
   roots=[{'host':x['host'],'html_bytes':len(x['html']),'text_chars':len(x['text']),'style':x['style']} for x in data['roots']]
   record={'case':key,'scenario':scenario,'exceptions':page.get_by_test_id('stException').count(),'javascript_errors':list(errors),'shadow_roots':roots}
   results.append(record);print(key,'roots',len(roots),'exceptions',record['exceptions'],'js',len(errors),flush=True)
   assert not record['exceptions'] and not errors,record
  page.goto('http://127.0.0.1:8517');page.get_by_text('SCAPP — UI Reference',exact=True).wait_for();capture('controls','default')
  for name,scenarios in SCENARIOS.items():
   page.goto('http://127.0.0.1:8517/'+name)
   page.get_by_test_id('stSelectbox').filter(has_text='Trạng thái tham chiếu').wait_for()
   for index,scenario in enumerate(scenarios):
    if index:select(scenario)
    capture(f'{name}-{index:02}',scenario)
  browser.close()
finally:
 server.terminate();server.wait(timeout=10);log.close()
 (root/'reports/BROWSER_CHECKS.json').write_text(json.dumps({'browser':'Chromium 143.0.7499.0','viewport':[1440,1000],'cases':results,'javascript_errors':errors,'external_requests':sorted(set(external)),'interactions':interactions},ensure_ascii=False,indent=2))
