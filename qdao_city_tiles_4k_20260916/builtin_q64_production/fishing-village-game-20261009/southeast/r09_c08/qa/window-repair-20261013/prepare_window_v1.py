from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
Q=Path(__file__).resolve().parent
Z=Q.parents[2]
sys.path.insert(0,str(Z))
from review_external_seams import Sources
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=[31744,36065,32998,37319]
s=Sources(); im,pieces,missing=s.extract(box)
assert not missing,missing
assert im.size==(1254,1254)
p=Q/'joint-input-v1-1254.png';assert not p.exists();im.save(p)
doc=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),frameGlobalBox=box,
 dimensions=[1254,1254],image=str(p),sha256=sha(p),sources=pieces,
 operation='Exact same-coordinate selected core crops only; no scaling, blending, blur or generated geometry.',
 correction='Only upper r09_c08 p44 window lattice; preserve south neighbor and all exterior details.',
 intendedEditableUpperWindowFrameBox=[607,528,900,799],
 nativeP44Origin=[31629,35725],seamYInFrame=799,
 originalNorthSource=str(Z/'r09_c08/native/p44-v2.png'),
 originalNorthSha256=sha(Z/'r09_c08/native/p44-v2.png'),
 originalSouthSource=str(Z/'r10_c08/processed/colorpass/p14-colorpass.png'),
 originalSouthSha256=sha(Z/'r10_c08/processed/colorpass/p14-colorpass.png'),
 formalAccepted=False)
(Q/'joint-input-v1.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:doc[k] for k in ['image','sha256','frameGlobalBox','originalNorthSha256','originalSouthSha256']}))
