from workflow import *
from PIL import Image
import numpy as np
folder=ROOT/'qa/roof-lower-row-v01';folder.mkdir(exist_ok=True)
def subtract(a,b):
 x0,y0,x1,y1=a;u0,v0,u1,v1=b;ix0,iy0,ix1,iy1=max(x0,u0),max(y0,v0),min(x1,u1),min(y1,v1)
 if ix0>=ix1 or iy0>=iy1:return [a]
 return [q for q in [[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]] if q[0]<q[2] and q[1]<q[3]]
def build(tid,basefile,outfile,tilex):
 base=ROOT/'tiles'/basefile;rec=read(Path(str(base)+'.generation.json'));parts=rec['contributions'];im=Image.open(base).convert('RGB')
 for letter,x in [('e',-397),('f',627)]:
  inter=[max(x+115,tilex),742,min(x+1139,tilex+4096),1996]
  if inter[0]>=inter[2]:continue
  src=ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png';crop=[inter[0]-x,0,inter[2]-x,1254];box=[inter[0]-tilex,742,inter[2]-tilex,1996];im.paste(Image.open(src).convert('RGB').crop(crop),box[:2]);keep=[]
  for p in parts:
   for b in subtract(p['destinationBox'],box):
    q=dict(p);dx,dy,_,_=p['destinationBox'];sx,sy,_,_=p['sourceCrop'];q.update({'sourceCrop':[sx+b[0]-dx,sy+b[1]-dy,sx+b[2]-dx,sy+b[3]-dy],'destination':b[:2],'destinationBox':b});keep.append(q)
  keep.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':box[:2],'destinationBox':box,'record':str(src)+'.generation.json'});parts=keep
 out=ROOT/'tiles'/outfile;assert not out.exists();im.save(out);cover=np.zeros((4096,4096),dtype=np.uint8);replay=Image.new('RGB',(4096,4096))
 for p in parts:
  assert sha(Path(p['file']))==p['sha256'];a=Image.open(p['file']).convert('RGB').crop(p['sourceCrop']);x0,y0,x1,y1=p['destinationBox'];assert a.size==(x1-x0,y1-y0);replay.paste(a,(x0,y0));cover[y0:y1,x0:x1]+=1
 assert np.all(cover==1) and replay.tobytes()==im.tobytes()
 write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Exact native source rectangular crops and hard-paste; no color changes or resampling','contributions':parts,'base':str(base),'baseSha256':sha(base),'fullCoverage':True,'allContributionsPixelExact':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'actualModel':None,'actualQuality':None,'status':'pending_lower_roof_boundary_review'})
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/(tid+'-preview.png'));return im,out
left,lp=build('r09_c11','r09_c11.candidate-v02.png','r09_c11.candidate-v03.png',-4096);right,rp=build('r09_c12','r09_c12.candidate-v06.png','r09_c12.candidate-v07.png',0)
big=Image.new('RGB',(8192,4096));big.paste(left,(0,0));big.paste(right,(4096,0));entries=[]
def save(name,box):
 f=folder/(name+'.png');big.crop(box).save(f);entries.append({'id':name,'file':str(f),'sha256':sha(f),'sourceCropInTwoTileCanvas':box,'status':'pending_visual_review'})
for x in [-282,742]:
 save('top-'+str(x),[4096+x,614,4096+x+1024,870]);save('bottom-'+str(x),[4096+x,1868,4096+x+1024,2124])
for x in [-282,742,1766]:
 for y in [742,1369]:save('side-'+str(x)+'-'+str(y),[4096+x-128,y,4096+x+128,y+627])
write(folder/'review-index.json',{'createdAt':now(),'candidates':[{'file':str(lp),'sha256':sha(lp)},{'file':str(rp),'sha256':sha(rp)}],'entries':entries,'formalAccepted':False});print(str(lp));print(sha(lp));print(str(rp));print(sha(rp))

