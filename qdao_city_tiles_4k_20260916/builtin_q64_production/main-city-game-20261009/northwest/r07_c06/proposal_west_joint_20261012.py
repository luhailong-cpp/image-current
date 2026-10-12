from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');id='west-seam-r3-fix03'
out=r/('qa/'+id+'-proposal01');out.mkdir(exist_ok=False)
src=r/'layout-only/west-seam-r3-fix01.actual-1254.png';donor=r/('repair-native/'+id+'.png')
a=Image.open(src).convert('RGB');d=Image.open(donor).convert('RGB')
box=(627,555,795,716);p=a.copy();p.paste(d.crop(box),box[:2])
p.save(out/'proposal-native-1254.png')
p.crop((560,540,835,755)).save(out/'joint-and-four-perimeters.png')
p.crop((610,608,650,648)).save(out/'exact-west-endpoint.png')
p.crop((499,74,755,1098)).save(out/'actual-west-r3.png')
aa=np.array(a);dd=np.array(d);pp=np.array(p);mask=np.zeros((1254,1254),dtype=bool);mask[555:716,627:795]=True
assert np.array_equal(pp[mask],dd[mask]) and np.array_equal(pp[~mask],aa[~mask])
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
rec=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='proposal-pending-visual-review',sourceROI=list(box),sourceFrameWorldBox=[19853,26550,21107,27804],worldROI=[19853+box[0],26550+box[1],19853+box[2],26550+box[3]],preservesAllWestNeighborPixels=True,base=dict(file=str(src),sha256=sha(src)),native=dict(file=str(donor),sha256=sha(donor)),proposal=dict(file=str(out/'proposal-native-1254.png'),sha256=sha(out/'proposal-native-1254.png')),pixelProofEveryPixelEqualsOneOriginalSource=True,sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,formalAccepted=False)
(out/'proposal-proof.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
