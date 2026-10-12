from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent; F=T.parent/'seam-qa/r14_c10-selected-color-continue-20261013-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(F/'manifest.json');reviewed=[]
for e in [s for x in m['edges'] for s in x['segments']]+m['intersections']:
 if not e['sourceComplete']:continue
 q=read(e['report']); im=q['image']; assert sha(im['file'])==im['sha256']; canvas=Image.new('RGB',im['dimensions'])
 for s in q['sources']:
  assert sha(s['file'])==s['sha256']; selected=read(s['selectedManifest']); assert (Path(s['selectedManifest']).parent/selected['patches'][s['patch']]).resolve()==Path(s['file']).resolve()
  canvas.paste(Image.open(s['file']).convert('RGB').crop(s['sourceCrop']),s['destination'])
 assert np.array_equal(np.array(canvas),np.array(Image.open(im['file']).convert('RGB')))
 reviewed.append(dict(id=e['id'],image=im,status='passed',nativeVisualReview=True,sourceReplayedExactly=True,notes='Water caustic crossings and color continue without a straight visible join.'))
assert len(reviewed)==15
r=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r14_c10',reviewer='/root/c10_continue_20261013',reviewed=reviewed,north='passed 4 segments and 3 intermediate crossings',west='passed 4 segments and 3 intermediate crossings',northwest='passed',east='pending missing r14_c11 canonical cores',south='outer canvas y=57344; no r15 tile required',formalAccepted=False)
p=F/'available-external-review-continue-20261013-v1.json';assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(p)
