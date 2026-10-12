import json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np
O=Path(__file__).parent;S=O.parents[2];I=S/"integrated-20261011"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert("RGB"))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
e=read(O/"v5-mechanical-evidence.json")
e["status"]="integrated_v5_replay_verified_visual_pending"
e["visualReviewMethod"]="11 of16 actual-scale seam segments are pixel-identical to previously independently reviewed v2. All5 changed actual-scale segments were viewed again. G01-object-plane and first-bevel proposals had independent local visual acceptance before this exact integration replay."
e["visualReviewedChangedSegments"]=e.pop("pendingVisualReviewOfChangedSegments")
e["sharedEdges"]=[
{"id":"west_horizontal","status":"pass_seam_continuity","overallSurfaceMaterial":"still_global_pending","finding":"Original accepted seam registration preserved. Changed pixels in segment4 are the reviewed staircase material patch above the seam; immediate bottom50 rows stay original and continuous."},
{"id":"east_horizontal","status":"pass_seam_continuity","overallSurfaceMaterial":"still_global_pending","finding":"Stone-base and parapet continue; changed segment1 shows the reviewed north staircase material; no new horizontal seam break."},
{"id":"north_vertical","status":"pending","finding":"Wood and long stair color join improve. First short bevel near worldy40507 closes locally. Short bevel near y40734 remains visible, and broad scaly material is not accepted."},
{"id":"south_vertical","status":"pending_material","geometry":"S1/S2 grout geometry remains repaired; no new break from G01/object change.","finding":"Reviewed segment2 has correct red scrap on horizontal tread and corrected stair width; broad brightness/texture mismatch remains."}]
e["locallyClosedIssuesAfterExactReplay"]=["r11_c06 G01 stair width","r11_c06 G01-object-plane red scrap support/contact","north_vertical first bevel y40507"]
exterior=[]
for tile,sides in [("r10_c05",["north","west"]),("r10_c06",["north","east"]),("r11_c05",["south","west"]),("r11_c06",["south","east"])]:
 old=arr(I/"v2"/(tile+".candidate.png"));new=arr(I/"v5"/(tile+".candidate.png"))
 for side in sides:
  if side=="north":a,b=old[0],new[0]
  elif side=="south":a,b=old[-1],new[-1]
  elif side=="west":a,b=old[:,0],new[:,0]
  else:a,b=old[:,-1],new[:,-1]
  exterior.append({"tile":tile,"side":side,"pixelExactToV2":bool(np.array_equal(a,b)),"neighborVisualAcceptance":"pending"})
