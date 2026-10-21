from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard,minimum_vertical_seam
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
O=W/(sys.argv[1] if len(sys.argv)>1 else 'base-v1');O.mkdir(exist_ok=True);Q=O/'qa';Q.mkdir(exist_ok=True)
sources=[];cache={}
def add(s):
 p=Path(s['file']);p=p if p.is_absolute() else B/p
 h=sha(p);assert h==s['sha256']
 k=(str(p),tuple(s['globalNativeBox']))
 if k in cache:return cache[k][0]
 sid=len(sources)+1;rec={'sourceId':sid,'file':str(p),'sha256':h,'globalNativeBox':s['globalNativeBox'],'generationRecord':str(p)+'.generation.json'}
 cache[k]=(sid,np.asarray(Image.open(p).convert('RGB')));sources.append(rec);return sid
strips=[];maps=[];seams=[]
for r in range(1,5):
 for c in range(1,5):
  sel=read(W/'selections'/f's{r:02d}_s{c:02d}.json');p=Path(sel['file']);g=read(str(p)+'.generation.json');sid=add({**sel,'globalNativeBox':g['globalNativeBox']});im=cache[(str(p),tuple(g['globalNativeBox']))][1];mi=np.full((1254,1254),sid,np.uint16)
  if c==1:a=im.copy();ids=mi
  else:a,ids,detail=append_hard(a,ids,im,mi,f'r{r}c{c}');seams.append(detail)
 strips.append(a);maps.append(ids)
a= strips[0];ids=maps[0]
for r in range(1,4):
 at,it,d=append_hard(a.transpose(1,0,2),ids.T,strips[r].transpose(1,0,2),maps[r].T,f'row{r+1}');a=at.transpose(1,0,2);ids=it.T;seams.append(d)
origin=[3981,20365]
def sample(ap,box):
 aa=read(ap);bb=aa['globalCoreBox'];sp=Path(aa['sourceIdMap']['file']);sp=sp if sp.is_absolute() else B/sp
 oldids=np.asarray(Image.open(sp));yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]];chosen=oldids[np.clip(yy-bb[1],0,oldids.shape[0]-1),np.clip(xx-bb[0],0,oldids.shape[1]-1)]
 ar=np.zeros((*xx.shape,3),np.uint8);ii=np.zeros(xx.shape,np.uint16)
 for so in aa['sources']:
  sidold=so.get('sourceId',so.get('jointSourceId'));gb=so['globalNativeBox'];m=(chosen==sidold)&(xx>=gb[0])&(xx<gb[2])&(yy>=gb[1])&(yy<gb[3])
  if m.any():
   sid=add(so);fp=Path(so['file']);fp=fp if fp.is_absolute() else B/fp;img=np.asarray(Image.open(fp).convert('RGB'));ar[m]=img[yy[m]-gb[1],xx[m]-gb[0]];ii[m]=sid
 assert (ii>0).all(),('uncovered',box,int((ii==0).sum()))
 return ar,ii
idx=read(B/'current-artifacts.json')
old,oi=sample(B/idx['r05_c02']['assembly'],[3981,20365,8307,20595])
seam,cost=minimum_vertical_seam(old[115:].transpose(1,0,2),a[115:230].transpose(1,0,2));take=np.arange(230)[:,None]<(115+seam[None,:]);a[:230]=np.where(take[:,:,None],old,a[:230]);ids[:230]=np.where(take,oi,ids[:230]);seams.append({'label':'external-north-native-only','path':(115+seam).tolist()})
# Exact source replay over full native halo canvas.
for s in sources:
 yy,xx=np.where(ids==s['sourceId'])
 if not len(xx):continue
 gb=s['globalNativeBox'];im=np.asarray(Image.open(s['file']).convert('RGB'));sx=xx+origin[0]-gb[0];sy=yy+origin[1]-gb[1]
 assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254
 assert np.array_equal(a[yy,xx],im[sy,sx]),s['sourceId']
def save(arr,ip,box,name):
 p=O/(name+'.png');mp=O/(name+'.source-id.png');Image.fromarray(arr).save(p);Image.fromarray(ip).save(mp)
 used=set(map(int,np.unique(ip)));ss=[s for s in sources if s['sourceId'] in used]
 wr(O/(name+'.assembly.json'),{'candidate':{'file':str(p),'sha256':sha(p)},'sourceIdMap':{'file':str(mp),'sha256':sha(mp)},'globalCoreBox':box,'sources':ss,'proof':{'pixels':ip.size,'mismatches':0},'formalAccepted':False,'status':'candidate-pending-visual-repairs','composition':{'nativeOnly':True,'resample':False,'blend':False}})
save(a,ids,[3981,20365,8307,24691],'extended')
core=a[115:4211,115:4211];mid=ids[115:4211,115:4211];save(core,mid,[4096,20480,8192,24576],'r06_c02.candidate')
wr(O/'seams.json',seams)
pre=Image.fromarray(core);pre.thumbnail((1400,1400));pre.save(O/'overview.preview-only.jpg',quality=94)
for r in range(4):
 for c in range(4):Image.fromarray(core[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(Q/f'core-{r+1}-{c+1}.png')
for j in range(1,4):
 for k in range(4):
  Image.fromarray(core[k*1024:(k+1)*1024,j*1024-240:j*1024+240]).save(Q/f'v{j}-{k+1}.png')
  Image.fromarray(core[j*1024-240:j*1024+240,k*1024:(k+1)*1024]).save(Q/f'h{j}-{k+1}.png')
for r in range(1,4):
 for c in range(1,4):Image.fromarray(core[r*1024-300:r*1024+300,c*1024-300:c*1024+300]).save(Q/f'junction-{r}-{c}.png')
for k in range(4):
 Image.fromarray(a[0:480,115+k*1024:115+(k+1)*1024]).save(Q/f'north-{k+1}.png')
 Image.fromarray(a[115+k*1024:115+(k+1)*1024,-480:]).save(Q/f'east-{k+1}.png')
print(json.dumps({'candidate':str(O/'r06_c02.candidate.png'),'sources':len(sources),'nativePixels':ids.size,'mismatches':0}))
