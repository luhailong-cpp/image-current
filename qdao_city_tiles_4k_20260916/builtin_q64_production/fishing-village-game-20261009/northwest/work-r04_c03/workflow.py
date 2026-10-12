from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
sys.dont_write_bytecode=True
WORK=Path(__file__).resolve().parent
ROOT=WORK.parent
PROJECT=Path('D:/work/image')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ident(sr,sc,v):return f'r04_c03_s{sr:02d}_s{sc:02d}_v{v:02d}'
def boxes(sr,sc):
 x,y=8192+(sc-1)*1024,12288+(sr-1)*1024
 return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def selected(sr,sc):
 p=WORK/'selections'/f's{sr:02d}_s{sc:02d}.json'
 return read(p)['file'] if p.exists() else None
def prepare(sr,sc,v):
 name=ident(sr,sc,v);core,box=boxes(sr,sc);con=read(ROOT.parent/'production-contract.json');ref=Path(con['layoutReference']);ob=[q*1254/57344 for q in box]
 im=Image.open(ref).transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
 refs=[{'file':str(ref),'sha256':sha(ref),'role':'global layout-only'}]
 ns=[]
 for rr,cc,role in [(sr,sc-1,'west'),(sr,sc+1,'east'),(sr+1,sc,'south'),(sr-1,sc,'north')]:
  if rr==0:
   pp=read(WORK/'plan.json')['northBoundary'][sc-1]['file']
  else:pp=selected(rr,cc)
  if not pp:continue
  p=Path(pp);r=read(str(p)+'.generation.json');bb=r['globalNativeBox']
  inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
  if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
  src=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]];dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]]
  im.paste(Image.open(p).crop(src),tuple(dst[:2]));entry={'file':str(p),'sha256':sha(p),'role':role+' exact unscaled native neighbor','sourceCrop':src,'destinationBox':dst};refs.append(entry);ns.append(entry)
 out=WORK/'guides'/f'{name}.positional.png';im.save(out)
 rec={'file':str(out),'sha256':sha(out),'role':'layout-only fuzzy pixels plus exact listed native neighbor strips; never final pixels','operation':'fractional layout extent crop plus integer native overlap pastes; no feather/resizing native','globalCoreBox':core,'globalNativeBox':box,'overviewFractionalBox':ob,'nativeCoreCropBox':[115,115,1139,1139],'derivedFrom':refs,'neighbors':ns}
 write(str(out)+'.derivation.json',rec);print(json.dumps(rec))
def record(name):
 q=read(WORK/'receipts'/f'{name}.request.json');r=read(WORK/'receipts'/f'{name}.receipt.json');p=ROOT/'native'/f'{name}.png';shutil.copy2(r['originalFile'],p);im=Image.open(p);sr,sc=[int(v[1:]) for v in name.split('_')[2:4]];core,box=boxes(sr,sc)
 g={'file':str(p),'sha256':sha(p),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(PROJECT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'evidence':{'receipt':str(WORK/'receipts'/f'{name}.receipt.json'),'request':str(WORK/'receipts'/f'{name}.request.json'),'fields':['output_hint']},'prompt':q['promptFile'],'references':[{'file':f,'sha256':sha(f),'role':q['referenceRoles'][i]} for i,f in enumerate(q['referenced_image_paths'])],'globalCoreBox':core,'globalNativeBox':box,'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'status':'candidate-pending-seam-QA'}
 write(str(p)+'.generation.json',g)
 if im.size!=(1254,1254):raise RuntimeError('Native size differs; coverage must be replanned without resize')
 write(WORK/'selections'/f's{sr:02d}_s{sc:02d}.json',{'file':str(p),'sha256':sha(p),'row':sr,'column':sc,'status':'candidate-pending-seam-QA'})
 print(json.dumps({'file':str(p),'nativePixels':im.size,'sha256':sha(p)}))
if __name__=='__main__':
 a=sys.argv
 if a[1]=='prepare':prepare(*map(int,a[2:5]))
 elif a[1]=='record':record(a[2])

