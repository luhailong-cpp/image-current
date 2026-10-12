from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=Path('C:/Users/luyua/.codex/generated_images/01a13554-e65d-71e2-a119-8c3677ffd303/exec-e9137e04-8193-4767-a99e-ac409a1a9ed8.png')
p=Q/'bracket-v1-raw.png';assert not p.exists();shutil.copyfile(raw,p)
im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
g=dict(savedAtUtc=datetime.now(timezone.utc).isoformat(),tool='image_gen__imagegen',route='builtin',actualModel=None,
 actualQuality=None,file=str(p),sha256=sha(p),nativeDimensions=[1254,1254],sourcePath=str(raw),
 prompt=str(Q/'bracket-v1.prompt.txt'),request=str(Q/'bracket-v1.request.json'),receipt=str(Q/'bracket-v1.receipt.json'),
 selected=False,operation='Byte-exact copy of actual builtin output')
(Q/'bracket-v1-raw.png.generation.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
base=Image.open(Q/'joint-input-v1-1254.png').convert('RGB')
box=[595,211,863,464]
composite=base.copy();composite.paste(im.crop(box),tuple(box[:2]))
c=Q/'bracket-v1-upper-only-QA.png';composite.save(c)
composite.crop([550,170,910,600]).save(Q/'bracket-v1-upper-only-boundary-100pct.png')
base.crop([550,170,910,600]).save(Q/'bracket-original-boundary-100pct.png')
im.crop([550,170,910,600]).save(Q/'bracket-v1-raw-boundary-100pct.png')
(Q/'bracket-v1-preliminary-QA.json').write_text(json.dumps(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),
 frameBox=box,globalBox=[31117+box[0],35840+box[1],31117+box[2],35840+box[3]],
 original=str(Q/'joint-input-v1-1254.png'),originalSha256=sha(Q/'joint-input-v1-1254.png'),
 raw=str(p),rawSha256=sha(p),qaImage=str(c),qaSha256=sha(c),
 operation='Exact raw at same coordinates inside bounded region; original outside unchanged',
 protectsLanternCupAndStem=True,canonicalModified=False,visualReview='pending',adoptRecommended=False),indent=2)+'\n',encoding='utf-8')
print(json.dumps(g))
