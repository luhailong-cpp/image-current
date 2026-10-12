from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verified_candidate(T,sel,olde):
 candidates=[]
 cand=sel.get('candidate');cand=cand.get('file') if isinstance(cand,dict) else cand
 if cand:candidates.append(cand)
 if olde.get('candidate'):candidates.append(olde['candidate'])
 if (T/'qa').exists():
  for p in sorted((T/'qa').glob('*/manifest.json'),key=lambda p:p.stat().st_mtime,reverse=True):
   m=read(p)
   if not isinstance(m,dict):continue
   v=m.get('candidate')
   v=v.get('file') if isinstance(v,dict) else v
   if not v and (p.parent/'candidate-4096.png').exists():v=str(p.parent/'candidate-4096.png')
   if v:candidates.append(v)
 sources={}
 for k,v in sel.get('patches',{}).items():
  v=(v.get('file') or v.get('path')) if isinstance(v,dict) else v
  p=Path(v);p=p if p.is_absolute() else T/p
  if not p.exists():return None
  im=Image.open(p).convert('RGB')
  if im.size!=(1254,1254):return None
  sources[k]=(p,np.asarray(im)[115:1139,115:1139].copy(),sha(p))
 seen=set()
 for v in candidates:
  p=Path(v);p=p if p.is_absolute() else T/p
  if str(p).lower() in seen or not p.exists():continue
  seen.add(str(p).lower())
  im=Image.open(p).convert('RGB')
  if im.size!=(4096,4096):continue
  a=np.asarray(im);good=True
  for k,(_,core,_) in sources.items():
   r,c=int(k[1])-1,int(k[2])-1
   if not np.array_equal(a[r*1024:(r+1)*1024,c*1024:(c+1)*1024],core):good=False;break
  if good:return p,[dict(patch=k,file=str(v[0]),sha256=v[2]) for k,v in sources.items()]
 return None
now=datetime.now(timezone.utc).isoformat()
current_tile=sys.argv[1] if len(sys.argv)>1 else 'r13_c08'
current_patch=sys.argv[2] if len(sys.argv)>2 else 'p23'
old=read(Z/'delivery-index-20261011.json')
previous={e['tile']:e for e in old['entries']}
existing=Z/'delivery-index-20261012.json'
if existing.exists(): previous.update({e['tile']:e for e in read(existing)['entries']})
entries=[]; generation_count=0
for r in range(8,15):
 for c in range(8,15):
  tile=f'r{r:02}_c{c:02}'; T=Z/tile; sp=T/'selected-patches.json'; olde=previous[tile]
  patches={}; sel={}
  if sp.exists(): sel=read(sp); patches=sel.get('patches',{})
  n=len(patches); missing=[f'p{a}{b}' for a in range(1,5) for b in range(1,5) if f'p{a}{b}' not in patches]
  e=dict(tile=tile,selectedPositions=n,missing=missing,internalReady=bool(sel.get('internalReady',False)),formalAccepted=False,status='not_generated' if not n else 'partial')
  if sp.exists(): e.update(selection=str(sp),selectionSha256=sha(sp))
  if n==16:
   checked=verified_candidate(T,sel,olde)
   if checked and sha(sp)==e['selectionSha256']:
    cp,source_records=checked
    e.update(candidate=str(cp),candidateSha256=sha(cp),dimensions=[4096,4096],coreReplayVerified=True,sources=source_records,status='internal_ready_external_pending' if e['internalReady'] else 'full_candidate_QA_or_repairs_pending')
   else:e.update(internalReady=False,status='full_native_selection_candidate_rebuild_or_review_pending')
  generation_count+=len({str(p).lower() for p in T.rglob('*.png.generation.json')})
  entries.append(e)
