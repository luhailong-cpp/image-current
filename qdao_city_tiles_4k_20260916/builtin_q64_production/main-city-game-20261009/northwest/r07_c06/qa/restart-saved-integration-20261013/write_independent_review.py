from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

out=Path(__file__).parent
tile=out.parent.parent
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ref(path): return {'file':str(path),'sha256':sha(path)}
def arr(path): return np.array(Image.open(path).convert('RGB'))
def verify(record):
    actual=sha(record['file'])
    assert actual==record['sha256'],record
    return {'file':record['file'],'sha256':actual,'matchesRecordedHash':True}

wide=read(tile/'repair-batches/c3c4-upper-gap-02/trial.json')
narrow=read(out/'c3c4-narrow-trial.json')
micro=read(out/'micro-trial.json')
bound=[]
for r in [wide['source'],wide['baseCandidate'],wide['trialCandidate'],*wide['qa'],narrow['candidate'],narrow['base'],narrow['source'],narrow['mask'],*narrow['qa'],micro['source'],micro['generation'],micro['base'],micro['trial'],*micro['qa']]:
    bound.append(verify(r))

base=arr(narrow['base']['file']); trial=arr(narrow['candidate']['file']); source=arr(narrow['source']['file'])
mask=np.array(Image.open(narrow['mask']['file']).convert('L'))>0
x,y=narrow['nativeTileOriginXY']
fullmask=np.zeros(base.shape[:2],dtype=bool)
fullmask[y:y+mask.shape[0],x:x+mask.shape[1]]=mask
assert np.array_equal(trial[~fullmask],base[~fullmask])
assert np.array_equal(trial[y:y+mask.shape[0],x:x+mask.shape[1]][mask],source[mask])
assert int(mask.sum())==narrow['selectedPixels']==1014
oldbase=arr(wide['baseCandidate']['file'])
oldnewcontextEqual=bool(np.array_equal(oldbase[450:750,2940:3210],base[450:750,2940:3210]))

mbase=arr(micro['base']['file']); mtrial=arr(micro['trial']['file']); msource=arr(micro['source']['file'])
mmask=np.zeros(mbase.shape[:2],dtype=bool)
for l,t,r,b in micro['sourceROIs']: mmask[t:b,l:r]=True
assert np.array_equal(mtrial[~mmask],mbase[~mmask])
assert np.array_equal(mtrial[mmask],msource[mmask])

visualfiles=[Path(x['file']) for x in wide['qa']]+[out/'base-context-native.png',out/'source-context-native.png']+[tile/'repair-batches/shared-west-micro-01'/n for n in ['input-y395.png','output-y395.png','input-y1090.png','output-y1090.png']]+[Path(x['file']) for x in micro['qa']]+[Path(x['file']) for x in narrow['qa']]+[Path(narrow['mask']['file'])]
report={
 'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'/root/resume_r07_c06_oct13/review_saved_local',
 'status':'local_geometry_and_micro_rois_reviewed_material_still_needsrepair',
 'reviewMethod':'Every listed visual viewed through view_image detail=original at native pixel scale, no resizing. Same-world native-selection proof independently checked with pixel arrays.',
 'wholeTileAccepted':False,'formalAccepted':False,
 'c3c4WideRectangle':{
   'trialMetadata':ref(tile/'repair-batches/c3c4-upper-gap-02/trial.json'),
   'sourceROI':wide['sourceROI'],'candidateROI':wide['candidateROI'],
   'geometry':'passed_local_scope',
   'material':'needsrepair_inherited_vertical_material_seam',
   'finding':'The two formerly disconnected diagonal grout endpoints are joined. The conspicuous vertical change in pavement grain/colour is visible in the original base crop, extending outside the new rectangle; it is not newly caused by this ROI.',
   'initialFindingCorrection':'Initial attribution of the prominent upright material edge to the new rectangle was corrected after viewing the original base. No claim is made that this source resolves material continuity.',
   'preferredSelection':'The later narrow binary selection changes fewer floor pixels while retaining the geometry repair.'},
 'c3c4NarrowSelection':{
   'trialMetadata':ref(out/'c3c4-narrow-trial.json'),
   'status':'passed_local_scope','scope':'grout geometry and no new visibly cut line at the narrow mask perimeter',
   'selectedPixels':int(mask.sum()),'pureSameWorldNativePixelsVerified':True,'unchangedOutsideMaskVerified':True,
   'baseContextMatchesPreviouslyViewedV07':oldnewcontextEqual,
   'geometry':'Both diagonal tips meet the short vertical grout segment, with no detached tip or open gap at either endpoint.',
   'maskPerimeter':'No additional visibly clipped stroke or rectangular colour edge is apparent in the native context and detail.',
   'material':'needsrepair_inherited_vertical_material_seam',
   'adoption':'May be adopted as local geometry improvement only; do not mark the full seam or tile passed.'},
 'microSelections':{
   'trialMetadata':ref(out/'micro-trial.json'),
   'status':'passed_local_scope','sourceROIs':micro['sourceROIs'],
   'selectedPixels':int(mmask.sum()),'pureSameWorldNativePixelsVerified':True,'unchangedOutsideROIsVerified':True,
   'items':[
     {'nativeCenterY':395,'status':'passed_local_scope','geometry':'Small gap at the kink is closed with a continuous brown grout line.','materialPerimeter':'No new discernible rectangular material edge at the 22 by 26 pixel selection boundary.'},
     {'nativeCenterY':1090,'status':'passed_local_scope','geometry':'Small interruption in the diagonal is closed; the local angular bevel is continuous.','materialPerimeter':'No new discernible rectangular material edge at the 22 by 26 pixel selection boundary.'}
   ],
   'adoption':'Both exact ROIs may be adopted into the shared edge at their recorded world coordinates; this does not accept other parts of the west seam.'},
 'viewedVisuals':[ref(p) for p in visualfiles],
 'hashBoundInputs':bound,
 'unchangedCandidateFiles':True,'generationPerformed':False,
 'remainingProblems':['Original c3/c4 vertical pavement material seam remains unresolved.','Whole-tile internal and complete actual-neighbor acceptance is outside this local review.']}
target=out/'independent-local-review-v1.json'
assert not target.exists()
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':ref(target),'narrowPixels':int(mask.sum()),'microPixels':int(mmask.sum()),'oldNewBaseContextEqual':oldnewcontextEqual},indent=2))
