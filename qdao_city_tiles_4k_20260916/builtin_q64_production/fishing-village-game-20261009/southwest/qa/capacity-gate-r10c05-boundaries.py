from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;R=Q.parent;P='capacity-gate-r10c05'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=read(Q/(P+'-audit.json'));details=[]
def seam(a,b):
 cost=((a.astype(float)-b.astype(float))**2).sum(2);hh,ww=cost.shape;prev=np.zeros((hh,ww),np.int16);total=cost[0].copy()
 for y in range(1,hh):
  z=np.stack([np.r_[np.inf,total[:-1]],total,np.r_[total[1:],np.inf]]);c=z.argmin(0);prev[y]=np.arange(ww)+c-1;total=cost[y]+z[c,np.arange(ww)]
 s=np.zeros(hh,np.int16);s[-1]=total.argmin()
 for y in range(hh-1,0,-1):s[y-1]=prev[y,s[y]]
 return s
for axis,count in [('north',4),('west',3)]:
 for i in range(1,count+1):
  item=next(x for x in audit['selectedSlots'] if x['row']==(1 if axis=='north' else i) and x['column']==(i if axis=='north' else 1))
  req=read(Path(item['path']).with_suffix('.request.json'))
  match=f'r09_c05_p04_{i:02d}_' if axis=='north' else f'r10_c04_p{i:02d}_04_'
  src=next(x for x in req['overlaps'] if Path(x['path']).name.startswith(match))
  if not Path(src['path']).exists():
   details.append({'axis':axis,'part':i,'sourceUnavailable':src});continue
  a=np.asarray(Image.open(src['path']).convert('RGB'));b=np.asarray(Image.open(item['path']).convert('RGB'))
  if axis=='north':a=a.transpose(1,0,2);b=b.transpose(1,0,2)
  s=seam(a[:,-230:],b[:,:230]);merged=np.concatenate([a[:,:-230],np.where((np.arange(230)[None,:]>=s[:,None])[:,:,None],b[:,:230],a[:,-230:]),b[:,230:]],1)
  strip=merged[115:1139,819:1459]
  if axis=='north':strip=strip.transpose(1,0,2)
  p=Q/(P+f'-{axis}-{i}-100pct.png');Image.fromarray(strip).save(p)
  details.append({'axis':axis,'part':i,'path':p.as_posix(),'sha256':sha(p),'dimensions':[strip.shape[1],strip.shape[0]],'sources':[{'path':src['path'],'sha256':sha(src['path']),'historicalOverlapHash':src['sha256'],'hashMatches':sha(src['path'])==src['sha256']},{'path':item['path'],'sha256':item['sha256']}],'method':'Integer crop and minimal-error hard source-pixel choice across 230px overlap, no resample or feather','seamPath':s.tolist()})
checks=[]
for item in audit['allSavedAttempts']:
 rec=read(item['record'])
 for ref in rec['references']:
  p=Path(ref['path']);exists=p.exists();actual=sha(p) if exists else None
  checks.append({'attempt':Path(item['path']).stem,'reference':p.as_posix(),'exists':exists,'expectedSha256':ref['sha256'],'actualSha256':actual,'matches':actual==ref['sha256']})
audit['provenance']['referenceChecks']=checks
audit['provenance']['referenceHashesChecked']=len(checks)
audit['provenance']['referenceHashesVerified']=sum(x['matches'] for x in checks)
audit['provenance']['referenceMissingCount']=sum(not x['exists'] for x in checks)
audit['provenance']['referenceHashMismatchWhenPresent']=sum(x['exists'] and not x['matches'] for x in checks)
audit['provenance']['missingReferenceExplanation']='Original approved-mail style file no longer exists at recorded path; do not rewrite historical records or claim current replayability. All14 attempts had actual attached style at generation time per prior tool calls.'
audit['mechanicalAssembly']['externalBoundaryQa']=details
(Q/(P+'-audit.json')).write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'boundaryQA':len(details),'referencesChecked':len(checks),'verified':audit['provenance']['referenceHashesVerified'],'missing':audit['provenance']['referenceMissingCount'],'presentMismatch':audit['provenance']['referenceHashMismatchWhenPresent']}))

