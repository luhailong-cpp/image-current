import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
z=Path(__file__).resolve().parent.parent;q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=q/'joint-r09c04-c05-northjoined-v1-context-native.png'
bp=q/'pair-r09c05-c06-final-v2-r09_c05-context-native.png'
assert sha(ap)=='6a5edf263c23043e2c62bc8c7764424102ab187deb5a38e4fa6b33fbe726ad31'
assert sha(bp)=='0c691dc43ad510cb51982d6a0b56d79f3209179164be8f3f8a84cd3de1bb7e71'
old=np.array(Image.open(ap).convert('RGB'));new=np.array(Image.open(bp).convert('RGB'))
assert old.shape==(4326,8422,3) and new.shape==(4326,4326,3)
assert np.array_equal(old[:,4096:7596],new[:,:3500])
after=old.copy();after[:,4096:]=new
p=q/'joint-r09c04-c05-eastjoined-v2-context-native.png';assert not p.exists();Image.fromarray(after).save(p)
change=np.any(after!=old,axis=2);ys,xs=np.where(change)
trace=q/'joint-r09c04-c05-eastjoined-v2-trace.json'
write(trace,{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'integer replacement of accepted c05 context after eastern join; no resampling or blending','base':ref(ap),'newRight':ref(bp),'output':ref(p),'sourcePixelIdentity':True,'changedPixelCount':int(change.sum()),'changedContextBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'provenance':[ref(q/'pair-r09c05-c06-final-v2-trace.json'),ref(q/'joint-r09c04-c05-northjoined-v1-trace.json')]})
manifest=q/'block2x2-r09r10c04c05-v1.manifest.json'
write(manifest,{'outputPrefix':'block2x2-r09r10c04c05-v1','topJoint':ref(p),'southwest':ref(q/'repair-r10_c04-sixstep-v4-context-native.png'),'southeast':ref(q/'joint-r09c05-r10c05-v1-r10_c05-context-native.png'),'provenance':[ref(trace),ref(q/'repair-r10_c04-sixstep-v4-trace.json'),ref(q/'r10_c04-sixstep-rebuild-handoff.json'),ref(q/'joint-r09c05-r10c05-v1-trace.json')]})
print(json.dumps({'manifest':ref(manifest),'topJoint':ref(p),'changed':int(change.sum())}))
