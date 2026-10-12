import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
O=Path(__file__).parent;S=O.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
aPath=S/"r12_c05/pipeline/output/a5704019021dd0ee/assembly.json";a=read(aPath)
p02Path=S/"r12_c05/native/p02_01.png";p02=np.array(Image.open(p02Path).convert("RGB"))
gray=p02.mean(axis=2)
horizontal=[{"x":x,"firstLineY":int(np.argmin(gray[830:900,x])+830),"secondLineY":int(np.argmin(gray[920:1000,x])+920)} for x in [100,500,800,1150]]
vertical=[{"y":y,"firstLineX":int(np.argmin(gray[y,250:370])+250),"secondLineX":int(np.argmin(gray[y,880:1000])+880)} for y in [1020,1100,1210]]
partial=np.array(Image.open(a["output"]["file"]));ctx=np.array(Image.open(a["contextOutput"]["file"]))
issues=[
{"id":"R12-G01","priority":"P1","scope":"local_geometry_lower_part_of_p02_01","status":"repair_required","nativeBox":[0,900,1254,1254],"worldBox":[16269,46865,17523,47219],"finding":"Second horizontal course join is at native y958-962, whereas the submitted geometry asks about y1150. This compresses the broad course between y~865 and y~1150 to about 98 pixels. Not a material-only defect.","target":"Restore the lower course proportion from approved guide/request. Keep first horizontal join near y865-870 and upper diagonal unchanged. Rebuild second join near y1150 and connect the intended sparse transverse joins; no extra strip or new subdivision.","caveat":"Exact transverse coordinates are coarse-guide targets, unlike the exact inherited top edge. Current x311/942 versus prompt x275/925 are secondary alignment deviations; evaluate after restoring the course."},
{"id":"R12-M01","priority":"P1","scope":"global_material_all_five_saved_native_patches_and_inherited_north_context","status":"repair_required","worldRegions":[[16384,45056,20480,46080],[16384,46080,17408,47104]],"finding":"Dense diagonal crosshatching/scaly cells and clustered small flecks cover broad stone faces. Approved detail v1 has broad calm pale-gray faces, low-contrast sparse strokes and restrained rounded fine joins. Some smooth islands in p01_01 and p02_01 do not fix the surrounding repeated texture.","target":"Use an approved close material swatch as style-only reference; repaint broad stone surfaces with smooth broad tonal variation and sparse faint brush marks while preserving all actual grout geometry. Do not blur or enlarge reference pixels into final art.","method":"Validate one representative material pilot before extending the same inherited texture to more patches. Once style is established, revise adjacent surface groups together and re-review their joins; keeping wide old woven bands around every patch would retain the global defect."},
{"id":"R12-M02","priority":"P2","scope":"local_material_transition_firstrow_p01_01_to_p01_02","status":"repair_required_after_global_material_direction_is_set","tileBox":[768,0,1280,1024],"worldBox":[17152,45056,17664,46080],"finding":"A broad relatively warm/smooth area on the left meets a cooler denser woven area near the first internal boundary. It reads as a vertical material patch despite no broken architectural line.","target":"Match broad face value and texture density across this region without painting a false grout line or hiding it with extra cracks."},
{"id":"R12-S01","priority":"P2","scope":"world_y45056_shared_border","status":"geometry_pass_material_pending","worldBox":[16384,44800,20480,45312],"finding":"Four actual-size 1024-wide comparisons show continuous inherited diagonal grout trajectories, with no definite P1 stop or lateral jump. The strip remains visibly overtextured relative to approved stone on both sides.","target":"Retain grout registration during material edits; coordinate any stone face correction with the r11_c05 lower edge. Do not promote to complete visual/formal edge pass solely because coordinates are continuous."}
]
nativeSources=[{"file":str(S/f"r12_c05/native/p01_{i:02d}.png"),"sha256":sha(S/f"r12_c05/native/p01_{i:02d}.png")} for i in range(1,5)]
nativeSources.append({"file":str(p02Path),"sha256":sha(p02Path)})
refs=read(O/"crop-manifest.json")
review={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","status":"geometry_largely_continuous_but_material_fails_and_p02_01_course_repair_required","scope":"r12_c05 first row assembled from four native patches plus newly saved p02_01; no complete tile yet","assembly":{"file":str(aPath),"sha256":sha(aPath)},"output":{"file":a["output"]["file"],"sha256":sha(a["output"]["file"]),"pixels":list(Image.open(a["output"]["file"]).size),"coreMatchesContext":bool(np.array_equal(partial,ctx[115:1139,115:4211]))},"nativeSources":nativeSources,"visualEvidence":"Viewed all first-row native-scale internal joins, 4 north shared-border segments, p02_01 whole native and its exact continuity seed, direct p02_01 upper core boundary, p02 lower course and approved-detail material crops.","northSharedEdge":{"worldY":45056,"worldXRange":[16384,20480],"geometry":"pass_local_visual","material":"pending_global_surface_repair","formalAccepted":False},"firstrowInternalJoins":[{"tileX":1024,"geometry":"no_definite_P1_break","material":"visible_density_and_tone_transition"},{"tileX":2048,"geometry":"no_definite_P1_break","material":"globally_overtextured"},{"tileX":3072,"geometry":"continuous_diagonal","material":"globally_overtextured"}],"p02_01":{"topDiagonal":"visually continuous with first-row source across direct core boundary; no definite P1 break","firstHorizontal":"near requested y870","secondHorizontal":"approximately190pixels_early","measurements":{"horizontal":horizontal,"vertical":vertical},"geometryFormalPass":False,"materialPass":False},"issues":issues,"recommendedMaterialReferences":[{"source":str(S.parents[1]/"parallel_20261005/daylight-only-20261009/tianyong/tianyong-natural-stone-detail-v1.png"),"sha256":"c10e878611dc2f373159257f5fc42d26957f04e35f19dee78fe1658e364e4809","sourceBox":[477,865,773,989],"crop":str(O/"ref-stone-context.png"),"use":"Primary crop: broad calm stone faces and restrained join edges; ignore small red scrap at upper-left. Style only, not new layout."},{"sourceBox":[523,920,741,978],"crop":str(O/"ref-stone-face.png"),"use":"Quiet face swatch with faint broad variation; exclude its grout/curved perimeter when borrowing surface style."},{"sourceBox":[1183,500,1254,865],"crop":str(O/"ref-right-paving.png"),"use":"Secondary straight-joint finish and low-contrast stone tones; do not copy its grid or slab count."}],"referenceScaleCaveat":"These are unresized crops from the approved 1254 reference, not 1254 generated replacement patches. Use their surface language, not pixel density or grid layout, and do not upscale/paste them into final artwork.","cropManifest":str(O/"crop-manifest.json"),"formalAccepted":False,"sourceArtworkModified":False,"newImageGenerationCalls":0}
save("qa-review.json",review)
(O/"repair-list.txt").write_text("""r12_c05 independent review
North boundary y45056: grout geometry visually continuous in four native-size crops; material still pending.
First-row internal joins: no definite P1 line break; first seam has warm/smooth to cool/woven face transition.
p02_01: top diagonal continues; upper horizontal join near y865 is plausible. Lower horizontal join is y958-962 instead of requested y~1150, shortening the course by about190px. Restore lower-course geometry in native [0,900,1254,1254] before material approval; transverse joins also need guide alignment review.
All five saved native patches: broad dense crosshatching/scaly texture fails approved quiet stone style. This is global surface work, not a tiny seam repair. Establish a representative material pilot using ref-stone-context.png/ref-stone-face.png, then coordinate neighboring surfaces and north border. Preserve real grout paths, do not blur or add cracks.
Reference crops retain native reference resolution and are style-only. Never enlarge/paste the approved overview or reference as production artwork.
No formal tile or full edge acceptance from this review.
""",encoding="utf-8")
# Independently verify v3 merged G01 only and all external boundary strips remain unchanged.
v2=S/"integrated-20261011/v2";v3=S/"integrated-20261011/v3";va=read(v3/"assembly.json")
gp=read(S/"r11_c06/repairs-restored-20261011/G01.proposal.json")
patch=np.array(Image.open(gp["premixed"]["file"]).convert("RGB"));mask=np.array(Image.open(gp["pasteMask"]["file"]).convert("L"))>0
checks=[]
for tile,x in va["outputs"].items():
 old=np.array(Image.open(v2/(tile+".candidate.png")).convert("RGB"));new=np.array(Image.open(x["candidate"]["file"]).convert("RGB"))
 oldctx=np.array(Image.open(v2/(tile+".candidate.context.png")).convert("RGB"));newctx=np.array(Image.open(x["context"]["file"]).convert("RGB"))
 expected=old.copy();expectedctx=oldctx.copy()
 if tile=="r11_c06":
  l,t,r,b=gp["candidateBox"]
  expected[t:b,l:r]=np.where(mask[...,None],patch,expected[t:b,l:r])
  expectedctx[t+115:b+115,l+115:r+115]=np.where(mask[...,None],patch,expectedctx[t+115:b+115,l+115:r+115])
 bands={}
 for side,v,w in [("north",old[:115],new[:115]),("south",old[-115:],new[-115:]),("west",old[:,:115],new[:,:115]),("east",old[:,-115:],new[:,-115:])]:bands[side]=bool(np.array_equal(v,w))
 c={"tile":tile,"candidateSha256":sha(x["candidate"]["file"]),"contextSha256":sha(x["context"]["file"]),"assemblyHashesMatch":sha(x["candidate"]["file"])==x["candidate"]["sha256"] and sha(x["context"]["file"])==x["context"]["sha256"],"coreEqualsContextCrop":bool(np.array_equal(new,newctx[115:4211,115:4211])),"expectedCandidateReplayExact":bool(np.array_equal(new,expected)),"expectedContextReplayExact":bool(np.array_equal(newctx,expectedctx)),"changedCorePixels":int(np.any(old!=new,axis=2).sum()),"changedContextPixels":int(np.any(oldctx!=newctx,axis=2).sum()),"outer115PixelCoreBandsUnchanged":bands}
 if tile=="r11_c06":c["pixelsEqualG01ReviewedProposal"]=bool(np.array_equal(new,np.array(Image.open(gp["proposal"]["file"]).convert("RGB"))))
 checks.append(c)
save("v3-mechanism-qa.json",{"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"mechanical_integration_pass_visual_readiness_unchanged_except_local_G01_geometry","assembly":{"file":str(v3/"assembly.json"),"sha256":sha(v3/"assembly.json")},"checks":checks,"boundaryConclusion":"All four tiles' 115-pixel outer core bands are unchanged from v2; shared edges retain prior 2pass/2material-pending dispositions. Existing r12 north anchor remains byte-identical source because r11_c05 is unchanged.","G01":"Merged pixels match the independently viewed proposal exactly; local geometry pass; red paper support plane and contact shadow remain pending at tile [392,1438,464,1484].","formalAccepted":False,"newImageGenerationCalls":0,"sourceArtworkModified":False})
print(json.dumps({"p02Measures":{"horizontal":horizontal,"vertical":vertical},"v3":checks},ensure_ascii=False))

