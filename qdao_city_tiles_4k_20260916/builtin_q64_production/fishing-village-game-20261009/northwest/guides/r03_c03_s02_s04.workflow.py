from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def boxes(sr):
 x,y=11264,8192+(sr-1)*1024
 return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def prepare(sr,north,west=''):
 core,box=boxes(sr);con=read(ROOT.parent/'production-contract.json');lp=Path(con['layoutReference']);ob=[v*1254/57344 for v in box]
 im=Image.open(lp).transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
 refs=[{'file':str(lp),'sha256':sha(lp),'role':'layout-only global map'}]
 for ident,role in [(west,'west native neighbor'),(north,'north native neighbor')]:
  if not ident:continue
  p=ROOT/'native'/f'{ident}.png';r=read(str(p)+'.generation.json');bb=r['globalNativeBox']
  inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
  src=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]]
  dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]]
  im.paste(Image.open(p).crop(src),tuple(dst[:2]));refs.append({'file':str(p),'sha256':sha(p),'role':role,'sourceCrop':src,'destinationBox':dst,'globalIntersection':inter})
 p=ROOT/'guides'/f'r03_c03_s{sr:02d}_s04.layout-and-native-overlap.png';im.save(p)
 rec={'file':str(p),'sha256':sha(p),'role':'layout-only fuzzy image with exact native neighbor overlap strips; not final art','operation':'fractional layout extent and unscaled native overlap paste; no feather','derivedFrom':refs,'globalNativeBox':box,'globalCoreBox':core,'nativeCoreCropBox':[115,115,1139,1139],'overviewFractionalBox':ob};write(str(p)+'.derivation.json',rec)
 print(json.dumps(rec))
def record(ident):
 sr=int(ident.split('_')[2][1:]);core,box=boxes(sr);r=read(ROOT/'receipts'/f'{ident}.receipt.json');q=read(ROOT/'receipts'/f'{ident}.request.json');p=ROOT/'native'/f'{ident}.png';shutil.copy2(r['originalFile'],p);im=Image.open(p)
 rec={'file':str(p),'sha256':sha(p),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read('D:/work/image/config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'evidence':{'receipt':str(ROOT/'receipts'/f'{ident}.receipt.json'),'request':str(ROOT/'receipts'/f'{ident}.request.json'),'fields':['output_hint']},'prompt':q['promptFile'],'references':[{'file':f,'sha256':sha(f),'role':q['referenceRoles'][i]} for i,f in enumerate(q['referenced_image_paths'])],'globalCoreBox':core,'globalNativeBox':box,'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'status':'candidate-pending-seam-review'}
 write(str(p)+'.generation.json',rec)
 print(json.dumps({'file':str(p),'size':im.size,'sha256':sha(p)}))
 if im.size!=(1254,1254):raise RuntimeError('Native size differs; stop/replan coverage')
def qa(ident,north,west=''):
 im=Image.open(ROOT/'native'/f'{ident}.png')
 for nid,axis in [(north,'north'),(west,'west')]:
  if not nid:continue
  n=Image.open(ROOT/'native'/f'{nid}.png');out=Image.new('RGB',(1254,400) if axis=='north' else (400,1254))
  if axis=='north':out.paste(n.crop((0,939,1254,1139)),(0,0));out.paste(im.crop((0,115,1254,315)),(0,200))
  else:out.paste(n.crop((939,0,1139,1254)),(0,0));out.paste(im.crop((115,0,315,1254)),(200,0))
  p=ROOT/'qa'/f'{ident}.{axis}-seam-100pct.png';out.save(p)
  write(str(p)+'.derivation.json',{'file':str(p),'sha256':sha(p),'operation':'native unscaled hard seam crop; join at 200px; no feather','derivedFrom':[{'file':str(ROOT/'native'/f'{nid}.png'),'sha256':sha(ROOT/'native'/f'{nid}.png')},{'file':str(ROOT/'native'/f'{ident}.png'),'sha256':sha(ROOT/'native'/f'{ident}.png')}]})
a=sys.argv
if a[1]=='prepare':prepare(int(a[2]),*a[3:])
elif a[1]=='record':record(a[2])
elif a[1]=='qa':qa(*a[2:])