e["outer2x2EightBoundarySegments"]=exterior
e["contextNote"]="r11 lower-row context PNG hashes change because the north-stair world patch also updates their north halos. r11_c05 core remains unchanged. Context changes are verified replay, not unintended core edits."
e["mechanicalPass"]=all(x["declaredHashesMatch"] and x["expectedContextReplayFromV2Exact"] and x["coreEqualsContextCrop"] and x["outsideAllAddedMasksChangedPixels"]==0 for x in e["tileChecks"])
e["remainingIssues"]=["north_vertical y40734 short bevel","south_vertical material/brightness","broad dense scaly/woven stone material","r10_c06 guide fragment/red sliver","r11_c06 G02/G06 geometry","remaining tiles and outer native-neighbor visual acceptance"]
e["formalAcceptedCount"]=0;e["wholeTileFormalAcceptance"]=False
save(I/"v5/qa-review.json",e)
# macro topology report
f=S.parents[1]/"parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png"
der=read(S/"r12_c05/guides/p02_03.layout-only.png.derivation.json")
q={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","tile":"r12_c05","patch":"p02_03","status":"approved_macro_contains_real_paving_joints_neighbor_natives_conflict","source":{"file":str(f),"sha256":sha(f),"pixels":[1254,1254]},"sourceContextBox":der["layoutSourceBox"],"worldContextBox":der["contextWorldBox"],"worldCoreBox":der["coreWorldBox"],"conclusion":"The gray upper-right-to-lower-left diagonal is a true paving joint. In wider original approved layout it joins the surrounding angled slab topology; treating it as mere shading would erase an approved structural line.","evidence":{"wideOriginalCrop":[300,820,430,950],"pixelCoordinateInspectionCrop":[346,875,380,908],"savedPreview":str(O/"p02_03-source-pixel-coordinates.png"),"previewResizedNearestOnly":True,"gameArt":False},"topology":{"lowerJunction":{"type":"T_junction_on_diagonal_boundary","sourceApprox":[353.7,898.6],"nativeApprox":[168,997],"worldApprox":[18485,46962]},"upperJunction":{"type":"junction_near_or_just_outside_right_context_edge","sourceApprox":[374.8,883.9],"nativeApprox":[1271,229],"worldApprox":[19588,46194]},"minimumVisibleSegments":[{"id":"main_paving_joint","nativeApproxPolyline":[[1254,242],[168,997]],"description":"One sparse joint from right edge near y230-250 down-left to T-junction; no floating interior termination."},{"id":"lower_diagonal_boundary","nativeApproxPolyline":[[0,885],[168,997],[544,1254]],"description":"One continuous diagonal passes through lower-left T-junction from left edge to bottom edge."},{"id":"upper_right_clipped_joint","nativeApproxPolyline":[[926,0],[1254,217]],"description":"Small clipped diagonal in upper-right; connects to neighboring joint near/just outside right edge."}],"uncertainty":"Approximate line center estimates from only about24x24 source pixels. A1-source-pixel error maps to about52 native pixels. Use these as topology/entry-zone guidance, not claims of exact52K line registration.","doNotAdd":["No dense grid","No new parallel decorative band","No center-wide grout lattice","No freestanding groove end","No props, buildings or stair geometry"]},"neighborConflict":{"topSource":str(S/"r12_c05/native/p01_03.png"),"leftSource":str(S/"r12_c05/native/p02_02.png"),"viewedNativeSourceCrops":[{"sourceCrop":[0,1024,1254,1254],"image":str(O/"p01_03-bottom230.png")},{"sourceCrop":[1024,0,1254,1254],"image":str(O/"p02_02-right230.png")}],"finding":"Current exact top and left native strips contain material but lack the macro joints. They cannot be used as evidence that the approved layout is joint-free. The prior no-groove prompt froze this conflict.","repairImplication":"Coordinate boundary corrections in top p01_03 and left p02_02 with p02_03. Do not stop a new correct joint against a preserved blank230px strip. Establish sparse line topology first, then apply the approved quiet material treatment."},"sourceArtworkModified":False,"newImageGenerationCalls":0}
save(O/"p02_03-macro-topology.json",q)
# material pilot independent review
stem=S/"r12_c05/repairs-material-20261011/p01_02-quiet-material-v01"
f=Path(str(stem)+".native.png");req=read(str(stem)+".request.json")
oldpath=Path(req["references"][0]["file"]);new=arr(f);old=arr(oldpath)
positions=[]
for y in [10,40,80,110]:
 # upper-left clipped seam, allow the observed diagonal region only
 xs=max(0,160-int(y*1.3)-55);xe=min(300,160-int(y*1.3)+70)
 positions.append({"nativeY":y,"newSeamDarkCenterX":int(np.argmin(new[y,xs:xe].mean(axis=1))+xs),"oldSeamDarkCenterX":int(np.argmin(old[y,xs:xe].mean(axis=1))+xs)})
q={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","status":"local_material_pilot_pass_pending_neighbor_integration","source":{"file":str(f),"sha256":sha(f),"pixels":list(Image.open(f).size),"expectedSha256Matches":sha(f)=="7c5d01b7f2ea78ceaf3b18e900647fb4edfdf45df61db0106a098588b346e019"},"request":{"file":str(stem)+".request.json","sha256":sha(str(stem)+".request.json")},"targetBaseline":{"file":str(oldpath),"recordedSha256":req["references"][0]["sha256"],"currentFileSha256":sha(oldpath)},"worldContextBox":[17293,44941,18547,46195],"visualFindings":{"referenceFit":"Broad pale-gray face with restrained cloudy tone is sufficiently close to the approved quiet material direction for a representative pilot.","texture":"Dense original crosshatched grid is greatly reduced. Faint residual small-scale marks remain but do not dominate the face at native scale.","blur":"No obvious global defocus; upper-left grout remains crisp and face variation is naturally soft. Lack of dense detail is the requested surface treatment, not by itself blur.","plastic":"No obvious hard specular highlight, waxy rim or plastic gloss. The surface reads matte/satin stone.","geometry":"One tiny upper-left clipped diagonal retained with no new interior grout grid; gross location unchanged.","color":"Calm pale warm-gray/blue-gray variation acceptable within the reference direction."},"seamPositionSupport":positions,"mayUseAsMaterialDirectionForFurtherRepairs":True,"promptReuseRecommendation":"Reuse short concrete material-only prompt and approved close material crop, but replace one-line geometry restriction with each target's actual sparse joints. Do not copy this patch's one-corner-joint topology onto others.","integrationCaveat":"This is a whole-face material repaint, so edges differ from old woven neighbors. Jointly correct adjacent face materials or inspect natural-mask transitions; keep neighboring/source registration evidence. Local material approval is not whole tile or seam acceptance.","formalAccepted":False,"newImageGenerationCalls":0}
save(O/"p01_02-quiet-material-independent-qa.json",q)
print(json.dumps({"v5MechanicalPass":e["mechanicalPass"],"v5QA":str(I/"v5/qa-review.json"),"materialHash":sha(f),"materialSourceStatus":q["status"],"seamPositions":positions},ensure_ascii=False))

