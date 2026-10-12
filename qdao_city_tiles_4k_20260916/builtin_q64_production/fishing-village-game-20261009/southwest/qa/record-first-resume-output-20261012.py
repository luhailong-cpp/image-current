import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
stem='r10_c03_p03_02_v2'
record=read(z/'native'/f'{stem}.png.generation.json')
im=z/'native'/f'{stem}.png'
assert prod.sha(im)==record['sha256']
rp=z/'production-resume-20261012.json';r=read(rp)
if not r.get('firstNewNativeOutput'):
 r['firstNewNativeOutput']={'image':ref(im),'generation':ref(z/'native'/f'{stem}.png.generation.json'),'receipt':ref(z/'native'/f'{stem}.receipt.json'),'prompt':ref(z/'native'/f'{stem}.prompt.txt'),'request':ref(z/'native'/f'{stem}.request.json'),'nativeDimensions':[record['width'],record['height']],'generatedAt':record['generatedAt']}
 r['updatedAtUtc']=datetime.now(timezone.utc).isoformat();prod.write(rp,r)
p=read(z/'progress.json');p.update({'productionResume':ref(rp),'status':'active_art_production','currentMilestone':'Resumed first native saved; root r11_c06 five localized repairs submitted','updatedAtUtc':datetime.now(timezone.utc).isoformat()});prod.write(z/'progress.json',p)
print(json.dumps(r['firstNewNativeOutput']))
