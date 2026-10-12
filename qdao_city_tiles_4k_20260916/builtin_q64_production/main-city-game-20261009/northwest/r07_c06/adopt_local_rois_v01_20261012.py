from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    assert not p.exists(),p
    p.write_text(json.dumps(x,indent=2),encoding='utf-8')
overlays=[
dict(id='s02_01_anchorfix01',file=str(r/'native/s02_01_anchorfix01.png'),nativeWorldBox=[20365,25485,21619,26739],sourceROI=[119,212,292,249],localReview=str(r/'qa/s02_01_anchorfix01-proposal01/local-review.json')),
dict(id='west-seam-r3-fix03',file=str(r/'repair-native/west-seam-r3-fix03.png'),nativeWorldBox=[19853,26550,21107,27804],sourceROI=[627,555,795,716],localReview=str(r/'qa/west-seam-r3-fix03-proposal01/local-review.json'))]
write(Path(overlays[0]['localReview']),dict(actuallyViewed=['detail-and-all-four-perimeters.png','actual-west-row2.png','h-r1-c1.png','proposal-native-1254.png'],verdict='local-grout-geometry-and-closed-perimeter-pass',materialReview='Original pale horizontal texture band remains for full QA; no formal acceptance.',formalAccepted=False))
write(Path(overlays[1]['localReview']),dict(actuallyViewed=['joint-and-four-perimeters.png','exact-west-endpoint.png','proposal-native-1254.png','actual-west-r3.png'],verdict='single-pinned-joint-and-closed-perimeter-pass',reason='The modified left-to-right grout is continuous with a small bevel corner at the original tile boundary. Other west-row3 cuts remain and are not approved.',preservesAllWestNeighborPixels=True,formalAccepted=False))
base=r/'candidate/r07_c06-candidate-hard-2e59491c741a.png'
c=Image.open(base).convert('RGB');before=np.array(c)
for o in overlays:
    o['sha256']=sha(Path(o['file']))
    x0,y0,x1,y1=o['sourceROI'];wx,wy,_,_=o['nativeWorldBox']
    cb=[wx+x0-20480,wy+y0-24576,wx+x1-20480,wy+y1-24576]
    assert cb[0]>=0 and cb[1]>=0 and cb[2]<=4096 and cb[3]<=4096
    o['candidateROI']=cb;o['roiWorldBox']=[wx+x0,wy+y0,wx+x1,wy+y1]
    d=Image.open(o['file']).convert('RGB')
    c.paste(d.crop((x0,y0,x1,y1)),cb[:2])
out=r/'candidate/r07_c06-candidate-native-roi-v01.png';assert not out.exists();c.save(out)
rec=dict(schemaVersion=1,tile=r.name,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='candidate-with-two-locally-reviewed-native-rois-pending-full-visual-repair',baseCandidate=dict(file=str(base),sha256=sha(base),assembly=str(base.with_suffix('.assembly.json'))),overlays=overlays,candidate=dict(file=str(out),sha256=sha(out),pixels=[4096,4096]),original16SelectionsUnchanged=True,completePixelProof='Baseline exact-source core proof plus ordered same-world native source ROI replacement; no transformations.',sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,formalAccepted=False)
write(r/'candidate/native-overlays-20261012-v01.json',rec)
# Exact actual neighbor/current candidate frame for subsequent single joints.
f=r/'layout-only/west-seam-r3-fix04.actual-1254.png'
westpath=r.parent/'r07_c05/candidate/r07_c05-candidate-hard-1672ae5e4698.png'
w=Image.open(westpath).convert('RGB')
frame=Image.new('RGB',(1254,1254));frame.paste(w.crop((3469,1974,4096,3228)),(0,0));frame.paste(c.crop((0,1974,627,3228)),(627,0));assert not f.exists();frame.save(f)
write(f.with_suffix('.png.derivation.json'),dict(worldBox=[19853,26550,21107,27804],guideOnly=True,notFinalArt=True,sources=[dict(file=str(westpath),sha256=sha(westpath),crop=[3469,1974,4096,3228],paste=[0,0]),dict(file=str(out),sha256=sha(out),crop=[0,1974,627,3228],paste=[627,0])],sourceResampled=False,warped=False,blended=False,recolored=False))
print(json.dumps(rec['candidate']))
