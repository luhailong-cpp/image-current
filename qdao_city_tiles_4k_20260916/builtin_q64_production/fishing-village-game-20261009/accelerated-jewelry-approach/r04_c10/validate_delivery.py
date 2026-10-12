from pathlib import Path
import json,hashlib
from PIL import Image
d=Path(__file__).parent
entries=[]
for r in range(1,5):
 for c in range(1,5):
  sel=json.loads((d/'records'/f'p{r}{c}.selection.json').read_text())
  p=Path(sel['file']); g=json.loads(Path(sel['generationRecord']).read_text())
  assert Image.open(p).size==(1254,1254)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==sel['sha256']==g['sha256']
  for suffix in ['prompt.txt','request.json','receipt.json']:
   assert (d/'records'/f'p{r}{c}-v1.{suffix}').exists()
  for q in g['references']:
   assert hashlib.sha256(Path(q['file']).read_bytes()).hexdigest()==q['sha256']
  entries.append({'patch':f'p{r}{c}','file':str(p),'sha256':sel['sha256'],'nativeDimensions':list(Image.open(p).size)})
candidate=d/'candidate/r04_c10-4096-candidate-v1.png'
mfile=candidate.with_suffix('.manifest.json')
m=json.loads(mfile.read_text()); assert Image.open(candidate).size==(4096,4096); assert hashlib.sha256(candidate.read_bytes()).hexdigest()==m['sha256']
m['seamReview']='24 internal seam regions visually reviewed at native scale; north segment1 sharpness mismatch in r03_c10 owner source pending repair; other external seams pending'
m['qaRecord']=str(d/'qa/seam-review-v1.json');m['formalAccepted']=False
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
audit={'verifiedSourceCount':16,'candidateDimensions':[4096,4096],'candidateSha256':m['sha256'],'sourceEntries':entries,'referencesHashesVerified':True,'requestsPromptsReceiptsPresent':True,'noFinalResize':True,'formalAccepted':False}
(d/'qa/provenance-audit-v1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verifiedSources':16,'candidateSha256':m['sha256'],'formalAccepted':False}))

