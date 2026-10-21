"""Exact core QA for one newly selected patch; only assigned tile outputs."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Z))
from review_external_seams import Sources
tile,pid,label=sys.argv[1:4]
assert tile in ('r14_c11','r13_c11')
T=Z/tile
Q=T/'qa'/('quick-'+pid+'-'+label)
Q.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=json.loads((T/'selected-patches.json').read_text(encoding='utf-8-sig'))
im=Image.open(T/sel['patches'][pid]);assert im.size==(1254,1254)
x=(int(tile[5:7])-1)*4096+(int(pid[2])-1)*1024
y=(int(tile[1:3])-1)*4096+(int(pid[1])-1)*1024
S=Sources(); records=[]
for side,box in [('west',[x-256,y,x+256,y+1024]),('north',[x,y-256,x+1024,y+256]),('east',[x+768,y,x+1280,y+1024]),('south',[x,y+768,x+1024,y+1280])]:
 if min(box)<0 or max(box)>57344:continue
 out,pieces,missing=S.extract(box)
 if out is None:continue
 p=Q/(side+'.png');out.save(p)
 records.append(dict(side=side,file=str(p),sha256=sha(p),globalBox=box,sources=pieces,missing=missing,resamplingApplied=False,visualReview='pending'))
record=dict(tile=tile,patch=pid,createdAt=datetime.now(timezone.utc).isoformat(),selectionSha256=sha(T/'selected-patches.json'),patchSha256=sha(T/sel['patches'][pid]),evidence=records,formalAccepted=False)
(Q/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({'directory':str(Q),'files':[r['file'] for r in records]}))

