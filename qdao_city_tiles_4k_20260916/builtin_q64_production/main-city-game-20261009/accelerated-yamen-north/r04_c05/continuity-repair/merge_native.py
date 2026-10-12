from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np,json,hashlib,sys
D=Path(__file__).parent; T=D.parent; ROOT=T.parent
sys.path.insert(0,str(ROOT));import pipeline
O=D/'merged-v1';O.mkdir(exist_ok=False)
P=1254;S=1024;V=230;E=4326
# 4*1024 + two115-pixel exterior halos =4326.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def edges(a,b):
 def edge(v):
  f=v.astype(np.float32);g=np.zeros(f.shape[:2],np.float32)
  g[:,1:]=np.maximum(g[:,1:],np.max(abs(f[:,1:]-f[:,:-1]),2))
  g[1:]=np.maximum(g[1:],np.max(abs(f[1:]-f[:-1]),2));return g
 m=(np.maximum(edge(a),edge(b))>26).astype(np.uint8)*255
 return np.asarray(Image.fromarray(m).filter(ImageFilter.MaxFilter(11)))>0
def alpha_join(a,b):
 seam=pipeline.minimum_seam(a,b);xx=np.arange(a.shape[1])[None,:]
 binary=(xx>=seam[:,None]).astype(np.float32);soft=smooth((xx-seam[:,None]+64)/128)
 # Only feather similarly colored material, protect high-contrast geometry.
 diff=np.max(abs(a.astype(float)-b.astype(float)),axis=2)
 material=(~edges(a,b))&(diff<70)
 al=np.where(material,soft,binary).astype(np.float32)
 return al,seam
