import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
ROOT=Path('D:/work/image');BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'island-game-20261009'; AUDIT=BASE/'parallel-review-20261013/island-game-20261009'
OUT=AUDIT/'resume-v03/west';OLD=AUDIT/'resume-v02/west';OUT.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def norm(p):return str(p).replace('\\','/')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
stamp=now();old=read(OLD/'source-delta.json');oldsum=read(OLD/'summary.json');meta=[]
def snap(z,n):
 p=PROD/z/n;data=p.read_bytes();dest=OUT/'snapshots'/z/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 meta.append({'path':norm(p),'snapshot':norm(dest),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'mtimeNs':p.stat().st_mtime_ns,'readAtUtc':now()})
 return json.loads(data.decode('utf-8-sig'))
nw=snap('northwest','current-adopted-20261012.json');nr=snap('northwest','root-current-selection-20261012.json');nri=snap('northwest','right-current-selection-20261012.json');nwst=snap('northwest','west-current-selection-20261012.json');nb=snap('northwest','selected-native.json');np=snap('northwest','progress.json');sw=snap('southwest','current-native-map.json');sp=snap('southwest','progress.json')
snapshot=now();oldtiles={z:{t['tileId']:t for t in d['tiles']} for z,d in old['zones'].items()}
sources={z:{tile:{(s['subrow'],s['subcolumn']):{'path':s['path'],'expectedSha256':s['sha256']} for s in t['selectedSources']} for tile,t in ts.items()} for z,ts in oldtiles.items()}
def setcells(tile,cells):
 src={}
 for c in cells:
  m=re.search(r'_s(\d+)_(\d+)_',c['stem'])
  if m:src[(int(m[1]),int(m[2]))]={'path':norm(c.get('image',{}).get('path',PROD/'northwest/native'/f"{c['stem']}.png")),'expectedSha256':c.get('image',{}).get('sha256')}
 sources['northwest'][tile]=src
for t,d in nw.get('partialTiles',{}).items():
 if d.get('cells'):setcells(t,d['cells'])
for d in [nr,nri]:
 for t,v in d['tiles'].items():setcells(t,v.get('cells',[]))
for t in nwst.get('partialTiles',[]):
 if 'selectedNative' in t:setcells(t['tileId'],t['selectedNative'])
 elif 'selectedNativeStems' in t:setcells(t['tileId'],[{'stem':s} for s in t['selectedNativeStems']])
for t,m in sw.items():
 if re.fullmatch(r'r\d\d_c\d\d',t) and isinstance(m,list):sources['southwest'][t]={(r,c):{'path':norm(PROD/'southwest/native'/f'{s}.png'),'expectedSha256':None} for r,row in enumerate(m,1) for c,s in enumerate(row,1) if s}
