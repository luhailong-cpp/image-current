from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
now=datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=read(B/'migration-freeze-20261011.json');progress=read(B/'progress.json')
tiles=[];selected_candidates=[];references={};issues=[]
legacy=read(B/'current-candidates.json')['tiles']
for row in range(9,17):
    for col in range(1,9):
        tile=f'r{row:02d}_c{col:02d}';t=B/tile;s=t/'refinement/selection.json';selection=read(s) if s.exists() else {}
        natives=[];missing=[]
        for pr in range(1,5):
            for pc in range(1,5):
                key=f'p{pr:02d}_{pc:02d}';rec=t/selection.get(key,f'native/{key}.png.generation.json')
                if not rec.exists():missing.append(key);continue
                d=read(rec);natives.append({'patch':key,'generationRecord':str(rec),'nativeFile':d.get('file'),'sha256':d.get('sha256'),'nativeExists':Path(d.get('file','')).is_file()})
                for rf in d.get('references',[]):
                    if isinstance(rf,dict) and rf.get('file'):references[rf['file']]=rf
        outputs=list((t/'pipeline/output').glob('*/assembly.json')) if (t/'pipeline/output').exists() else []
        latest=max(outputs,key=lambda p:p.stat().st_mtime) if outputs else None
        last=read(latest) if latest else None
        entry={'tile':tile,'selectedNativeCount':len(natives),'selectedNativeFiles':natives,'missingPatchIds':missing,'formalAccepted':False}
        if tile in legacy:entry['currentIntegratedCandidate']=legacy[tile];selected_candidates.append({'tile':tile,'source':'integrated-v5',**legacy[tile]})
        if last:
            entry['latestPipelineAssembly']=str(latest);entry['latestPipelineOutput']=last.get('output');entry['latestPipelineContext']=last.get('contextOutput');entry['pipelineAssemblyCoverageComplete']=last.get('complete4kCandidate',False)
            if last.get('complete4kCandidate') and tile not in legacy:selected_candidates.append({'tile':tile,'source':'latest-pipeline-assembly','assembly':str(latest),'candidate':last.get('output'),'context':last.get('contextOutput'),'formalAccepted':False})
        tiles.append(entry)
worker_files=sorted(p for p in B.rglob('migration-freeze-20261011.json') if p!=B/'migration-freeze-20261011.json')
worker_reports=[{'file':str(p),'sha256':sha(p),'report':read(p)} for p in worker_files]
all_drained=len(worker_reports)==3 and all(x['report'].get('inFlightRequestCount')==0 and x['report'].get('unsavedSuccessfulOutputCount')==0 for x in worker_reports)
r12path=B/'r12_c05/repairs-audit-line-20261011/integrated-local-v06/assembly.json'
if r12path.exists():
    r12=read(r12path)
    selected_candidates=[x for x in selected_candidates if x['tile']!='r12_c05']
    selected_candidates.append({'tile':'r12_c05','source':'latest-protected-local-repair-assembly','assembly':str(r12path),'candidate':r12['output'],'context':r12['contextOutput'],'formalAccepted':False,'internalAccepted':False})
