from pathlib import Path
from PIL import Image
import json,hashlib,sys,numpy as np
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/'r09_c03/pipeline/output/9f21c0744b4d7769/assembly.json';a=read(ap);assert a['complete4kCandidate'] and len(a['nativeSources'])==16
for n in a['nativeSources']:
 for fk,hk in [('nativeFile','nativeSha256'),('recordFile','recordSha256'),('receiptFile','receiptSha256')]:assert sha(n[fk])==n[hk]
 assert Image.open(n['nativeFile']).size==(1254,1254)
for e in [a['output'],a['contextOutput']]:assert sha(e['file'])==e['sha256']
im=Image.open(a['output']['file']).convert('RGB');ctx=Image.open(a['contextOutput']['file']).convert('RGB');assert np.array_equal(np.array(im),np.array(ctx.crop((115,115,4211,4211))))
q=ap.parent/'root-handoff-review-20261013';q.mkdir(exist_ok=False)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-QA-only.png')
boxes=[(1423,1000,2677,2254),(2450,2800,3704,4054)]
for i,box in enumerate(boxes,1):im.crop(box).save(q/f'targeted-{i}.native.png')
atomic_json(q/'verification.json',{'assembly':str(ap),'assemblySha256':sha(ap),'native16SourcesAndReceiptHashesVerified':True,'coreAndContextHashesVerified':True,'coreEqualsExactContextCrop':True,'targetedBoxesInCore':boxes,'sourceResampling':False,'overviewOnlyResized':True,'actualRootVisualReview':'pending','internalPassed':False,'formalAccepted':False})
print(q)
