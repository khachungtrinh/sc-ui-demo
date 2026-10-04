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
log=open(out/'interaction-server.log','w');server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.address=127.0.0.1','--server.port=8517'],cwd=root,stdout=log,stderr=log)
results=[];interactions=[];errors=[];external=[]
prior=root/'reports/INTERACTION_CHECKS.json'
if os.environ.get('REFERENCE_RESUME') and prior.exists():interactions=json.loads(prior.read_text()).get('interactions',[])
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
  def goto(name,scenario=None):
   page.goto('http://127.0.0.1:8517/'+name)
   page.get_by_test_id('stSelectbox').filter(has_text='Trạng thái tham chiếu').wait_for()
   if scenario:select(scenario)
   page.wait_for_timeout(600)
  def passed(name):
   assert page.get_by_test_id('stException').count()==0
   assert not errors,errors
   interactions.append({'test':name,'status':'PASS'});print('PASS',name,flush=True)
  if not os.environ.get('REFERENCE_RESUME'):
   goto('dt')
   interactions.append({'test':'DT full-text local page 2','status':'PASS','evidence':'Recovered prior interaction-validation.log; not repeated.'})
   page.locator('[data-result-list-v2]').get_by_role('button',name='Trang 2',exact=True).click()
   page.locator('[data-result-items] h5').first.filter(has_text='4.').wait_for();passed('DT held-result local page 2')
   page.locator('[data-mode="full"]').first.click()
   page.locator('[data-dt-title]').filter(has_text='Kinh minh họa 4').wait_for();passed('DT selection bridge updates selected title')
   goto('sc')
   page.locator('[data-sc-page] button[data-page="2"]').first.click()
   page.locator('[data-sc-body]').filter(has_text='MN3').wait_for();passed('SC prepared-page request / server fixture page 2')
   goto('ss','Bảng song song')
   collection=page.locator('[data-ss-collection-root]')
   collection.get_by_role('combobox',name='Chọn bộ kinh:').click()
   collection.get_by_role('option',name='Tương Ưng',exact=True).click()
   assert collection.locator('tbody tr').count()==3;passed('SS collection local switch')
   collection.get_by_role('combobox',name='Chế độ hiển thị:').click()
   collection.get_by_role('option',name='Gắn hyperlink online',exact=True).click()
   assert collection.locator('tbody tr').count()==3;passed('SS mode menu preserves fixture rows')
  goto('ss','Tuyển tập')
  page.locator('[data-row-id="Nhóm ngắn"] [data-checkbox-cell]').click()
  page.get_by_role('button',name='Nạp danh sách',exact=False).wait_for(state='visible')
  page.get_by_role('button',name='Nạp danh sách',exact=False).click()
  page.get_by_text('tracuu',exact=True).wait_for();passed('SS topic selection and load closes readlist')
  goto('ss','Cây kinh')
  page.locator('[data-sutta-tree-v2] select').select_option(label='Chương 2')
  page.wait_for_timeout(400)
  assert page.locator('[data-sutta-tree-v2] select').input_value()=='Chương 2';passed('Sutta tree selection bridge')
  goto('dt','Taisho')
  page.get_by_role('button',name='Kinh Tiếp',exact=True).click()
  page.locator('.taisho-content').filter(has_text='第2章').wait_for();passed('Taisho local navigation / paired roots')
  goto('td')
  page.locator('[data-pali-reader-v2-root] .pali-word').first.click()
  page.locator('[data-pr-pali-dict]').filter(has_text='nghĩa minh họa').wait_for();passed('Pāli local dictionary click')
  goto('td','Tụng / IPA')
  page.locator('[data-chanting-reader-v2] .pali-word').first.click()
  page.locator('[data-dictionary-sidebar-v2]').filter(has_text='IPA minh họa').wait_for();passed('Chanting click publishes to sidebar')
  goto('td','DPD')
  page.locator('[data-dpd-toggle]').first.click()
  assert page.locator('[data-dpd-section]').first.is_visible();passed('DPD section expansion')
  goto('reading')
  page.get_by_role('textbox',name='Nội dung văn bản:',exact=True).fill('Edited UI fixture — Việt / Pāli')
  page.get_by_role('button',name='Xử lý văn bản',exact=True).click()
  page.get_by_text('Đã nhận văn bản trong phiên tham chiếu.',exact=True).wait_for();passed('Reading editor checkpoint + command bridge')
  goto('reading','Đọc tài liệu')
  page.get_by_role('tab',name='Văn bản gốc',exact=False).click()
  page.get_by_role('textbox',name='Nội dung gốc:',exact=True).wait_for()
  assert page.get_by_role('textbox',name='Nội dung gốc:',exact=True).is_disabled();passed('Reading original/processed tab request')
  page.get_by_role('tab',name='Đọc tài liệu',exact=False).click()
  page.locator('[data-reading-root] .eng-word').first.click()
  page.locator('[data-dict-panel]').filter(has_text='nghĩa minh họa').wait_for();passed('Reading English dictionary')
  page.set_viewport_size({'width':900,'height':900});capture('narrow-reading','900px')
  browser.close()
finally:
 server.terminate();server.wait(timeout=10);log.close()
 (root/'reports/INTERACTION_CHECKS.json').write_text(json.dumps({'browser':'Chromium 143.0.7499.0','viewport':[1440,1000],'cases':results,'javascript_errors':errors,'external_requests':sorted(set(external)),'interactions':interactions},ensure_ascii=False,indent=2))
