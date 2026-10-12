from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,shutil
Z=Path(__file__).resolve().parents[1]
WORK=Path('D:/work/image')
def rd(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):
 p=Path(p); return {'path':p.as_posix(),'workspaceRelativePath':p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else None,'sha256':sha(p),'bytes':p.stat().st_size}
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
w=rd(Z/'qa/west-migration-freeze-20261011.json')
r=rd(Z/'qa/right-migration-freeze-20261011.json')
c=rd(Z/'qa/connected-migration-freeze-20261011.json')
assert r['inflightCount']==c['inflightCount']==0
assert r['unarchivedUniqueOutputCount']==c['unarchivedUniqueOutputCount']==0
assert w.get('inflightCount')==0 and w.get('unarchivedUniqueOutputCount')==0
native=list((Z/'native').glob('*.png'))
byhash={}
for p in native: byhash.setdefault(sha(p),[]).append(p)
rootraw=Path('C:/Users/luyua/.codex/generated_images/01a1216d-5a60-7332-b4ee-8acad0d64dba')
archive=[]; recovered=[]
for p in sorted(rootraw.glob('*.png')):
 h=sha(p); dests=byhash.get(h,[])
 if not dests:
  out=Z/'migration-recovered-outputs'/p.name;out.parent.mkdir(exist_ok=True)
  if out.exists(): assert sha(out)==h
  else: shutil.copy2(p,out)
  dests=[out]; recovered.append(rec(out))
 archive.append({'originalPath':p.as_posix(),'sha256':h,'archivedCopies':[rec(x) for x in dests],'rawFilePreserved':True})
save(Z/'qa/root-generated-output-migration-inventory-20261011.json',{'createdAtUtc':now,'outputCount':len(archive),'archive':archive,'recoveredPreviouslyUnindexed':recovered,'allUniqueOutputsArchived':True,'inflightCount':0,'unarchivedUniqueOutputCount':0,'notNewGeneration':True})
adopt={}
for mp in ['qa/connected-closure-current-v5.manifest.json','qa/connected-r04-r05-current-v5.manifest.json']:
 for item in rd(Z/mp)['tiles']:
  for k in ['image','record']: assert sha(Path(item[k]['path']))==item[k]['sha256']
  adopt[item['tileId']]={**item,'selectionBasis':mp,'internalClosurePassedBeforeFreeze':True,'formalAccepted':False}
for item in w['selectedCandidates']:
 adopt[item['tileId']]={'tileId':item['tileId'],'image':item['candidate'],'record':item['record'],'selectionBasis':'qa/west-migration-freeze-20261011.json','internalClosurePassedBeforeFreeze':item['internalClosurePassed'],'formalAccepted':False}
assert len(adopt)==8
rootstems=[]
for sr in range(1,5):
 for sc in range(1,5):
  if (sr,sc)==(4,4):continue
  a='a02' if (sr,sc) in [(1,3),(2,4)] else 'a01'
  rootstems.append(f'r06_c03_s{sr:02d}_{sc:02d}_{a}')
partials={}
for tile,stems in [('r06_c03',rootstems),('r06_c04',r['provisionalSelected'])]:
 cells=[]
 for stem in stems:
  p=Z/'native'/f'{stem}.png';g=Path(str(p)+'.generation.json')
  assert sha(p)==rd(g)['sha256']
  cells.append({'stem':stem,'image':rec(p),'generationRecord':rec(g),'receipt':rec(Z/'receipts'/f'{stem}.receipt.json'),'selection':'provisional_not_assembled_or_QA_accepted'})
 partials[tile]={'selectedCount':len(cells),'requiredCount':16,'cells':cells,'assembled4k':False,'internalClosurePassed':False}