d=dict(updatedAt=now,scope='southeast rows8..14 cols8..14 only',totalTiles=49,fullCoverageCandidateCount=sum('candidate' in e for e in entries),internalPassedCount=sum(e['internalReady'] for e in entries),formalAcceptedCount=0,selectedNativePositions=sum(e['selectedPositions'] for e in entries),generatedNativeCount=generation_count,entries=entries,all49Complete=False,productionAuthorization='D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json',historicalIndex=str(Z/'delivery-index-20261011.json'),generationState='resumed_builtin_requests',gitOperations=False)
d['remainingIncompleteTiles']=49-d['fullCoverageCandidateCount']
d['missingSelectedPositions']=784-d['selectedNativePositions']
model_rule=Z.parents[3]/'docs/IMAGE_MODEL_REQUIREMENT.md'
root_rule=Z.parents[3]/'AGENTS.md'
model_hold=model_rule.exists() and 'verified GPT Image 2.5' in model_rule.read_text(encoding='utf-8-sig')
if model_hold:d.update(generationState='paused_required_image_model_route_unverified',requestedImageModel='GPT Image 2.5',actualImageModel=None,newImageGenerationAllowed=False,modelRequirement=str(model_rule),modelRequirementSha256=sha(model_rule),rootInstructions=str(root_rule),rootInstructionsSha256=sha(root_rule) if root_rule.exists() else None,localQAAllowed=True)
else:d.update(generationState='resumed_builtin_free_included_fallback_allowed',preferredImageModel='GPT Image 2.5',fallbackImageModel='GPT Image 2.0',actualImageModel=None,newImageGenerationAllowed=True,modelRequirement=str(model_rule),modelRequirementSha256=sha(model_rule) if model_rule.exists() else None,rootInstructions=str(root_rule),rootInstructionsSha256=sha(root_rule) if root_rule.exists() else None)
write(Z/'delivery-index-20261012.json',d)
p=read(Z/'progress.json')
p.update(updatedAt=now,status='native_generation_and_seam_QA_in_progress',generationStopped=False,currentTile='r12_c08',currentPatch='p43',latestNetworkError=None,fullCoverageCandidateCount=d['fullCoverageCandidateCount'],internalPassedCount=d['internalPassedCount'],formalAcceptedCount=0,complete4kCount=0,selectedNativePositions=d['selectedNativePositions'],generatedNativeCount=generation_count,missingSelectedPatchPositions=d['missingSelectedPositions'],deliveryIndex=str(Z/'delivery-index-20261012.json'),productionResume=str(Z/'production-resume-20261012.json'),nextStep='Continue missing native patches and targeted seam repairs under 20261012 resume authorization; upload owner captures new assets separately.')
p.update(currentTile=current_tile,currentPatch=current_patch)
p.update(deduplicatedTargetTileCount=49,fullyDrawn16PatchTileCount=sum(e['selectedPositions']==16 for e in entries),tilesStillMissingNativePatches=sum(e['selectedPositions']<16 for e in entries),fullyDrawnButInternalReviewPendingCount=sum(e['selectedPositions']==16 and not e['internalReady'] for e in entries),assembled4kCandidateCount=d['fullCoverageCandidateCount'],internallyReviewed4kCount=d['internalPassedCount'],tilesWithoutComplete4kCandidate=49-d['fullCoverageCandidateCount'],complete4kCountBasis='legacy formal external acceptance count; not the count of fully drawn 16-patch tiles',nextPreparedCoordinate=f'{current_tile}/{current_patch}')
p['activeTiles']=[dict(tile=e['tile'],selectedPatchPositions=e['selectedPositions'],targetPatchPositions=16,selectedManifest=e.get('selection'),status=e['status'],assembled4kCandidate='candidate' in e,internalReady=e['internalReady'],formalAccepted=False) for e in entries if e['selectedPositions']]
if model_hold:p.update(status='local_QA_active_new_generation_paused_model_gate',generationStopped=True,newImageGenerationAllowed=False,requestedImageModel='GPT Image 2.5',actualImageModel=None,modelRequirement=str(model_rule),rootInstructions=str(root_rule),nextStep='Finish permitted local assembly, review and delivery inventory; missing artwork and AI seam repairs await a verifiable GPT Image 2.5 route. Paid API is not authorized.',generationPauseReason='Built-in tool does not expose a verifiable GPT Image 2.5 selector or actual returned model; new project rules prohibit further unverified generation.',localQAAllowed=True)
else:p.update(generationStopped=False,newImageGenerationAllowed=True,generationPauseReason=None,preferredImageModel='GPT Image 2.5',fallbackImageModel='GPT Image 2.0',actualImageModel=None,modelRequirement=str(model_rule),rootInstructions=str(root_rule))
try: write(Z/'progress.json',p)
except OSError as ex:
 write(Z/'progress-resume-20261012.json',p)
 d['normalProgressWriteError']=str(ex); write(Z/'delivery-index-20261012.json',d)
