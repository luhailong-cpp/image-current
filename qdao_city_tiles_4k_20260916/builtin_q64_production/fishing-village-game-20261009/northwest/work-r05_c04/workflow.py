from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
import numpy as np
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;T='r05_c04';OX,OY=12288,16384
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in ['guides','receipts','prompts','qa','tiles','selections']:(W/d).mkdir(parents=True,exist_ok=True)
NEIGHBORS=[B/'delivery-2x2/stage-v4/r04_c04.assembly.json',B/'work-r05_c03/final-v1/assembly.json']
def sample(ap,box):
 a=read(ap);bb=a['globalCoreBox'];ids=np.asarray(Image.open(a['sourceIdMap']['file']));yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]]
 cy=np.clip(yy-bb[1],0,ids.shape[0]-1);cx=np.clip(xx-bb[0],0,ids.shape[1]-1);chosen=ids[cy,cx]
 valid=(xx>=bb[0]-115)&(xx<bb[2]+115)&(yy>=bb[1]-115)&(yy<bb[3]+115)
 arr=np.zeros((*xx.shape,3),np.uint8);covered=np.zeros(xx.shape,bool);sidmap=np.zeros(xx.shape,np.uint16)
 for s in a['sources']:
  sid=s.get('sourceId',s.get('jointSourceId'));g=s['globalNativeBox'];m=valid&(chosen==sid)&(xx>=g[0])&(xx<g[2])&(yy>=g[1])&(yy<g[3])
  if not m.any():continue
  assert sha(s['file'])==s['sha256'];im=np.asarray(Image.open(s['file']).convert('RGB'));arr[m]=im[yy[m]-g[1],xx[m]-g[0]];covered|=m;sidmap[m]=sid
 return arr,covered,sidmap,a
def boxes(r,c):
 x,y=OX+(c-1)*1024,OY+(r-1)*1024;return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def selected(r,c):
 p=W/'selections'/f's{r:02d}_s{c:02d}.json';return Path(read(p)['file']) if p.exists() else None
def prepare(r,c,v):
 id=f'{T}_s{r:02d}_s{c:02d}_v{v:02d}';core,box=boxes(r,c);con=read(B.parent/'production-contract.json');ref=Path(con['layoutReference'])
 guide=np.asarray(Image.open(ref).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in box),resample=Image.Resampling.BICUBIC)).copy();der=[]
 for ap in NEIGHBORS:
  a,m,sidmap,rec=sample(ap,box)
  if m.any():guide[m]=a[m];der.append({'assembly':str(ap),'sha256':sha(ap),'nativePixelsPasted':int(m.sum()),'method':'exact integer native source-ID global lookup; only halo ownership uses nearest edge source ID'})
 for rr,cc,role in [(r,c-1,'west'),(r,c+1,'east'),(r+1,c,'south'),(r-1,c,'north')]:
  p=selected(rr,cc)
  if not p:continue
  g=read(str(p)+'.generation.json')['globalNativeBox'];it=[max(box[0],g[0]),max(box[1],g[1]),min(box[2],g[2]),min(box[3],g[3])]
  if it[2]<=it[0] or it[3]<=it[1]:continue
  dst=[it[0]-box[0],it[1]-box[1],it[2]-box[0],it[3]-box[1]];src=[it[0]-g[0],it[1]-g[1],it[2]-g[0],it[3]-g[1]]
  guide[dst[1]:dst[3],dst[0]:dst[2]]=np.asarray(Image.open(p).convert('RGB').crop(src));der.append({'file':str(p),'sha256':sha(p),'role':role,'sourceCrop':src,'destinationBox':dst})
 out=W/'guides'/(id+'.positional.png');Image.fromarray(guide).save(out);write(str(out)+'.derivation.json',{'file':str(out),'sha256':sha(out),'globalCoreBox':core,'globalNativeBox':box,'layout':str(ref),'layoutSha256':sha(ref),'neighbors':der,'role':'position-only fuzzy layout plus exact native neighbors; no guide pixels in final'})
 print(json.dumps({'id':id,'guide':str(out),'globalNativeBox':box,'neighbors':len(der)}))
