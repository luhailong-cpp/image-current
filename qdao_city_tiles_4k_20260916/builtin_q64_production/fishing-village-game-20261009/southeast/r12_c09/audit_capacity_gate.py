import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
sel=read(ROOT/'selected-patches.json');plan=read(ROOT/'coordinate-plan.json');entries={p['id']:p for p in plan['patches']}
manifest=read(ROOT/'candidate/manifest.json');candidate=np.array(Image.open(manifest['candidate']).convert('RGB'))
inventory=[];issues=[]
for pid,rel in sorted(sel['patches'].items()):
 p=ROOT/rel;g=Path(str(p)+'.generation.json');rec=read(g);im=Image.open(p);r=int(pid[1]);c=int(pid[2]);x=(c-1)*1024;y=(r-1)*1024
 check={'patch':pid,'path':str(p),'sha256':sha(p),'dimensions':list(im.size),'globalBox':entries[pid]['globalBox'],'coreBox':entries[pid]['coreBox'],'candidateDestination':[x,y,x+1024,y+1024],'candidateCoreByteIdentical':bool(np.array_equal(candidate[y:y+1024,x:x+1024],np.array(im.convert('RGB'))[115:1139,115:1139])),'nativeShaMatchesRecord':sha(p)==rec['sha256'],'actualModelNull':rec['actualModel'] is None,'actualQualityNull':rec['actualQuality'] is None,'submittedModelNull':rec['submittedParameters']['model'] is None,'submittedQualityNull':rec['submittedParameters']['quality'] is None,'configSnapshotPresent':bool(rec['configSnapshot']),'generationRecord':str(g),'references':[]}
 for kind,key in [('prompt','prompt'),('request','request'),('receipt','receipt')]:
  path=Path(rec[key] if kind=='prompt' else rec['evidence'][key]);expected=rec['promptSha256'] if kind=='prompt' else rec['evidence'][key+'Sha256']
  check[kind+'Exists']=path.exists();check[kind+'ShaMatches']=path.exists() and sha(path)==expected
 for ref in rec['references']:
  rp=Path(ref['path']);present=rp.exists();match=sha(rp)==ref['sha256'] if present else None
  check['references'].append({'path':str(rp),'role':ref['role'],'sha256':ref['sha256'],'existsNow':present,'shaMatchesNow':match})
  if not present: issues.append({'patch':pid,'kind':'reference_missing_now','path':str(rp),'recordedSha':ref['sha256']})
 if 'ingestException' in rec: check['ingestException']=rec['ingestException']
 inventory.append(check)
qa=ROOT/'qa'
for c in range(1,4):
 canvas=Image.new('RGB',(768,1024),'white')
 for r in range(1,4):
  p=qa/f'p{r}{c}-p{r}{c+1}-vertical.png'
  if p.exists():canvas.paste(Image.open(p),((r-1)*256,0))
 canvas.save(qa/f'gate-vertical-col{c}-100pct.png')
for r in range(1,3):
 canvas=Image.new('RGB',(1024,1024),'white')
 for c in range(1,5):
  p=qa/f'p{r}{c}-p{r+1}{c}-horizontal.png'
  if p.exists():canvas.paste(Image.open(p),(0,(c-1)*256))
 canvas.save(qa/f'gate-horizontal-row{r}-100pct.png')
for r in range(1,3):
 canvas=Image.new('RGB',(1152,384),'white')
 for c in range(1,4):
  p=qa/f'cross-r{r}c{c}-native.png'
  if p.exists():canvas.paste(Image.open(p),((c-1)*384,0))
 canvas.save(qa/f'gate-cross-row{r}-100pct.png')
out={'schemaVersion':1,'tile':'r12_c09','status':'paused_by_capacity_layout_gate','gatePath':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/capacity-layout-gate-20261010.json','createdAt':datetime.now(timezone.utc).isoformat(),'inflight':False,'newImageCallsPaused':True,'newCoordinateExpansionPaused':True,'generatedPositions':sorted(sel['patches']),'nativeFileCount':len(list((ROOT/'native').glob('*.png'))),'selectedPositionCount':len(inventory),'remainingPositions':['p41','p42','p43','p44'],'notStartedTiles':['r13_c09','r14_c09'],'rawRejectedVariants':[{'patch':'p23-v1','reason':'Invented water at coordinate that contains retaining wall; p23-v2 selected.'}],'candidate':manifest['candidate'],'candidateSha256':sha(manifest['candidate']),'candidateComplete':False,'internalReady':False,'formalAccepted':False,'partialCoveragePixels':len(inventory)*1024*1024,'unfilledBottomRowIsPlaceholderNotArtwork':True,'sourceCrop':[115,115,1139,1139],'unscaledNativeCoreCopies':True,'layoutOnlyPixelsUsedInCandidate':False,'inventory':inventory,'currentReplayIssues':issues,'configSourceMissingNow':not Path('D:/work/image/config/image-generation.json').exists(),'p34Exception':'Successful returned image saved using explicitly labeled prior p33 reference SHA/configSnapshot because shared mail style and config paths were absent at ingest. No model/version assertion inferred.','existingQa':{'seamCount':len(manifest['internalSeams']),'crossCount':6,'contactPages':['gate-vertical-col1-100pct.png','gate-vertical-col2-100pct.png','gate-vertical-col3-100pct.png','gate-horizontal-row1-100pct.png','gate-horizontal-row2-100pct.png','gate-cross-row1-100pct.png','gate-cross-row2-100pct.png']},'capacitySensitiveObservations':[{'feature':'Paved road / plaza','location':'Upper rows, strongest open area in p12-p14/p13-p23','risk':'Fence/retaining wall boundary fixes usable footprint. Existing native art must not be treated as proof of 5000-player walkable capacity; pixel-to-world scale and client collision masks are unconfirmed.'},{'feature':'Dock / bridge corner','location':'p24/p34 near right boundary','risk':'Narrow transition is sensitive to collision and desired route width; adjoining east tile is needed to quantify connected capacity.'},{'feature':'Rock and dense shrub coast','location':'p21,p22,p31-p34','risk':'Conservative non-walkable unless engine collision design explicitly allows it. Do not count broad rock surfaces as open plaza.'}],'capacity5000Validated':False,'releaseAuthority':'root','resumeNext':'Only after root releases gate: condition/generate p41 from p31; then p42-p44, complete QA, before any r13/r14 expansion.'}
save(ROOT/'capacity-gate-checkpoint.json',out)
print(json.dumps({'positions':len(inventory),'nativeFiles':out['nativeFileCount'],'seams':len(manifest['internalSeams']),'referenceMissingInstances':len(issues),'allSelected1254':all(x['dimensions']==[1254,1254] for x in inventory),'allCoreExact':all(x['candidateCoreByteIdentical'] for x in inventory),'allNativeShaMatch':all(x['nativeShaMatchesRecord'] for x in inventory),'candidateSha256':out['candidateSha256']}))

