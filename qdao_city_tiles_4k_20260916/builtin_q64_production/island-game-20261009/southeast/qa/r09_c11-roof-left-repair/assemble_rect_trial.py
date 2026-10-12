from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
base=[R/'tiles/r09_c11.candidate-v04.png',R/'tiles/r09_c12.candidate-v08.png'];b=Image.new('RGB',(8192,4096))
for i,f in enumerate(base):b.paste(Image.open(f).convert('RGB'),(4096*i,0))
up=R/'native/r09_c11_roof_color_upper_v01.png';lo=R/'native/r09_c11_roof_color_lower_v01.png'
U=np.asarray(Image.open(up).convert('RGB'));L=np.asarray(Image.open(lo).convert('RGB'));B=np.asarray(b.crop((3300,0,4554,1854))).copy()
cuty=737;C=B.copy();C[:cuty]=U[:cuty];C[cuty:]=L[cuty-600:]
a=C.astype(np.int16);blue=(a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45);ys=np.arange(1854);bottom=1853-blue[::-1].argmax(0)+2;mask=ys[:,None]<=bottom[None,:]
# First unshifted rectangle proposal, assess before optional per-object seam ownership.
mask[:,:68]=False;mask[:,1230:]=False
sid=np.zeros((4096,8192),np.uint8);region=sid[:1854,3300:4554];region[mask&(ys[:,None]<cuty)]=1;region[mask&(ys[:,None]>=cuty)]=2
out=np.asarray(b).copy();out[:1854,3300:4554][mask]=C[mask]
records=[]
for i,tid in enumerate(['r09_c11','r09_c12']):
 im=Image.fromarray(out[:,i*4096:(i+1)*4096]);f=Q/f'{tid}-trial-rect-v01.png';im.save(f);sf=Q/f'{tid}-source-id-rect-v01.png';Image.fromarray(sid[:,i*4096:(i+1)*4096]).save(sf)
 records.append({'tile':tid,'file':str(f),'sha256':sh(f),'sourceID':str(sf),'sourceIDSha256':sh(sf),'base':str(base[i]),'baseSha256':sh(base[i])})
trial=Image.fromarray(out)
ev=[]
for name,box in [('left-upper',[3200,0,3600,750]),('left-lower',[3200,750,3600,1550]),('right-upper',[4380,0,4650,750]),('right-lower',[4380,750,4650,1650]),('upper-lower',[3300,609,4554,865]),('bottom-left',[3300,1150,3927,1650]),('bottom-right',[3927,1300,4554,1854]),('fixed-v14',[3072,768,4096,1280]),('shared-upper',[3840,0,4352,1024]),('shared-lower',[3840,1024,4352,1854])]:
 f=Q/f'{name}-rect-v01.png';trial.crop(box).save(f);ev.append({'file':str(f),'sha256':sh(f),'canvasCrop':box})
north=Image.new('RGB',(458,512));north.paste(Image.open(R/'tiles/r08_c12.candidate-v15.png').crop((0,3840,458,4096)),(0,0));north.paste(trial.crop((4096,0,4554,256)),(0,256));north.save(Q/'north-r08-rect-v01.png')
wr(Q/'rect-trial-v01.json',{'outputs':records,'sources':[{'id':1,'file':str(up),'sha256':sh(up),'originInTwoTileCanvas':[3300,0]},{'id':2,'file':str(lo),'sha256':sh(lo),'originInTwoTileCanvas':[3300,600]}],'selection':'0 base;1 upper;2 lower. Same native coordinates, binary source copy only.','upperLowerBoundaryY':cuty,'leftCut':3368,'rightCut':4530,'evidence':ev,'formalAccepted':False,'status':'pending_visual'})
print('Trial rectangles and10perimeter/evidence crops saved')