def request(r,c,v,detailfile):
 id=f'{T}_s{r:02d}_s{c:02d}_v{v:02d}';core,box=boxes(r,c);con=read(B.parent/'production-contract.json');guide=W/'guides'/(id+'.positional.png')
 prefix='Use case native map detail. IMAGE1 is the ONLY crop target, output exactly opaque 1254x1254 at its exact framing, scale and camera. Keep the sharp existing neighbor strips and continue every silhouette and material boundary smoothly into the blurry area. Replace blurred pixels with fresh crisp original detail. Never zoom out or reframe. IMAGE2 whole village is layout identification only; IMAGE3 independent material-painting reference only, never import its structures; IMAGE4 primary approved rounded refined Q Daoist style. Match the sharp native strips, bright warm daylight, natural rounded materials, soft shadow. No gritty cracks, repeated fractures, plastic gloss, flat black silhouette, UI, characters, text, grid or borders. Low-resolution overview supplies shape only and must never become final pixels. '
 detail=Path(detailfile).read_text(encoding='utf-8');prompt=prefix+'Exact native global frame '+str(box)+'. '+detail
 pf=W/'prompts'/(id+'.prompt.txt');pf.write_text(prompt,encoding='utf-8');refs=[str(guide),con['layoutReference'],con['detailStyleReference'],con['primaryStyleReference']]
 q={'id':id,'createdAt':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(pf),'referenced_image_paths':refs,'referenceRoles':['native positional guide + exact neighbor pixels','layout only','material only','primary approved style'],'referenceHashes':[sha(p) for p in refs],'globalCoreBox':core,'globalNativeBox':box,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
 write(W/'receipts'/(id+'.request.json'),q);print(json.dumps({'id':id,'request':str(W/'receipts'/(id+'.request.json'))}))
def record(id):
 q=read(W/'receipts'/(id+'.request.json'));r=read(W/'receipts'/(id+'.receipt.json'));p=B/'native'/(id+'.png')
 assert not p.exists();shutil.copy2(r['originalFile'],p);im=Image.open(p);assert im.size==(1254,1254)
 g={'file':str(p),'sha256':sha(p),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read('D:/work/image/config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'evidence':{'receipt':str(W/'receipts'/(id+'.receipt.json')),'request':str(W/'receipts'/(id+'.request.json')),'fields':['output_hint']},'prompt':q['promptFile'],'references':[{'file':f,'sha256':sha(f),'role':q['referenceRoles'][i]} for i,f in enumerate(q['referenced_image_paths'])],'globalCoreBox':q['globalCoreBox'],'globalNativeBox':q['globalNativeBox'],'nativeScaleResampled':False,'status':'candidate-pending-full-tile-QA'}
 write(str(p)+'.generation.json',g)
 sr,sc=[int(v[1:]) for v in id.split('_')[2:4]];write(W/'selections'/f's{sr:02d}_s{sc:02d}.json',{'file':str(p),'sha256':sha(p),'row':sr,'column':sc,'status':'candidate-pending-full-tile-QA'})
 print(json.dumps({'file':str(p),'sha256':sha(p)}))
if __name__=='__main__':
 a=sys.argv
 if a[1]=='prepare':prepare(*map(int,a[2:5]))
 elif a[1]=='request':request(*map(int,a[2:5]),a[5])
 elif a[1]=='record':record(a[2])
 elif a[1]=='overview':
  con=read(B.parent/'production-contract.json');Image.open(con['layoutReference']).transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in [OX,OY,OX+4096,OY+4096]),resample=Image.Resampling.BICUBIC).save(W/'guides/r05_c04.layout-only.png')