present={k:{f's{sr:02d}_{sc:02d}' for sr in range(1,5) for sc in range(1,5)} for k in adopt}
for tile,part in partials.items():present[tile]={x['stem'][8:14] for x in part['cells']}
missing={f'r{tr:02d}_c{tc:02d}':[f's{sr:02d}_{sc:02d}' for sr in range(1,5) for sc in range(1,5) if f's{sr:02d}_{sc:02d}' not in present.get(f'r{tr:02d}_c{tc:02d}',set())] for tr in range(1,8) for tc in range(1,8)}
# Explicit indices select existing bytes only; no art assembly or QA runs.
idx={'schemaVersion':1,'createdAtUtc':now,'zone':'northwest','selectionPolicy':'One existing actual 4096 candidate per full tile; no newest-file inference. Partial cells remain provisional.','tiles':[adopt[k] for k in sorted(adopt)],'partialTiles':partials,'target4kCount':49,'assembledCandidateTileCount':8,'internalPassed4kCount':7,'formalAcceptedCount':0,'wholeZoneComplete':False}
save(Z/'migration-current-adopted-20261011.json',idx)
freeze=rd(Z/'migration-freeze-20261011.json')
freeze.update(status='migration_frozen_archive_complete',archivalCompletedAtUtc=now,inflightCount=0,unarchivedUniqueOutputCount=0,inflightCountRoot=0,unarchivedUniqueOutputCountRoot=0,aggregateInflightCount=0,subtaskRuntimeSnapshot={x:'completed_local_archive_and_stopped' for x in ['connected_closure','right_completion','west_closure']},currentAdoptedIndex=rec(Z/'migration-current-adopted-20261011.json'),currentAdoptedIndexStatus='complete_existing_bytes_only',lastSavedRootNative=rec(Z/'native/r06_c03_s04_03_a01.png'),rootRecoveredLastOutputSource='C:/Users/luyua/.codex/generated_images/01a1216d-5a60-7332-b4ee-8acad0d64dba/exec-d20a3c6c-a3cb-4dbf-a8b6-bc6d10bfa859.png',rootUnarchivedSource=None,rootOutputInventory=rec(Z/'qa/root-generated-output-migration-inventory-20261011.json'),subtaskArchives=[rec(Z/'qa'/f'{owner}-migration-freeze-20261011.json') for owner in ['right','west','connected']],target4kCount=49,assembledCandidateTileCount=8,internalPassed4kCount=7,formalAcceptedCount=0,selectedNativeCoordinateCount=sum(map(len,present.values())),missingNativeCoordinateCount=sum(map(len,missing.values())),missingNativeCoordinates=missing,fullyMissingTileIds=[k for k,v in missing.items() if len(v)==16],partialNativeTileIds=['r06_c03','r06_c04'],generatedNativePngCount=len(native),selectedPartialRootAttemptMatrix=[['a01','a01','a02','a01'],['a01','a01','a01','a02'],['a01','a01','a01','a01'],['a01','a01','a01',None]],remainingRootWork=['r06_c03_s04_04 has no generation; no new guide was prepared after freeze.','r06_c03 has 15/16 provisional native cells, no 4096 assembly or internal33 QA yet.','r06_c03_s01_04 stone rail is visibly softer than adjacent material; rail geometry continuity with r06_c04 still needs resolution.','Keep rejected r06c03 s01c03a01 grout-offset and s02c04a01 missing-third-rail versions as history.','r04c02 v3 has pending recorded repairs and latest33 QA; two raw eastupper/eastroof repairs archived but not composited.','r04/r05 connected group17 shared crops and full lantern passed before freeze; final closure.json not yet created. Outer edges and full-zone acceptance remain pending.','r05c03 connected south edge changed7 pixels at x4089..4095 versus v8; r05c04 south unchanged versus v4. Use pinned current versions when resuming shared seams.'],outsideWorkspaceMustCarryUniqueReferences=[],outsideWorkspaceRawOutputHandling='Original generated files remain on C: and all root unique output bytes have workspace copies in native or migration-recovered-outputs; source-to-copy hashes are in inventory. Agents attest0 unarchived; their external ancestry inventories retained.',workspaceReferencesOutsideZone=[str(Z.parent/'production-contract.json'),'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png','D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-detail-v1.png','D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg'],historicalMissingReference={'path':'D:/work/image/designs/mail-ui-v1/01-mail-event.png','status':'already missing before freeze; historical exception retained; do not falsify or substitute old evidence'},portability='All existing provenance JSON paths remain unchanged. Migration current index and root inventory include workspaceRelativePath for relocation. Preserve the full northwest directory and referenced files in the workspace, including old candidates, native sources, guides, masks, NPZ source planes and previews.',newGenerationAfterFreeze=0,newArtCompositesAfterFreeze=0,gitOperationsPerformed=False,noDeletion=True,resumeRequiresFreshUserAuthorization=True,wholeZoneComplete=False)
save(Z/'migration-freeze-20261011.json',freeze)
p=Z/'progress.json';d=rd(p);d.update(status='migration_frozen_incomplete',updatedAtUtc=now,generationHold=True,nextStep='Migration freeze: do not resume art until fresh user authorization. Use migration-freeze-20261011.json and migration-current-adopted-20261011.json.',generatedNativeCount=len(native),candidateCoordinateCount=sum(map(len,present.values())),assembledCandidateTileCount=8,fullyCovered4kCount=8,internalPassed4kCount=7,usableNativeCount=112,formalAcceptedCount=0,complete4kCount=0,currentTile='r06_c03',currentPatch='r06_c03_s04_04_missing_not_started',latest4kCandidate=adopt['r05_c03']['image']['path'],currentAdoptedIndex='migration-current-adopted-20261011.json',missingNativeCoordinateCount=sum(map(len,missing.values())),connectedClusterCount=2,connectedInternalSeamsPassed=34,externalPassed4kCount=0,inflightCount=0,unarchivedUniqueOutputCount=0,freezeRecord='migration-freeze-20261011.json',staleCountersCorrected=True);save(p,d)
p=Z/'local-continuation-20261011.json';d=rd(p);d.update(status='migration_frozen_incomplete',updatedAtUtc=now,candidateTileIds=sorted(adopt),candidateTileCount=8,internalPassedTileIds=[k for k,v in adopt.items() if v['internalClosurePassedBeforeFreeze']],missingNativeCoordinates=missing,currentAdoptedIndex='migration-current-adopted-20261011.json',inflightCount=0,unarchivedUniqueOutputCount=0);save(p,d)
print(json.dumps({'status':freeze['status'],'rawPngs':len(native),'assembledCandidates':8,'internalPassed':7,'formalAccepted':0,'selectedNativeCoordinates':freeze['selectedNativeCoordinateCount'],'missingNativeCoordinates':freeze['missingNativeCoordinateCount'],'rootGeneratedOutputsChecked':len(archive),'previouslyUnindexedRecovered':len(recovered),'inflight':0,'unarchivedUnique':0,'freezeSha256':sha(Z/'migration-freeze-20261011.json')},ensure_ascii=False))
