from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys,shutil,importlib.util
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('previous',ROOT/'workflow.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
TILES=['r03_c10','r03_c11','r04_c10','r04_c11','r05_c10','r05_c11']
NEW=['r05_c10','r05_c11'];old.TILES=TILES
FINAL={'r03_c10':4,'r03_c11':2,'r04_c10':2,'r04_c11':3}
read=old.read;sha=old.sha
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.tmp');temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(p)
def setup():
 for t in NEW:
  for d in ['guides','native','records','qa','candidate']:(ROOT/t/d).mkdir(parents=True,exist_ok=True)
 e=ROOT/'extension-20261011';e.mkdir(exist_ok=True)
 source=old.CONTRACT['layoutReference'];im=Image.open(source)
 for name,box,size in [('south-two-layout-only',[36864,16384,45056,20480],(1254,627)),('six-region-layout-only',[36864,8192,45056,20480],(836,1254))]:
  im.transform(size,Image.Transform.EXTENT,[v*1254/57344 for v in box],Image.Resampling.NEAREST).save(e/(name+'.png'))
 write(e/'coordinate-plan.json',{'newTiles':NEW,'allAssignedTiles':TILES,'newGlobalPixelBox':[36864,16384,45056,20480],'sixTileGlobalPixelBox':[36864,8192,45056,20480],'corePixels':1024,'haloPixels':115,'expectedNativePixels':1254,'preservedFinalVersions':FINAL,'source':source,'sourceSha256':sha(source),'overviewPixelsFinal':False})
 for t in NEW:update(t)
def update(t):
 selected=[];nextp=None
 for r in range(1,5):
  for c in range(1,5):
   if (ROOT/t/'records'/f'p{r}{c}.selection.json').exists():selected.append(f'p{r}{c}')
   elif nextp is None:nextp=f'p{r}{c}'
 write(ROOT/t/'progress.json',{'updatedAt':old.now(),'tile':t,'status':'native_generation_in_progress','selectedNativeCoreCount':len(selected),'requiredNativeCoreCount':16,'selected':selected,'nextCoordinate':nextp,'formalAccepted':False,'actualModel':None,'actualQuality':None,'builtinOnly':True})
def prepare(t,r,c,v=1):
 assert t in NEW
 old.prepare(t,r,c,v)
 guide=ROOT/t/'guides'/f'p{r}{c}-v{v}-positional.png';data=read(guide.with_suffix('.derivation.json'));box=data['globalNativeBox'];im=Image.open(guide).convert('RGB')
 for tile,version in FINAL.items():
  rr,cc=int(tile[1:3]),int(tile[5:7]);bb=[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096]
  inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
  if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
  p=ROOT/tile/'candidate'/f'{tile}-4096-candidate-v{version}.png';crop=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]];at=[inter[0]-box[0],inter[1]-box[1]]
  im.paste(Image.open(p).crop(crop),at);data['nativeOverlaps'].append({'file':str(p),'sha256':sha(p),'sourceCrop':crop,'pasteAt':at,'role':'LATEST repaired final candidate; overrides outdated original native pixels'})
 # The final net repair also provides a real native continuation below r04_c11.
 p=ROOT/'r04_c11/repairs/net-lower-v1/native-result.png';maskp=p.parent/'native-alpha-mask.png';bb=[41472,15245,42726,16499]
 inter=[max(box[0],bb[0]),max(box[1],16384),min(box[2],bb[2]),min(box[3],bb[3])]
 if inter[2]>inter[0] and inter[3]>inter[1]:
  crop=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]];at=[inter[0]-box[0],inter[1]-box[1]]
  im.paste(Image.open(p).crop(crop),at,Image.open(maskp).crop(crop));data['nativeOverlaps'].append({'file':str(p),'sha256':sha(p),'sourceCrop':crop,'pasteAt':at,'maskFile':str(maskp),'maskSha256':sha(maskp),'role':'true repaired native south halo of existing net; no resampling'})
 im.save(guide);write(guide.with_suffix('.derivation.json'),data)
 print(json.dumps({'finalGuide':str(guide),'nativeContexts':len(data['nativeOverlaps'])}))
def record(t,r,c,v,src):
 assert t in NEW
 old.update=lambda:update(t)
 old.record(t,r,c,v,src)
if __name__=='__main__':
 a=sys.argv
 if a[1]=='setup':setup()
 elif a[1]=='prepare':prepare(a[2],*map(int,a[3:]))
 elif a[1]=='record':record(a[2],*map(int,a[3:6]),a[6])
 elif a[1]=='assemble':
  assert a[2] in NEW;old.assemble(a[2])
 elif a[1]=='update':update(a[2])
