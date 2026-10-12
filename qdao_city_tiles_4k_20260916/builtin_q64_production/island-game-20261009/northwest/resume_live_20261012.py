from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
A=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p): return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
authority=read(A)
assert authority['newArtworkGenerationAllowed'] and authority['builtinOnly'] and not authority['gitMutationsAllowedForProductionWorkers']
historical=[Z/'migration-freeze-20261011.json',Z/'migration-current-adopted-20261011.json']
before={p:sha(p) for p in historical}
current=Z/'current-adopted-20261012.json'
if not current.exists():
 d=read(historical[1]);d.update(createdAtUtc=now,status='resumed_current_selection',resumeAuthority=rec(A),historicalBaseline=rec(historical[1]));write(current,d)
resume=Z/'production-resume-20261012.json'
if not resume.exists():
 write(resume,{'schemaVersion':1,'issuedAtUtc':now,'zone':'northwest','status':'art_production_resumed','authority':rec(A),'userAuthorization':authority['userAuthorization'],'latestDirectUserInstruction':'继续做完给我','builtinOnly':True,'paidApiAllowed':False,'gitMutationsAllowed':False,'fixedUploadSnapshotIndependent':True,'historicalRecordsPreserved':[rec(p) for p in historical],'currentAdoptedIndex':rec(current),'firstNewSavedOutput':None,'target4kCount':49,'assembledCandidateTileCount':8,'internalPassed4kCount':7,'formalAcceptedCount':0,'selectedNativeCoordinateCount':148,'missingNativeCoordinateCount':636,'wholeZoneComplete':False,'remainingWork':'Complete r06_c03 last native and internal QA; r06_c04 remaining11; close r04_c02 then expand west/south/north/east until all49 coordinates and shared/perimeter QA complete.','workers':{'root':'r06_c03 native/assembly/internal QA and current progress','right_completion':'r06_c04 thenr07_c04','west_closure':'r04_c02 closure thenr05_c02/r06_c02','connected_closure':'r04/r05 closure thenr05/r06 shared QA, r07_c03 preparation'},'candidateQA':'8 candidates exist;7 internally passed; r04_c02 stillpending','sharedQA':'2 connected clusters,34 shared crops passed; outer perimeter pending','generationHold':False})
p=read(Z/'progress.json');p.update(status='production_resumed_native_generation',generationHold=False,resumeAuthority=rec(A),currentAdoptedIndex=current.name,resumeRecord=resume.name,currentPatch='r06_c03_s04_04_a01',nextStep='Paint last r06_c03 native, exact assembly and33 internal seam QA; parallel west/right production.',updatedAtUtc=now);write(Z/'progress.json',p)
assert all(sha(p)==s for p,s in before.items())
print(json.dumps({'resume':rec(resume),'currentSelection':rec(current),'historicalUnchanged':True},ensure_ascii=False))
