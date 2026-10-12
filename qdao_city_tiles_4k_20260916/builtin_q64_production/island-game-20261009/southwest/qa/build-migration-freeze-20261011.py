"""Freeze existing southwest artifacts and exact continuation state; no image generation."""
import sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *

idx=load(ROOT/'current-native-map.json')
worker_freezes={}
worker_maps={}
for region in ['north','east','west','central']:
 p=ROOT/'qa'/f'expansion-{region}-worker-map.json'
 if not p.exists():continue
 d=load(p);worker_maps[region]=str(p)
 for tile,arr in d.items():
  if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list):idx[tile]=arr
 for tile,art in d.get('candidateArtifacts',{}).items():idx.setdefault('candidateArtifacts',{})[tile]=art
 f=ROOT/'qa'/f'expansion-{region}-migration-freeze-20261011.json'
 if f.exists():worker_freezes[region]={'path':str(f),'contents':load(f)}

# The east review explicitly completed internal checks; west edge exceptions remain open.
east=idx['candidateArtifacts'].get('r09_c05')
if east and (ROOT/'qa/east-r09c05-native-review.json').exists():
 east.update(internalPassed=True,internalTileSeamsPassed=True,internalStatus='pass; west external boundary exceptions remain',formalAccepted=False)
idx['updatedAtUtc']=now()
dump(ROOT/'current-native-map.json',idx)
remaining={};selected=0
for r in range(8,15):
 for c in range(1,8):
  tile=f'r{r:02}_c{c:02}';arr=idx.get(tile,[[None]*4 for _ in range(4)])
  selected+=sum(bool(s) for row in arr for s in row)
  missing=[{'subrow':sr+1,'subcolumn':sc+1} for sr,row in enumerate(arr) for sc,s in enumerate(row) if not s]
  if missing:remaining[tile]=missing
records=list((ROOT/'native').glob('*.png.generation.json'))
arts=idx['candidateArtifacts'];adopted={}
for tile,a in arts.items():
 p=Path(a['path']);assert p.exists()
 adopted[tile]={**a,'sha256':hashfile(p),'workspaceRelativePath':p.relative_to(REPO).as_posix(),'zoneRelativePath':p.relative_to(ROOT).as_posix()}
