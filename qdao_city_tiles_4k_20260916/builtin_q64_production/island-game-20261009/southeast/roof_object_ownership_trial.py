from workflow import *
from PIL import Image
import numpy as np
from PIL import ImageFilter,ImageDraw,ImageOps
def binary_dilation(a,iterations=2):
 return np.asarray(Image.fromarray(a.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(iterations*2+1)))>0
def binary_fill_holes(a):
 im=ImageOps.expand(Image.fromarray(a.astype(np.uint8)*255),border=1,fill=0);ImageDraw.floodfill(im,(0,0),128);return np.asarray(im)[1:-1,1:-1]!=128
folder=ROOT/'qa/roof-object-ownership';folder.mkdir(exist_ok=True)
lp=ROOT/'tiles/r09_c11.candidate-v02.png';rp=ROOT/'tiles/r09_c12.candidate-v06.png';left=Image.open(lp).convert('RGB');right=Image.open(rp).convert('RGB');la=np.asarray(left).copy();ra=np.asarray(right).copy();jobs=[]
for letter,ox in [('e',-397),('f',627)]:
 source=ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png';src=np.asarray(Image.open(source).convert('RGB'));target=ROOT/'guides'/f'r09_c12_roof_surface_{letter}_v01.target.png';orig=np.asarray(Image.open(target).convert('RGB'))
 def blue(a):
  a=a.astype(np.int16);return (a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45)
 mask=binary_fill_holes(binary_dilation(blue(src)|blue(orig),iterations=2));mask[:,:115]=False;mask[:,1139:]=False
 mp=folder/f'{letter}-mask.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp)
 xs=np.arange(1254)+ox
 for im,tilex in [(la,-4096),(ra,0)]:
  valid=(xs>=tilex)&(xs<tilex+4096)
  if not valid.any():continue
  si=np.where(valid)[0];destx=xs[si]-tilex;smallmask=mask[:,si];reg=im[742:1996,destx].copy();reg[smallmask]=src[:,si][smallmask];im[742:1996,destx]=reg
 jobs.append({'source':str(source),'sourceSha256':sha(source),'mask':str(mp),'maskSha256':sha(mp),'originRelativeR09c12':[ox,742],'generatedNativePixelsUsed':int(mask.sum()),'selectionOnly':'1 source original RGB copied; 0 leaves unchanged native base RGB. No resampling, blending, filters or changed output colors.'})
Image.fromarray(la).save(folder/'r09_c11-trial.png');Image.fromarray(ra).save(folder/'r09_c12-trial.png');Image.fromarray(ra).resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png')
for i,(x0,y0,x1,y1) in enumerate([[0,600,1024,1400],[742,600,1766,1400],[0,1300,1024,1900],[742,1300,1766,2000]]):Image.fromarray(ra).crop([x0,y0,x1,y1]).save(folder/f'edge-{i}.png')
write(folder/'trial.json',{'createdAt':now(),'bases':[{'file':str(lp),'sha256':sha(lp)},{'file':str(rp),'sha256':sha(rp)}],'jobs':jobs,'rule':'Complete blue roof surfaces including enclosed gold medallions, exact binary native-source ownership. Two-pixel ownership expansion encompasses original/generated antialiased silhouette; does not modify source pixels.','status':'trial_pending_native_boundary_visual_review','formalAccepted':False});print(jobs)

