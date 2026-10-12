"""Adopt AI-redrawn cloth only; preserve structural edges and all other art."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,hashlib,json
from datetime import datetime,timezone
z=Path(__file__).resolve().parent;t=z/'r10_c09';outdir=t/'processed/clothpass';outdir.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(z/'colorpass-selected.json')
editpath=t/'repairs/cloth-v1.png';inputpath=t/'repair-inputs/cloth-seam-v1.png'
src=np.asarray(Image.open(inputpath).convert('RGB'),dtype=np.int16)
edit=np.asarray(Image.open(editpath).convert('RGB'),dtype=np.float32)
assert src.shape==edit.shape==(1254,1254,3)
r,g,b=src[:,:,0],src[:,:,1],src[:,:,2]
yy,xx=np.mgrid[0:1254,0:1254]
iscloth=(r<130)&(b>130)&(b-r>45)&(g-r>22)&(b-g>30)&(yy>=400)&(yy<1190)
# Protect at least3 source pixels along every cloth/wood/lantern silhouette.
m=Image.fromarray(np.uint8(iscloth)*255).filter(ImageFilter.MinFilter(7))
alpha=np.zeros((1254,1254),dtype=np.float32)
for k in range(8):
    m=m.filter(ImageFilter.MinFilter(3))
    alpha+=(np.asarray(m)>0).astype(np.float32)/8
# Only the crop's left border intersects cloth;32px fine-texture transition,
# wholly inside the cloth and away from its object boundary.
u=np.clip(xx/32,0,1).astype(np.float32);alpha*=u*u*(3-2*u)
maskpath=outdir/'cloth-v1-adoption-alpha.npy';np.save(maskpath,alpha)
Image.fromarray(np.uint8(np.rint(alpha*255))).save(outdir/'cloth-v1-adoption-mask.png')
box=[1180,420,2434,1674]
newsel={'tile':'r10_c09','status':'cloth_texture_candidate_pending_native_QA','patches':{},'colorSourceSelection':{'file':str(z/'colorpass-selected.json'),'sha256':sha(z/'colorpass-selected.json')},'aiRepair':{'file':str(editpath),'sha256':sha(editpath),'generationRecord':str(editpath)+'.generation.json'},'adoptionMask':{'file':str(maskpath),'sha256':sha(maskpath),'tileBox':box,'structuralEdgeProtectionPixels':3,'textureTransitionPixels':8,'leftCropTextureTransitionPixels':32,'geometryWarp':False,'sourcePixelResampling':False},'formalAccepted':False}
checks=[]
for pid,rel in base['patches'].items():
    p=t/rel;arr=np.asarray(Image.open(p).convert('RGB'),dtype=np.float32);old=arr.copy()
    row,col=int(pid[1])-1,int(pid[2])-1;nx,ny=col*1024-115,row*1024-115
    ix0,iy0,ix1,iy1=max(nx,box[0]),max(ny,box[1]),min(nx+1254,box[2]),min(ny+1254,box[3])
    if ix0<ix1 and iy0<iy1:
        ax0,ay0,ax1,ay1=ix0-box[0],iy0-box[1],ix1-box[0],iy1-box[1]
        px0,py0,px1,py1=ix0-nx,iy0-ny,ix1-nx,iy1-ny
        aa=alpha[ay0:ay1,ax0:ax1,None]
        arr[py0:py1,px0:px1]=arr[py0:py1,px0:px1]*(1-aa)+edit[ay0:ay1,ax0:ax1]*aa
        output=np.uint8(np.clip(np.rint(arr),0,255))
        dest=outdir/(pid+'-clothpass.png');Image.fromarray(output).save(dest)
        meta={'file':str(dest),'sha256':sha(dest),'createdAt':datetime.now(timezone.utc).isoformat(),'dimensions':[1254,1254],'classification':'derived native candidate with AI-redrawn cloth texture','source':{'file':str(p),'sha256':sha(p)},'aiRepair':newsel['aiRepair'],'adoptionMask':newsel['adoptionMask'],'nativePixelOriginInTile':[nx,ny],'adoptedTileIntersection':[ix0,iy0,ix1,iy1],'repairSourceCrop':[ax0,ay0,ax1,ay1],'destinationBox':[px0,py0,px1,py1],'operation':'integer-aligned cloth-only alpha adoption;8px fine texture transition and32px left crop transition, no structural blending','geometryWarp':False,'sourcePixelResampling':False,'pixelShift':[0,0],'changedPixelCount':int(np.count_nonzero(np.any(output!=old,axis=2))),'status':'pending_visual_review'}
        write(dest.with_suffix('.png.derivation.json'),meta)
        newsel['patches'][pid]=str(dest.relative_to(t))
    else:newsel['patches'][pid]=rel
canvas=Image.new('RGB',(4096,4096))
for pid,rel in newsel['patches'].items():
    row,col=int(pid[1])-1,int(pid[2])-1
    im=Image.open(t/rel)
    canvas.paste(im.crop((115,115,1139,1139)),(col*1024,row*1024))
candidate=outdir/'r10_c09-clothpass-candidate.png';canvas.save(candidate)
preview=outdir/'r10_c09-clothpass-QA-preview-1024.png';canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
newsel['candidate']={'file':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096],'operation':'16 native1024 cores unscaled, with recorded AI cloth adoption'}
newsel['qaPreview']={'file':str(preview),'sha256':sha(preview),'classification':'downsampled QA only, never formal asset'}
oldcan=np.asarray(Image.open(base['candidate']['file']).convert('RGB'))
can=np.asarray(canvas)
tilemask=np.zeros((4096,4096),dtype=bool);tilemask[box[1]:box[3],box[0]:box[2]]=alpha>0
assert np.array_equal(oldcan[~tilemask],can[~tilemask])
newsel['validation']={'allPixelsOutsideAdoptionMaskByteIdentical':True,'changedPixelCount':int(np.count_nonzero(np.any(oldcan!=can,axis=2))),'adoptionPixelCount':int(np.count_nonzero(tilemask)),'repairDimensions':[1254,1254],'sourcePixelResampling':False,'geometryWarp':False}
write(z/'clothpass-selected.json',newsel)
# Unscaled before/after view of the full repair context, for validation.
canvas.crop(box).save(outdir/'adopted-cloth-context-100pct.png')
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'validation':newsel['validation']},indent=2))

