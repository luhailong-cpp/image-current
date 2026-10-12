import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
ap=Path(sys.argv[1]);a=read(ap);assert a['status'] in ['passed','internal_visual_qa_passed_south_join_pending','internal_visual_qa_passed']
for r in [a['candidate'],a['context'],a.get('trace',a.get('repairTrace'))]:assert prod.sha(r['path'])==r['sha256']
l=read(z/'current-tile-ledger.json')
for e in l['tiles']:
 if e['tile']==a['tile']:e.update({'current4096':a['candidate'],'nativeContext':a['context'],'sourceTrace':a.get('trace',a.get('repairTrace')),'internalQa':'passed','internalAudit':ref(ap),'knownSharedEdgesQa':'pending','artExport':False})
prod.write(z/'current-tile-ledger.json',l)
print(json.dumps({'adopted':a['tile'],'audit':ref(ap)}))
