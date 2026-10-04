"""Python-side navigation/scenario checks. Browser evidence is separate."""
import json,os,sys
from pathlib import Path
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parents[1];os.chdir(root);sys.path.insert(0,str(root))
results=[]
for name in ['controls','dt','sc','ss','td','reading','tools']:
 from new_component_v2_support import get_v2_component
 get_v2_component.cache_clear() # Each AppTest has a fresh component registry.
 a=AppTest.from_file(str(root/'app.py'),default_timeout=30).run()
 if name!='controls':a.switch_page('reference_pages/'+name+'.py').run()
 results.append({'page':name,'scenario':'default','errors':[e.message for e in a.exception],'v2_elements':len(a.get('bidi_component'))})
 selectors=[s for s in a.selectbox if s.label=='Trạng thái tham chiếu']
 if selectors:
  for option in selectors[0].options[1:]:
   selector=next(s for s in a.selectbox if s.label=='Trạng thái tham chiếu');selector.select(option).run()
   results.append({'page':name,'scenario':option,'errors':[e.message for e in a.exception],'v2_elements':len(a.get('bidi_component'))})
   if a.exception:break
(root/'reports/PYTHON_RUNTIME_CHECKS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
assert not any(x['errors'] for x in results)
