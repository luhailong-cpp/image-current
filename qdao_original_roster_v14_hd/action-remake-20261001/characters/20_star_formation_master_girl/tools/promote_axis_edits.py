"""Promote only individually approved axial corrections; preserve prior text evidence."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,copy,io
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=rd(R/'axis-review-20261004/approved.json')
out=R/'provenance/axis-edits-applied.json'
assert not out.exists(),'Already promoted'
sel=rd(R/'selection.json'); frames={(f['direction'],f['frame']):f for f in sel['frames'] if f['action']=='run'}
prepared=[]
for a in plan:
 assert a['visualApproved']
 f=frames[(a['direction'],a['frame'])];p=(R/a['export']).resolve(); assert p.is_relative_to(R/'axis-review-20261004')
 raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();assert h==a['sha256']
 im=Image.open(io.BytesIO(raw));assert im.size==(1024,1024) and im.mode=='RGBA'
 er=rd(Path(str(p)+'.generation.json'));assert er['sha256']==h
 native=R/er['derivedFrom']['file'];nr=Path(str(native)+'.generation.json');nrec=rd(nr)
 assert sha(native)==nrec['sha256'] and min(nrec['width'],nrec['height'])>=1024
 oldrec=R/f['generationRecord'];arc=R/'provenance/axis-prior-records'/str(oldrec.relative_to(R/'runtime')).replace('\\','--').replace('/','--')
 assert arc.read_bytes()==oldrec.read_bytes()
 prepared.append((a,f,p,raw,h,er,native,nr,nrec,arc))
stamp=datetime.now(timezone.utc).isoformat(); applied=[]
for a,f,p,raw,h,er,native,nr,nrec,arc in prepared:
 target=R/f['source'];old=rd(R/f['generationRecord']); origin={'file':native.relative_to(R).as_posix(),'sha256':nrec['sha256'],'nativeSize':[nrec['width'],nrec['height']],'generationRecord':nr.relative_to(R).as_posix(),'generationRecordSha256':sha(nr)}
 prior={'file':f['source'],'sha256':f['sourceSha256'],'generationRecord':arc.relative_to(R).as_posix(),'generationRecordSha256':sha(arc),'nativeOrigin':copy.deepcopy(f['nativeOrigin'])}
 history=[]
 for ref in nrec.get('references',[]):
  rp=Path(ref['path'])
  if rp.is_relative_to(R/'runtime'):
   apath=R/'provenance/axis-prior-records'/(str(rp.relative_to(R/'runtime')).replace('\\','--').replace('/','--')+'.generation.json')
   if apath.exists():
    assert sha(apath)==ref.get('generationRecordSha256')
    history.append({'submittedPath':ref['path'],'inputImageSha256':ref['sha256'],'sourceRecordAtRequest':apath.relative_to(R).as_posix(),'recordSha256':sha(apath),'imagePathMayNowContainNewRevision':True})
 rec={**old,**er,'file':f['source'],'nativeOrigin':origin,'nativeSize':origin['nativeSize'],'derivedFrom':origin,'sourceExport':{'file':p.relative_to(R).as_posix(),'sha256':h,'generationRecord':p.relative_to(R).as_posix()+'.generation.json','generationRecordSha256':sha(Path(str(p)+'.generation.json'))},'priorFrame':prior,'axisRevision':'2026-10-04_knee_ankle_boot','axisCorrection':a['reason'],'visualReview':'axis_static_reviewed','dynamicReview':'pending_axis_browser_review','exportedAt':stamp}
 rec['inputReferenceHistory']=history
 target.write_bytes(raw);wr(R/f['generationRecord'],rec)
 f.update(sourceSha256=h,nativeOrigin=origin,nativeSize=origin['nativeSize'],priorFrame=prior,visualReview=rec['visualReview'],dynamicReview=rec['dynamicReview'],axisRevision=rec['axisRevision'],axisCorrection=a['reason'])
 applied.append({'direction':a['direction'],'frame':a['frame'],'runtime':f['source'],'sha256':h,'reason':a['reason'],'nativeOrigin':origin,'prior':prior})
sel.update(updatedAt=stamp,axisRevision='2026-10-04_knee_ankle_boot');wr(R/'selection.json',sel)
wr(out,{'time':stamp,'count':len(applied),'retainedRun':128-len(applied),'combatRetained':68,'applied':applied,'priorRecords':'provenance/axis-prior-records','clientIntegrated':False})
print(json.dumps({'promoted':len(applied),'retainedRun':128-len(applied)},ensure_ascii=False))
