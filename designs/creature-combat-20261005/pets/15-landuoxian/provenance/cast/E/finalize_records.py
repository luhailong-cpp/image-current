from pathlib import Path
import json,hashlib
p=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian/provenance/cast/E')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for file in p.glob('*.generation.json'):
    j=json.loads(file.read_text(encoding='utf8'))
    for k,ref in enumerate(j['references']):
        original=Path(ref['path'])
        actual=original
        if k==3:
            if file.name in [f'{i:02}.generation.json' for i in range(9,14)]:
                ref['role']='AI edit target: same frame before local chime shape correction; preserve pose, scale and support'
                j['editedFrom']={'file':str(actual),'sha256':sha(actual),'generationRecord':str(p/f'{file.name[:2]}.pre-chimefix.generation.json')}
            elif file.name=='14.generation.json' or file.name in [f'{i:02}.pre-chimefix.generation.json' for i in range(10,14)]:
                actual=original.with_name(original.stem+'.pre-chimefix.png')
                ref['originalInputPath']=str(original)
                ref['path']=str(actual)
                ref['retainedSourceExplanation']='Original submitted path was later replaced by accepted local chime repair; this retained native is the exact input at submission.'
        if actual.exists(): ref['sha256']=sha(actual)
    if file.name in [f'{i:02}.generation.json' for i in range(1,17)]:
        j['visualQA']['acceptedSingleFrame']=True
        j['visualQA']['motionPreview']='pending root combined normal/0.25x review'
        if 9<=int(file.name[:2])<=13:
            j['visualQA']['localRepair']='Short flared right chime restored; hands, instrument holding and pose re-inspected.'
    file.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
review={
'action':'cast','direction':'E','frameCount':16,'durationMs':45,
'singleFrameVisualInspection':'All 16 final full-size generated outputs inspected, followed by two sequential contact sheets.',
'finalPaths':'runtime/cast/E/01.png through16.png',
'provenance':'provenance/cast/E/NN.prompt.txt, NN.receipt.json, NN.generation.json',
'consistentChecks':['E three-quarter front lower-right','two arms/two hands/two legs','anatomical right hand gold ring; anatomical left jade mallet','exactly three jade chimes; short flared far-right chime restored in09–13','no wings/tails introduced','true RGBA transparent background','single frame per builtin imagegen request; no mirrored/copied/interpolated frame'],
'repairs':[{'frame':9,'reason':'excessive rebound in initial release pose','status':'corrected'},{'frames':[9,10,11,12,13],'reason':'rightmost short chime silhouette had elongated','status':'corrected'},{'frame':10,'reason':'one chime repair candidate added a third arm/second mallet','status':'rejected; corrected final is two arms and one mallet'}],
'normalAndSlowPlayback':'not claimed; root performs combined six-group browser review',
'remainingReviewFocus':['01→02 initial ring lift is comparatively fast','10→11 ring lowering is comparatively fast','small AI contour/ornament and foot-support variation should be assessed at runtime scale; no per-frame alignment was applied'],
'clientIntegration':'not tested',
'retention':'native and rejected images retained temporarily as root instructed; root performs final retention cleanup after six-group verification. Preserve all text provenance.'
}
(p/'group-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')
print('final source chains enriched; group review saved')
