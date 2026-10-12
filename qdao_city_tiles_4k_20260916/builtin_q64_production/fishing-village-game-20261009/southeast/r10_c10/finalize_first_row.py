"""Write first-row inspection and provenance handoff, never changes artwork."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

TILE=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
qa=read(TILE/'qa'/'first-row-qa.json')
findings=[
 {'visualStatus':'geometry_redraw_required','notes':'At the core join x256 in strip, the flower tile end-cap is split into displaced halves and the orange eave kinks. Upper tile-course boundaries also shift slightly. p11-v4 repaired its internal vertical step but changed the west overlap. Recheck against r10_c09 final colorpass and repair geometry jointly; color correction alone cannot fix it.','repairRegionTargetNative':[0,650,430,1254]},
 {'visualStatus':'geometry_redraw_required','notes':'The gold roof edge changes slope/width abruptly at the core join, leaving a triangular fork/step around strip y650..770. Blue tile courses also shift at the join. The cloth rib near y1060 is close but still needs recheck after the geometric repair.','repairRegionTargetNative':[0,0,470,1100]},
 {'visualStatus':'geometry_candidate_color_texture_match_required','notes':'Upper wooden/canopy binding and lower thin binding continue without a large geometric break at native view. There is a visible fabric color/weave discontinuity, mean RGB core-join step 8.05; no acceptance is claimed before local matching and complete surrounding QA.','repairRegionTargetNative':[0,0,400,1254]},
 {'visualStatus':'geometry_redraw_required','notes':'Deck plank seams and upper canopy binding continue approximately, but the lower curved canopy side edge is displaced substantially at the join, appearing as two separate diagonal hems. It requires structural redraw, not blur or color blending.','repairRegionTargetNative':[0,800,650,1254]},
]
for seam,finding in zip(qa['seams'],findings):
    seam.update(finding)
    seam['reviewedAt']=stamp
    seam['formalAccepted']=False
qa.update(reviewedAt=stamp,status='first_row_candidates_inspected_geometry_repairs_outstanding',formalAcceptedCount=0)
write(TILE/'qa'/'first-row-qa.json',qa)
selected=read(TILE/'selected-patches.json')
selected.update(status='first_row_candidates_geometry_repairs_outstanding',formalAccepted=False,updatedAt=stamp)
write(TILE/'selected-patches.json',selected)
entries=[]
for path in sorted((TILE/'native').glob('*.png')):
    rec_path=path.with_suffix('.png.generation.json')
    rec=read(rec_path)
    image=Image.open(path)
    assert image.size==(1254,1254)
    assert rec['sha256']==sha(path)
    assert Path(rec['prompt']).exists() and Path(rec['evidence']['receipt']).exists()
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert rec['submittedParameters']=={'model':None,'quality':None}
    for ref in rec['references']:
        assert sha(ref['path'])==ref['sha256']
    entries.append({'file':str(path),'sha256':sha(path),'record':str(rec_path),'recordSha256':sha(rec_path),'nativeDimensions':list(image.size),'selectedCandidate':path.relative_to(TILE).as_posix() in selected['patches'].values(),'configTarget':{'model':rec['configSnapshot']['model'],'quality':rec['configSnapshot']['quality']},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None})
write(TILE/'generation-index.json',{'tile':'r10_c10','updatedAt':stamp,'route':'builtin','count':len(entries),'images':entries,'actualModelQualityConfirmed':False})
progress=read(TILE/'progress.json')
progress.update(updatedAt=stamp,status='first_row_candidates_inspected_geometry_repairs_outstanding',currentPatch=None,generatedNativeCount=len(entries),selectedNativeCount=4,firstRowCandidateCount=4,complete4kCount=0,formalAcceptedCount=0,externalSeamsRequireRecheck=True,nextStep='Repair west external flower/eave join, p11-p12 gold edge, and p13-p14 canopy hem geometry; locally match p12-p13 cloth; then recheck before next row generation',errors=[{'kind':'visual_geometry','attempt':'p11-v1','detail':'Internal pasted seam at x209; roof courses and fascia step.'},{'kind':'visual_geometry','attempt':'p11-v2','detail':'Internal seam removed but left anchor roof/eave moved.'},{'kind':'visual_geometry','attempt':'p11-v3','detail':'Upper course continuity improved but lower eave step persists.'},{'kind':'visual_geometry','attempt':'p11-v4','detail':'Internal step removed; external flower tile/eave no longer aligns.'}],toolFailures=[])
write(TILE/'progress.json',progress)
print(json.dumps({'nativeImages':len(entries),'referenceHashesVerified':sum(len(read(p.with_suffix('.png.generation.json'))['references']) for p in (TILE/'native').glob('*.png')),'selectedCandidates':4,'formalAccepted':0,'qaStatus':qa['status']},indent=2))