sel=json.loads((T/'pipeline-selection.json').read_text());sources=[];arr=[];hw=[];rows=[];joins=[]
for r in range(4):
 strip=None
 for c in range(4):
  pid=f's{r+1:02d}_{c+1:02d}';p=Path(sel[pid]);a=np.asarray(Image.open(p).convert('RGB'))
  assert a.shape==(P,P,3)
  sources.append({'sourceId':len(arr)+1,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','offsetXY':[c*S,r*S],'worldBox':[16269+c*S,12173+r*S,17523+c*S,13427+r*S]})
  arr.append(a);w=np.ones((P,P),np.float32)
  if strip is None:strip=a.copy()
  else:
   al,seam=alpha_join(strip[:,-V:],a[:,:V]);hw[-1][:,-V:] *= 1-al;w[:,:V]=al
   overlap=np.rint(strip[:,-V:]*(1-al[:,:,None])+a[:,:V]*al[:,:,None]).astype(np.uint8)
   strip=np.concatenate([strip[:,:-V],overlap,a[:,V:]],axis=1)
   joins.append({'axis':'x','row':r+1,'column':c+1,'seamPath':seam.tolist(),'bandWidth':128,'geometryProtection':'11px dilation of >26 RGB neighbor gradient; max RGB source delta<70'})
  hw.append(w)
 rows.append(strip)
rw=[np.ones((P,E),np.float32) for _ in range(4)];whole=rows[0]
for r in range(1,4):
 al,seam=alpha_join(whole[-V:].transpose(1,0,2),rows[r][:V].transpose(1,0,2));al=al.T
 rw[r-1][-V:] *=1-al;rw[r][:V]=al
 overlap=np.rint(whole[-V:]*(1-al[:,:,None])+rows[r][:V]*al[:,:,None]).astype(np.uint8)
 whole=np.concatenate([whole[:-V],overlap,rows[r][V:]],axis=0)
 joins.append({'axis':'y','nextRow':r+1,'seamPath':seam.tolist(),'bandWidth':128})
weights=[hw[i]*rw[i//4][:,i%4*S:i%4*S+P] for i in range(16)]
def render_float():
 im=np.zeros((E,E,3),np.float32)
 for s,a,w in zip(sources,arr,weights):
  x,y=s['offsetXY'];im[y:y+P,x:x+P]+=a*w[:,:,None]
 return np.clip(np.rint(im),0,255).astype(np.uint8)
whole=render_float();Image.fromarray(whole[115:4211,115:4211]).save(O/'material-only-candidate.png')
# Imagegen repaired center holds equal native coordinates; no transform.
rp=D/'shaft-cord-v2/native.png';repair=np.asarray(Image.open(rp).convert('RGB'));x,y=895,512
old=whole[y:y+P,x:x+P]
top=180+pipeline.minimum_seam(old[180:400].transpose(1,0,2),repair[180:400].transpose(1,0,2))
bottom=810+pipeline.minimum_seam(repair[810:1000].transpose(1,0,2),old[810:1000].transpose(1,0,2))
yy=np.arange(P)[:,None];xx=np.arange(P)[None,:]
binary=((yy>=top[None,:])&(yy<bottom[None,:])).astype(np.float32)
soft=smooth((yy-top[None,:]+64)/128)*smooth((bottom[None,:]-yy+64)/128)
safe=(~edges(old,repair))&(np.max(abs(old.astype(float)-repair.astype(float)),2)<70)
al=np.where(safe,soft,binary)
# Fixed spatial support only around shaft and bead chain; no full-frame replacement.
shaft=smooth((xx-40)/40)*smooth((690-xx)/50)
beads=smooth((xx-1020)/50)*smooth((1254-xx)/30)*smooth((yy-450)/60)*smooth((920-yy)/60)
al=(al*np.maximum(shaft,beads)).astype(np.float32)
for s,w in zip(sources,weights):
 sx,sy=s['offsetXY'];l=max(sx,x);t=max(sy,y);rr=min(sx+P,x+P);bb=min(sy+P,y+P)
 if rr>l and bb>t:w[t-sy:bb-sy,l-sx:rr-sx]*=1-al[t-y:bb-y,l-x:rr-x]
sources.append({'sourceId':17,'file':str(rp),'sha256':sha(rp),'generationRecord':str(rp)+'.generation.json','offsetXY':[x,y],'worldBox':[17164,12685,18418,13939]});arr.append(repair);weights.append(al)
# Archive compact local weight maps, exact uint16 denominator and reconstruction.
den=np.zeros((E,E),np.uint32);dom=np.zeros((E,E),np.uint8);maxw=np.zeros((E,E),np.float32);qs=[]
for i,(s,w) in enumerate(zip(sources,weights)):
 sx,sy=s['offsetXY'];q=np.floor(w*65535).astype(np.uint16);qs.append(q);den[sy:sy+P,sx:sx+P]+=q
 hit=w>maxw[sy:sy+P,sx:sx+P];dom[sy:sy+P,sx:sx+P][hit]=i;maxw[sy:sy+P,sx:sx+P][hit]=w[hit]
rem=65535-den
assert int(rem.max())<32
sumq=np.zeros((E,E),np.uint32);num=np.zeros((E,E,3),np.uint32);count=np.zeros((E,E),np.uint8);maps=[]
for i,(s,a,q) in enumerate(zip(sources,arr,qs)):
 sx,sy=s['offsetXY'];hit=dom[sy:sy+P,sx:sx+P]==i;q[hit]+=rem[sy:sy+P,sx:sx+P][hit].astype(np.uint16)
 sumq[sy:sy+P,sx:sx+P]+=q;num[sy:sy+P,sx:sx+P]+=q.astype(np.uint32)[:,:,None]*a
 count[sy:sy+P,sx:sx+P]+=(q>0).astype(np.uint8)
 wp=O/f'source-{i+1:02d}-weights-u16.png';Image.fromarray(q).save(wp);maps.append({'sourceId':i+1,'file':str(wp),'sha256':sha(wp),'pixels':[P,P],'offsetXY':s['offsetXY'],'denominator':65535})
assert np.all(sumq==65535)
whole=np.rint(num.astype(np.float64)/65535).astype(np.uint8)
ext=O/'extended-native-context.png';Image.fromarray(whole).save(ext);cand=O/'candidate-4096.png';Image.fromarray(whole[115:4211,115:4211]).save(cand)
Image.fromarray((count>1).astype(np.uint8)*255).save(O/'blended-pixel-mask.png')
newsel={};derived=[]
for r in range(4):
 for c in range(4):
  pid=f's{r+1:02d}_{c+1:02d}';p=O/f'{pid}-derived.png';Image.fromarray(whole[r*S:r*S+P,c*S:c*S+P]).save(p)
  rec={'recordType':'multi_source_native_resolution_weighted_derivation','nativeToolOutput':False,'actualModel':None,'tool':None,'route':'derived_from_builtin_native_pixels','width':P,'height':P,'sha256':sha(p),'file':str(p),'worldBoxWithHalo':[16269+c*S,12173+r*S,17523+c*S,13427+r*S],'resizedAfterGeneration':False,'finalArtUpscaled':False,'resampled':False,'blended':True,'colorCorrected':False,'cropBoxInExtendedNative':[c*S,r*S,c*S+P,r*S+P],'derivationManifest':str(O/'derivation.json'),'formalAccepted':False}
  p.with_suffix('.png.generation.json').write_text(json.dumps(rec,indent=2));newsel[pid]=str(p);derived.append(rec)
M={'recordType':'multi_source_native_resolution_weighted_derivation','nativeToolOutput':False,'pixels':[E,E],'worldBox':[16269,12173,20595,16499],'file':str(ext),'sha256':sha(ext),'candidate':str(cand),'candidateSha256':sha(cand),'sources':sources,'sourceWeightMaps':maps,'joins':joins,'repairJoin':{'sourceId':17,'topPath':top.tolist(),'bottomPath':bottom.tolist(),'materialBandWidth':128,'sameWorldCoordinates':True},'resampled':False,'blended':True,'colorCorrected':False,'weightedReconstruction':'round(sum(original RGB same-world-coordinate * archived uint16 coefficient)/65535)','weightsSum65535':True,'blendedPixelCount':int((count>1).sum()),'derivedPatches':derived,'overlaps230pxExact':True,'formalAccepted':False}
(O/'derivation.json').write_text(json.dumps(M,indent=2))
(O/'selection-before.json').write_text(json.dumps(sel,indent=2));(O/'selection-after.json').write_text(json.dumps(newsel,indent=2))
for r in range(4):
 for c in range(4):
  a=np.asarray(Image.open(newsel[f's{r+1:02d}_{c+1:02d}']))
  if c<3:assert np.array_equal(a[:,-V:],np.asarray(Image.open(newsel[f's{r+1:02d}_{c+2:02d}']))[:,:V])
  if r<3:assert np.array_equal(a[-V:],np.asarray(Image.open(newsel[f's{r+2:02d}_{c+1:02d}']))[:V])
# No shared status touched. Selection switch only after independent visual review.
print(json.dumps({'directory':str(O),'candidate':str(cand),'blendedPixelCount':M['blendedPixelCount'],'sourceCount':len(sources),'overlapsExact':True,'sourceWeightsExact':True}))

