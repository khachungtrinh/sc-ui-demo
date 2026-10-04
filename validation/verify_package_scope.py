"""Validate new deliverable scope without rerunning frozen UI tests."""
from pathlib import Path
import ast,json,hashlib
root=Path(__file__).resolve().parents[1]
backend={'sqlite3','whoosh','api_client','google','requests','httpx','subprocess','constants','new_dictionary_data'}
imports=[];mutations=[];parsed=0
for p in list(root.glob('*.py'))+list((root/'reference_pages').glob('*.py')):
 t=ast.parse(p.read_text());parsed+=1
 for n in ast.walk(t):
  if isinstance(n,(ast.Import,ast.ImportFrom)):
   names=[n.module or ''] if isinstance(n,ast.ImportFrom) else [a.name for a in n.names]
   imports += [{'file':str(p.relative_to(root)),'line':n.lineno,'module':name} for name in names if name.split('.')[0] in backend]
  if isinstance(n,ast.Call):
   call=ast.unparse(n.func)
   if call.endswith(('.write_text','.write_bytes','.unlink','.mkdir','.rmdir')) or call in {'os.remove','shutil.rmtree'}:mutations.append({'file':p.name,'line':n.lineno,'call':call})
assert not imports,imports
assert not mutations,mutations
for p in root.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:
  assert p.suffix not in {'.db','.sqlite','.sqlite3','.apkg','.mdx','.mdd','.pdf','.mp3','.mp4'},p
  assert p.name not in {'secrets.toml','.env'},p
reuse=json.loads((root/'reports/REUSE_MANIFEST.json').read_text())
assert all(hashlib.sha256((root/r['target']).read_bytes()).hexdigest()==r['reference_sha256'] for r in reuse)
report={'status':'PASS','runtime_python_files_parsed':parsed,'production_backend_imports':imports,'runtime_filesystem_mutation_calls':mutations,'excluded_sensitive_file_types':'not included','fixtures':'synthetic authored data; no production datasets copied','network_evidence':'Frozen BROWSER_CHECKS.json: no external requests observed in 39 scenarios','limits':'Static selected-call scan and observed scenarios, not a formal security audit. Original public navigation/clipboard/browser-local UI storage are retained. Framework caches/logging are not SCAPP persistence.'}
(root/'reports/PUBLIC_SAFETY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