rd=read(Z/'production-resume-20261012.json')
if not rd.get('firstNewOutput'):
 g=read(Z/'r12_c08/native/p42-v2.png.generation.json')
 rd['firstNewOutput']=dict(file=g['file'],sha256=g['sha256'],nativeDimensions=g['nativeDimensions'],receipt=str(Z/'r12_c08/p42-v2.receipt.json'),receivedAt=read(Z/'r12_c08/p42-v2.receipt.json')['receivedAt'])
rd.update(updatedAtUtc=now,status='actual_generation_resumed_new_native_output_saved',currentCoordinate='r12_c08/p43',fullCoverageCandidates=d['fullCoverageCandidateCount'],internalPassed=d['internalPassedCount'],formalAccepted=0,selectedNativePositions=d['selectedNativePositions'],missingNativePositions=d['missingSelectedPositions'],deliveryIndex=str(Z/'delivery-index-20261012.json'),internalQA='New partial native patches require seam inspection; prior 7 internal-ready candidates retained',externalQA='All 9 prior full candidates still await complete external acceptance',next=['r12_c08 p43,p44 and p14 targeted repair','r12_c10 p43,p44 and targeted G1/G2 repair','r09_c09 missing upper three rows','r12_c09 shared G3 and r10_c08 defects remain pending'])
rd.update(currentCoordinate=f'{current_tile}/{current_patch}',internalQA='Current internal pass count is taken from tile-local reviewed selections; all reported 4096 candidates replay exactly from current selected cores; targeted joints remain material pending',externalQA='Complete current neighbor seam/cross reviews are required before formal acceptance',next=['Continue r14_c08 then r09_c08 and r08_c08 original native patches','Finish col10 current QA and missing tiles','Continue r08_c09 native production','Finish r10_c08 bench/deck and shared wall/stairs material repairs','Complete remaining cols11..14 native tiles and all external QA'])
if model_hold:rd.update(status='new_generation_paused_required_GPT_Image_2_5_route_unverified_local_QA_allowed',requestedImageModel='GPT Image 2.5',actualModel=None,actualQuality=None,newArtworkGenerationAllowed=False,modelRequirement=str(model_rule),modelRequirementSha256=sha(model_rule),rootInstructions=str(root_rule),rootInstructionsSha256=sha(root_rule) if root_rule.exists() else None,paidApiAllowed=False,localQAAllowed=True,next=['Finish existing native output recovery and local QA/inventory','Resume missing native artwork and AI repairs only after explicit verifiable GPT Image 2.5 route is available; no fallback or paid route authorized'])
else:rd.update(newArtworkGenerationAllowed=True,preferredImageModel='GPT Image 2.5',fallbackImageModel='GPT Image 2.0',actualModel=None,actualQuality=None,modelPreference='Free/existing included 2.5 preferred; builtin fallback explicitly allowed, unknown returned model stays null',modelRequirement=str(model_rule),modelRequirementSha256=sha(model_rule) if model_rule.exists() else None,rootInstructions=str(root_rule),rootInstructionsSha256=sha(root_rule) if root_rule.exists() else None,paidApiAllowed=False)
write(Z/'production-resume-20261012.json',rd)
print(json.dumps({k:d[k] for k in ['fullCoverageCandidateCount','internalPassedCount','selectedNativePositions','generatedNativeCount','missingSelectedPositions']}))
