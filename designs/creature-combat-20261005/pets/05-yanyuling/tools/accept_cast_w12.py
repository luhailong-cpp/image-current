"""Accept the independently AI-edited W12 using the existing direction export."""
from pathlib import Path
from PIL import Image
from io import BytesIO
import hashlib,json,copy
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rp=BASE/'provenance/cast/W/12.generation.json'
candidate=BASE/'provenance/cast/W/12-repair-candidate.png'
archive=rp.with_name('12.superseded-before-continuity-repair.generation.json')
assert not archive.exists(),'Already accepted; do not apply twice'
old=read(rp);r=read(candidate.with_suffix('.generation.json'))
outpath=BASE/'runtime/cast/W/12.png'
assert sha(outpath)==old['sha256']
assert sha(candidate)==r['sha256']
registration=read(BASE/'export-registration.json')
index=next(i for i,x in enumerate(registration['frames']) if x['file']=='runtime/cast/W/12.png')
previous=copy.deepcopy(registration['frames'][index])
assert previous['afterSha256']==old['sha256']
native=Image.open(candidate).convert('RGBA')
work=native.resize((1024,1024),Image.Resampling.LANCZOS)
buf=BytesIO();work.save(buf,format='PNG');worksha=hashlib.sha256(buf.getvalue()).hexdigest()
out=Image.new('RGBA',(1024,1024));out.alpha_composite(work.resize((840,840),Image.Resampling.LANCZOS),(114,151))
old['superseded']={'reason':'AI-edited intermediate wing-fold pose improves frame11 to frame13 continuity','retainedRaster':False,'replacementRecord':'provenance/cast/W/12.generation.json'}
write(archive,old)
out.save(outpath)
now=datetime.now(timezone.utc).isoformat()
r.update(file='runtime/cast/W/12.png',sha256=sha(outpath),width=1024,height=1024,pivot=[0.5,0.08],candidateStatus='accepted_after_fixed_direction_export',acceptedAt=now)
r['operation']=copy.deepcopy(old['operation']);r['operation']['sourceBeforeExportSha256']=worksha
r['anchor']=old['anchor']
r['exportHistory']=[{'sha256':worksha,'width':1024,'height':1024,'operationBeforeRegistration':{'type':'whole_canvas_uniform_resize','sourceSize':[1254,1254],'outputSize':[1024,1024],'resampler':'LANCZOS'},'replacedBy':r['sha256'],'retained':False}]
r['supersedes']={'sha256':old['sha256'],'record':archive.relative_to(BASE).as_posix(),'retainedRaster':False}
r['derivedFrom']=copy.deepcopy(r['nativeOutput'])
r['visualReview']['status']='native_individually_reviewed_final_export_pending_playback'
r['localCandidate']={'file':candidate.relative_to(BASE).as_posix(),'sha256':sha(candidate),'retained':True,'cleanupAfterFinalVerification':True}
write(rp,r)
new=copy.deepcopy(previous);new.update(beforeSha256=worksha,afterSha256=r['sha256'],visibleBBoxBefore=work.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox(),visibleBBoxAfter=out.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox())
registration.setdefault('revisionHistory',[]).append({'performedAt':now,'reason':'independent AI continuity repair of cast W12; same fixed export transform','supersededFrame':previous,'replacementFrame':copy.deepcopy(new)})
registration['frames'][index]=new
write(BASE/'export-registration.json',registration)
print(json.dumps({'accepted':r['file'],'sha256':r['sha256'],'beforeRegistrationSha256':worksha,'nativeSha256':r['nativeOutput']['sha256']},indent=2))
