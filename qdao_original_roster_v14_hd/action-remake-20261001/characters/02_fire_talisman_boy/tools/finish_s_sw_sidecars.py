import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
inv=json.loads((R/'inventory-hit.json').read_text(encoding='utf-8-sig'))
for f in inv['frames']:
 if f['action']!='run' or f['direction'] not in ['S','SW']: continue
 p=R/f['path']
 for suffix in ['.png.generation.json','.generation.json']:
  sp=p.with_suffix(suffix)
  if not sp.exists():continue
  sc=json.loads(sp.read_text(encoding='utf-8-sig'));sc['file']=f['path'];sc['sha256']=f['sha256'];sc['generationRecord']=f['source_record']
  sc.setdefault('derivedFrom',{})['generationRecord']=f['source_record']
  sc['derivedFrom']['record']=f['source_record']
  sp.write_text(json.dumps(sc,ensure_ascii=False,indent=2),encoding='utf-8')
print('S/SW current sidecar record links synchronized')