missing_outputs=[str(p) for p in records if not Path(load(p)['file']).exists()]
pending_workers=[r for r in ['north','east','west'] if r not in worker_freezes]
freeze_path=ROOT/'migration-freeze-20261011.json'
old=load(freeze_path) if freeze_path.exists() else {}
state={
 'freezeRequestedAtUtc':old.get('freezeRequestedAtUtc'),
 'freezeRequestTimeNote':'Exact incoming message timestamp unavailable; root stop observed by clock at 2026-10-12T02:29:35Z.',
 'rootStoppedObservedAtUtc':old.get('rootStoppedObservedAtUtc','2026-10-12T02:29:35+00:00'),
 'updatedAtUtc':now(),'userLocalDate':'2026-10-11','timezone':'America/New_York',
 'status':'frozen' if not pending_workers else 'root_frozen_waiting_for_worker_save_confirmations',
 'reason':'Migration stop relayed by coordinator; stop new generation, retain all existing artifacts.',
 'newGenerationAllowed':False,'rootInFlightRequests':[],
 'workerFreezeConfirmations':worker_freezes,'workersAwaitingConfirmation':pending_workers,
 'remainingInFlightStatus':'none reported' if not pending_workers else 'awaiting worker confirmations; root has none',
 'rootUnsubmittedPreparedRequest':{'stem':'r11_c04_s03_01_v01','request':str(ROOT/'prompts/r11_c04_s03_01_v01.request.json'),'guide':str(ROOT/'guides/r11_c04_s03_01_v01.native-overlap-guide.png'),'submitted':False,'promptSaved':False,'actionOnResume':'Reuse prepared guide/request, inspect guide, write prompt, then submit only after generation is authorized again.'},
 'unsavedSuccessfulOutputs':missing_outputs,'unsavedSuccessfulOutputsDefinition':'Every ingested successful result has a native copy; workers separately confirm any returned/in-flight results.',
 'generatedNativeCount':len(records),'selectedCoreCount':selected,'totalCoreCount':784,
 'missingCoreCount':784-selected,'remainingCoreCoordinates':remaining,
 'completeCandidate4kCount':len(arts),'internallyPassed4kCount':sum(bool(a.get('internalPassed') or a.get('internalTileSeamsPassed')) for a in arts.values()),
 'formalAcceptedCount':0,'remainingTilesWithoutComplete4kCandidate':49-len(arts),
 'adopted4kFiles':adopted,'workerSelectionMaps':worker_maps,
 'continuationOwnership':str(ROOT/'qa/expansion-ownership-20261011.json'),
 'pendingRepairs':[
  {'tile':'r11_c04','core':'r11_c04_s02_04_v01','status':'provisional; NOT passed','globalBox':[15575,42099,15675,42429],'issue':'Artificial stepped gold eave. v02 and v03 failed to remove it.','nextAction':'After remaining eight tile cores, make a centered 1254 native assembled guide and repair the uninterrupted gold eave using builtin imagegen.','rejectedRetries':['r11_c04_s02_04_v02','r11_c04_s02_04_v03']},
  {'tile':'r09_c02','issue':'Vertical fine seam/bamboo node step and polygon material cuts','review':str(ROOT/'qa/c04-hardseam-west-r09c02-v01-review.json')},
  {'tile':'r09_c05','issue':'West x0..115 material/leaf/gold-frame discontinuities near tile-local y909,1950,3185; joint c04/c05 repair needed','review':str(ROOT/'qa/east-r09c05-native-review.json')},
  {'tiles':['r08_c03','r08_c04'],'issue':'North worker native top paving and internal/outer seam checks pending','queue':str(ROOT/'qa/expansion-north-repair-queue.json')}
 ],
 'completedDoNotRedraw':['r09_c03','r09_c04','r10_c03','r10_c04'],
 'r11c03Status':{'internal':'pass root and independent reviewer','north-r10c03':'geometry_pass','otherOuterEdges':'pending unfinished neighbors','review':str(ROOT/'qa/expansion-west-root-r11c03-review.json')},
 'outsideWorkspaceRequiredUniqueReferences':[],
 'portableReferenceCopies':str(ROOT/'migration-inputs-20261011/manifest.json'),
 'sourceOutputAudit':str(ROOT/'qa/migration-reference-and-saved-output-audit-20261011.json'),
 'sharedFilesNeededFromRepository':[str(ROOT.parent/'production-contract.json'),str(REPO/'config/image-generation.json')],
 'relocationNote':'Historical absolute paths must be rebased on the new computer. Preserve prompt/reference hashes and use workspaceRelativePath or zoneRelativePath; do not modify original image pixels.',
 'gitMutationsPerformed':False,'allOriginalsDraftsAndPreviewsRetained':True,
 'migrationOwnerThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4'
}
dump(freeze_path,state)
s=load(ROOT/'progress.json')
s.update(status=state['status'],updatedAtUtc=now(),generationHoldActive=True,generationHoldReason='migration freeze; no new image requests authorized',currentTile='r11_c04',currentPatch='r11_c04_s03_01_v01 prepared only; unsubmitted',nextStep='Migrate saved outputs and metadata; await authorization to resume on new computer.',generatedNativeCount=len(records),selectedCandidateCoreCount=selected,corePositionsCovered=selected,candidate4kCount=len(arts),complete4kCount=len(arts),fullyCovered4kCount=len(arts),internalPassed4kCount=state['internallyPassed4kCount'],formalAcceptedCount=0,remainingTiles=49-len(arts),missingCoreCount=784-selected,remainingCoreCoordinates=remaining,currentAdopted4kFiles={t:a['path'] for t,a in adopted.items()},migrationFreeze=str(freeze_path),networkGenerationBlocked=False)
dump(ROOT/'progress.json',s)
dump(ROOT/'continuation-status-20261011-evening.json',state)
print(json.dumps({k:state[k] for k in ['status','generatedNativeCount','selectedCoreCount','missingCoreCount','completeCandidate4kCount','internallyPassed4kCount','formalAcceptedCount','workersAwaitingConfirmation']},ensure_ascii=False))
