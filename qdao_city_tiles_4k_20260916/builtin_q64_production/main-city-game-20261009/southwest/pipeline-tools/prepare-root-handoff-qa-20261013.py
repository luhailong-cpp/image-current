from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[('r09_c02','8550093af869f2fe'),('r10_c07','a53dc8484e14fa8d'),('r14_c05','ab1faa3c5ebbd269')]
out=[]
for tile,aid in items:
 ap=B/tile/'pipeline/output'/aid/'assembly.json';a=read(ap)
 assert a['complete4kCandidate'] and len(a['nativeSources'])==16 and not a['sourceResampling']
 for e in [a['output'],a['contextOutput']]: assert sha(e['file'])==e['sha256']
 core=Image.open(a['output']['file']).convert('RGB');ctx=Image.open(a['contextOutput']['file']).convert('RGB')
 assert core.size==(4096,4096) and ctx.size==(4326,4326)
 assert np.array_equal(np.array(core),np.array(ctx.crop((115,115,4211,4211))))
 for n in a['nativeSources']:
  for f,h in [('nativeFile','nativeSha256'),('recordFile','recordSha256'),('receiptFile','receiptSha256'),('promptFile','promptSha256')]:assert sha(n[f])==n[h],(tile,n['id'],f)
  assert Image.open(n['nativeFile']).size==(1254,1254)
  g=read(n['recordFile']);assert sha(g['request'])==g['requestSha256']
 q=ap.parent/'root-handoff-qa-20261013';q.mkdir(exist_ok=False)
 core.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-QA-only.png')
 crops={
  'r09_c02':[(1423,2600,2677,3854),(2450,500,3704,1754)],
  'r10_c07':[(400,600,1654,1854),(1700,1400,2954,2654),(2800,2800,4054,4054)],
  'r14_c05':[(1423,1800,2677,3054),(2450,2500,3704,3754),(500,400,1754,1654)]}[tile]
 files=[]
 for i,box in enumerate(crops,1):
  fp=q/f'targeted-{i}.native.png';core.crop(box).save(fp);files.append({'file':str(fp),'sha256':sha(fp),'boxInCore':box,'sourceResampling':False})
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'assembly':str(ap),'assemblySha256':sha(ap),'tile':tile,'nativeSlotCount':16,'allSourceReceiptRequestPromptHashesVerified':True,'coreEqualsExactContextCrop':True,'sourceResampling':False,'qaOnlyOverviewResized':True,'targetedNativeCrops':files,'visualReviewStatus':'pending_root_actual_view','internalPassed':False,'formalAccepted':False}
 atomic_json(q/'verification.json',report);out.append(report)
print(json.dumps(out,ensure_ascii=False))
