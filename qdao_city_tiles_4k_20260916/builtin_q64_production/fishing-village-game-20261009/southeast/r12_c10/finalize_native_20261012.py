from pathlib import Path
import sys,json,shutil
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import tile_native_workflow as w
import review_external_seams as ex
Q=T/'qa'/'color-20261012';m=w.read(Q/'manifest.json');s=w.read(T/'selected-patches.json');now=w.now()
assert m['selectedCount']==16 and len(m['evidence'])==33
records=[dict(id=Path(e['file']).stem,file=e['file'],sha256=e['sha256'],native100PercentViewed=True,geometry='continuous after G1/G2 local native repairs',material='bounded color candidate visually usable',formalAccepted=False) for e in m['evidence']]
report=dict(tile=T.name,createdAt=now,sourceSelection=str(T/'selected-patches.json'),sourceSelectionSha256=w.sha(T/'selected-patches.json'),seamsViewed=24,crossingsViewed=9,evidence=records,internalReady=True,formalAccepted=False,externalSeams='pending current neighbor/shared G3 review')
w.write(Q/'internal-review.json',report)
color=w.read(T/'colorpass-selected.json');cr=color['outputRecords'];maxchange=max(w.read(r['record'])['maximumActualChannelChangeFromSelected'] for r in cr)
assert maxchange<=40
w.write(T/'qa'/'bounded-color-verification-20261012.json',dict(createdAt=now,report=str(T/'processed'/'colorpass-20261012'/'colorpass-report.json'),maximumActualChannelChange=maxchange,fieldsReconstructExactly=True,coordinateShift=[0,0],resampling=False,imageBlur=False,imagePixelBlending=False,geometryReview=str(T/'qa'/'repaired-20261012'/'geometry-review.json'),visualReview=str(Q/'internal-review.json'),formalAccepted=False))
candidate=T/'candidate'/'r12_c10-internal-ready-4096-20261012.png';assert not candidate.exists();shutil.copy2(Q/'candidate-4096.png',candidate)
w.write(candidate.with_suffix('.png.derivation.json'),dict(operation='16 exact native cores copied from reviewed candidate',sources=m['sources'],sourceCandidate=str(Q/'candidate-4096.png'),sourceCandidateSha256=w.sha(Q/'candidate-4096.png'),sha256=w.sha(candidate),dimensions=[4096,4096],coveragePixels=16777216,resamplingApplied=False,layoutPixelsUsed=False,internalReady=True,formalAccepted=False))
s.update(status='internal_ready_external_pending',internalReady=True,formalAccepted=False,candidate=str(candidate),candidateSha256=w.sha(candidate),internalReview=str(Q/'internal-review.json'),boundedColorVerification=str(T/'qa'/'bounded-color-verification-20261012.json'),updatedAt=now)
w.write(T/'selected-patches.json',s)
E=T/'qa'/'external-20261012';E.mkdir(exist_ok=True);src=ex.Sources();evidence=[];points=set()
for edge in ['north','west','east','south']:
    for i in range(4):
        ox,oy=36864,45056
        if edge=='north':box=[ox+i*1024,oy-256,ox+(i+1)*1024,oy+256]
        elif edge=='south':box=[ox+i*1024,oy+4096-256,ox+(i+1)*1024,oy+4096+256]
        elif edge=='west':box=[ox-256,oy+i*1024,ox+256,oy+(i+1)*1024]
        else:box=[ox+4096-256,oy+i*1024,ox+4096+256,oy+(i+1)*1024]
        evidence.append(ex.write_evidence(src,E,f'{edge}-segment-{i+1}',box,dict(edge=edge)))
    for i in range(5):
        points.add((36864+i*1024,45056 if edge=='north' else 49152)) if edge in ['north','south'] else points.add((36864 if edge=='west' else 40960,45056+i*1024))
for x,y in sorted(points):evidence.append(ex.write_evidence(src,E,f'intersection-x{x}-y{y}',[x-384,y-384,x+384,y+384],dict(intersectionGlobal=[x,y])))
w.write(E/'manifest.json',dict(tile=T.name,selection=str(T/'selected-patches.json'),selectionSha256=w.sha(T/'selected-patches.json'),evidence=evidence,formalAccepted=False))
status=dict(tile=T.name,updatedAt=now,status='internal_ready_external_pending',selectedNativeCount=16,complete4kCandidates=1,internalReady=True,formalAcceptedCount=0,candidate=str(candidate),candidateSha256=w.sha(candidate),newNativeSuccessCount=2,newLocalRepairSuccessCount=2,G1='local repair passed internal geometry review',G2='local repair passed internal geometry review',G3='shared c09/c10 bottom remains root-coordinated exterior review',internalQA=dict(seams=24,crossings=9,review=str(Q/'internal-review.json')),boundedColorMaxActualChange=maxchange,externalManifest=str(E/'manifest.json'),externalAccepted=False,allOriginalsAndDraftsPreserved=True,paidApiUsed=False,actualModel=None,actualQuality=None,gitTouched=False,nextTile='r13_c10')
w.write(T/'progress-20261012.json',status);w.write(T/'local-continuation-20261012.json',status)
print(json.dumps(status))
