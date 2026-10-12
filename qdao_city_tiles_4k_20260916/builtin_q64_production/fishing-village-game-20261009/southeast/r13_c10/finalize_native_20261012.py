from pathlib import Path
import sys,json,shutil
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import tile_native_workflow as w
import review_external_seams as ex
Q=T/'qa'/'color-20261012';m=w.read(Q/'manifest.json');s=w.read(T/'selected-patches.json');now=w.now()
assert m['selectedCount']==16 and len(m['evidence'])==33
records=[dict(id=Path(e['file']).stem,file=e['file'],sha256=e['sha256'],native100PercentViewed=True,geometry='connected native geometry after p21-v2 and p32-v3 repairs',material='bounded additive color candidate visually usable at the regular core seam',formalAccepted=False) for e in m['evidence']]
w.write(T/'qa'/'repaired-20261012'/'geometry-review.json',dict(tile=T.name,createdAt=now,seamsViewed=24,crossingsViewed=9,sourceSelection=str(T/'native-selected-before-color-20261012.json'),sourceSelectionSha256=w.sha(T/'native-selected-before-color-20261012.json'),geometryPassed=True,formalAccepted=False))
color=w.read(T/'colorpass-selected.json');cr=color['outputRecords'];maxchange=max(w.read(r['record'])['maximumActualChannelChangeFromSelected'] for r in cr)
assert maxchange<=40
for r in cr:
    d=w.read(r['record']);assert d['correctionEvidence']['reconstructionPixelsExactlyMatch'] and d['actualCoordinateShift']==[0,0] and not d['resampling'] and not d['imageBlur'] and not d['imagePixelBlending']
    assert Image.open(r['file']).size==(1254,1254) and w.sha(r['file'])==r['sha256']
w.write(T/'qa'/'bounded-color-verification-20261012.json',dict(createdAt=now,report=str(T/'processed'/'colorpass-20261012'/'colorpass-report.json'),maximumActualChannelChange=maxchange,fieldsReconstructExactly=True,coordinateShift=[0,0],resampling=False,imageBlur=False,imagePixelBlending=False,geometryReview=str(T/'qa'/'repaired-20261012'/'geometry-review.json'),formalAccepted=False))
E=T/'qa'/'external-20261012';E.mkdir(exist_ok=True);src=ex.Sources();evidence=[];points=set();tr,tc=w.tile_indices(T.name);ox=(tc-1)*4096;oy=(tr-1)*4096
for edge in ['north','west','east','south']:
    for i in range(4):
        if edge=='north':box=[ox+i*1024,oy-256,ox+(i+1)*1024,oy+256]
        elif edge=='south':box=[ox+i*1024,oy+4096-256,ox+(i+1)*1024,oy+4096+256]
        elif edge=='west':box=[ox-256,oy+i*1024,ox+256,oy+(i+1)*1024]
        else:box=[ox+4096-256,oy+i*1024,ox+4096+256,oy+(i+1)*1024]
        evidence.append(ex.write_evidence(src,E,f'{edge}-segment-{i+1}',box,dict(edge=edge)))
    for i in range(5):
        points.add((ox+i*1024,oy if edge=='north' else oy+4096)) if edge in ['north','south'] else points.add((ox if edge=='west' else ox+4096,oy+i*1024))
for x,y in sorted(points):evidence.append(ex.write_evidence(src,E,f'intersection-x{x}-y{y}',[x-384,y-384,x+384,y+384],dict(intersectionGlobal=[x,y])))
w.write(E/'manifest.json',dict(tile=T.name,selection=str(T/'selected-patches.json'),selectionSha256=w.sha(T/'selected-patches.json'),evidence=evidence,formalAccepted=False))
I=T/'qa'/'inner-adoption-20261012';I.mkdir(exist_ok=True);extra=[]
for label,box in [('p21-left-face',[ox,oy+1024+70,ox+350,oy+1024+480]),('p32-rounded-upper-left',[ox+1024,oy+2048,ox+1024+760,oy+2048+650]),('p24-water-left-transition',[ox+3072,oy+1024,ox+3072+450,oy+2048]),('p34-water-left-transition',[ox+3072,oy+2048,ox+3072+450,oy+3072])]:
    extra.append(ex.write_evidence(src,I,label,box,dict(kind='inner conditioning boundary beyond normal seam crops')))
w.write(I/'manifest.json',dict(tile=T.name,createdAt=now,evidence=extra,formalAccepted=False))
report=dict(tile=T.name,createdAt=now,sourceSelection=str(T/'selected-patches.json'),sourceSelectionSha256=w.sha(T/'selected-patches.json'),seamsViewed=24,crossingsViewed=9,evidence=records,additionalReview=str(I/'manifest.json'),internalReady=False,formalAccepted=False,externalSeams='pending actual neighbor and intersection visual review')
w.write(Q/'internal-review.json',report)
candidate=T/'candidate'/(T.name+'-reviewed-native-4096-20261012.png');candidate.parent.mkdir(exist_ok=True);assert not candidate.exists();shutil.copy2(Q/'candidate-4096.png',candidate)
w.write(candidate.with_suffix('.png.derivation.json'),dict(operation='16 exact native cores copied from reviewed candidate',sources=m['sources'],sourceCandidate=str(Q/'candidate-4096.png'),sourceCandidateSha256=w.sha(Q/'candidate-4096.png'),sha256=w.sha(candidate),dimensions=[4096,4096],coveragePixels=16777216,resamplingApplied=False,layoutPixelsUsed=False,internalReady=False,formalAccepted=False))
s.update(status='additional_inner_and_external_review_pending',internalReady=False,formalAccepted=False,candidate=str(candidate),candidateSha256=w.sha(candidate),internalReview=str(Q/'internal-review.json'),boundedColorVerification=str(T/'qa'/'bounded-color-verification-20261012.json'),updatedAt=now);w.write(T/'selected-patches.json',s)
status=dict(tile=T.name,updatedAt=now,status=s['status'],selectedNativeCount=16,complete4kCandidates=1,internalReady=False,formalAcceptedCount=0,candidate=str(candidate),candidateSha256=w.sha(candidate),newNativeSuccessCount=18,newLocalRepairSuccessCount=2,internalQA=dict(seams=24,crossings=9,review=str(Q/'internal-review.json')),boundedColorMaxActualChange=maxchange,externalManifest=str(E/'manifest.json'),additionalInnerManifest=str(I/'manifest.json'),externalAccepted=False,allOriginalsAndDraftsPreserved=True,paidApiUsed=False,actualModel=None,actualQuality=None,gitTouched=False,nextTile='r14_c10')
w.write(T/'progress-20261012.json',status);w.write(T/'local-continuation-20261012.json',status)
print(json.dumps(status))
