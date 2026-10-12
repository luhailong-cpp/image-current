from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json, hashlib

O=Path(__file__).resolve().parent
R=O.parents[1]
P=R.parents[1]/'island-game-20261009'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read(R/'root-audit-v01/inventory.json'); baseline={t['tileId']:t for t in old['tiles']}
snap={x['file']:x['sha256'] for x in read(R/'root-audit-v01/input-snapshot.json')['files']}
now=datetime.now(timezone.utc).isoformat(); checks=[]; sources={}; tiles=[]
for tid,t in baseline.items():
 sel=read(t['selectionFile'])
 if t['zone']=='accelerated-northeast-coast':
  q=next(x for x in sel['candidates'] if x['tileId']==tid); matrix=q['selectedCores']; candidate=q['file']; overlays=[]
 else:
  q=sel;matrix=q['cores'];candidate=q.get('candidatePath',str(P/'northeast/tiles'/f'{tid}.png'));overlays=q.get('overlays',[])
 same=matrix==t['selectedCores'] and overlays==[x['id'] for x in t.get('overlays',[])]
 assert same,('new effective selection needs targeted followup',tid)
 images=t['sources']+([t] if t.get('file') else [])+t.get('overlays',[])
 for s in images:
  f=s.get('file',s.get('source')); expected=s.get('sha256')
  if f not in sources:sources[f]={'file':f,'expectedSha256':expected,'currentSha256':sha(f)}
  assert sources[f]['currentSha256']==expected,('changed selected pixels',f)
 f=t['selectionFile'];cur=sha(f)
 checks.append({'tileId':tid,'selectionFile':f,'selectionSha256':cur,'metadataChanged':cur!=snap.get(f),'effectiveSelectionUnchanged':same,'selectedCoreCount':t['coreCount'],'candidatePathUnchanged':not t.get('file') or Path(candidate)==Path(t['file']),'candidatePixelsUnchanged':True if t.get('file') else None})
 assert checks[-1]['candidatePathUnchanged'],tid
 tiles.append({'tileId':tid,'coreCount':t['coreCount'],'file':t.get('file'),'sha256':t.get('sha256'),'fullCoverage':t['fullCoverage'],'selectedCores':matrix,'formalAccepted':False})
write(O/'source-delta.json',{'capturedAtUtc':now,'scope':'current selected source PNGs and current effective selections only; no historical raw archive rescan','metadata':checks,'selectedSourcePixels':list(sources.values()),'allSelectedPixelsUnchanged':True,'allEffectiveSelectionsUnchanged':True})
full={tid:t for tid,t in baseline.items() if t['fullCoverage']}
def rc(tid):return int(tid[1:3]),int(tid[5:7])
def id(r,c):return f'r{r:02d}_c{c:02d}'
existing_pairs={};existing_cross=set()
for m in (R/'root-audit-v01').glob('g*/manifest.json'):
 d=read(m)
 if 'coordinates' not in d:continue
 ts=d['coordinates']; existing_cross.add(tuple(sorted(ts)))
 for a in ts:
  r,c=rc(a)
  for b in [id(r+1,c),id(r,c+1)]:
   if b in ts:existing_pairs[tuple(sorted([a,b]))]=m.as_posix()
new=[];reused=[]
for a,t in full.items():
 r,c=rc(a)
 for b,orientation in [(id(r,c+1),'vertical'),(id(r+1,c),'horizontal')]:
  if b not in full:continue
  pair=tuple(sorted([a,b]))
  if pair in existing_pairs:
   reused.append({'tiles':[a,b],'evidence':existing_pairs[pair],'sourceHashesUnchanged':True,'status':'reuse_previous_result_including_open_findings'})
   continue
  directory=O/f'{a}__{b}';directory.mkdir(exist_ok=True)
  records=[];board=Image.new('RGB',(2048,1024))
  with Image.open(t['file']) as ai,Image.open(full[b]['file']) as bi:
   for s in range(4):
    if orientation=='vertical':
     im=Image.new('RGB',(512,1024));im.paste(ai.crop((3840,s*1024,4096,(s+1)*1024)),(0,0));im.paste(bi.crop((0,s*1024,256,(s+1)*1024)),(256,0));world=[c*4096-256,(r-1)*4096+s*1024,c*4096+256,(r-1)*4096+(s+1)*1024]
     board.paste(im,(s*512,0))
    else:
     im=Image.new('RGB',(1024,512));im.paste(ai.crop((s*1024,3840,(s+1)*1024,4096)),(0,0));im.paste(bi.crop((s*1024,0,(s+1)*1024,256)),(0,256));world=[(c-1)*4096+s*1024,r*4096-256,(c-1)*4096+(s+1)*1024,r*4096+256]
     board.paste(im,((s%2)*1024,(s//2)*512))
    f=directory/f'segment-{s+1}-100pct.png';im.save(f);records.append({'file':f.as_posix(),'sha256':sha(f),'worldBox':world,'segment':s+1,'dimensions':list(im.size)});im.close()
  f=directory/'board-100pct.png';board.save(f);board.close()
  new.append({'tiles':[a,b],'orientation':orientation,'inputs':[{'file':full[x]['file'],'sha256':full[x]['sha256']} for x in [a,b]],'segments':records,'board':f.as_posix(),'status':'pending_visual_review','formalAccepted':False})
cross=[]
for a,t in full.items():
 r,c=rc(a);ids=[a,id(r,c+1),id(r+1,c),id(r+1,c+1)]
 if not all(x in full for x in ids) or tuple(sorted(ids)) in existing_cross:continue
 im=Image.new('RGB',(1024,1024))
 for j,x in enumerate(ids):
  with Image.open(full[x]['file']) as src:
   box=[3584 if j%2==0 else 0,3584 if j<2 else 0,4096 if j%2==0 else 512,4096 if j<2 else 512]
   im.paste(src.crop(box),((j%2)*512,(j//2)*512))
 f=O/f'cross-{a}-100pct.png';im.save(f);im.close()
 cross.append({'tiles':ids,'worldPoint':[c*4096,r*4096],'file':f.as_posix(),'sha256':sha(f),'status':'pending_visual_review','formalAccepted':False})
write(O/'summary.json',{'capturedAtUtc':now,'tiles':tiles,'selectedCoreCount':sum(t['coreCount'] for t in tiles),'fullCoverageCount':len(full),'partialCount':len(tiles)-len(full),'selectionAndSourcePixelsUnchanged':True,'reusedPairs':reused,'newEdgeReviews':new,'newCrossReviews':cross,'formalAcceptedCount':0,'generationCalls':0,'productionWrites':False})
print(json.dumps({'unchangedSelectedImages':len(sources),'reusedPairs':len(reused),'newPairs':[x['tiles'] for x in new],'newCrosses':[x['tiles'] for x in cross]},ensure_ascii=False))
