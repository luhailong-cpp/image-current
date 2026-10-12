from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys

OUT=Path(__file__).resolve().parent
Z=OUT.parents[2]
sys.path.insert(0,str(Z))
import production_v2 as p
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ref(path): return {'file':str(path),'sha256':sha(path)}
def write(path,data,replace=False):
    with Path(path).open('w' if replace else 'x',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')
now=datetime.now(timezone.utc).isoformat()
assembly_path=OUT/'r07_c05-assembly.json'; assembly=read(assembly_path)
review={'createdAtUtc':now,'reviewer':'/root/integrate_shared_micro_status','assembly':ref(assembly_path),
 'actuallyViewed':[ref(OUT/f'micro-y{y}-{label}-native.png') for y in (395,1090) for label in ('before','after')]+[ref(Z/'r07_c05/bridges/shared-east-lower-03/internal-y3072-segment04.png')],
 'localMicroReview':[{'frameY':y,'status':'passed_local_native_roi','observation':'The small interrupted grout tip is connected. The surrounding diagonal endpoints and narrow ROI perimeter remain coherent in the joined actual left candidate and right v10 crop.'} for y in (395,1090)],
 'internalQA':{'cropCount':33,'unchangedFromImmediateBase':33,'priorPassedIdentityReused':32,
   'newlyReviewedInheritedCrop':'internal-y3072-segment04','status':'passed_internal_only',
   'observation':'The inherited changed strip was viewed at native scale; grout connections are continuous and no new cut crosses the internal boundary.'},
 'nativePixelProof':assembly['pixelProof'],'outsideAdoptedROIsUnchanged':True,
 'northWestPreviousBoundaryChecksReusable':assembly['northAndWest160PixelBoundaryBandsUnchanged'],
 'eastBoundaryStatus':'needs_repair','remainingDefects':assembly['eastBoundaryRemainingDefects'],
 'formalAccepted':False,'wholeZoneComplete':False,'existingAcceptanceOrDeliveryFilesModified':False}
review_path=OUT/'local-visual-review.json'; write(review_path,review)

status_path=Z/'generation-tool-status-current.json'
status_bytes=status_path.read_bytes(); old_hash=hashlib.sha256(status_bytes).hexdigest()
old_history=OUT/f'generation-tool-status-before-recovery-{old_hash[:16]}.json'
with old_history.open('xb') as f: f.write(status_bytes)
evidence_path=Z/'r08_c04/native/s01_03_native01.png.generation.json'; evidence=read(evidence_path)
assert sha(evidence['file'])==evidence['sha256']
assert sha(evidence['evidence']['hostOutputPath'])==evidence['sha256']
assert sha(evidence['evidence']['request'])==evidence['evidence']['requestSha256']
assert sha(evidence['evidence']['receipt'])==evidence['evidence']['receiptSha256']
recovery={'updatedAtUtc':now,'userLocalDate':'2026-10-13','status':'observed_builtin_generation_recovered',
 'networkPermissionRevoked':False,'generationToolBlocked':False,'error':None,'historicalError':ref(old_history),
 'recoveryEvidence':{'generationRecord':ref(evidence_path),'nativeImage':{'file':evidence['file'],'sha256':evidence['sha256']},
   'request':ref(evidence['evidence']['request']),'receipt':ref(evidence['evidence']['receipt']),
   'hostOutputPath':evidence['evidence']['hostOutputPath'],'hostByteIdentical':True,'generatedAt':evidence['generatedAt']},
 'observationLimit':'Successful built-in image output after the historical error. No claim about application permission settings or future availability.',
 'route':'builtin_image_gen','actualModel':evidence['actualModel'],'actualQuality':evidence['actualQuality'],
 'modelPolicyStillAllowsBuiltinFallback':True,'modelSettingsChanged':False,'credentialsOrPermissionsChanged':False,
 'paidAPIUsed':False,'returnedImagesSaved':True,'wholeZoneComplete':False}
assert sha(status_path)==old_hash,'Another writer changed the status; do not overwrite'
write(status_path,recovery,replace=True)

scope_path=Z.parents[3]/'docs/MAP_PARALLEL_SPLIT_20261013.json'; scope=read(scope_path)
assignment_path=Z.parents[1]/'acceleration-20261010/assignments.json'; assignment=read(assignment_path)
old_assignment=next(a for a in assignment['assignments'] if a['id']=='city_yamen_north' and a['previousZone']=='northwest')
excluded=set(old_assignment['coordinates'])
for batch in scope['batches']:
    if batch['owner']=='01a12075-f5cf-7c30-9edc-ceb79ed8cfbd' and batch['status']=='allocated_root_reserved': excluded.update(batch['tiles'])
progress_path=Z/'progress.json'; prior=read(progress_path)
rows=[]; errors=[]
for r in range(1,9):
    for c in range(1,9):
        tile=f'r{r:02}_c{c:02}'
        if tile in excluded: continue
        directory=Z/tile; selection=read(directory/'selection.json') if (directory/'selection.json').exists() else {}
        selected=[]
        for sr in range(1,5):
            for sc in range(1,5):
                pid=f's{sr:02}_{sc:02}'; source=p.selected_path(directory,pid,selection)
                if not source.is_file(): continue
                try:
                    p.validate_native(source,directory,pid)
                    selected.append({'id':pid,**ref(source)})
                except Exception as exc: errors.append({'tile':tile,'id':pid,'error':str(exc)})
        rows.append({'tile':tile,'selectedUsableNativeCount':len(selected),'selectedSources':selected})
counts={'effectiveOwnedTileCount':len(rows),'expectedNativeCoreCount':len(rows)*16,
 'selectedUsableNativeCount':sum(x['selectedUsableNativeCount'] for x in rows),
 'tilesWithAll16NativePatches':sum(x['selectedUsableNativeCount']==16 for x in rows),
 'tilesStillMissingNativePatches':sum(x['selectedUsableNativeCount']!=16 for x in rows),
 'internallyPassedDeliveredTiles':prior['internalQAPassedCount'],'formalAcceptedCount':prior['formalAcceptedCount']}
counts['missingNativePatchCount']=counts['expectedNativeCoreCount']-counts['selectedUsableNativeCount']
counts['fullSourceTilesPendingInternalRepairOrReview']=counts['tilesWithAll16NativePatches']-counts['internallyPassedDeliveredTiles']
checkpoint={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'northwest current owned coordinates',
 'currentLocalAssembly':ref(assembly_path),'currentLocalVisualReview':ref(review_path),'toolStatus':ref(status_path),
 'scopeAssignment':ref(scope_path),'priorAssignment':ref(assignment_path),'excludedCoordinates':sorted(excluded),
 'currentScopeCounts':counts,'currentSelectedSourceCensus':rows,'selectedSourceValidationErrors':errors,
 'deliveryCountSource':ref(progress_path),'deliveryCountVerification':'Inherited prior 11 delivered internal passes; this task does not add a delivered tile or re-audit historical delivery packages.',
 'historicalZipFilesReadOrRebuilt':False,'productionProgressJsonModified':False,
 'refreshProgressReview':{'file':str(Z/'refresh_progress.py'),'sha256':sha(Z/'refresh_progress.py'),
   'finding':'main() recomputes historical eight/nine/eleven ZIP hashes, some twice; aggregate_progress() also traverses old candidate manifests.',
   'recommendation':'For routine progress, use current selected-source census and cached passed manifests keyed by input hashes; defer ZIP CRC/hash verification until a changed package or delivery milestone. The existing script was inspected but not edited or executed.'},
 'remainingLocalDefects':assembly['eastBoundaryRemainingDefects'],'formalAccepted':False,'wholeZoneComplete':False,
 'nextStep':'Continue missing native sources in r06_c03 and r08_c04; retain failed shared-edge and r07_c06 material repairs as unpassed for consolidated repair.'}
write(OUT/'local-checkpoint-and-counts.json',checkpoint)
print(json.dumps({'counts':counts,'errors':errors,'checkpoint':ref(OUT/'local-checkpoint-and-counts.json'),'review':ref(review_path),'toolStatus':ref(status_path)},indent=2))
