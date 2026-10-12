from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,shutil,re
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r02_c03'
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009')
REFS=[P/'donghai-natural-stone-clear-routes-v10.png',P/'donghai-natural-stone-detail-v1.png',P/'user-references-20261009/mail-daoist-style.jpg']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,a):Path(p).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
for d in ['native','guides','receipts','prompts','qa','tiles']: (W/d).mkdir(exist_ok=True)
def name(r,c,v=1):return f'r02_c03_s{r:02d}_s{c:02d}_v{v:02d}'
def native(r,c):
 p=W/'native'/(name(r,c)+'.png')
 if p.exists():return p
 p=B/'native'/(name(r,c)+'.png')
 return p if p.exists() else None
def box(r,c):
 x=8192+(c-1)*1024;y=4096+(r-1)*1024
 return [x-115,y-115,x+1139,y+1139]
def southern_context():
 p=W/'guides/current-r03-north-context.png'
 if p.exists():return p
 d=B/'work-r03_c02/west-final';m=read(d/'final-joint.assembly.json');a=np.asarray(Image.open(d/'final-pair.png'));ids=np.asarray(Image.open(d/'final-pair.source-id.png'));x0=8077-4096;x1=12403-4096
 out=np.zeros((1254,4326,3),dtype=np.uint8);gy,gx=np.indices(out.shape[:2]);gx+=8077;gy+=8077
 oi=ids[np.clip(gy-8192,0,4095),np.clip(gx-4096,0,8191)]
 for k in np.unique(oi):
  s=m['sources'][str(k)];im=np.asarray(Image.open(s['file']));yy,xx=np.nonzero(oi==k);sx=gx[yy,xx]-s['globalNativeBox'][0];sy=gy[yy,xx]-s['globalNativeBox'][1]
  assert np.all((sx>=0)&(sx<1254)) and np.all((sy>=0)&(sy<1254))
  out[yy,xx]=im[sy,sx]
 Image.fromarray(out).save(p);write(str(p)+'.derivation.json',{'globalBox':[8077,8077,12403,9331],'sourceAssembly':str(d/'final-joint.assembly.json'),'sourceAssemblySHA256':sha(d/'final-joint.assembly.json'),'nativeScale':1,'upperHalo':'same source selected in first current tile row, native-coordinate continuation','guideOnly':True})
 return p
def prepare(r,c):
 n=name(r,c);b=box(r,c);lay=Image.open(REFS[0]);fraction=[v*1254/57344 for v in b];im=lay.transform((1254,1254),Image.Transform.EXTENT,fraction,Image.Resampling.BICUBIC);neighbors=[]
 for rr,cc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
  p=native(rr,cc) if 1<=rr<=4 and 1<=cc<=4 else None
  if p:
   nb=box(rr,cc);inter=[max(b[0],nb[0]),max(b[1],nb[1]),min(b[2],nb[2]),min(b[3],nb[3])]
   if inter[2]>inter[0] and inter[3]>inter[1]:
    crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-b[0],inter[1]-b[1]];im.paste(Image.open(p).crop(crop),dest);neighbors.append({'file':str(p),'sha256':sha(p),'crop':crop,'destination':dest,'role':'actual unscaled existing neighbor'})
 if r==4:
  p=southern_context();im.paste(Image.open(p).crop(((c-1)*1024,0,(c-1)*1024+1254,230)),(0,1024));neighbors.append({'file':str(p),'sha256':sha(p),'crop':[(c-1)*1024,0,(c-1)*1024+1254,230],'destination':[0,1024],'role':'current accepted r03 south neighbor, exact source pixels'})
 p=W/'guides'/(n+'.guide.png');im.save(p);write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'globalNativeBox':b,'layout':{'file':str(REFS[0]),'sha256':sha(REFS[0]),'fractionalBox':fraction,'guideOnly':True},'neighbors':neighbors,'nativeOutputResampled':False})
 print(json.dumps({'name':n,'guide':str(p),'globalNativeBox':b,'neighbors':neighbors},ensure_ascii=False))
def save(n):
 req=read(W/'receipts'/(n+'.request.json'));rec=read(W/'receipts'/(n+'.receipt.json'));original=Path(re.search(r' as (C:\\[^\n]+?\.png) by default',rec['output_hint']).group(1));p=W/'native'/(n+'.png');shutil.copy2(original,p)
 im=Image.open(p);assert im.size==(1254,1254)
 b=req['globalNativeBox'];g={'file':str(p),'sha256':sha(p),'generatedAt':rec['returnedAt'],'width':1254,'height':1254,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','configSnapshot':read('D:/work/image/config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin exposes no model/quality selectors or actual response metadata; config snapshot is target only.','globalNativeBox':b,'globalCoreBox':[b[0]+115,b[1]+115,b[2]-115,b[3]-115],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'evidence':{'receipt':str(W/'receipts'/(n+'.receipt.json')),'request':str(W/'receipts'/(n+'.request.json'))},'prompt':str(W/'prompts'/(n+'.prompt.txt')),'references':[{'file':p,'sha256':sha(p),'role':role} for p,role in zip(req['referenced_image_paths'],req['referenceRoles'])],'toolOriginal':{'file':str(original),'sha256':sha(original)},'status':'candidate-pending-full-join-review'}
 write(str(p)+'.generation.json',g);print(json.dumps({'file':str(p),'sha256':sha(p),'dimensions':im.size}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
 elif sys.argv[1]=='save':save(sys.argv[2])