candidates={'northwest':{t['tileId']:t['image'] for t in nw['tiles']},'southwest':sw['candidateArtifacts']};cache={}
def info(p):
 p=norm(p)
 if p not in cache:
  s=Path(p).stat()
  with Image.open(p) as im:dims=list(im.size)
  cache[p]={'path':p,'sha256':sha(p),'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'dimensions':dims}
 return cache[p]
res={'startedAtUtc':stamp,'metadataSnapshotCompletedAtUtc':snapshot,'baseline':norm(OLD/'source-delta.json'),'metadata':meta,'zones':{},'newDiagnosticAssemblies':[],'candidatePixelComparisons':[],'newCoreEvidence':[],'edges':[],'formalAcceptedCount':0,'generationCalls':0,'productionWrites':False,'gitOperations':False}
changed=[]
for z,ts in sources.items():
 out=[]
 for tile,ss in sorted(ts.items()):
  ot=oldtiles[z].get(tile,{});osm={(s['subrow'],s['subcolumn']):s for s in ot.get('selectedSources',[])};selected=[]
  for rc,s in sorted(ss.items()):
   d={**info(s['path']),'subrow':rc[0],'subcolumn':rc[1]};o=osm.get(rc);d['oldSha256']=o['sha256'] if o else None;d['change']='added' if not o else 'unchanged' if o['sha256']==d['sha256'] else 'changed';d['recordedHashMatches']=s.get('expectedSha256') in [None,d['sha256']];selected.append(d)
   if d['change']!='unchanged':
    changed.append((z,tile,rc))
    rp=Path(s['path']+'.generation.json')
    if rp.exists():
     data=rp.read_bytes();dest=OUT/'snapshots/new-core-records'/z/rp.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
     j=json.loads(data.decode('utf-8-sig'));res['newCoreEvidence'].append({'tileId':tile,'subrow':rc[0],'subcolumn':rc[1],'image':d,'record':norm(rp),'recordSnapshot':norm(dest),'recordSha256':hashlib.sha256(data).hexdigest(),'record':j})
  ca=None;oc=ot.get('adopted4kCandidate')
  if tile in candidates[z]:
   ca={**info(candidates[z][tile]['path']),'recordedSha256':candidates[z][tile].get('sha256')};ca['unchangedFromBaseline']=bool(oc and ca['sha256']==oc['sha256']);ca['statusRecord']=candidates[z][tile]
  diag=next((a for a in oldsum['newDiagnosticAssemblies'] if a['tileId']==tile),None)
  diagunchanged=diag and len(selected)==16 and all(s['change']=='unchanged' for s in selected)
  t={'tileId':tile,'coreCount':len(selected),'oldCoreCount':ot.get('coreCount',0),'coreCountDelta':len(selected)-ot.get('coreCount',0),'fullCoverage':len(selected)==16,'adopted':bool(ca),'file':ca['path'] if ca else diag['path'] if diagunchanged else None,'sha256':ca['sha256'] if ca else diag['sha256'] if diagunchanged else None,'adopted4kCandidate':ca,'selectedSources':selected,'formalAccepted':False,'priorEvidenceReusable':all(s['change']=='unchanged' for s in selected) and (not ca or ca['unchangedFromBaseline'])}
  if diagunchanged:t['reusedDiagnosticAssembly']=diag
  out.append(t)
 res['zones'][z]={'tiles':out,'selectedCoreCount':sum(t['coreCount'] for t in out),'adoptedCandidateCount':sum(t['adopted'] for t in out),'fullCoreCoverageCount':sum(t['fullCoverage'] for t in out),'partialTileCount':sum(0<t['coreCount']<16 for t in out),'emptyTileCount':sum(t['coreCount']==0 for t in out),'formalAcceptedCount':0}
res['frozenInputHashCompletedAtUtc']=now();tmap={t['tileId']:(z,t) for z,d in res['zones'].items() for t in d['tiles']}
# Compare newly adopted r12_c03 to the already reviewed diagnostic pixels.
for z,d in res['zones'].items():
 for t in d['tiles']:
  ca=t['adopted4kCandidate'];diag=t.get('reusedDiagnosticAssembly')
  if ca and not ca['unchangedFromBaseline'] and diag:
   with Image.open(ca['path']) as a,Image.open(diag['path']) as b:
    diff=ImageChops.difference(a.convert('RGB'),b.convert('RGB'));bbox=diff.getbbox()
   comp={'tileId':t['tileId'],'candidate':ca['path'],'priorDiagnostic':diag['path'],'identicalDecodedPixels':bbox is None,'differenceBBox':bbox};res['candidatePixelComparisons'].append(comp)
   if bbox is None:t['priorEvidenceReusable']=True
# New complete selected-core tile: exact hard assembly for independent diagnostic QA only.
for z,d in res['zones'].items():
 for t in d['tiles']:
  if t['fullCoverage'] and not t['adopted'] and not t.get('reusedDiagnosticAssembly'):
   im=Image.new('RGB',(4096,4096))
   for s in t['selectedSources']:
    with Image.open(s['path']) as si:
     assert si.size==(1254,1254);im.paste(si.convert('RGB').crop((115,115,1139,1139)),((s['subcolumn']-1)*1024,(s['subrow']-1)*1024))
   path=OUT/'native-assemblies'/f"{z}-{t['tileId']}-selected-core-hard-join-4096-v03.png";path.parent.mkdir(exist_ok=True);im.save(path)
   t['file']=norm(path);t['sha256']=sha(path);res['newDiagnosticAssemblies'].append({'tileId':t['tileId'],**info(path),'adopted':False,'mode':'exact native 1024 core hard paste; no resize or feather'})
# Build only new/changed native core adjacency edges, plus all edges of newly complete tile.
newfull={a['tileId'] for a in res['newDiagnosticAssemblies']};globalcores={};changedset=set()
for z,d in res['zones'].items():
 for t in d['tiles']:
  rr=int(t['tileId'][1:3]);cc=int(t['tileId'][5:7])
  for s in t['selectedSources']:
   key=((rr-1)*4+s['subrow']-1,(cc-1)*4+s['subcolumn']-1);globalcores[key]=(t,s)
   if s['change']!='unchanged' or t['tileId'] in newfull:changedset.add(key)
def core(t,s):
 if t['adopted4kCandidate']:
  with Image.open(t['file']) as im:x=(s['subcolumn']-1)*1024;y=(s['subrow']-1)*1024;return im.convert('RGB').crop((x,y,x+1024,y+1024))
 with Image.open(s['path']) as im:return im.convert('RGB').crop((115,115,1139,1139))
pairs=set()
for k in changedset:
 for dr,dc in [(-1,0),(0,-1),(1,0),(0,1)]:
  n=(k[0]+dr,k[1]+dc)
  if n in globalcores:pairs.add(tuple(sorted((k,n))))
for i,(ka,kb) in enumerate(sorted(pairs),1):
 ta,sa=globalcores[ka];tb,sb=globalcores[kb];a=core(ta,sa);b=core(tb,sb);vertical=ka[0]==kb[0]
 im=Image.new('RGB',(512,1024) if vertical else (1024,512))
 if vertical:im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0));line=[kb[1]*1024,ka[0]*1024,kb[1]*1024,(ka[0]+1)*1024]
 else:im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256));line=[ka[1]*1024,kb[0]*1024,(ka[1]+1)*1024,kb[0]*1024]
 name=f"{i:03d}-{ta['tileId']}-s{sa['subrow']}{sa['subcolumn']}--{tb['tileId']}-s{sb['subrow']}{sb['subcolumn']}";p=OUT/'edges'/f'{name}.png';p.parent.mkdir(exist_ok=True);im.save(p)
 res['edges'].append({'id':name,'path':norm(p),'axis':'vertical' if vertical else 'horizontal','tiles':[ta['tileId'],tb['tileId']],'globalSeamLine':line,'dimensions':list(im.size),'sourceA':sa,'sourceB':sb,'sourceCandidateA':ta['file'] if ta['adopted'] else None,'sourceCandidateB':tb['file'] if tb['adopted'] else None,'status':'pending_visual_review','actuallyViewed':False})
