from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,datetime,re
O=Path(__file__).resolve().parent
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
R=O.parent.parent/'northeast'
snap={}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def track(p):
 p=Path(p);s=sha(p);snap[p.as_posix()]=s;return s
def read(p):track(p);return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(im,name,**kw):
 p=O/name;im.save(p);return dict(file=p.as_posix(),sha256=sha(p),dimensions=list(im.size),resized=False,actuallyViewed=False,**kw)
start=now();parent=read(R/'summary.json');t=next(t for t in parent['tiles'] if t['tileId']=='r04_c10');s=read(R/'snapshots/selection-r04_c10.json')
assert s['cores']==t['selectedCores'] and not s['overlays'] and s['candidatePath']==t['file']
assert track(t['file'])==t['sha256'];im=Image.open(t['file']).convert('RGB');assert im.size==(4096,4096)
replay=Image.new('RGB',(4096,4096));sources=[]
for r,row in enumerate(s['cores']):
 for c,ident in enumerate(row):
  p=P/'native'/f'{ident}.png';h=track(p);rec=read(str(p)+'.generation.json')
  assert h==rec['sha256'] and rec['coreCrop']==[115,115,1139,1139] and rec['resizedAfterGeneration'] is False
  assert rec['coreWorldBox']==[36864+c*1024,12288+r*1024,36864+(c+1)*1024,12288+(r+1)*1024]
  with Image.open(p) as core:
   assert core.size==(1254,1254);replay.paste(core.crop((115,115,1139,1139)),(c*1024,r*1024))
  sources.append(dict(id=ident,file=p.as_posix(),sha256=h,nativeDimensions=[1254,1254],coreCrop=rec['coreCrop'],worldBox=rec['coreWorldBox'],actualModel=rec.get('actualModel')))
assert ImageChops.difference(replay,im).getbbox() is None
tiles=[dict(tileId='r04_c10',coreCount=16,fullCoverage=True,adopted=True,file=t['file'],sha256=t['sha256'],dimensions=[4096,4096],selectedCores=s['cores'],sources=sources,replayMatchesCandidate=True,replayPixelCount=16777216,formalAccepted=False,evidence=[],recordDiscrepancy='Frozen selectionIsPartialCandidate remains true although all 16 cores and exact 4096 candidate exist.')]
evidence=[];boards=[]
def board(name,entries,cols):
 w,h=entries[0]['dimensions'];b=Image.new('RGB',(w*cols,h*((len(entries)+cols-1)//cols)))
 for i,e in enumerate(entries):
  with Image.open(e['file']) as ci:b.paste(ci,((i%cols)*w,(i//cols)*h))
 boards.append(save(b,name,panels=[e['file'] for e in entries],operation='exact unscaled pixel paste'))
for ori in ['horizontal','vertical']:
 for n in range(1,4):
  es=[]
  for seg in range(4):
   box=[seg*1024,n*1024-256,(seg+1)*1024,n*1024+256] if ori=='horizontal' else [n*1024-256,seg*1024,n*1024+256,(seg+1)*1024]
   e=save(im.crop(box),f'{ori}-{n}-segment-{seg+1}-100pct.png',kind='internal_seam',orientation=ori,boundary=n,segment=seg+1,tileLocalBox=box,worldBox=[box[0]+36864,box[1]+12288,box[2]+36864,box[3]+12288]);es.append(e);evidence.append(e)
  board(f'{ori}-{n}-board-100pct.png',es,2 if ori=='horizontal' else 4)
crosses=[]
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  e=save(im.crop(box),f'cross-{r}-{c}-100pct.png',kind='internal_cross',row=r,col=c,tileLocalBox=box,worldBox=[box[0]+36864,box[1]+12288,box[2]+36864,box[3]+12288]);crosses.append(e);evidence.append(e)
board('crosses-board-100pct.png',crosses,3)
edges=[]
for side in ['north','east']:
 rp=P/'qa'/f'r04_c10-west-recovery-{side}-border.json';q=read(rp)
 assert q['sources'][0]['sha256']==t['sha256']
 nf=q['sources'][1]['file'];assert track(nf)==q['sources'][1]['sha256'];neighbor=Image.open(nf).convert('RGB');es=[]
 for seg in range(4):
  if side=='north':
   cr=Image.new('RGB',(1024,512));cr.paste(neighbor.crop((seg*1024,3840,(seg+1)*1024,4096)),(0,0));cr.paste(im.crop((seg*1024,0,(seg+1)*1024,256)),(0,256));wb=[36864+seg*1024,12032,36864+(seg+1)*1024,12544]
  else:
   cr=Image.new('RGB',(512,1024));cr.paste(im.crop((3840,seg*1024,4096,(seg+1)*1024)),(0,0));cr.paste(neighbor.crop((0,seg*1024,256,(seg+1)*1024)),(256,0));wb=[40704,12288+seg*1024,41216,12288+(seg+1)*1024]
  e=save(cr,f'{side}-segment-{seg+1}-100pct.png',kind='neighbor_edge',side=side,neighbor=q['neighbor'],segment=seg+1,worldBox=wb);es.append(e);evidence.append(e)
 board(f'{side}-board-100pct.png',es,2 if side=='north' else 4)
 edges.append(dict(side=side,tiles=[q['neighbor'],'r04_c10'] if side=='north' else ['r04_c10',q['neighbor']],sources=q['sources'],segments=es,priorProductionStatus=q['status']))
tiles[0]['evidence']=evidence
write(O/'input-snapshot.json',dict(capturedAtUtc=start,parentSnapshotCapturedAtUtc=parent.get('capturedAtUtc'),files=[dict(file=p,sha256=h) for p,h in snap.items()]))
write(O/'prepared.json',dict(capturedAtUtc=start,tiles=tiles,boards=boards,edges=edges,evidence=evidence,internalSeamCount=24,internalCrossCount=9,neighborEdgeSegmentCount=8,newImageCalls=0,productionWrites=0,gitOperations=0,formalAcceptedCount=0))
print('Exact replay; 24 seams + 9 crosses + 8 neighbor edge segments; 9 unscaled boards prepared')
