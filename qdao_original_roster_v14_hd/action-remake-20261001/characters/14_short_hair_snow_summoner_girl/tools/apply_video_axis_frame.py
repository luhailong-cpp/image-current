"""Publish one visually selected local AI repair on the already registered canvas."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib
from export_frame import run
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('direction');a.add_argument('frame',type=int);a.add_argument('source');a.add_argument('--observation',required=True);x=a.parse_args()
assert x.direction in ['N','NE','E','SE','S','SW','W','NW'] and 1<=x.frame<=16
src=(R/x.source).resolve();assert R in src.parents
dst=R/f'run/{x.direction}/{x.frame:02}.png';meta=Path(str(dst)+'.generation.json');old=read(meta)
hist=R/f'provenance/video-axis-prior-{x.direction}-{x.frame:02}-{old["sha256"][:12]}.json'
if not hist.exists():save(hist,old)
run(src,dst)
m=read(meta);h=sha(dst)
m['registrationTransform']={'status':'applied','method':'direct_registered_canvas_redraw','globalScale':1.0,'inheritedCharacterScale':.8,'sourceRoot':[512,942],'targetRoot':[512,942],'outputSha256':h,'note':'AI edited registered frame; whole canvas downsample only; no extra scale, translation, limb manipulation or sole alignment.'}
m['videoAxisRepair']={'reviewedAt':datetime.now(timezone.utc).isoformat(),'previousSha256':old['sha256'],'priorGenerationRecord':hist.relative_to(R).as_posix(),'observation':x.observation,'status':'static_selected_pending_continuous_preview'}
save(meta,m)
cp=R/f'audit/contact-{x.direction}-review.json';c=read(cp)
ch=R/f'audit/video-axis-prior-contact-{x.direction}.json'
if not ch.exists():save(ch,c)
for f in c['frames']:
 if f['file']==dst.relative_to(R).as_posix():f['sha256']=h
c['status']='static_pending_root_preview';c.pop('rootPreview',None)
c.setdefault('videoAxisRepairs',{})[f'{x.frame:02}']={'sha256':h,'observation':x.observation}
save(cp,c)
print(json.dumps({'file':str(dst),'sha256':h,'status':'static_selected_pending_continuous_preview'}))
