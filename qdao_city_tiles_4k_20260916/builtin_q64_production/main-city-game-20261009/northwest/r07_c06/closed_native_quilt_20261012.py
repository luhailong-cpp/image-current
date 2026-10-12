"""QA-only closed binary native-pixel selection; never blends or changes sources."""
from pathlib import Path
from PIL import Image
import numpy as np
import importlib.util
import json
import argparse

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v2',HERE.parent/'production_v2.py')
v2=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
BASE=HERE/'layout-only/west-seam-r3-fix01.actual-1254.png'
DONOR=HERE/'repair-native/west-seam-r3-fix01.png'
parser=argparse.ArgumentParser()
parser.add_argument('--version',default='quilt01')
parser.add_argument('--strict-grout',action='store_true')
args=parser.parse_args()
OUT=HERE/('qa/west-seam-r3-fix01-'+args.version)
OUT.mkdir(exist_ok=False)
a=np.array(Image.open(BASE).convert('RGB'))
b=np.array(Image.open(DONOR).convert('RGB'))
assert a.shape==b.shape==(1254,1254,3)
af,bf=a.astype(np.float32),b.astype(np.float32)
def grout(im):
    return (im[:,:,0]>im[:,:,1]*1.18)&(im[:,:,1]<175)&(im[:,:,2]<150)
cost=np.abs(af-bf).mean(axis=2)+np.logical_xor(grout(af),grout(bf))*650
if args.strict_grout:
    cost[np.logical_xor(grout(af),grout(bf))]=np.inf
def path(c):
    height,width=c.shape
    previous=c[0].astype(np.float64).copy()
    backs=np.zeros((height,width),dtype=np.int8)
    for y in range(1,height):
        left=np.r_[np.inf,previous[:-1]]
        center=previous
        right=np.r_[previous[1:],np.inf]
        stack=np.stack((left,center,right))
        choices=np.argmin(stack,axis=0)
        backs[y]=choices-1
        previous=c[y]+stack[choices,np.arange(width)]
    if not np.isfinite(previous.min()):
        raise RuntimeError('No continuous source-selection path avoids all mismatched grout in this perimeter band')
    result=np.zeros(height,dtype=np.int32)
    result[-1]=np.argmin(previous)
    for y in range(height-1,0,-1):
        result[y-1]=result[y]+backs[y,result[y]]
    return result
left=100+path(cost[:,100:320])
right=925+path(cost[:,925:1180])
top=30+path(cost[30:220,:].T)
bottom=1040+path(cost[1040:1220,:].T)
yy,xx=np.mgrid[:1254,:1254]
mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
proposal=np.where(mask[:,:,None],b,a).astype(np.uint8)
assert np.array_equal(proposal[mask],b[mask]) and np.array_equal(proposal[~mask],a[~mask])
image=Image.fromarray(proposal,'RGB')
v2.save_png(OUT/'proposal-native-1254.png',image)
v2.save_png(OUT/'source-mask-native-1254.png',Image.fromarray(mask.astype(np.uint8)*255,'L'))
crops=[]
for name,box in [('left-perimeter',(70,0,350,1254)),('right-perimeter',(900,0,1200,1254)),
                 ('top-perimeter',(0,0,1254,250)),('bottom-perimeter',(0,1010,1254,1254)),
                 ('actual-west-r3',(499,74,755,1098))]:
    out=OUT/(name+'.png')
    v2.save_png(out,image.crop(box))
    crops.append(dict(name=name,file=str(out),sha256=v2.sha(out),sourceBox=list(box),actuallyViewed=False,verdict='pending'))
record=dict(status='proposal-pending-all-closed-perimeter-and-actual-seam-review',formalAccepted=False,
            base=dict(file=str(BASE),sha256=v2.sha(BASE),derivation=str(BASE.with_suffix('.png.derivation.json'))),
            supplementalNative=dict(file=str(DONOR),sha256=v2.sha(DONOR),generationRecord=str(DONOR.with_suffix('.png.generation.json'))),
            worldBox=v2.read(BASE.with_suffix('.png.derivation.json'))['worldBox'],
            proposal=dict(file=str(OUT/'proposal-native-1254.png'),sha256=v2.sha(OUT/'proposal-native-1254.png')),
            sourceMask=dict(file=str(OUT/'source-mask-native-1254.png'),sha256=v2.sha(OUT/'source-mask-native-1254.png'),
                            zeroMeaning='same-coordinate base actual candidate pixels',oneMeaning='same-coordinate supplemental native pixels'),
            selectedSupplementalPixels=int(mask.sum()),pixelProofEveryPixelEqualsOneUnmodifiedSource=True,
            sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,
            paths=dict(left=left.tolist(),right=right.tolist(),top=top.tolist(),bottom=bottom.tolist()),crops=crops,
            strictGroutPath=args.strict_grout,
            sourceSelection='closed four-sided minimum-error binary mask; no output adoption')
v2.write_json(OUT/'proposal-proof.json',record)
print(json.dumps(dict(directory=str(OUT),selectedNativePixels=int(mask.sum()),proposal=record['proposal'],formalAccepted=False)))
