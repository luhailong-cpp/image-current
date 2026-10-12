from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
D=T/'qa/local-caps-trial-01';D.mkdir(exist_ok=True);assert not (D/'index.json').exists()
bp=T/'qa/bridge-trial-curb-junction-03/index.json';m=p.read(bp);pix=np.array(Image.open(m['candidate']['file']).convert('RGB'));own=np.array(Image.open(m['sourceIndex']['file']));sources=m['sources'];operations=[]
bid='curb-junction-04';gd=T/'bridges'/bid;g=p.read(gd/'generation.json');new=np.array(Image.open(g['file']).convert('RGB'));sid=len(sources);sources.append({'id':bid,'file':g['file'],'sha256':g['sha256'],'tileOriginXY':[397,2445],'generationRecord':ref(gd/'generation.json')})
previous=T/'bridges/curb-junction-03/native.png';guide=gd/'edit-target.png';assert np.array_equal(np.array(Image.open(previous)),np.array(Image.open(guide)))
cp=gd/'source-derivation-correction.json'
if not cp.exists():p.write_json(cp,{'note':'placement.json derivedFrom/baseManifest retain original assembly ancestry; immediate editTarget was copied pixel-for-pixel from bridge03 native, not directly cropped from original assembly. Exact request reference and placement world box are correct. This record explicitly identifies the immediate derivation.','editTarget':ref(guide),'immediateSource':ref(previous),'immediateGenerationRecord':ref(previous.with_name('generation.json')),'samePixels':True},replace=False)
sources[-1]['sourceDerivationCorrection']=ref(cp)
for name,box,b in [('upper-nick',[550,150,740,295],35),('floor-cap',[530,995,760,1250],40)]:
 bx,by,bx2,by2=box;x,y=397+bx,2445+by;w,h=bx2-bx,by2-by;patch=new[by:by2,bx:bx2];old=pix[y:y+h,x:x+w].copy()
 left=A.minimum_vertical_seam(old[:,:b],patch[:,:b]);right=A.minimum_vertical_seam(patch[:,-b:],old[:,-b:])+w-b;top=A.minimum_vertical_seam(old[:b].transpose(1,0,2),patch[:b].transpose(1,0,2));bottom=A.minimum_vertical_seam(patch[-b:].transpose(1,0,2),old[-b:].transpose(1,0,2))+h-b
 yy,xx=np.indices((h,w));mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);mask[[0,-1]]=False;mask[:,[0,-1]]=False
 pix[y:y+h,x:x+w][mask]=patch[mask];own[y:y+h,x:x+w][mask]=sid;operations.append({'name':name,'sourceIndex':sid,'sourceCropLTRB':box,'tileBox':[x,y,x+w,y+h],'maskPaths':{'left':left.tolist(),'right':right.tolist(),'top':top.tolist(),'bottom':bottom.tolist()},'selectedPixels':int(mask.sum())})
proof=[]
for i,s in enumerate(sources):
 ys,xs=np.where(own==i);n=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['tileOriginXY'];assert p.sha(s['file'])==s['sha256'];assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':True})
im=Image.fromarray(pix);out=A.save_png(im,D/'candidate.png');oi=A.save_png(Image.fromarray(own),D/'source-index.png');qa=A.write_qa(im,out,D/'internal');entries=[]
for o in operations:
 x,y,x2,y2=o['tileBox'];box=[x-100,y-100,x2+100,y2+100];e=A.save_png(im.crop(box),D/(o['name']+'-region.png'));e.update(name=o['name'],cropLTRB=box,nativePixelScale=1,actuallyViewed=False);entries.append(e)
p.write_json(D/'index.json',{'candidate':out,'sourceIndex':oi,'sources':sources,'pixelProof':proof,'fullNativePixelProof':True,'resampled':False,'blended':False,'priorTrial':ref(bp),'operations':operations,'internalQa':qa,'entries':entries,'formalAccepted':False},replace=False);print(out)
