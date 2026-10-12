from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
# Reclassify newly observed internal repair-boundary defects without deleting history.
sp=Z/'r10_c08/selected-patches.json';s=read(sp)
snapshot=Z/'r10_c08/selected-before-active-review-20261011.json'
if not snapshot.exists():write(snapshot,s)
s.update(internalReady=False,status='full_candidate_internal_repair_boundary_geometry_open',activeReview='qa/active-review-20261011.json');write(sp,s)
write(Z/'r10_c08/qa/active-review-20261011.json',dict(updatedAt=now,internalReady=False,formalAccepted=False,reason='Latest independent external context revealed actual geometry steps along an internal generated-joint adoption edge',issues=[dict(id='G3',worldX=31117,worldY=[40830,40950],type='small contour steps at bench repair left adoption boundary'),dict(id='C2',worldX=32371,type='straight shadow cutoff at bench right adoption boundary')],evidence=str(Z/'seam-qa/independent-20261010/r11_c08-final-external/independent-review.json'),historyPreserved=True))
# Export only the 12 actually selected native cores as a transparent partial.
T=Z/'r12_c08';sel=read(T/'selected-patches.json');canvas=Image.new('RGBA',(4096,4096),(0,0,0,0));sources=[]
for pid,rel in sorted(sel['patches'].items()):
 p=T/rel;im=Image.open(p).convert('RGBA');assert im.size==(1254,1254)
 xy=((int(pid[2])-1)*1024,(int(pid[1])-1)*1024);canvas.paste(im.crop((115,115,1139,1139)),xy);sources.append(dict(patch=pid,file=str(p),sha256=sha(p),crop=[115,115,1139,1139],destination=list(xy)))
cp=T/'candidate/r12_c08-partial-12cores-4096.png';cp.parent.mkdir(exist_ok=True);canvas.save(cp)
write(str(cp)+'.derivation.json',dict(file=str(cp),sha256=sha(cp),classification='INCOMPLETE partial assembly; transparent pixels are missing, not generated',coreCount=12,coverage=0.75,dimensions=[4096,4096],resampling=False,sources=sources,missing=['p14','p42','p43','p44'],internalReady=False,formalAccepted=False))
# Inspect full candidates and keep delivery index honest about active review state.
entries=[];full=0;ready=0;accepted=0
allp=[f'p{r}{c}' for r in range(1,5) for c in range(1,5)]
for r in range(8,15):
 for c in range(8,15):
  name=f'r{r:02}_c{c:02}';t=Z/name;sp=t/'selected-patches.json';override=t/'selected-continuation-20261011.json'
  if override.exists():sp=override
  if not sp.exists():entries.append(dict(tile=name,status='not_generated',selectedPositions=0,missing=allp));continue
  d=read(sp);patches=d.get('patches',{});n=len(patches);item=dict(tile=name,selection=str(sp),selectionSha256=sha(sp),selectedPositions=n,missing=[p for p in allp if p not in patches],internalReady=bool(d.get('internalReady',False)),formalAccepted=bool(d.get('formalAccepted',False)))
  if n==16:
   full+=1;expected=np.zeros((4096,4096,3),np.uint8)
   for pid,rel in patches.items():expected[(int(pid[1])-1)*1024:int(pid[1])*1024,(int(pid[2])-1)*1024:int(pid[2])*1024]=np.asarray(Image.open(t/rel).convert('RGB'))[115:1139,115:1139]
   cand=d.get('candidate');cand=cand.get('file') if isinstance(cand,dict) else cand
   path=Path(cand) if cand else None
   if path is not None and not path.is_absolute():path=t/path
   if path is None or not path.exists() or not np.array_equal(np.asarray(Image.open(path).convert('RGB')),expected):
    path=t/'candidate/active-core-assembly-20261011.png';path.parent.mkdir(exist_ok=True);Image.fromarray(expected).save(path);write(str(path)+'.derivation.json',dict(operation='16 exact current native core crops; no resize',selection=str(sp),selectionSha256=sha(sp),formalAccepted=False))
   item.update(candidate=str(path),candidateSha256=sha(path),dimensions=[4096,4096],exactMatchToSelectedCores=True,status='internal_ready_external_pending' if item['internalReady'] else 'full_candidate_known_defects')
  else:item['status']='partial'
  ready+=int(item['internalReady']);accepted+=int(item['formalAccepted']);entries.append(item)
report=dict(updatedAt=now,scope='southeast rows8..14 cols8..14 only',totalTiles=49,fullCoverageCandidateCount=full,internalPassedCount=ready,formalAcceptedCount=accepted,fullCandidatesWithExternalAcceptancePending=full,selectedNativePositions=sum(e.get('selectedPositions',0) for e in entries),remainingIncompleteTiles=49-full,entries=entries,all49Complete=False,network=dict(state='latest_subagent_builtin_request_permission_revoked; no further network requests',latestSuccessfulRootOutput=str(T/'native/p41-v1.png'),latestSuccessfulRootSha256=sha(T/'native/p41-v1.png'),errors=['south10 p43: Fatal error: application network permission was revoked; no output','prior subagent response:401 unauthorized; no alternate provider used']),git='No Git or migration internals modified',next=['Restore network authorization before further imagegen','r12c08: p14 lower-wall and rock geometry repair; p42/p43/p44 missing; local rail joint saved but not promoted','r12c10: p43/p44 missing; G1 stairs and G2 railing repair, G3 shared deck adoption bottom','r12c09: G3 at y47219 requires geometry repair before internal readiness can be restored','r10c08: internal joint G3/C2 and external deck G2 require native repair','r09c09: continue from current four saved bottom-row cores'])
write(Z/'delivery-index-20261011.json',report);write(Z/'local-continuation-20261011.json',report)
roundpath=Z/'continuation-round-20261011.json';rd=read(roundpath);rd.update(updatedAt=now,currentCoordinate='r12_c08/p42 pending generation; p14 local rail candidate saved',candidateCount=full,internalPassedCount=ready,formalAcceptedCount=accepted,deliveryIndex=str(Z/'delivery-index-20261011.json'),networkState=report['network'],next=report['next']);write(roundpath,rd)
print(json.dumps({k:report[k] for k in ('fullCoverageCandidateCount','internalPassedCount','formalAcceptedCount','selectedNativePositions','remainingIncompleteTiles')}))

