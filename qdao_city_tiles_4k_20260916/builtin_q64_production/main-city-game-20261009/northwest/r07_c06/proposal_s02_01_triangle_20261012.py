from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
out=r/'qa/s02_01_anchorfix01-proposal01';out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=Image.open(r/'native/s02_01_resume01.png').convert('RGB')
d=Image.open(r/'native/s02_01_anchorfix01.png').convert('RGB')
box=(119,212,292,249)
p=a.copy();p.paste(d.crop(box),box[:2])
arr=np.array(p);aa=np.array(a);dd=np.array(d)
mask=np.zeros((1254,1254),dtype=bool);mask[212:249,119:292]=True
assert np.array_equal(arr[mask],dd[mask]) and np.array_equal(arr[~mask],aa[~mask])
p.save(out/'proposal-native-1254.png')
p.crop((70,180,350,340)).save(out/'detail-and-all-four-perimeters.png')
base=r/'candidate/r07_c06-candidate-hard-2e59491c741a.png'
c=Image.open(base).convert('RGB')
cb=(box[0]-115,1024+box[1]-115,box[2]-115,1024+box[3]-115)
c.paste(d.crop(box),cb[:2]);c.save(out/'proposal-candidate-4096.png')
west=Image.open(r.parent/'r07_c05/candidate/r07_c05-candidate-hard-1672ae5e4698.png').convert('RGB')
seam=Image.new('RGB',(256,1024));seam.paste(west.crop((3968,1024,4096,2048)),(0,0));seam.paste(c.crop((0,1024,128,2048)),(128,0));seam.save(out/'actual-west-row2.png')
c.crop((0,896,1024,1152)).save(out/'h-r1-c1.png')
p.save(out/'full-native-with-one-adoptable-region.png')
rec=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='proposal-only-pending-visual-review',formalAccepted=False,baseCandidate=dict(file=str(base),sha256=sha(base)),sourceOriginal=dict(file=str(r/'native/s02_01_resume01.png'),sha256=sha(r/'native/s02_01_resume01.png')),additionalNative=dict(file=str(r/'native/s02_01_anchorfix01.png'),sha256=sha(r/'native/s02_01_anchorfix01.png'),generationRecord=str(r/'native/s02_01_anchorfix01.png.generation.json')),sourceROI=list(box),candidateROI=list(cb),roiWorldBox=[20480+cb[0],24576+cb[1],20480+cb[2],24576+cb[3]],pixelsSelected=int(mask.sum()),everyPixelEqualsOneOriginalNative=True,sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,candidate=dict(file=str(out/'proposal-candidate-4096.png'),sha256=sha(out/'proposal-candidate-4096.png')),qa=[dict(file=str(x),sha256=sha(x),actuallyViewed=False) for x in out.glob('*.png')])
(out/'proposal-proof.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps(rec['candidate']))
