from native_work import *
tid='r05_c14'; tag='r05_c14-v2-20261012'; dest=ZONE/'tiles'/f'{tag}.png'; d=read(dest.with_suffix('.png.derivation.json')); qdir=Path(d['inspectionCrops'])
crops=[]
for p in sorted(qdir.glob('*.png')):
    with Image.open(p) as im: size=list(im.size)
    crops.append({'file':p.as_posix(),'sha256':sha(p),'size':size,'inspectionScale':1,'resized':False,'status':'passed_visual_100pct'})
assert len(crops)==57
reviewpath=ZONE/'qa'/f'{tag}-review.json'
review={'tileId':tid,'candidatePath':dest.as_posix(),'sha256':sha(dest),'size':[4096,4096],'status':'complete_internal_QA_passed_upper_left_boundaries_passed','internalReview':'passed16core24seam9cross','nativeCoreCount':16,'internalSeamCount':24,'internalCrossCount':9,'externalBoundarySegmentsInspected':8,'inspectedCrops':crops,'findings':'Sixteen native core crops, twenty-four exact internal seam segments, nine four-way cross crops inspected at1:1. Cupboard fascia repaired in p03_01_v2; faint cupboard-foot floor tone strip removed by native floor repair overlay. Rocks, leaves, paving joints and sea caustics visually continuous. Complete upper4096 boundary against r04_c14 and left4096 boundary against r05_c13 passed in four1024 segments each. Natural sea reaches right map border without black padding.','remainingBoundaries':{'right':'world boundary at57344; natural sea, no adjacent tile','bottom':'pending r06_c14 completion'},'formalAccepted':False,'actualModel':None,'actualQuality':None,'reviewedAtUtc':now(),'preview':d['preview'],'derivationRecord':dest.with_suffix('.png.derivation.json').as_posix(),'builtinOnly':True,'resizedFinalArt':False,'uncoveredPixels':0}
write(reviewpath,review); d.update(status='complete_internal_QA_passed_external_assembly_pending',internalReview='passed16core24seam9cross',acceptanceRecord=reviewpath.as_posix(),reviewedAtUtc=now())
for e in d['externalSeams']: e['status']='passed_complete4096_boundary_four1024_segments_visual_100pct'
d['externalSeams'].extend([{'side':'right','status':'world_boundary_natural_sea_no_black_padding'},{'side':'bottom','status':'pending r06_c14 completion'}]); write(dest.with_suffix('.png.derivation.json'),d)
sp=ZONE/f'selection-{tid}.json'; s=read(sp); s.update(internalReview='passed16core24seam9cross',review=reviewpath.as_posix(),pendingIssues=[],resolvedIssues=['cupboard fascia45pxstep','cupboardfoot rectangularfloor tone strip'],formalAccepted=False,updatedAtUtc=now());write(sp,s)
print(json.dumps({'candidatePath':dest.as_posix(),'preview':d['preview'],'review':reviewpath.as_posix(),'sha256':sha(dest)}))

