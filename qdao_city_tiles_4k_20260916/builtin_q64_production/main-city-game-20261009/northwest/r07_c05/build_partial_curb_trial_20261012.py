from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent
sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
D=T/'qa'/'partial-curb-trial-01';D.mkdir(exist_ok=True)
if (D/'index.json').exists(): raise SystemExit('Immutable trial already exists')
pix=np.zeros((4096,4096,3),dtype=np.uint8);owners=np.zeros((4096,4096),dtype=np.uint8);sources=[]
for r in range(1,5):
 for c in range(1,5):
  pid=f's{r:02}_{c:02}';f=p.selected_path(T,pid);im=np.array(Image.open(f).convert('RGB'))
  x=(c-1)*1024;y=(r-1)*1024
  pix[y:y+1024,x:x+1024]=im[115:1139,115:1139];owners[y:y+1024,x:x+1024]=len(sources)
  sources.append({'id':pid,'file':str(f),'sha256':p.sha(f),'tileOriginXY':[x-115,y-115]})
before=pix.copy()
f=T/'native/s04_01_curbfix01.png';native=np.array(Image.open(f).convert('RGB'))
x,y,w,h=0,3072,650,600
old=pix[y:y+h,x:x+w].copy();new=native[115:115+h,115:115+w]
band=180
right=A.minimum_vertical_seam(new[:,-band:],old[:,-band:])+w-band
bottom=A.minimum_vertical_seam(new[-band:].transpose(1,0,2),old[-band:].transpose(1,0,2))+h-band
yy,xx=np.indices((h,w));mask=(xx<right[:,None])&(yy<bottom[None,:])
mask[-1,:]=False;mask[:,-1]=False
pix[y:y+h,x:x+w][mask]=new[mask];owners[y:y+h,x:x+w][mask]=len(sources)
sources.append({'id':'s04_01_curbfix01-partial','file':str(f),'sha256':p.sha(f),'tileOriginXY':[-115,2957]})
proof=[]
for i,s in enumerate(sources):
 ys,xs=np.where(owners==i);n=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['tileOriginXY']
 valid=bool(np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]));assert valid
 proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':valid})
im=Image.fromarray(pix);candidate=A.save_png(im,D/'candidate.png');owner=A.save_png(Image.fromarray(owners),D/'source-index.png')
q=A.write_qa(im,candidate,D/'internal')
west=Image.open(Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png').convert('RGB')
combo=Image.new('RGB',(640,4096));combo.paste(west.crop((3776,0,4096,4096)),(0,0));combo.paste(im.crop((0,0,320,4096)),(320,0))
images={'repair-region':im.crop((0,2912,850,3822)),'right-perimeter':im.crop((350,3072,810,3822)),'bottom-perimeter':im.crop((0,3392,810,3822)), 'north':im.crop((0,2752,1024,3392)),'west':combo.crop((0,3072,640,4096)).transpose(Image.Transpose.ROTATE_90),'north-west-junction':combo.crop((160,2912,480,3232))}
entries=[]
for name,v in images.items():
 e=A.save_png(v,D/(name+'.png'));e.update({'name':name,'nativePixelScale':1,'actuallyViewed':False});entries.append(e)
outline=np.zeros((h,w),np.uint8);outline[mask]=255;A.save_png(Image.fromarray(outline),D/'mask.png')
p.write_json(D/'index.json',{'candidate':candidate,'sourceIndex':owner,'sources':sources,'pixelProof':proof,'fullNativePixelProof':True,'resampled':False,'blended':False,'roiLTRB':[x,y,x+w,y+h],'changedPixelCount':int(np.any(before!=pix,axis=2).sum()),'internalQa':q,'entries':entries,'formalAccepted':False},replace=False)
print(json.dumps({'directory':str(D),'candidate':candidate,'overlayPixelCount':int(mask.sum())}))
