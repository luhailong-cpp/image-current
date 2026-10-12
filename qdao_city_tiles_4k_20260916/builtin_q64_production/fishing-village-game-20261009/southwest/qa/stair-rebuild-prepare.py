import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image, ImageDraw
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent
D=Z/'stair-rebuild'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch,version=sys.argv[1:3]
stem='r10_c04_'+patch+'_'+version
plan=read(Z/'coordinate-plan.json')
t=next(t for t in plan['tiles'] if t['tile']=='r10_c04')
p=next(p for p in t['patches'] if p['id']==patch)
box=p['globalContextBox']; tx,ty=box[0]-12288,box[1]-36864
oldp=Z/'native'/('r10_c04_'+patch+'_v1.png')
base=np.array(Image.open(oldp).convert('RGB'))
structure=D/'r10_c04_sixstep_structure_v1.png'
src=np.array(Image.open(structure).convert('RGB'))
fits=read(Z/'qa/r10_c04-six-step-layout-line-fits.json')['lines']
yy,xx=np.mgrid[0:1254,0:1254]
gx=xx+tx; gy=yy+ty
u=(gx-256)*1254/4096; v=(gy+768)*1254/4096
# GUIDE ONLY: piecewise vertical remap six noses to original layout. No output game pixels use this resampling.
want=np.stack([f['slope']*(u+78.375-700)+f['yAtGuideX700']+235.125 for f in fits])
seen=np.stack([-0.43*(u-700)+b for b in [349,456,561,665,769,874]])
vm=v.copy()
for k in range(7):
    lo=np.full_like(v,-1000.) if k==0 else want[k-1]
    hi=np.full_like(v,2254.) if k==6 else want[k]
    slo=np.full_like(v,-1000.) if k==0 else seen[k-1]
    shi=np.full_like(v,2254.) if k==6 else seen[k]
    take=(v>=lo)&(v<hi)
    vm[take]=(slo+(v-lo)/(hi-lo)*(shi-slo))[take]
# Extrapolate only the guide's occluded left flight from clear central treads;
# otherwise the structure reference's different lantern and new left pillar would leak into native guidance.
sample_u=np.where(u<420,650,u)
sample_v=vm-0.43*(sample_u-u)
guide=src[np.clip(np.rint(sample_v).astype(int),0,1253),np.clip(np.rint(sample_u).astype(int),0,1253)]
# Geometry-guide flight domain includes old stair edges requiring removal; foreground objects retain native pixels.
poly=[(650,1110),(3070,-30),(3200,300),(3400,780),(3630,1250),(3930,1520),(3950,1640),(1260,2780),(630,2190)]
mask=Image.new('1',(1254,1254)); ImageDraw.Draw(mask).polygon([(x-tx,y-ty) for x,y in poly],fill=1)
m=np.asarray(mask).copy()
r,g,b=base[:,:,0].astype(float),base[:,:,1].astype(float),base[:,:,2].astype(float)
objbox=((gx>=740)&(gx<1320)&(gy>=450)&(gy<1940))|((gx>=420)&(gx<735)&(gy<3000))|((gx<430)&(gy>450)&(gy<1930))
objects=objbox&(r>b*1.50)&(r>g*1.10)
filled=Image.fromarray(np.pad(objects.astype('uint8'),1)).copy()
ImageDraw.floodfill(filled,(0,0),2,thresh=0)
objects=np.asarray(filled)[1:-1,1:-1]<2
m[objects]=False
base[m]=guide[m]
overlaps=[]
for rp in sorted(D.glob('r10_c04_p*_v*.png.generation.json')):
    rec=read(rp)
    if rec.get('status') in ['rejected','superseded']: continue
    if patch=='p02_04' and rec.get('coordinates',{}).get('id','').startswith('p03_'): continue
    cb=rec['coordinates']['globalContextBox']
    inter=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
    if inter[2]<=inter[0] or inter[3]<=inter[1]: continue
    if inter[2]-inter[0]>230 and inter[3]-inter[1]>230: continue
    im=np.array(Image.open(rec['file']).convert('RGB'))
    dest=(slice(inter[1]-box[1],inter[3]-box[1]),slice(inter[0]-box[0],inter[2]-box[0]))
    base[dest]=im[inter[1]-cb[1]:inter[3]-cb[1],inter[0]-cb[0]:inter[2]-cb[0]]
    overlaps.append({'path':rec['file'],'sha256':sha(rec['file']),'globalOverlapBox':inter})