portable=B/'migration-preserved-external-20261011/manifest.json';external=read(portable)
result={**prior,'savedAtUtc':now,'generationStopped':True,'rootRequestsInFlight':0,'rootUnsavedSuccessfulOutputCount':0,'unsavedSuccessfulOutputPaths':[],
'activeCoordinates':['r09_c06:p01_03 prepared but never submitted','r09_c01 pending worker frozen manifest','r09_c07 pending worker frozen manifest','r12_c05 pending repair frozen manifest'],
'selectedCandidatePaths':selected_candidates,'tileInventory':tiles,'selectedNativePatchCountFromRecords':sum(t['selectedNativeCount'] for t in tiles),'missingNativePatchCountFromRecords':sum(len(t['missingPatchIds']) for t in tiles),
'countsSnapshotUtc':progress.get('countsSnapshotUtc'),'latestCounts':{k:progress.get(k) for k in ['generatedNativeCount','rejectedNativeCount','failedBuiltinCallCount','selectedNativePatchCount','complete4kCandidateCount','formalAcceptedCount','partialTileCount','untouchedTileCount','remainingCorePatchCount']},
'nextMissingCoordinate':'r09_c06:p01_03','preparedUnsubmittedRequest':str(B/'r09_c06/pipeline/prompts/p01_03.arena-continuity-v01.request.json'),
'pendingRepairs':[
'r09_c05 full candidate 270f210e60b79873 has visible wood/taupe paint tone seams and ellipse/emblem geometry issues; see pipeline/qa/full-candidate-review-20261011.json.',
'r09_c06 p01_01 and p01_02 selected genuine native candidates only, stone/material and shared edges unaccepted; p01_03 viewed/prepared, never generated.',
'r12_c05 whole coverage exists; latest selected native versions and protected roof/stone proposals require final seam and macro QA; do not treat 48px historical feather proposal as selected.',
'Integrated v5 four candidates have open north/south seams, stone material, r11_c06 G02/G06 layout and r10_c06 red sliver/layout findings.',
'64-tile acceptance incomplete: 112 shared edges, 49 four-tile junctions and 16 cross-region neighbor checks outstanding; external r08 row and c09 neighboring files not yet verified.'],
'workerFreezeReports':worker_reports,'workerDrainStatus':'Awaiting all three worker final confirmations' if len(worker_reports)<3 else 'Worker freeze manifests present; inspect reports for in-flight detail',
'externalReferencePaths':list(references.values()),'externalImagePreservationManifest':str(portable),'externalImagePreservationManifestSha256':sha(portable),'externalImagePreservation':{'referencedOutsideWorkspace':external['uniqueExternalPathCount'],'unpreserved':external.get('unpreservedExternalImages',external.get('missingSourcePaths')),'originalsPreserved':True},
'migrationNotes':['Preserve all current files, rejected outputs, historical assemblies, previews and provenance.','External generated images copied byte-for-byte into migration-preserved-external-20261011, including recovery of one missing historical host path from its hash-verified workspace native.','Original absolute paths remain in immutable receipts; use preservation manifest to locate byte-identical files after migration.','No new generation, artwork edits, Git mutation or deletion during freeze. No re-review of passed art performed.'],
'all64Complete':False,'all64Accepted':False}
result.update(workerDrainStatus='All three worker states verified drained: two direct final replies and one independent runtime inspection; freeze finalized' if all_drained else 'Worker final confirmations incomplete',allGenerationRequestsInFlight=0 if all_drained else None,allWorkersConfirmedStopped=all_drained,freezeFinalized=all_drained,activeCoordinates=['r09_c06:p01_03 prepared, never submitted','r09_c01:p03_02 v02 completed return saved and attributed; selection and review deferred','r09_c07:p03_03 prepared, never submitted','r12_c05:integrated-local-v06 saved, remaining visual QA deferred'],additionalPreservedCacheOutput=str(B/'r09_c01/migration-unattributed-cache-return-20261011.json'),additionalCacheOutputIncludedInGenerationReceiptCount=True,undefinedPathAudit={'observedDirectory':'D:/work/image/undefined','southwestR09OrR12FilesFound':False,'action':'Unrelated existing files and directories preserved untouched; no deletion or relocation.'})
atomic_json(B/'migration-freeze-20261011.json',result)
progress.update(updatedAtUtc=now,status='migration_frozen',holdNewImageGeneration=True,generationStopped=True,generationResumeAuthority='migration_freeze_requires_explicit_resume',rootImageGenerationInFlight=False,imageGenerationInFlight=None,inFlightStatus='root_none_workers_freezing',activeCoordinate='r09_c06:p01_03_prepared_not_submitted',primaryNewTileNativeCount=2,productionLines=0,nextStep='Migration freeze: preserve and transfer files. Do not resume generation until explicitly authorized after migration.',migrationFreeze=str(B/'migration-freeze-20261011.json'))
progress.update(imageGenerationInFlight=False if all_drained else None,inFlightStatus='none_all_workers_confirmed_frozen' if all_drained else 'root_none_workers_freezing',freezeFinalized=all_drained,externalImagePreservedCount=external['uniqueExternalPathCount'],additionalPreservedCacheOutputCount=1)
atomic_json(B/'progress.json',progress)
continuation=read(B/'full64-continuation-20261011.json');continuation.update(updatedAtUtc=now,status='migration_frozen',generationStopped=True,migrationFreeze=str(B/'migration-freeze-20261011.json'));atomic_json(B/'full64-continuation-20261011.json',continuation)
print(json.dumps({'freeze':str(B/'migration-freeze-20261011.json'),'workerReports':len(worker_reports),'nativeRecords':sum(t['selectedNativeCount'] for t in tiles),'missingPatches':sum(len(t['missingPatchIds']) for t in tiles),'candidateFiles':len(selected_candidates),'outsideImages':external['uniqueExternalPathCount']},ensure_ascii=False))

