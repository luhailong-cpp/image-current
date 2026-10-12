from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

B = Path(__file__).resolve().parent
OUT = B / 'output'
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):
    with Image.open(p) as im: size=list(im.size)
    return {'path':str(p),'sha256':sha(p),'pixels':size,'resampled':False}
old = np.array(Image.open(B/'inputs/B.native-target.png').convert('RGB'))
sources = {n: np.array(Image.open(B/f'native/B-v{n}.png').convert('RGB')) for n in (1,2)}
assert old.shape == (1254,1254,3)
assert all(a.shape == old.shape for a in sources.values())
specs = [
    {'id':'G03','source':1,'lines':[([(530,469),(700,336),(888,183)],52)],'ellipses':[(853,140,938,224)]},
    {'id':'G04','source':2,'lines':[([(155,1031),(300,920),(450,804),(575,708),(585,672),(810,493)],38), ([(155,1030),(300,913),(450,789),(570,689),(810,493)],38)],'ellipses':[]},
    {'id':'G05','source':1,'lines':[([(500,1174),(650,1058),(670,1051),(800,949)],34), ([(500,1175),(650,1063),(675,1044),(800,949)],34)],'ellipses':[]},
]
candidate = old.copy()
combined_mask = np.zeros(old.shape[:2],bool)
patches=[]
for spec in specs:
    mask = Image.new('L',(1254,1254),0)
    draw = ImageDraw.Draw(mask)
    for points,width in spec['lines']: draw.line(points, fill=255, width=width, joint='curve')
    for box in spec['ellipses']: draw.ellipse(box,fill=255)
    # Two pixels of bounded mask feather; every interior pixel is copied from
    # the returned native image, never painted, warped or color adjusted.
    raw=np.array(mask)>0
    inner1=np.array(mask.filter(ImageFilter.MinFilter(3)))>0
    inner2=np.array(mask.filter(ImageFilter.MinFilter(5)))>0
    alpha=np.zeros(raw.shape,np.float32)
    alpha[raw]=.25;alpha[inner1]=.75;alpha[inner2]=1
    # Hard exclusion of A's G02 and the already accepted p04_02 local repair.
    alpha[160:250,670:760]=0
    alpha[510:965,822:1254]=0
    active=alpha>0
    assert not np.any(active & combined_mask)
    new=sources[spec['source']]
    blended=np.rint(old.astype(np.float32)*(1-alpha[:,:,None])+new.astype(np.float32)*alpha[:,:,None]).astype(np.uint8)
    candidate[active]=blended[active]
    combined_mask|=active
    ys,xs=np.where(active);box=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    x0,y0,x1,y1=box
    patch=OUT/f'{spec["id"]}.preblended.patch.png';paste=OUT/f'{spec["id"]}.paste-mask.png';am=OUT/f'{spec["id"]}.alpha-evidence.png'
    Image.fromarray(blended[y0:y1,x0:x1]).save(patch)
    Image.fromarray((active[y0:y1,x0:x1]*255).astype(np.uint8)).save(paste)
    Image.fromarray(np.rint(alpha[y0:y1,x0:x1]*255).astype(np.uint8)).save(am)
    patches.append({'id':spec['id'],'nativeSource':info(B/f'native/B-v{spec["source"]}.png'),'cropLocalBox':box,'contextBox':[x0+512,y0+3072,x1+512,y1+3072],'tileCoreBox':[x0+397,y0+2957,x1+397,y1+2957],'worldBox':[x0+16781,y0+43917,x1+16781,y1+43917],'patch':info(patch),'pasteMask':info(paste),'alphaEvidence':info(am),'affectedPixelCount':int(active.sum()),'instruction':'Paste patch at contextBox top-left using binary pasteMask exactly once. Patch already contains its bounded two-pixel transition; do not re-feather, resize, or replace the entire rectangle.'})
Image.fromarray(candidate).save(OUT/'B.candidate.native-crop.png')
Image.fromarray((combined_mask*255).astype(np.uint8)).save(OUT/'B.combined-paste-mask.png')
assert np.array_equal(candidate[~combined_mask],old[~combined_mask])
assert np.array_equal(candidate[160:250,670:760],old[160:250,670:760])
assert np.array_equal(candidate[510:965,822:1254],old[510:965,822:1254])
for label,box in [('G03',[490,95,985,520]),('G04',[110,450,855,1075]),('G05',[460,905,845,1225])]:
    a=Image.fromarray(old).crop(box);c=Image.fromarray(candidate).crop(box)
    side=Image.new('RGB',(a.width*2,a.height));side.paste(a,(0,0));side.paste(c,(a.width,0));side.save(B/'qa'/f'{label}-original-composite.png')
record={'status':'mechanically-composed-awaiting-visual-review','createdAtUtc':datetime.now(timezone.utc).isoformat(),'formalAccepted':False,'input':info(B/'inputs/B.native-target.png'),'fullContextSource':json.loads((B/'inputs/crop-derivation.json').read_text())['source'],'requiredFullContextSha256':'09e3107e74361a9c2cc3a1b2911554ad3dbb470843a833d6e648e47b86804686','contextCropBox':[512,3072,1766,4326],'candidate':info(OUT/'B.candidate.native-crop.png'),'patches':patches,'checks':{'outsideMasksExact':True,'protectedG02Exact':True,'protectedExistingJointRegionExact':True,'resampling':False,'colorAdjustment':False,'nativeGeometryWarping':False,'maximumFeatherRadiusPixels':2},'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__))}
(OUT/'assembly.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'patches':[{k:p[k] for k in ['id','contextBox','affectedPixelCount']} for p in patches],'checks':record['checks']}))
