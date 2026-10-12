"""Root-owned current art checkpoint; leaves migration freeze/audits unchanged."""
import datetime as dt
import hashlib
import json
import runpy
import uuid
from pathlib import Path

Z = Path(__file__).resolve().parent

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, data):
    p = Path(p)
    temporary = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(p)

runpy.run_path(str(Z / 'update_production_census_v2.py'), run_name='__main__')
now = dt.datetime.now(dt.timezone.utc).isoformat()
census = read(Z / 'records/production-census-20261010.json')
resume_path = Z / 'production-resume-20261012.json'
resume = read(resume_path)
model_rules=Path('D:/work/image/AGENTS.md');model_requirement=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
assert 'GPT Image 2.5' in model_rules.read_text(encoding='utf-8-sig') and 'GPT Image 2.5' in model_requirement.read_text(encoding='utf-8-sig')
assert 'allows GPT Image 2.0' in model_requirement.read_text(encoding='utf-8-sig')
model_gate={'preferredImageModel':'GPT Image 2.5 on free/included route','permittedFallback':'GPT Image 2.0 or existing builtin image tool; no metadata confirmation gate','verifiedActualRoute':'builtin image_gen.imagegen','actualImageModel':None,'newGenerationAllowed':True,'reason':'User clarification revokes mandatory2.5 pause and authorizes current builtin production when free2.5 unavailable. Paid API remains unauthorized.','projectRules':{'path':str(model_rules),'sha256':sha(model_rules)},'modelRequirement':{'path':str(model_requirement),'sha256':sha(model_requirement)},'existingArtworkModelRelabelAllowed':False}
assert sha(Z / 'migration-freeze-20261011.json') == resume['historicalFreeze']['sha256']
active_path = Z / 'records/active-candidates.json'
active = read(active_path)
missing = {}
for tile in read(Z / 'records/zone-tile-plan.json')['tiles']:
    if not tile['ownedByThisZone']:
        continue
    name = tile['id']
    have = set(census['coverageByTile'].get(name, []))
    absent = [f'{name}_p{r}{c}' for r in range(1, 5) for c in range(1, 5) if f'{r}{c}' not in have]
    if absent:
        missing[name] = absent
new = []
for item in census['successfulGenerations'].values():
    record = read(item['generationRecord']['path'])
    observed = record.get('observedAtUtc', record.get('createdAtUtc', ''))
    if observed < '2026-10-12T11:23:29':
        continue
    new.append({'path': item['image'], 'sha256': item['sha256'], 'nativeSize': record.get('nativeSize', record.get('nativeDimensions')), 'generationRecord': item['generationRecord'], 'receipt': item['receipt'], 'observedAtUtc': observed, 'formalAccepted': False})
new.sort(key=lambda item: item['observedAtUtc'])
resume.update(updatedAtUtc=now, status='active_native_art_production', productionAuthorized=True, authorizationRevoked=False, newArtworkGenerationAllowed=True, generationGate=model_gate, currentNativeOutputCount=census['generatedNativeCount'], newNativeOutputCount=census['generatedNativeCount']-resume['baseNativeOutputCount'], newOutputs=new, currentAdoptedCandidates=active['tiles'], currentCompleteCandidateCount=len(active['tiles']), remainingCoordinates=missing, missingGeneratedCoordinateCount=sum(map(len, missing.values())), formalAcceptedCount=0, taskComplete=False, historicalFreezeHashVerifiedUnchanged=True)
resume['workingSelections'] = [{'path': str(p), 'sha256': sha(p)} for p in sorted((Z / 'records').glob('*.working-selection.json'))]
save(resume_path, resume)
progress_path = Z / 'progress.json'
progress = read(progress_path)
progress.update(updatedAtUtc=now, status='active_native_art_production', generationStopped=False, newGenerationAllowed=True, newArtworkGenerationAllowed=True, productionAuthorized=True, authorizationRevoked=False, currentPatch='Root r04_c12 then c12 northward plus r05_c12 west-roof repair and independent QA; central_sol r05_c14 independent review then c13 northward; east_sol c14 northward; roof_sol r06_c11/r07_c11 then r06_c10/r07_c10', nextStep='Complete each owned 16-core tile and native seam closure, then continue the next assigned tile without stopping at a status report', inFlightImageGenCount=None, inFlightState='Active owner calls; each submitted request and returned result has separate records', productionResumeRecord=str(resume_path), activeBlockers=active['activeBlockers'], newNativeOutputsSinceResume=resume['newNativeOutputCount'], freezeRecordHistoricalOnly=True)
progress.update(status=resume['status'],generationStopped=False,newGenerationAllowed=True,newArtworkGenerationAllowed=True,generationGate=model_gate,currentPatch='Root r04_c12 missing cores and r05_c12 west roof repair; central_sol c14 independent QA then c13 northward; east_sol r07_c14 independent QA then c14 northward; roof_sol c11/c10 extension',nextStep='Continue original exclusive owned native coordinates and necessary seam repairs; finish existing independent QA and continue next tile',inFlightState='Fresh builtin generation authorized under corrected free2.5 preference/2.0 fallback; actual image model remains unreturned',allRequiredNativeQAPassed=False,taskComplete=False)
complete={tile for tile,cells in census['coverageByTile'].items() if len(cells)==16}
assembled={x.name.split('.candidate')[0] for x in (Z/'tiles').glob('*.candidate*.png')}
breakdown={'ownedDistinct4kTarget':progress['target4kCount'],'native16FullyCovered4kCount':len(complete),'assembledDistinct4kCandidateCount':len(assembled),'rootIndependentInternalPassed4kCount':progress['internalPassed4kCount'],'tilesStillMissingNativeCoordinates':len(missing),'missingNativeCoordinateCount':sum(map(len,missing.values())),'completeCandidatesPendingIndependentInternalReview':len(assembled)-progress['internalPassed4kCount'],'completeCandidatesWithKnownLocalSeamRepair':1,'knownLocalSeamRepairTiles':['r05_c12'],'completeCandidatesPendingFinalSeamClosure':len(assembled),'formalAccepted4kCount':0,'note':'Missing-neighbor outer boundaries are pending final QA, not missing artwork. Candidate counts deduplicate tile IDs across all retained versions.'}
progress['completionBreakdown']=breakdown;resume['completionBreakdown']=breakdown;resume['currentCompleteCandidateCount']=len(assembled);resume['currentAdoptedCandidateCount']=len(active['tiles']);save(resume_path,resume)
save(progress_path, progress)
ack_path = Z / 'resume-ack-20261010.json'
ack = read(ack_path)
ack.update(status=resume['status'],newArtworkGenerationAllowed=True,generationGate=model_gate,currentAuthorizationRecord=str(resume_path))
save(ack_path, ack)
print(json.dumps({'currentNativeOutputCount': census['generatedNativeCount'], 'newNativeOutputsSinceResume': resume['newNativeOutputCount'], 'assembledCandidates': len(active['tiles']), 'missingCoordinates': resume['missingGeneratedCoordinateCount'], 'censusErrors': census['errors'], 'historicalFreezeUnchanged': True}))
