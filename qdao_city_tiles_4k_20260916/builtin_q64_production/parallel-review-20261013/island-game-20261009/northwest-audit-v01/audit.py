from pathlib import Path
from PIL import Image, ImageChops
import hashlib,json,re,datetime,gc

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest'
OUT=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/northwest-audit-v01'
OUT.mkdir(parents=True,exist_ok=True)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def path(p):
 p=Path(p)
 return p if p.is_absolute() else BASE/p
def meta(p,expected=None):
 p=path(p); d={'file':p.as_posix(),'exists':p.exists()}
 if p.exists():
  d.update(sha256=sha(p),bytes=p.stat().st_size)
  if p.suffix.lower()=='.png':
   with Image.open(p) as im:d['dimensions']=list(im.size)
  if expected:d['expectedSha256']=expected;d['hashMatches']=d['sha256']==expected
 return d
def coord(t):
 r,c=map(int,re.match(r'r(\d+)_c(\d+)',t).groups());return r,c
def box(t):
 r,c=coord(t);return [(c-1)*4096,(r-1)*4096,c*4096,r*4096]
snapnames=['current-adopted-20261012.json','progress.json','root-current-selection-20261012.json','west-current-selection-20261012.json','right-current-selection-20261012.json','selected-native.json']
snaps=[meta(BASE/n) for n in snapnames]
adopted=read(BASE/snapnames[0]); progress=read(BASE/'progress.json')
full={t['tileId']:t for t in adopted['tiles']}
west=read(BASE/'west-current-selection-20261012.json')
partial={t['tileId']:t for t in west['partialTiles'] if t.get('selectedNativeStems')}
source_inputs={x['file']:x for x in snaps}
def track(m):source_inputs[m['file']]=m;return m
tiles=[]
for r in range(1,8):
 for c in range(1,8):
  tid=f'r{r:02d}_c{c:02d}';t={'tileId':tid,'row':r,'column':c,'globalBoxHalfOpen':box(tid),'fullCoverage':False,'coreCount':0,'requiredCoreCount':16,'formalAccepted':False,'file':None,'sha256':None,'dimensions':None,'selectedSources':[]}
  if tid in full:
   f=full[tid];m=track(meta(f['image']['path'],f['image']['sha256']));rec=track(meta(f['record']['path'],f['record']['sha256']))
   t.update({k:m.get(k) for k in ['file','sha256','dimensions']});t.update(fullCoverage=m.get('hashMatches') and m.get('dimensions')==[4096,4096],coreCount=16,coverageEvidence=rec,selectionBasis=f.get('selectionBasis'),internalPassed=f.get('internalClosurePassed',f.get('internalClosurePassedBeforeFreeze',False)))
   assemblies=list((BASE/'tiles').glob(f'{tid}_candidate-v1_4096.assembly.json'))
   if assemblies:
    am=track(meta(assemblies[0]));a=read(assemblies[0]);t['rootAssembly']=am;t['coverageAssertions']=a.get('coverageAssertions');matrix=a.get('manifestSnapshot',{}).get('patchMatrix',[])
    for sr,row in enumerate(matrix,1):
     for sc,cell in enumerate(row,1):
      sm=track(meta(cell['path'],cell.get('sha256')));sm=dict(sm,patchId=f'{tid}_s{sr:02d}_{sc:02d}',subrow=sr,subcolumn=sc,globalCoreBoxHalfOpen=[(c-1)*4096+(sc-1)*1024,(r-1)*4096+(sr-1)*1024,(c-1)*4096+sc*1024,(r-1)*4096+sr*1024],role='root_assembly_source_before_explicit_repairs')
      gp=cell.get('generationRecord')
      if gp:
       gm=track(meta(gp));gd=read(path(gp));sm['generationRecord']=gm
       sm['referenceEvidence']={k:v for k,v in gd.items() if 'reference' in k.lower() or 'model' in k.lower() or 'dimension' in k.lower() or 'size' in k.lower()}
      t['selectedSources'].append(sm)
  elif tid in partial:
   pt=partial[tid];t['status']=pt.get('status');t['knownOpenIssues']=pt.get('openIssues',[])
   for stem in pt['selectedNativeStems']:
    sr,sc=map(int,re.search(r'_s(\d+)_(\d+)_',stem).groups());m=track(meta(BASE/'native'/f'{stem}.png'));gm=track(meta(BASE/'native'/f'{stem}.png.generation.json'))
    t['selectedSources'].append(dict(m,patchId=f'{tid}_s{sr:02d}_{sc:02d}',subrow=sr,subcolumn=sc,generationRecord=gm,globalCoreBoxHalfOpen=[(c-1)*4096+(sc-1)*1024,(r-1)*4096+(sr-1)*1024,(c-1)*4096+sc*1024,(r-1)*4096+sr*1024]))
   t['coreCount']=len({s['patchId'] for s in t['selectedSources'] if s['exists'] and s.get('dimensions')==[1254,1254]})
  covered={(s['subrow'],s['subcolumn']) for s in t['selectedSources']}
  t['missingCores']=[f'{tid}_s{sr:02d}_{sc:02d}' for sr in range(1,5) for sc in range(1,5) if (sr,sc) not in covered] if not t['fullCoverage'] else []
  tiles.append(t)
