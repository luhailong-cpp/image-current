from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
Q=Path(__file__).resolve().parent
Z=Q.parents[2]
sys.path.insert(0,str(Z))
from review_external_seams import Sources
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=[31117,35840,32371,37094]
im,pieces,missing=Sources().extract(box)
assert not missing,missing
assert im.size==(1254,1254)
p=Q/'joint-input-v1-1254.png';assert not p.exists();im.save(p)
doc=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),frameGlobalBox=box,image=str(p),sha256=sha(p),
 dimensions=[1254,1254],seamX=627,sources=pieces,
 operation='Exact current selected core crops only; no resizing, movement, drawing, blending or blur.',
 bottom230Pixels='Immutable read-only southern neighbor context; excluded from any repair adoption.',
 targetUpperBracketFrameBox=[570,200,870,530],
 canonicalModified=False,formalAccepted=False)
(Q/'joint-input-v1.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:doc[k] for k in ['image','sha256','frameGlobalBox']}))
