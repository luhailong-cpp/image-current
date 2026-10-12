from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import production as p
mp=ROOT/'qa'/'expansion-east-worker-map.json';d=p.load(mp)
owned=[]
for rp in (ROOT/'native').glob('*.png.generation.json'):
    stem=rp.name.removesuffix('.png.generation.json')
    if stem.startswith(('r09_c05_','r10_c05_')):
        rec=p.load(rp);fp=ROOT/'native'/f'{stem}.png';assert fp.exists() and p.hashfile(fp)==rec['sha256']
        assert Path(rec['prompt']).exists() and p.hashfile(rec['prompt'])==rec['promptSha256']
        assert (ROOT/'receipts'/f'{stem}.tool.json').exists()
        owned.append({'stem':stem,'file':fp.as_posix(),'sha256':rec['sha256'],'record':rp.as_posix(),'toolOriginalOutsideWorkspace':rec.get('sourceToolPath'),'toolOriginalRequiredForMigration':False})
requests=[q for q in (ROOT/'prompts').glob('*.request.json') if q.name.startswith(('r09_c05_','r10_c05_'))]
pending=[q.stem.removesuffix('.request') for q in requests if not (ROOT/'native'/(q.name.removesuffix('.request.json')+'.png')).exists()]
assert not pending,pending
stopped=p.now();d.update({'status':'migration_frozen','migrationFrozenAtUtc':stopped,'inFlight':False,'unsavedSuccessfulOutput':False})
p.dump(mp,d)
selected={t:d.get(t,[[None]*4 for _ in range(4)]) for t in d['assignedTiles']}
missing=[]
for tile,grid in selected.items():
    slots=[f's{r+1:02}_{c+1:02}' for r in range(4) for c in range(4) if not grid[r][c]]
    if slots:missing.append({'tile':tile,'missingSlots':slots})
refs=[p.metadata(*ref) for ref in p.REFS]
for ref in refs:assert Path(ref['path']).is_file()
artifacts=d.get('candidateArtifacts',{})
for art in artifacts.values():assert p.hashfile(art['path'])==art['sha256']
freeze={'worker':'finish_c04/east','status':'migration_frozen','stoppedAtUtc':stopped,'freezeReason':'Parent relayed user request to commit/push and migrate to another computer; no further generation or repair requests.','inFlight':False,'inFlightRequestCount':0,'unsavedSuccessfulOutput':False,'unsavedSuccessfulOutputCount':0,'pendingPreparedRequestsWithoutNative':pending,'lastSuccessfulSavedSource':next(x for x in owned if x['stem']=='r10_c05_s01_03_v01'),'selectedMap':{'path':mp.as_posix(),'sha256':p.hashfile(mp),'selectedSlots':selected},'currentCandidates':artifacts,'savedNativeCount':len(owned),'savedNatives':owned,'remainingSlotCount':sum(len(x['missingSlots']) for x in missing),'missingTilesAndSlots':missing,'resumeCheckpoint':{'nextTile':'r10_c05','nextCore':'s01_04','nextGuidePrepared':False,'r10_c05':'3 of 16 selected; no assembled tile yet; seam QA pending','r09_c05':'16 base cores plus 1 local round-cap repair in adopted 17-source candidate; 24 native strips and 9 junctions reviewed; west border exceptions remain','remainingBoundaryRepairs':p.load(ROOT/'qa'/'east-r09c05-native-review.json')['remainingBoundaryIssues'],'reviewReport':str(ROOT/'qa'/'east-r09c05-native-review.json'),'doNotAdoptTrial':'east-r09c05-groundselect-v01 introduced paving mismatch; adopted version is groundselect-v02','rawRejectedButRetained':'r09_c05_s03_02_v01 has extra flower wall relief; selected v02 removes it'},'requiredInputsOutsideSouthwest':refs,'requiredInputsOutsideWorkspace':[],'outsideWorkspaceNotes':'Imagegen originals under C:/Users/luyua/.codex/generated_images are duplicated byte-for-byte in southwest/native and not required to resume. Python runtime and builtin imagegen tool are environment capabilities, not artwork inputs.','allOuterTileEdgesPassed':False,'formalAccepted':False,'artworkOperationsFrozen':True,'noDeletionPerformed':True,'noGitPerformedByWorker':True,'helperFiles':['qa/expansion-east-worker.py','qa/expansion-east-assemble.py','qa/expansion-east-repair-prepare.py','qa/expansion-east-reselect.py'],'preservation':'All originals, rejected variants, working guides, previews, source masks, prompts, receipts, generation records, QA trials and adopted candidates retained.'}
fp=ROOT/'qa'/'expansion-east-migration-freeze-20261011.json';p.dump(fp,freeze)
print(json.dumps({'freeze':fp.as_posix(),'stoppedAtUtc':stopped,'savedNativeCount':len(owned),'remainingSlotCount':freeze['remainingSlotCount'],'inFlight':False,'unsavedSuccessfulOutput':False,'selectedMapSha256':p.hashfile(mp)}))
