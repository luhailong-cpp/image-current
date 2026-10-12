from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
d=Path(__file__).parent;root=d.parents[1];candidate=root/'delivery/jewelry-approach-8192-candidate-v1.png'
im=Image.open(candidate).convert('RGB');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[]
for orientation in ['horizontal','vertical']:
 for offset in range(0,8192,1024):
  name=f'{orientation}-'+('x' if orientation=='horizontal' else 'y')+str(offset)+'.png';p=d/name
  img=Image.open(p).convert('RGB')
  box=[offset,3968,offset+1024,4224] if orientation=='horizontal' else [3968,offset,4224,offset+1024]
  equal=(img.size==im.crop(box).size and img.tobytes()==im.crop(box).tobytes())
  items.append({'file':name,'dimensions':list(img.size),'sha256':sha(p),'candidateCropBox':box,'matchesCandidateNativeCrop':equal,'visualFinding':'No apparent cross-boundary object discontinuity, hard color step or ghosting.'})
p=d/'center-four-way-native.png';img=Image.open(p).convert('RGB');box=[3584,3584,4608,4608]
items.append({'file':p.name,'dimensions':list(img.size),'sha256':sha(p),'candidateCropBox':box,'matchesCandidateNativeCrop':img.size==im.crop(box).size and img.tobytes()==im.crop(box).tobytes(),'visualFinding':'Four-way center: continuous stone-joint geometry, no cross-shaped hard edge or duplicated crack.'})
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'south_native independent tile-boundary pass','scope':'All 16 inter-tile seam strips plus four-way center; visual inspection at native scale','candidate':str(candidate),'candidateDimensions':list(im.size),'candidateSha256':sha(candidate),'boundaryVersions':{'r03_c10':'v4','r03_c11':'v2','r04_c10':'v2','r04_c11':'v1'},'imagesReviewed':17,'blockingFindings':[],'observations':['North/south gold curl repair is crisp and continuous.','Stone joints, timber, lantern fragments, net support ropes and mesh cross checked tile boundaries without apparent geometric discontinuity.','No hard seam-aligned color jump, doubled object outline or blend ghost was observed.','Some foliage and shadowed timber near vertical-y1024 have softer paint than nearby foreground surfaces; this does not form a hard line at the tile boundary.'],'limitations':['Only the 2x2 internal tile boundaries reviewed; external region edges remain unchecked.','Subsequent r04_c11 internal-only net repair is outside these boundary strips and requires separate root verification.'],'candidateMutated':False,'formalAccepted':False,'conclusion':'No actionable inter-tile seam defect found in the 17 inspected native crops; external region acceptance remains pending.','files':items}
(d/'findings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'reviewed':len(items),'nativeCropMatches':sum(i['matchesCandidateNativeCrop'] for i in items),'candidateDimensions':list(im.size),'blockingFindings':[],'formalAccepted':False}))

