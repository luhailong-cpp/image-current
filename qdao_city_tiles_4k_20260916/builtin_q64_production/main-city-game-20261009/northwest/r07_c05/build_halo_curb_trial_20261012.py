from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
base=T/'qa/partial-curb-trial-01';D=T/'qa/partial-curb-trial-02';D.mkdir(exist_ok=True)
if (D/'index.json').exists():raise SystemExit('Immutable trial exists')
prior=p.read(base/'index.json');pix=np.array(Image.open(prior['candidate']['file']).convert('RGB'));own=np.array(Image.open(prior['sourceIndex']['file']))
sources=prior['sources'];sid=next(i for i,s in enumerate(sources) if s['id']=='s03_02');s=sources[sid];src=np.array(Image.open(s['file']).convert('RGB'))
x,y,w,h=1030,3040,490,147;ox,oy=s['tileOriginXY'];new=src[y-oy:y-oy+h,x-ox:x-ox+w];old=pix[y:y+h,x:x+w].copy();assert new.shape==old.shape
left=A.minimum_vertical_seam(old[:,:60],new[:,:60]);right=A.minimum_vertical_seam(new[:,-120:],old[:,-120:])+w-120
bottom=A.minimum_vertical_seam(new[-28:].transpose(1,0,2),old[-28:].transpose(1,0,2))+h-28
yy,xx=np.indices((h,w));mask=(xx>=left[:,None])&(xx<right[:,None])&(yy<bottom[None,:]);mask[:,0]=False;mask[:,-1]=False;mask[-1]=False
pix[y:y+h,x:x+w][mask]=new[mask];own[y:y+h,x:x+w][mask]=sid
im=Image.fromarray(pix);candidate=A.save_png(im,D/'candidate.png');owners=A.save_png(Image.fromarray(own),D/'source-index.png')
proof=[]
for i,s in enumerate(sources):
 ys,xs=np.where(own==i);n=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['tileOriginXY'];valid=bool(np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]));assert valid;proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':True})
q=A.write_qa(im,candidate,D/'internal');entries=[]
for name,box in {'halo-repair-region':[870,2880,1680,3347],'halo-bottom-perimeter':[870,3060,1680,3347]}.items():
 e=A.save_png(im.crop(box),D/(name+'.png'));e.update({'name':name,'nativePixelScale':1,'actuallyViewed':False});entries.append(e)
p.write_json(D/'index.json',{'candidate':candidate,'sourceIndex':owners,'sources':sources,'pixelProof':proof,'fullNativePixelProof':True,'resampled':False,'blended':False,'priorTrial':{'file':str(base/'index.json'),'sha256':p.sha(base/'index.json')},'roiLTRB':[x,y,x+w,y+h],'internalQa':q,'entries':entries,'formalAccepted':False},replace=False)
print(candidate)
