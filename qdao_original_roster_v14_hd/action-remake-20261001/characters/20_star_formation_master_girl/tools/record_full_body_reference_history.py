"""Preserve source-record resolution after runtime references acquire later review metadata."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[]
for label in ['v1','v2']:
 path=R/f'hand-review-20261005/E/07-arms-{label}.png.generation.json';rec=rd(path)
 for ref in rec['references']:
  item={'consumerNativeRecord':path.relative_to(R).as_posix(),'consumerNativeRecordSha256':sha(path),'submittedPath':ref['path'],'role':ref['role'],'inputImageSha256':ref['sha256'],'submittedGenerationRecordSha256':ref.get('generationRecordSha256')}
  p=Path(ref['path'])
  if p.is_relative_to(R/'runtime'):
   saved=R/'provenance/full-body-prior-records'/(str(p.relative_to(R/'runtime')).replace('\\','--').replace('/','--')+'.generation.json')
   assert sha(saved)==ref['generationRecordSha256']
   assert rd(saved)['sha256']==ref['sha256']
   item.update(sourceRecordAtRequest=saved.relative_to(R).as_posix(),recordSha256=sha(saved),currentRuntimeRecordMayDiffer=True)
  elif ref.get('generationRecord'):
   saved=Path(ref['generationRecord']);assert sha(saved)==ref['generationRecordSha256']
   item.update(sourceRecordAtRequest=saved.relative_to(R).as_posix(),recordSha256=sha(saved))
  rows.append(item)
out=R/'provenance/full-body-reference-history.json'
wr(out,{'time':datetime.now(timezone.utc).isoformat(),'scope':'run/E/07 v1 and v2 input reference text evidence; historical native records unmodified','references':rows,'actualModel':None,'actualQuality':None})
p=R/'runtime/run/E/07.png.generation.json';rec=rd(p);rec['fullBodyReferenceHistory']=out.relative_to(R).as_posix();wr(p,rec)
print('Source record history verified: '+str(len(rows)))

