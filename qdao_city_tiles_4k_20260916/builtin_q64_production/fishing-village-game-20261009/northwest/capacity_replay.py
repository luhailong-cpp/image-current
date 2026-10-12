from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
cases=[('r03_c03','tiles/r03_c03.candidate-repair-v5.png','tiles/r03_c03.source-id-repair-v5.png','tiles/r03_c03.repair-v5.assembly.json'),('r04_c03','work-r04_c03/output/r04_c03.candidate.png','work-r04_c03/output/r04_c03.source-id.png','work-r04_c03/output/r04_c03.assembly.json'),('r03_c02','work-r03_c02/tiles/r03_c02.candidate.png','work-r03_c02/tiles/r03_c02.candidate.source-id.png','work-r03_c02/tiles/r03_c02.candidate.assembly.json')]
results=[];refs={}
for tile,cp,ip,rp in cases:
 a=np.asarray(Image.open(ROOT/cp).convert('RGB'));ids=np.asarray(Image.open(ROOT/ip));rec=read(ROOT/rp);box=rec['globalCoreBox'];count=0;mismatch=0;sources=[]
 assert a.shape==(4096,4096,3) and ids.shape==(4096,4096)
 for s in rec['sources']:
  f=resolve(s['file']);gr=read(resolve(s['generationRecord']));b=gr['globalNativeBox'];src=np.asarray(Image.open(f).convert('RGB'))
  assert sha(f)==s['sha256']==gr['sha256']
  ys,xs=np.nonzero(ids==s['sourceId']);sx=xs+box[0]-b[0];sy=ys+box[1]-b[1]
  assert ((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)).all()
  bad=int(np.any(a[ys,xs]!=src[sy,sx],axis=1).sum());mismatch+=bad;count+=len(xs)
  sources.append({'file':str(f),'sha256':sha(f),'pixels':len(xs),'mismatches':bad})
  for r in gr.get('references',[]):
   ref=resolve(r['file']);key=(str(ref),r['sha256'])
   refs[key]={'file':str(ref),'historicalSha256':r['sha256'],'existsNow':ref.is_file(),'currentHashMatches':sha(ref)==r['sha256'] if ref.is_file() else None}
 assert count==16777216 and mismatch==0
 results.append({'tile':tile,'candidate':cp,'candidateSha256':sha(ROOT/cp),'assembly':rp,'assemblySha256':sha(ROOT/rp),'sourceIdMap':ip,'sourceIdSha256':sha(ROOT/ip),'pixelsVerified':count,'mismatches':mismatch,'sources':sources})
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'method':'Independent per-pixel reconstruction from final source ID, global tile origin and native global box; no resizing','results':results,'totalPixelsVerified':sum(r['pixelsVerified'] for r in results),'nativeSourceReplayPassed':True,'referenceRevalidation':list(refs.values()),'referenceRevalidationComplete':all(r['currentHashMatches'] is True for r in refs.values()),'note':'Current reference presence is separate from historically saved generation evidence and source-exact pixel replay.'}
p=ROOT/'qa/capacity-gate/provenance-replay.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tiles':len(results),'verifiedPixels':out['totalPixelsVerified'],'mismatches':0,'referenceIssues':[r for r in refs.values() if r['currentHashMatches'] is not True]}))

