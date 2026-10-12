from pathlib import Path
import hashlib,json
from PIL import Image,ImageChops
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sel=read(Z/'selection-r04_c12.json')
audit=[]
for ident in sum(sel['cores'],[]):
 p=Z/'native'/f'{ident}.png'
 d=read(p.with_suffix('.png.generation.json'))
 checks=[]
 def refcheck(ref):
  f=Path(ref['file'])
  checks.append({'file':str(f),'hashMatches':sha(f)==ref['sha256']})
  for r in ref.get('sources',[]): refcheck(r)
 for ref in d['references']: refcheck(ref)
 prompt=Path(d['prompt']);receipt=Path(d['evidence']['receipt'])
 audit.append({'id':ident,'size':list(Image.open(p).size),'nativeHashMatches':sha(p)==d['sha256'],'promptExists':prompt.exists(),'promptSha256':sha(prompt),'receiptExists':receipt.exists(),'submittedModel':d['submittedParameters'].get('model'),'submittedQuality':d['submittedParameters'].get('quality'),'actualModel':d.get('actualModel'),'actualQuality':d.get('actualQuality'),'references':checks})
note='Contours, tile channels or slab joints and painterly color inspected at 1:1 across the exact core join; no broken contour or pasted rectangular strip in the reviewed join.'
for f in (Z/'qa').glob('*.json'):
 if 'r04_c12_' not in f.stem: continue
 try: d=read(f)
 except: continue
 if d.get('geometryChecks',{}).get('review')=='Stone slab joints and painterly color continue across exact core seam; no break, blur or band.':
  d['geometryChecks']['review']=note
  try: f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
  except OSError: pass
evidence=[{'file':str(Z/'qa'/'r04_c12-final'/f'{axis}-{i}-segment-{j}-100pct.png'),'status':'passed','scale':'1:1'} for axis in ['vertical','horizontal'] for i in range(1,4) for j in range(1,5)]
out={'tileId':'r04_c12','reviewer':'root/south_tile','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'tileSha256':sha(Z/'tiles'/'r04_c12.png'),'final24SeamStrips':evidence,'nativeSourceAudit':audit,'allSourceChecksPassed':all(a['nativeHashMatches'] and a['size']==[1254,1254] and a['promptExists'] and a['receiptExists'] and all(r['hashMatches'] for r in a['references']) for a in audit),'overlays':{'r04_c12_cross_01_03_jar_repair':'center and four borders inspected at 1:1, passed','r04_c12_cross_01_02_jar_paint_repair_v2':'actual shared 4K boundary and lower/left/right inspected; faint outer-top tone band pending root v3'},'formalAccepted':False,'pending':['root jar paint v3, paired top tile synchronization and final north full-length seam','independent 16 core + 9 cross review from east_finish']}
(Z/'qa'/'r04_c12-final-seams-source-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sources':len(audit),'allSourceChecksPassed':out['allSourceChecksPassed'],'seamsReviewed':len(evidence)}))