T={t['tileId']:t for t in tiles}
def world_crop(b):
 im=Image.new('RGB',(b[2]-b[0],b[3]-b[1]));filled=0
 for tid,t in full.items():
  tb=box(tid);inter=[max(b[0],tb[0]),max(b[1],tb[1]),min(b[2],tb[2]),min(b[3],tb[3])]
  if inter[0]<inter[2] and inter[1]<inter[3]:
   with Image.open(path(t['image']['path'])) as src:
    im.paste(src.crop((inter[0]-tb[0],inter[1]-tb[1],inter[2]-tb[0],inter[3]-tb[1])),(inter[0]-b[0],inter[1]-b[1]))
   filled+=(inter[2]-inter[0])*(inter[3]-inter[1])
 assert filled==im.width*im.height,('missing pixels',b,filled)
 return im
old=[]
for n,origin in [('qa/connected-closure-final-v1/closure.json',(8192,8192)),('qa/connected-r04-r05-final-v1/closure.json',(8192,12288))]:
 p=BASE/n;d=read(p);track(meta(p))
 for q in d['checks']:
  b=q['box'];gb=[b[0]+origin[0],b[1]+origin[1],b[2]+origin[0],b[3]+origin[1]]
  old.append((gb,q,p))
crops=[];pairs=[]
(OUT/'crops').mkdir(exist_ok=True)
for tid in sorted(full):
 r,c=coord(tid)
 for dr,dc,orientation in [(0,1,'vertical'),(1,0,'horizontal')]:
  nt=f'r{r+dr:02d}_c{c+dc:02d}'
  if nt not in full:continue
  pair=f'{tid}--{nt}';pb=[];tb=box(tid)
  for i in range(4):
   b=[tb[2]-240,tb[1]+i*1024,tb[2]+240,tb[1]+(i+1)*1024] if dc else [tb[0]+i*1024,tb[3]-240,tb[0]+(i+1)*1024,tb[3]+240]
   p=OUT/'crops'/f'{pair}_{i+1:02d}_100pct.png';im=world_crop(b);im.save(p);m=meta(p);m.update(kind='pair',pair=pair,orientation=orientation,segment=i+1,globalBoxHalfOpen=b,nativeScale100Percent=True,status='needs_visual_review')
   for ob,oq,op in old:
    if ob==b and oq.get('visualPassed'):
     om=track(meta(oq['output']['path'],oq['output']['sha256']))
     with Image.open(path(oq['output']['path'])) as oi:eq=ImageChops.difference(im,oi.convert('RGB')).getbbox() is None
     if om.get('hashMatches') and eq:m.update(status='reused_pass_exact_current_pixels',priorEvidence=om,priorReview=op.as_posix())
   im.close();crops.append(m);pb.append(m['file'])
  pairs.append({'pair':pair,'tiles':[tid,nt],'orientation':orientation,'cropFiles':pb})
