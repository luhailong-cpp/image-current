import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
GROUP=ROOT/'G04-southwest-southeast-r10-r11-v1'
AGENTS=Path('D:/work/image/AGENTS.md')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
images=[];sources={}
for name in ['V06-100pct.png','V07-100pct.png','VJ06-100pct.png']:
    tracepath=GROUP/(name+'.trace.json');trace=json.loads(tracepath.read_text(encoding='utf-8-sig'))
    actual=sha(GROUP/name)
    images.append({'file':str(GROUP/name),'actualSha256':actual,'recordedSha256':trace['output']['sha256'],'hashMatch':actual==trace['output']['sha256'],'dimensions':trace['output']['dimensions'],'globalBox':trace['global_box'],'viewMethod':'tools.view_image detail=original; actual image pixels viewed by independent audit_se agent','trace':str(tracepath),'traceSha256':sha(tracepath)})
    for s in trace['sources']:
        if s['file'] not in sources:
            h=sha(s['file']);sources[s['file']]={'file':s['file'],'actualSha256':h,'recordedSha256':s['sha256'],'hashMatch':h==s['sha256'],'tile':s['tile'],'globalBox':s['global_box']}

doc={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'audit_se independent native-resolution visual second review','updatedRootInstructionsRead':{'file':str(AGENTS),'sha256':sha(AGENTS),'modelRule':'2026-10-13 clarification read: existing free/builtin GPT Image 2.5 preferred, GPT Image 2.0 fallback permitted; no extra paid route authorized.','taskScope':'Review-only window; no generation or production writes. This is not a project-wide production stop.'},'images':images,'sources':list(sources.values()),'candidateUsableForCrossZoneAcceptance':False,'formalAccepted':False,'requiresAiMaterialRepair':True,'findings':[{'id':'SE_SW_R11_X28672_MATERIAL_01','classification':'cross-zone material and color-temperature discontinuity','severity':'blocks cross-zone visual acceptance','boundaryX':28672,'observedGlobalBox':[28416,41984,28928,44032],'primaryLine':'global x28672, pixel x256 in each reviewed strip','observations':['V06: warm yellow, fine fragmented/dappled material on the left switches at the exact vertical tile boundary to cooler blue-grey slab surfaces on the right. The line crosses continuous ground surfaces rather than following a physical paving edge or cast-shadow contour.','VJ06: the same change persists through the inter-segment junction, so it is not only a single isolated strip endpoint.','V07: the same material split is visible on the ground above and between/behind wooden rails where the ground is unobscured. Rails occlude portions, so no conclusion is made about hidden ground.'],'geometryAssessment':'No additional major contour displacement is confidently identified from these three strips. This does not certify all geometry or the entire 4096 boundary.','whyAiRepair':'The discontinuity changes fine texture/painterly material as well as hue. A scalar color correction alone is not adequate evidence of repair.','repairScopeRecommendation':{'diagnosticRegionGlobalBox':[28416,41984,28928,44032],'exactRepairMask':'Not defined by this review; production owner should select a ground-only native joint region with sufficient surrounding context.','retain':['existing stone grout and slab boundaries','wooden deck, fence and pillar contours','existing shadow geometry and light direction','native detail density and unscaled coordinates'],'target':'Continuous natural pale-grey/blue-grey stone material and compatible painterly texture on both sides, matching approved map style.','forbiddenWorkarounds':['blur or resampling across seam','stretching or shifting detail to hide mismatch','procedural repainting or invented ground fill','calling cropped/stitched pixels new generated native detail']},'unreviewedExtensions':'These three crops cover y41984..44032 with wood occlusions. Continue checking adjacent V05/V08 and junctions to establish the full affected extent; do not assume outside this interval passes.'}],'sourceHashChangesInvalidateReview':True,'countsSnapshot':{'sourceReport':str(OUT/'southeast-evidence-audit-v2.json'),'sourceReportCutoff':'2026-10-13T00:40:57.558594-04:00','fullySelected16PatchTiles':14,'internallyReadyByCurrentSelection':9,'formalAcceptedByCurrentSelection':0,'selectedPatchPositions':236,'missingSelectedPatchPositions':548,'note':'Counts are the earlier timestamp/hash snapshot, not a live production total.'}}
target=OUT/'visual-second-review-v1.json';assert not target.exists()
target.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(target),'allViewedCropHashesMatch':all(i['hashMatch'] for i in images),'allInputSourceHashesMatch':all(s['hashMatch'] for s in sources.values()),'requiresAiMaterialRepair':True,'observedGlobalBox':[28416,41984,28928,44032]},ensure_ascii=False))
