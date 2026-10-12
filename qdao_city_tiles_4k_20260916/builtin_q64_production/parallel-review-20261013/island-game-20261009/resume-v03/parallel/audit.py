import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
OUT=BASE/'parallel-review-20261013/island-game-20261009/resume-v03/parallel'
OLD=BASE/'parallel-review-20261013/island-game-20261009/resume-v02/residences'
OUT.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def path(p):
 p=Path(p);return p if p.is_absolute() else ROOT/p
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,d):
 p=OUT/name
 if p.exists():raise RuntimeError('Refuse overwrite '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def info(p):
 p=Path(p);d={'file':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'mtimeNs':p.stat().st_mtime_ns}
 if p.suffix=='.png':
  with Image.open(p) as im:d['dimensions']=list(im.size)
 return d
def pos(stem):
 m=re.search(r'(r\d+_c\d+)_[ps](\d+)_(\d+)',stem)
 return (m[1],int(m[2]),int(m[3])) if m else None

started=now();split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
batches=[b for b in split['batches'] if b['key'] in ['island-west-residences','island-east-residences','island-northwest-east-extension']]
meta={};native={};tile_batch={};selected={};holds={};evidence={};listing={}
def md(p):
 p=Path(p);k=p.as_posix()
 if k not in meta:meta[k]={'source':info(p),'content':read(p)}
 return meta[k]['content']
for batch in batches:
 folder=path(batch['outputDirectory']);k=batch['key']
 for t in batch['tiles']:tile_batch[t]=k
 listing[k]=[p.as_posix() for p in sorted((folder/'native').glob('*.png'))]
 for f in listing[k]:
  p=Path(f);po=pos(p.stem);native[p.stem]={'id':p.stem,'tileId':po[0],'subrow':po[1],'subcolumn':po[2],**info(p),'batch':k}
 if k=='island-east-residences':
  for t in batch['tiles']:
   ss=sorted((folder/'selections'/t).glob('selection-v*.json'))
   if not ss:continue
   p=ss[-1];j=md(p);evidence[t]=[info(p)]
   for coord,v in j['selected'].items():
    st=v['id'];n=native[st]
    assert n['sha256']==v['sha256'] and path(v['file'])==Path(n['file'])
    selected[pos(st)]=st
    if v.get('review'):md(path(v['review']))
 elif k=='island-west-residences':
  c3=sorted(folder.glob('c03-progress-v*.json'))[-1];j=md(c3)
  evidence['r02_c03']=[info(c3)]
  for v in j['selected']:
   st=v['stem'];assert native[st]['sha256']==v['raw']['sha256'];selected[pos(st)]=st;md(path(v['qa']['path']))
  for p in sorted((folder/'qa').glob('*.json')):
   j=md(p);st=j.get('stem','');po=pos(st)
   if not po or po[0] not in ['r02_c02','r02_c04']:continue
   active=j.get('selectedForContinuation',j.get('selectedForContinuedProduction',False))
   if active:
    assert native[st]['sha256']==j.get('sourceSha256',j.get('sha256'))
    if po not in selected or st>selected[po]:selected[po]=st
    evidence.setdefault(po[0],[]).append(info(p))
  p=folder/'qa/c02-geometry-review/continue-repair-result-v01.json';j=md(p)
  evidence.setdefault('r02_c02',[]).append(info(p))
  for v in j['hold']:
   po=pos(v['coordinate']);selected.pop(po,None);holds[po]=v
   if v.get('review'):md(path(v['review']))
  for v in j['continuationSelected']:
   st=v['stem'];assert native[st]['sha256']==v['sha256'];selected[pos(st)]=st
 elif k=='island-northwest-east-extension':
  md(folder/'progress.json')
  for n in [x for x in native.values() if x['batch']==k]:
   p=folder/'receipts'/(n['id']+'.json');j=md(p)
   assert j['sha256']==n['sha256']
   n['recordedStatus']=j['visualStatus'];evidence.setdefault(n['tileId'],[]).append(info(p))

old=read(OLD/'summary.json');oldnative=set(old['currentSelectedNativeIds']+old['currentUnselectedNativeIds'])
oldchecks=read(OLD/'visual-review.json')
reuse=[]
for c in oldchecks['seams']:
 ok=all(Path(s['path']).exists() and sha(s['path'])==s['sha256'] for s in c['sources'])
 reuse.append({'nativeId':c['nativeId'],'neighbor':c['neighbor'],'direction':c['direction'],'reused':ok,'status':c['status'],'finding':c['finding'],'evidence':c['output']['path'],'sources':c['sources']})

tiles=[]
for t,k in sorted(tile_batch.items()):
 ns=[n for n in native.values() if n['tileId']==t];ss=[n for n in ns if selected.get(pos(n['id']))==n['id']]
 matrix=[[None]*4 for _ in range(4)]
 for n in ss:matrix[n['subrow']-1][n['subcolumn']-1]={'id':n['id'],'file':n['file'],'sha256':n['sha256']}
 coords={(n['subrow'],n['subcolumn']) for n in ns}
 tiles.append({'tileId':t,'batch':k,'coreCount':len(ss),'fullCoverage':len(ss)==16,'adopted':False,'file':None,'sha256':None,'evidence':evidence.get(t,[]),'selectedCoreMatrix':matrix,'savedVersionCount':len(ns),'savedUniqueCoreCount':len(coords),'savedFullCoreCoverage':len(coords)==16,'availableNativeIds':[n['id'] for n in ns],'unselectedNativeIds':[n['id'] for n in ns if n not in ss],'missingSelectedCoreCount':16-len(ss),'formalAccepted':False})

# Pin directly adjacent existing tile sources; do not re-audit old interiors.
neighbors={};nwfile=BASE/'island-game-20261009/northwest/current-adopted-20261012.json'
for t in md(nwfile)['tiles']:
 if t['tileId'] in ['r03_c02','r03_c03','r03_c04','r04_c04']:
  v=info(path(t['image']['path']));assert v['sha256']==t['image']['sha256'];neighbors[t['tileId']]=v
old_snap=read(OLD/'snapshot.json')
for t,v in old_snap['neighborSources'].items():
 if t in ['r03_c10','r03_c11','r03_c12','r02_c13']:
  n=info(path(v['path']));assert n['sha256']==v['sha256'];neighbors[t]=n

edges=[];panels=[]
def openim(p):return Image.open(p).convert('RGB')
def edge(id,a,b,boxa,boxb,direction,scope,world):
 im1=openim(a['file']).crop(boxa);im2=openim(b['file']).crop(boxb)
 size=(1024,512) if direction=='south' else (512,1024)
 im=Image.new('RGB',size);im.paste(im1,(0,0));im.paste(im2,(0,256) if direction=='south' else (256,0))
 file=OUT/'crops'/(id+'.png');file.parent.mkdir(exist_ok=True);assert not file.exists();im.save(file)
 v={'id':id,'scope':scope,'direction':direction,'sources':[a,b],'sourceBoxes':[boxa,boxb],'worldBox':world,'output':info(file),'operation':'integer crop/hard join; no scaling or pixel modification','status':'pending_visual_review'}
 edges.append(v);panels.append((v,im))
for (tile,sr,sc),st in sorted(selected.items()):
 if sr!=4:continue
 r=int(tile[1:3]);c=int(tile[5:7]);nt=f'r{r+1:02d}_c{c:02d}'
 if nt not in neighbors:continue
 if any(x['nativeId']==st and x['neighbor']==nt and x['direction']=='south' and x['reused'] for x in reuse):continue
 n=native[st];x=(c-1)*4096+(sc-1)*1024;y=r*4096
 edge(st+'-south-'+nt,n,neighbors[nt],[115,883,1139,1139],[(sc-1)*1024,0,sc*1024,256],'south','selected-core external boundary',[x,y-256,x+1024,y+256])

# Complete saved extension grid is a diagnostic-only candidate: all 24 internal edges and west border.
ext=[n for n in native.values() if n['tileId']=='r03_c05'];grid={(n['subrow'],n['subcolumn']):n for n in ext}
for (r,c),a in sorted(grid.items()):
 x=16384+(c-1)*1024;y=8192+(r-1)*1024
 if (r+1,c) in grid:edge(f'extension-s{r}{c}-south',a,grid[r+1,c],[115,883,1139,1139],[115,115,1139,371],'south','unselected extension internal',[x,y+768,x+1024,y+1280])
 if (r,c+1) in grid:edge(f'extension-s{r}{c}-east',a,grid[r,c+1],[883,115,1139,1139],[115,115,371,1139],'east','unselected extension internal',[x+768,y,x+1280,y+1024])
 if c==1:edge(f'extension-s{r}{c}-west',neighbors['r03_c04'],a,[3840,(r-1)*1024,4096,r*1024],[115,115,371,1139],'east','unselected extension west border',[16128,y,16640,y+1024])

# Contact panels retain every source pixel; indexed manifest establishes panel order.
boards=[]
for group in ['selected-core external boundary','unselected extension internal','unselected extension west border']:
 for direction in ['south','east']:
  ps=[(e,im) for e,im in panels if e['scope']==group and e['direction']==direction]
  for off in range(0,len(ps),8):
   chunk=ps[off:off+8];board=Image.new('RGB',(2048,2048),(18,18,18));entries=[]
   for i,(e,im) in enumerate(chunk):
    dx=(i%2)*1024 if direction=='south' else (i%4)*512
    dy=(i//2)*512 if direction=='south' else (i//4)*1024
    board.paste(im,(dx,dy));entries.append({'id':e['id'],'destination':[dx,dy,dx+im.width,dy+im.height]})
   name=f'board-{len(boards)+1:02d}-100pct.png';p=OUT/name;assert not p.exists();board.save(p);boards.append({'file':info(p),'scope':group,'direction':direction,'panels':entries})

counts={'tileCount':len(tiles),'selectedCoreCount':sum(t['coreCount'] for t in tiles),'fullCoverageTileCount':sum(t['fullCoverage'] for t in tiles),'partialTileCount':sum(0<t['coreCount']<16 for t in tiles),'emptySelectedTileCount':sum(t['coreCount']==0 for t in tiles),'savedNativeVersionCount':len(native),'savedUniqueCoreCount':sum(t['savedUniqueCoreCount'] for t in tiles),'savedCompleteGridCount':sum(t['savedFullCoreCoverage'] for t in tiles),'formalAcceptedCount':0}
snapshot={'startedAtUtc':started,'frozenAtUtc':now(),'baseline':str(OLD/'summary.json'),'rules':[info(ROOT/'AGENTS.md'),info(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')],'counts':counts,'tiles':tiles,'native':list(native.values()),'metadata':list(meta.values()),'neighbors':neighbors,'selectionMap':{'|'.join(map(str,k)):v for k,v in selected.items()},'holds':[{'coordinate':list(k),**v} for k,v in holds.items()],'reusedChecks':reuse,'newNativeIdsSinceBaseline':sorted(set(native)-oldnative),'nativeListing':listing,'edges':edges,'boards':boards}
save('snapshot.json',snapshot)
print(json.dumps({'counts':counts,'tiles':[{k:t[k] for k in ['tileId','coreCount','savedVersionCount','savedUniqueCoreCount']} for t in tiles],'boards':boards},ensure_ascii=False,indent=2))
