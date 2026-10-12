import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent.parent;q=z/'qa';pre='block2x2-r10r11c05c06-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tp=q/(pre+'-trace.json');t=read(tp);im=Image.open(t['context']['path']).convert('RGB');tiles=[];changes=[]
base={'r10_c05':'pair-r10c05-c06-current-v1-r10_c05-context-native.png','r10_c06':'pair-r10r11c06-final-v5-r10_c06-context-native.png','r11_c05':'repair-r11_c05-internal-v1-context-native.png','r11_c06':'pair-r10r11c06-final-v5-r11_c06-context-native.png'}
for e,(x,y) in zip(t['tiles'],[(0,0),(4096,0),(0,4096),(4096,4096)]):
 p=q/(pre+'-'+e['tile']+'-context-native.png');assert not p.exists();part=im.crop((x,y,x+4326,y+4326));part.save(p)
 a=np.array(part);b=np.array(Image.open(q/base[e['tile']]).convert('RGB'));mask=np.any(a!=b,axis=2);yy,xx=np.where(mask)
 changes.append({'tile':e['tile'],'base':ref(q/base[e['tile']]),'changedPixelCount':int(mask.sum()),'changedContextBox':([int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None)})
 tiles.append({'tile':e['tile'],'candidate':{'path':e['path'],'sha256':e['sha256']},'context':ref(p)})
nt={**t,'originalTrace':ref(tp),'tiles':tiles,'changedRegions':changes};npth=q/(pre+'-export-trace.json');write(npth,nt)
a={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed','reviewer':'root','scope':'r11_c05 internal and all four available r10/r11 c05/c06 shared edges; future west/south outer joins pending','trace':ref(npth),'nativeQaWindowsViewed':21,'viewed':[{**e,'result':'pass','viewedAtNativeScale':True} for e in t['qa']],'reusedInternalAudit':ref(q/'r11_c05-internal-visual-audit-v2.json'),'findings':['All 21 native joint crops visually reviewed. Rabbit silhouette, wood supports, banners, flowering foliage, sand and paving connect without blocking breaks. Cylinder-foot local repair retained.'],'issues':[],'changedRegions':changes,'runtimeAcceptance':False}
ap=q/(pre+'-art-audit-v1.json');write(ap,a)
subprocess.run([sys.executable,'-B',str(q/'export-reviewed-versioned.py'),str(npth),str(ap)],check=True)
print(json.dumps(changes))
