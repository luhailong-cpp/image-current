from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R.parents[1]/'island-game-20261009';Z=P/'northeast'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old={t['tileId']:t for t in read(R/'root-audit-v01/inventory.json')['tiles']};tiles=[];partial={};full={};snaps=[]
O.mkdir(exist_ok=True);(O/'snapshots').mkdir(exist_ok=True)
captured=datetime.now(timezone.utc).isoformat()
for p in sorted(Z.glob('selection-*.json')):
 raw=p.read_bytes();q=json.loads(raw.decode('utf-8-sig'));s=hashlib.sha256(raw).hexdigest();(O/'snapshots'/p.name).write_bytes(raw);snaps.append({'file':p.as_posix(),'sha256':s})
 tid=q['tileId'];matrix=q['cores'];n=sum(bool(x) for row in matrix for x in row);f=Path(q.get('candidatePath',str(Z/'tiles'/f'{tid}.png')))
 t={'tileId':tid,'coreCount':n,'fullCoverage':n==16,'adopted':n==16,'file':f.as_posix() if n==16 else None,'sha256':sha(f) if n==16 else None,'selectedCores':matrix,'evidence':str(O/'snapshots'/p.name),'formalAccepted':False}
 if n==16:
  t['sourcePixelsUnchanged']=tid in old and t['sha256']==old[tid].get('sha256');full[tid]=t
 else:partial[tid]=t
 tiles.append(t)
a=P/'accelerated-northeast-coast/current-selection-20261012.json';q=read(a);snaps.append({'file':a.as_posix(),'sha256':sha(a)})
for c in q['candidates']:
 tid=c['tileId'];s=sha(c['file']);assert s==c['sha256'];tiles.append({'tileId':tid,'coreCount':16,'fullCoverage':True,'adopted':True,'file':c['file'],'sha256':s,'evidence':a.as_posix(),'sourcePixelsUnchanged':s==old[tid]['sha256'],'formalAccepted':False})
# Build global core grid for partials plus exact full candidate neighbors, preserving overlays.
grid={};imgs={};sourcechecks=[]
for tid,t in partial.items():
 tr,tc=int(tid[1:3]),int(tid[5:7]);prior=old.get(tid,{}).get('selectedCores',[[None]*4 for _ in range(4)])
 for r,row in enumerate(t['selectedCores']):
  for c,ident in enumerate(row):
   if not ident:continue
   f=Z/'native'/f'{ident}.png';s=sha(f);q=read(str(f)+'.generation.json');assert q['sha256']==s and q['coreCrop']==[115,115,1139,1139]
   with Image.open(f) as im:assert im.size==(1254,1254)
   pos=((tr-1)*4+r,(tc-1)*4+c);grid[pos]={'tileId':tid,'id':ident,'file':f.as_posix(),'crop':[115,115,1139,1139],'new':ident!=prior[r][c]};sourcechecks.append({'file':f.as_posix(),'sha256':s})
for tid,t in full.items():
 tr,tc=int(tid[1:3]),int(tid[5:7])
 for r in range(4):
  for c in range(4):grid[((tr-1)*4+r,(tc-1)*4+c)]={'tileId':tid,'id':tid+f'/{r+1}{c+1}','file':t['file'],'crop':[c*1024,r*1024,(c+1)*1024,(r+1)*1024],'new':False}
def core(pos):
 e=grid[pos]
 with Image.open(e['file']) as im:return im.crop(e['crop']).convert('RGB')
edges=[];crosses=[]
for pos,e in sorted(grid.items()):
 gr,gc=pos
 for nb,axis in [((gr,gc+1),'v'),((gr+1,gc),'h')]:
  if nb not in grid or not(e['new'] or grid[nb]['new']):continue
  a,b=core(pos),core(nb)
  if axis=='v':
   im=Image.new('RGB',(512,1024));im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0));wb=[(gc+1)*1024-256,gr*1024,(gc+1)*1024+256,(gr+1)*1024]
  else:
   im=Image.new('RGB',(1024,512));im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256));wb=[gc*1024,(gr+1)*1024-256,(gc+1)*1024,(gr+1)*1024+256]
  f=O/f'edge-{gr}-{gc}-{axis}.png';im.save(f);a.close();b.close();im.close();edges.append({'id':f.stem,'file':f.as_posix(),'sha256':sha(f),'axis':axis,'worldBox':wb,'sources':[e,grid[nb]],'status':'pending_visual'})
 for_cross=[pos,(gr,gc+1),(gr+1,gc),(gr+1,gc+1)]
 if all(x in grid for x in for_cross) and any(grid[x]['new'] for x in for_cross):
  im=Image.new('RGB',(512,512))
  for j,x in enumerate(for_cross):
   ci=core(x);cx=768 if j%2==0 else 0;cy=768 if j<2 else 0;im.paste(ci.crop((cx,cy,cx+256,cy+256)),((j%2)*256,(j//2)*256));ci.close()
  f=O/f'cross-{gr}-{gc}.png';im.save(f);im.close();crosses.append({'file':f.as_posix(),'sha256':sha(f),'worldPoint':[(gc+1)*1024,(gr+1)*1024],'status':'pending_visual'})
boards=[]
for axis in ['v','h']:
 es=[e for e in edges if e['axis']==axis]
 for k in range(0,len(es),4):
  chunk=es[k:k+4];im=Image.new('RGB',(2048,1024),(40,40,40))
  for j,e in enumerate(chunk):
   with Image.open(e['file']) as src:im.paste(src,(j*512,0) if axis=='v' else ((j%2)*1024,(j//2)*512))
  f=O/f'board-{axis}-{k//4+1}.png';im.save(f);im.close();boards.append({'file':f.as_posix(),'edgeIds':[e['id'] for e in chunk]})
for k in range(0,len(crosses),8):
 im=Image.new('RGB',(2048,1024),(40,40,40));chunk=crosses[k:k+8]
 for j,e in enumerate(chunk):
  with Image.open(e['file']) as src:im.paste(src,((j%4)*512,(j//4)*512))
 f=O/f'board-cross-{k//8+1}.png';im.save(f);im.close();boards.append({'file':f.as_posix(),'crosses':[e['file'] for e in chunk]})
write(O/'summary.json',{'capturedAtUtc':captured,'tiles':tiles,'selectionSnapshots':snaps,'partialSourceChecks':sourcechecks,'newEdges':edges,'newCrosses':crosses,'boards':boards,'formalAcceptedCount':0,'generationCalls':0,'productionWrites':False})
print(json.dumps({'tiles':[(t['tileId'],t['coreCount']) for t in tiles],'edgeCount':len(edges),'crossCount':len(crosses),'boards':[(Path(b['file']).name,b.get('edgeIds')) for b in boards]}))
