from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');id='west-seam-r3-fix04'
out=r/('qa/'+id+'-shared-proposal01');out.mkdir(exist_ok=False)
src=r/'layout-only/west-seam-r3-fix04.actual-1254.png';donor=r/('repair-native/'+id+'.png')
a=Image.open(src).convert('RGB');d=Image.open(donor).convert('RGB')
box=(540,230,780,390);p=a.copy();p.paste(d.crop(box),box[:2])
p.save(out/'proposal-native-1254.png');p.crop((510,200,810,420)).save(out/'joint-and-four-perimeters.png')
p.crop((520,345,580,410)).save(out/'west-perimeter-two-diagonals.png')
p.crop((600,270,650,345)).save(out/'actual-tile-boundary-detail.png')
aa=np.array(a);dd=np.array(d);pp=np.array(p);mask=np.zeros((1254,1254),dtype=bool);mask[230:390,540:780]=True
assert np.array_equal(pp[mask],dd[mask]) and np.array_equal(pp[~mask],aa[~mask])
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
rec=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='shared-proposal-pending-root-coordination-and-visual-review',sourceROI=list(box),sourceFrameWorldBox=[19853,26550,21107,27804],worldROI=[19853+box[0],26550+box[1],19853+box[2],26550+box[3]],touchesWestNeighbor=True,westNeighborNativeSourceROI=[540,230,627,390],ownTileNativeSourceROI=[627,230,780,390],base=dict(file=str(src),sha256=sha(src)),native=dict(file=str(donor),sha256=sha(donor)),proposal=dict(file=str(out/'proposal-native-1254.png'),sha256=sha(out/'proposal-native-1254.png')),pixelProofEveryPixelEqualsOneOriginalSource=True,sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,formalAccepted=False,adopted=False)
(out/'proposal-proof.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
