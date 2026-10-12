from workflow import *
from PIL import Image
import numpy as np
folder=ROOT/'qa/roof-surface-v01';folder.mkdir(exist_ok=True)
def subtract(a,b):
 x0,y0,x1,y1=a;u0,v0,u1,v1=b;ix0,iy0,ix1,iy1=max(x0,u0),max(y0,v0),min(x1,u1),min(y1,v1)
 if ix0>=ix1 or iy0>=iy1:return [a]
 return [q for q in [[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]] if q[0]<q[2] and q[1]<q[3]]
def cliprect(r,box):
 p=dict(r);x,y,_,_=r['destinationBox'];sx,sy,_,_=r['sourceCrop'];p.update({'sourceCrop':[sx+box[0]-x,sy+box[1]-y,sx+box[2]-x,sy+box[3]-y],'destination':box[:2],'destinationBox':box});return p
def build(tid,basename,outname,tilex):
 base=ROOT/'tiles'/basename;rec=read(Path(str(base)+'.generation.json'));im=Image.open(base).convert('RGB');parts=rec.get('contributions',rec.get('derivedFrom'));parts=[dict(p) for p in parts]
 for p in parts:
  if 'destinationBox' not in p:
   x,y=p['destination'][:2];sx,sy,ex,ey=p['sourceCrop'];p['destinationBox']=[x,y,x+ex-sx,y+ey-sy]
 overlays=[]
 for letter,originx in [('a',-397),('b',627),('c',1651)]:
  owned=[originx+115,0,originx+1139,1254];inter=[max(owned[0],tilex),0,min(owned[2],tilex+4096),1254]
  if inter[0]>=inter[2]:continue
  src=ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png';box=[inter[0]-tilex,0,inter[2]-tilex,1254];crop=[inter[0]-originx,0,inter[2]-originx,1254];im.paste(Image.open(src).convert('RGB').crop(crop),box[:2])
  parts=[cliprect(p,q) for p in parts for q in subtract(p['destinationBox'],box)];r={'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':box[:2],'destinationBox':box,'record':str(src)+'.generation.json'};parts.append(r);overlays.append(r)
 out=ROOT/'tiles'/outname;assert not out.exists();im.save(out);coverage=np.zeros((4096,4096),dtype=np.uint8);replay=Image.new('RGB',(4096,4096))
 for p in parts:
  assert sha(Path(p['file']))==p['sha256'];crop=Image.open(p['file']).convert('RGB').crop(p['sourceCrop']);x0,y0,x1,y1=p['destinationBox'];assert crop.size==(x1-x0,y1-y0);replay.paste(crop,(x0,y0));coverage[y0:y1,x0:x1]+=1
 assert np.all(coverage==1) and replay.tobytes()==im.tobytes()
 write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Exact unscaled source rectangles, once-only ownership, no blend/warp/painting','contributions':parts,'base':str(base),'baseSha256':sha(base),'newOverlays':overlays,'fullCoverage':True,'allContributionsPixelExact':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'actualModel':None,'actualQuality':None,'status':'pending_changed_roof_review'})
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/(tid+'-preview.png'));return im,out
left,lp=build('r09_c11','r09_c11.candidate.png','r09_c11.candidate-v02.png',-4096)
right,rp=build('r09_c12','r09_c12.candidate-v03.png','r09_c12.candidate-v04.png',0)
canvas=Image.new('RGB',(8192,4096));canvas.paste(left,(0,0));canvas.paste(right,(4096,0));entries=[]
def save(name,im,desc):
 f=folder/(name+'.png');im.save(f);entries.append({'id':name,'file':str(f),'sha256':sha(f),'description':desc,'status':'pending_visual_review'})
for y in [0,742]:save('shared-west-'+str(y),canvas.crop([3840,y,4352,y+512]),'Original pixels across tile border, local x256')
for x in [-282,742,1766,2790]:
 for y in [0,742]:save('vertical-'+str(x)+'-'+str(y),canvas.crop([4096+x-192,y,4096+x+192,y+512]),'Original pixels new source boundary at local x192')
for x in [-282,742,1766]:save('bottom-'+str(x),canvas.crop([4096+x,1062,4096+x+1024,1446]),'Original pixels lower insertion y1254 localy192')
north=Image.open(ROOT/'tiles/r08_c12.candidate-v13.png').convert('RGB')
for c in range(3):
 q=Image.new('RGB',(1024,512));q.paste(north.crop([1024*c,3840,1024*(c+1),4096]),(0,0));q.paste(right.crop([1024*c,0,1024*(c+1),256]),(0,256));save('north-'+str(c+1),q,'Originalpixels north edge local y256')
write(folder/'review-index.json',{'createdAt':now(),'candidates':[{'file':str(lp),'sha256':sha(lp)},{'file':str(rp),'sha256':sha(rp)}],'entries':entries,'formalAccepted':False})
print(str(lp));print(sha(lp));print(str(rp));print(sha(rp))

