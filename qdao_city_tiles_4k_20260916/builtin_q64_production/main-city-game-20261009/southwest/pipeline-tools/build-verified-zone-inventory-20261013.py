from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import hashlib,json,csv,sys,numpy as np
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=read(B/'pipeline-tools/live-counts-20261010.json');cat=read(B/'current-candidates.json')['tiles'];by={t['tile']:t for t in s['tiles']}
Q=B/'pipeline-tools/local-delivery-inventory-20261013';Q.mkdir(exist_ok=False)
tiles=[];total=0;records=[]
for row in range(9,17):
 for col in range(1,9):
  tid=f'r{row:02}_c{col:02}';t=by.get(tid,{});selected=t.get('nativeRecords',[]);ids=t.get('selectedIds',[]);assert len(selected)==len(ids)
  for n in selected:
   assert sha(n['file'])==n['sha256'] and Image.open(n['file']).size==(1254,1254)
   assert sha(n['record'])==n['recordSha256']
  total+=len(ids);e=cat.get(tid);verified=False
  if e:
   assert len(ids)==16
   for n in [e['candidate'],e['context']]:assert sha(n['file'])==n['sha256']
   core=Image.open(e['candidate']['file']).convert('RGB');ctx=Image.open(e['context']['file']).convert('RGB')
   assert core.size==(4096,4096) and ctx.size==(4326,4326)
   assert np.array_equal(np.array(core),np.array(ctx.crop((115,115,4211,4211))))
   verified=True
  tiles.append({'tile':tid,'selectedNativePatchCount':len(ids),'selectedIds':ids,'missingPatchIds':[f'p{r:02}_{c:02}' for r in range(1,5) for c in range(1,5) if f'p{r:02}_{c:02}' not in ids],'coverageState':'full_candidate_pending_QA' if verified else 'partial' if ids else 'untouched','candidate':e.get('candidate') if e else None,'context':e.get('context') if e else None,'currentCatalogOutputHashesDimensionsAndCoreCropVerified':verified,'formalAccepted':False,'internalPassed':False,'selectedNativeRecords':selected})
assert total==258 and len(cat)==15
report={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'coverageSnapshotUtc':s['snapshotCompletedAtUtc'],'targetTiles':64,'selectedNativePatches':total,'missingNativePatches':1024-total,'fullCandidates':len(cat),'partialTiles':sum(0<t['selectedNativePatchCount']<16 for t in tiles),'untouchedTiles':sum(t['selectedNativePatchCount']==0 for t in tiles),'formalAccepted':0,'internalPassed':0,'modelGate':str(B/'pipeline-tools/image-model-25-gate-20261013.json'),'newGenerationCalls':0,'sourceResamplingForArt':False,'tiles':tiles}
atomic_json(Q/'inventory.json',report)
with (Q/'missing-patches.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['tile','missing_patch','reason'])
 for t in tiles:
  for pid in t['missingPatchIds']:w.writerow([t['tile'],pid,'Await verified explicitly selected GPT Image 2.5 route; no paid API authorized'])
cell=188;art=176;header=68;canvas=Image.new('RGB',(8*cell,header+8*(cell+22)),(24,28,35));draw=ImageDraw.Draw(canvas)
draw.text((12,10),'SOUTHWEST COVERAGE QA ONLY - NOT A FINAL MAP',fill='white')
draw.text((12,30),'64 tiles | 15 full candidates | 3 partial | 46 untouched | 766 missing patches | accepted 0',fill=(230,230,230))
for i,t in enumerate(tiles):
 x=(i%8)*cell+6;y=header+(i//8)*(cell+22);tileim=Image.new('RGB',(art,art),(55,59,67))
 if t['candidate']:
  tileim=Image.open(t['candidate']['file']).convert('RGB').resize((art,art),Image.Resampling.LANCZOS)
 elif t['selectedNativePatchCount']:
  for n in t['selectedNativeRecords']:
   pid=n['patch'];r=int(pid[1:3])-1;c=int(pid[4:6])-1
   im=Image.open(n['file']).convert('RGB').crop((115,115,1139,1139)).resize((art//4,art//4),Image.Resampling.LANCZOS)
   tileim.paste(im,(c*(art//4),r*(art//4)))
 else:
  d=ImageDraw.Draw(tileim);d.text((15,80),'No native artwork',fill=(180,180,190))
 canvas.paste(tileim,(x,y+20));count=t['selectedNativePatchCount'];color=(240,185,65) if count else (165,165,175)
 draw.text((x,y),f'{t["tile"]} {count}/16',fill=color)
 draw.text((x,y+art+23),'Pending QA' if count==16 else f'Missing {16-count}',fill=(210,210,210))
canvas.save(Q/'coverage-QA-only.png')
atomic_json(Q/'preview-derivation.json',{'file':str(Q/'coverage-QA-only.png'),'sha256':sha(Q/'coverage-QA-only.png'),'QAOnly':True,'notFinalArtwork':True,'resizedOnlyForPreview':True,'allFullTilesUseCurrentCatalogCandidate':True,'partialCellsUseExactCentralNativeCropBeforePreviewResizing':True,'inventory':str(Q/'inventory.json'),'inventorySha256':sha(Q/'inventory.json'),'drawnLabelsOutsideArt':True})
print(json.dumps({k:report[k] for k in ['targetTiles','selectedNativePatches','missingNativePatches','fullCandidates','partialTiles','untouchedTiles','formalAccepted','internalPassed']}));print(Q)
