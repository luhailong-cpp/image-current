from pathlib import Path
from PIL import Image
import json,hashlib,sys,shutil,datetime
B=Path(__file__).resolve().parent
R=B.parents[3]
C=R/'qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def box(tile,patch):
 r,c=map(int,[tile[1:3],tile[5:7]]);a,b=map(int,[patch[1:3],patch[4:6]])
 x=(c-1)*4096+(b-1)*1024;y=(r-1)*4096+(a-1)*1024
 return [x-115,y-115,x+1139,y+1139]
contract=read(C/'production-contract.json')
def prepare(tile,patch):
 assert tile in ['r12_c13','r12_c14'] and not (B/'CONFLICT.json').exists()
 t=B/tile
 for d in ['guides','native','records','qa']: (t/d).mkdir(parents=True,exist_ok=True)
 cb=box(tile,patch); im=Image.open(contract['layoutReference']).convert('RGB')
 guide=im.transform((1254,1254),Image.Transform.EXTENT,[cb[0]*im.width/65536,cb[1]*im.height/65536,cb[2]*im.width/65536,cb[3]*im.height/65536],Image.Resampling.NEAREST)
 gp=t/'guides'/f'{patch}-geometry.png';guide.save(gp)
 anchors=[]
 sources=[]
 for tt in ['r12_c13','r12_c14']:
  mp=B/tt/'selected.json'
  if mp.exists():
   for pp,rec in read(mp).items():
    bx=box(tt,pp); sources.append((rec['path'],bx,[bx[0]+115,bx[1]+115,bx[2]-115,bx[3]-115]))
 progress=read(C/'southeast/progress.json')
 for entry in progress['tiles']:
  if entry['tile'] not in ['r13_c13','r13_c14']:continue
  rr,cc=int(entry['tile'][1:3]),int(entry['tile'][5:7]); bx=[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096]
  sources.append((entry['candidate']['path'],bx,bx))
 for path,sb,reliable in sources:
  ib=[max(cb[0],reliable[0]),max(cb[1],reliable[1]),min(cb[2],reliable[2]),min(cb[3],reliable[3])]
  if ib[0]>=ib[2] or ib[1]>=ib[3]:continue
  crop=Image.open(path).convert('RGB').crop((ib[0]-sb[0],ib[1]-sb[1],ib[2]-sb[0],ib[3]-sb[1]))
  guide.paste(crop,(ib[0]-cb[0],ib[1]-cb[1]))
  anchors.append({'path':path,'sha256':sha(path),'worldIntersection':ib,'targetBox':[ib[0]-cb[0],ib[1]-cb[1],ib[2]-cb[0],ib[3]-cb[1]],'nativeCoreOnly':True})
 sp=t/'guides'/f'{patch}-seed.png';guide.save(sp)
 record={'tile':tile,'patch':patch,'worldContextBox':cb,'nativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'geometryGuideOnly':str(gp),'seed':str(sp),'anchors':anchors,'contract':str(C/'production-contract.json'),'layout':contract['layoutReference'],'detail':contract['detailStyleReference'],'createdAt':now()}
 write(t/'records'/f'{patch}-prepared.json',record)
 print(json.dumps(record))
def ingest(tile,patch,source):
 t=B/tile;p=t/'native'/f'{patch}-v01.png';assert not p.exists()
 shutil.copyfile(source,p);im=Image.open(p);assert im.size==(1254,1254),f'Unexpected native size {im.size}'
 rec=read(t/'records'/f'{patch}-prepared.json');rec.update(path=str(p),originalOutput=source,sha256=sha(p),actualDimensions=list(im.size),actualModel=None,modelEvidence='Built-in image_gen did not return model identifier',tool='image_gen.imagegen',resized=False,selectedAt=now(),status='native_saved_pending_visual_review')
 write(t/'records'/f'{patch}-v01.json',rec)
 mp=t/'selected.json';m=read(mp) if mp.exists() else {};m[patch]=rec;write(mp,m)
 write(B/'progress.json',{'updatedAt':now(),'status':'native_production','tiles':{tt:len(read(B/tt/'selected.json')) if (B/tt/'selected.json').exists() else 0 for tt in ['r12_c13','r12_c14']},'formalAccepted':False,'actualModel':None})
 print(json.dumps({'path':str(p),'sha256':rec['sha256'],'nativeDimensions':im.size,'selectedCount':len(m)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
 elif sys.argv[1]=='ingest':ingest(*sys.argv[2:])