guidep=D/(stem+'-guide.png'); Image.fromarray(base).save(guidep)
Image.fromarray(m.astype('uint8')*255).save(D/(stem+'-flight-mask.png'))
refs=read(Z/'references.json')
inputs=[{'path':guidep.as_posix(),'sha256':sha(guidep),'role':'edit target: layout-corrected six-step guide, old foreground pixels retained, corrected newly generated neighbors retained'}, {'path':oldp.as_posix(),'sha256':sha(oldp),'role':'same native tile old version: preserve foreground objects and material rendering only; old eight-step structure is WRONG'}, {'path':structure.as_posix(),'sha256':sha(structure),'role':'complete six-step structure design reference only; slight positional drift already corrected in image 1'}, refs[1],refs[2]]
coord={**p,'role':'native staircase full-flight rebuild at fixed coordinates'}
req={'stem':stem,'tile':'r10_c04','patch':patch,'coordinates':coord,'references':inputs,'overlaps':overlaps,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'startedAtUtc':datetime.now(timezone.utc).isoformat(),'guideDerivation':{'source':structure.as_posix(),'sourceSha256':sha(structure),'role':'layout guide only, NEVER game pixels','operation':'nearest sampling with piecewise six-nose coordinate correction, paste retained native foreground and neighboring native overlap','fits':(Z/'qa/r10_c04-six-step-layout-line-fits.json').as_posix(),'oldNative':oldp.as_posix(),'oldNativeSha256':sha(oldp),'foregroundRetention':'native object colors in explicit object bounds; geometry guide only','flightPolygonTileCoordinates':poly}}
write(D/(stem+'.request.json'),req)
lineinfo=[]
for f in fits:
    def y_at(x): return f['slope']*((x+tx)-700*4096/1254)+f['yAtGuideX700']*4096/1254-ty
    lineinfo.append({'step':f['step'],'yAtX0':round(y_at(0)),'yAtX1253':round(y_at(1253))})
prompt='Use case: precise-object-edit. Produce one native 1254×1254 square detailed game-map patch at unchanged crop, scale, view and camera. Image 1 is the EXACT target composition: six-step structure positions have been corrected to the approved global layout and any already clean native neighboring overlap must be preserved. Redraw its visibly low-resolution stair guidance as crisp fine painterly native artwork. Image 2 is the OLD native version, use only its material palette, detail scale and non-stair foreground objects: its extra stair count/pitch is WRONG and must not be reproduced. Image 3 shows the complete six-nose staircase for understanding only; DO NOT zoom out or copy its full scene or its new left pillar. Image 4 material style and Image 5 approved Daoist chibi painterly style are references only; no UI, text, people or night lighting.\nIn this crop, projected nose lines have the following local coordinates (some endpoints lie outside the crop or behind foreground; do not invent steps to fit them): '+json.dumps(lineinfo)+'. Preserve these six global straight parallel rhythms, including top landing edge. Each visible tread nose must remain one straight continuous diagonal with no bends, kinks, stubs, extra stair, doubling or new block seams at image edges. Between adjacent noses there is one broad horizontal tread and one stone riser face; do not subdivide them. Any partial stair at crop edge continues outside frame.\nPreserve all old red lantern silhouettes, gold motifs, tassels, dark wood pole, existing outer sidewall silhouette and its upper stone pillar, road/sand boundary and ground objects exactly as image 1. Only stair flight surfaces, risers and contacts are being corrected. Preserve image 2 original natural warm-grey stone palette and soft finely stippled painted stone texture, cool grey top paving, bright sunny gentle shadows, smooth softly rounded bevels, natural quiet thin stone joints. Do not recolor to white marble, add giant white veins, extra moss, extra props, new walls, new pillars, labels, gridlines or border. Every visible surface must have fresh crisp native detail. Preserve all corrected native overlap bands from image 1 in their exact geometry and color. The output is exactly this patch, not the complete staircase.'
(D/(stem+'.prompt.txt')).write_text(prompt+'\n',encoding='utf-8')
print(json.dumps({'stem':stem,'guide':guidep.as_posix(),'references':[r['path'] for r in inputs],'prompt':prompt,'lineCoordinates':lineinfo,'overlapCount':len(overlaps)},ensure_ascii=False))