for r,c in [(3,2),(3,3),(4,3),(5,3)]:
 ids=[f'r{rr:02d}_c{cc:02d}' for rr in [r,r+1] for cc in [c,c+1]]
 if not all(i in full for i in ids):continue
 x,y=c*4096,r*4096;b=[x-320,y-320,x+320,y+320];p=OUT/'crops'/f'junction_r{r:02d}-{r+1:02d}_c{c:02d}-{c+1:02d}_100pct.png';im=world_crop(b);im.save(p);im.close();m=meta(p);m.update(kind='junction',tiles=ids,globalBoxHalfOpen=b,nativeScale100Percent=True,status='needs_visual_review');crops.append(m)
groups=[]
for name,ids in [('upper-left_r03-r04_c02-c03',['r03_c02','r03_c03','r04_c02','r04_c03']),('lower_r05-r06_c03-c04',['r05_c03','r05_c04','r06_c03','r06_c04'])]:
 b=[min(box(i)[0] for i in ids),min(box(i)[1] for i in ids),max(box(i)[2] for i in ids),max(box(i)[3] for i in ids)]
 im=world_crop(b);p=OUT/f'{name}_native8192_candidate_v01.png';im.save(p);m=meta(p);m.update(tiles=ids,globalBoxHalfOpen=b,method='exact_core_pixel_paste_no_resize_no_blend_no_synthesis',gameReady=False,scope='mechanical native assembly candidate; pending seam review');groups.append(m)
 preview=im.resize((1024,1024),Image.Resampling.LANCZOS);pp=OUT/f'{name}_preview1024_NOT_NATIVE.png';preview.save(pp);preview.close();im.close();gc.collect()
 m['preview']=meta(pp);m['preview']['nativeScale100Percent']=False
internal_paths=['qa/r03_c02_v7_internal_closure/review.json','qa/r04_c02_v9_internal_review/review.json','qa/r06_c03_v7_internal_closure_20261012/closure.json','qa/r07_c03_v1_owner_native33_review_20261013.json','qa/r06_c04_v1_independent_root_vertical12_review_20261012.json']
evidence=[]
for n in internal_paths:
 p=BASE/n;d=read(p);m=track(meta(p));m['summary']={k:d.get(k) for k in ['status','tileId','internalClosurePassed','nativeScale100Percent','passCropCount','repairRequiredCropCount','pendingCrossTile','repairGroups'] if k in d};evidence.append(m)
missing=[t['tileId'] for t in tiles if not t['fullCoverage']]
inv={'schemaVersion':1,'createdAtUtc':now(),'scope':'northwest r01..r07 c01..c07 only; independent read-only production audit','actualImageModel':'unconfirmed; no new image generation or AI edits performed','sourceSnapshots':snaps,'summary':{'targetTileCount':49,'fullCoverageCandidateCount':sum(t['fullCoverage'] for t in tiles),'internallyPassedReportedBySelection':sum(bool(t.get('internalPassed')) for t in tiles),'formalAcceptedCount':0,'selectedCoreCount':sum(t['coreCount'] for t in tiles),'missingCoreCount':sum(len(t['missingCores']) for t in tiles),'partialTileCounts':{t['tileId']:t['coreCount'] for t in tiles if 0<t['coreCount']<16},'missingFullTileCount':len(missing)},'tiles':tiles,'missingFullTiles':missing,'pairs':pairs,'crops':crops,'mechanicalNativeGroups':groups,'internalEvidence':evidence,'inputFiles':list(source_inputs.values()),'progressDiscrepancies':{'progressAssembledCount':progress.get('assembledCandidateTileCount'),'currentAdoptedCount':len(full),'progressPartialR07C03':progress.get('remainingWorkSummary',{}).get('partialTileSelectedCounts',{}).get('r07_c03'),'actualSelectedR07C03':T['r07_c03']['coreCount']},'limitations':['No source artwork changed, generated or repaired.','Output groups preserve all existing defects and are candidates only.','Record source chains and historical strict replay evidence are retained; this audit does not re-execute full recursive provenance replay.','Cross-zone neighbors and acceleration overlaps are root-agent scope.','Historical source model metadata stays unconfirmed.']}
(OUT/'inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'summary':inv['summary'],'crops':len(crops),'reused':sum(x['status'].startswith('reused') for x in crops),'reviewNeeded':[Path(x['file']).name for x in crops if x['status']=='needs_visual_review'],'inventory':str(OUT/'inventory.json')},ensure_ascii=False,indent=2))