# Original pixel contact sheets, separate axes, 4 segments per 2048x1024 sheet.
res['boards']=[]
for axis in ['vertical','horizontal']:
 es=[e for e in res['edges'] if e['axis']==axis]
 for k in range(0,len(es),4):
  group=es[k:k+4];im=Image.new('RGB',(2048,1024),(45,45,45))
  for i,e in enumerate(group):
   with Image.open(e['path']) as ci:im.paste(ci,(i*512,0) if axis=='vertical' else ((i%2)*1024,(i//2)*512))
  p=OUT/'edges'/f'board-{axis}-{k//4+1:02d}-100pct.png';im.save(p);res['boards'].append({'path':norm(p),'axis':axis,'edgeIds':[e['id'] for e in group],'noScaling':True})
res['imageHashCount']=len(cache);res['changedCoreCount']=len(changed);res['newEdgeCount']=len(res['edges']);res['completedPreparationAtUtc']=now();save(OUT/'source-delta.json',res)
summary={k:v for k,v in res.items() if k not in ['newCoreEvidence','edges','boards','metadata']};summary['zones']={z:{**d,'tiles':[{k:v for k,v in t.items() if k not in ['selectedSources','adopted4kCandidate']} for t in d['tiles']]} for z,d in res['zones'].items()};save(OUT/'summary.json',summary)
print(json.dumps({z:{k:v for k,v in d.items() if k!='tiles'} for z,d in res['zones'].items()},ensure_ascii=False));print('changed',changed);print('newEdges',len(res['edges']));print('comparison',res['candidatePixelComparisons']);print('boards',res['boards'])
