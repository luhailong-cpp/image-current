from pathlib import Path
from PIL import Image
import json,hashlib,datetime
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
d=T/'repair-batches/east-gold-material-01';q=d/'trials/v01-binary-seam'
save(d/'producer-review.json',dict(status='rejected_unadopted',actuallyViewed=[str(q/'before.png'),str(q/'perimeter.png')],reason='The left-only binary adoption does not remove the gold dark vertical line in actual east neighbor x0..few pixels around y2550..2635. It also leaves an exposure transition. Right side read-only in this worker. Best current v03 remains unchanged.',requiresCoordinatorBoundaryReview=True,adoptedPixels=0))
d=T/'repair-batches/east-lower-contours-02';old=Image.open(d/'edit-target.png').convert('RGB');new=Image.open(d/'native.png').convert('RGB');trial=old.copy();trial.paste(new.crop((350,565,627,1010)),(350,565));trial.crop((270,485,810,1090)).save(d/'trial-left-only-detail.png')
save(d/'producer-review.json',dict(status='deferred_unpassed_after_two_attempts',actuallyViewedGeneratedNative=True,reason='Second attempt preserved the original middle rim and lower end-cap jumps at the ownership border instead of correcting them. Full returned image still visibly mismatched at x627. No generated pixels adopted.',adoptedPixels=0,previousAttempt=str(T/'repair-batches/east-row4-contours-01')))
d=T/'repair-batches/internal-glaze-01';q=d/'trials/v01-binary-seam';im=Image.open(q/'candidate.png');boxes={'left-context':[750,830,1050,1250],'right-context':[1890,830,2190,1250],'full-context':[770,787,2120,1277]}
for name,box in boxes.items():im.crop(box).save(q/(name+'.png'))
save(q/'extra-crops.json',{name:dict(file=str(q/(name+'.png')),tileCropLTRB=box,sha256=sha(q/(name+'.png')),nativePixelScale=1,sourceResampled=False) for name,box in boxes.items()})
print(json.dumps(dict(glazeExtraCrops=list(boxes),eastTrialsRejected=True)))
