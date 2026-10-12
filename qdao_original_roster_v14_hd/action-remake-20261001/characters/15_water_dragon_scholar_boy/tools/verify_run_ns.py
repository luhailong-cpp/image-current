from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
d=json.loads((b/'audit/run-NS-selection.json').read_text(encoding='utf-8'))
errors=[]
for f in d['frames']:
 p=b/f['source'];h=hashlib.sha256(p.read_bytes()).hexdigest();im=Image.open(p)
 if h!=f['sha256']:errors.append(f"SHA mismatch {p.name}")
 if im.size!=(1254,1254) or im.mode!='RGBA':errors.append(f"format {p.name}")
 r=json.loads((b/f['generationRecord']).read_text(encoding='utf-8-sig'))
 if not r:errors.append(f"empty record {p.name}")
 if im.getchannel('A').getextrema()!=(0,255):errors.append(f"alpha {p.name}")
for di in ['N','S']:
 fs=[f for f in d['frames'] if f['direction']==di]
 if sorted(f['frame'] for f in fs)!=list(range(1,17)):errors.append(di+' incomplete')
 ap=Image.open(b/'audit/ns-review'/f'{di}-720ms.apng')
 if ap.n_frames!=16:errors.append(di+' APNG frames')
 times=[]
 for i in range(ap.n_frames):
  ap.seek(i);times.append(ap.info.get('duration'))
 if sum(times)!=720:errors.append(di+' APNG duration')
report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'counts':{di:sum(f['direction']==di for f in d['frames']) for di in ['N','S']},'uniqueSHA':len(set(f['sha256'] for f in d['frames'])),'errors':errors,'passed':not errors,'scope':'file integrity only; static/dynamic conclusions in run-NS-review.json'}
(b/'audit/run-NS-integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))

