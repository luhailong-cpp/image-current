import sys,json,hashlib,re
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
O=Path(__file__).parent
S=O.parents[1]
R=S/"r11_c06/repairs-restored-20261011"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=read(R/"G01.proposal.json")
a=np.array(Image.open(p["base"]["file"]).convert("RGB"))
b=np.array(Image.open(p["proposal"]["file"]).convert("RGB"))
patch=np.array(Image.open(p["premixed"]["file"]).convert("RGB"))
mask=np.array(Image.open(p["pasteMask"]["file"]).convert("L"))
alpha=np.array(Image.open(p["nativeAlpha"]["file"]).convert("L"))
donor=np.array(Image.open(R/"G01.native-reuse-donor.png").convert("RGB"))
native=np.array(Image.open(p["nativeSource"]["file"]).convert("RGB"))
l,t,r,bt=p["candidateBox"];old=a[t:bt,l:r]
rep=a.copy();rep[t:bt,l:r]=np.where(mask[...,None]>0,patch,old)
d=np.any(a!=b,axis=2);outside=d.copy();outside[t:bt,l:r]=False
w=alpha.astype(np.uint32)[...,None]
blend=((old.astype(np.uint32)*(255-w)+donor.astype(np.uint32)*w+127)//255).astype(np.uint8)
hashes={k:{"file":p[k]["file"],"expected":p[k]["sha256"],"actual":sha(p[k]["file"]),"matches":sha(p[k]["file"])==p[k]["sha256"]} for k in ["base","nativeSource","premixed","pasteMask","nativeAlpha","proposal"]}
def box(m):
 yy,xx=np.where(m)
 return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
red=(b[:,:,0].astype(int)>b[:,:,1].astype(int)*1.4)&(b[:,:,0].astype(int)>130)&(b[:,:,1]<130)&(b[:,:,2]<130)
red[:t]=False;red[bt:]=False;red[:,:l]=False;red[:,r:]=False
checks={"allDeclaredHashesMatch":all(x["matches"] for x in hashes.values()),"proposal4096Square":list(b.shape)==[4096,4096,3],"nativeSource1254Square":list(native.shape)==[1254,1254,3],"binaryPasteMask":set(np.unique(mask).tolist())<={0,255},"maskReplayExact":bool(np.array_equal(rep,b)),"nativeAlphaReplayExact":bool(np.array_equal(blend,patch)),"zeroMaskPixelsUnchanged":bool(np.array_equal(old[mask==0],b[t:bt,l:r][mask==0])),"outsideROIPixelsChanged":int(outside.sum()),"allFourOuterEdgesExact":bool(np.array_equal(a[0],b[0]) and np.array_equal(a[-1],b[-1]) and np.array_equal(a[:,0],b[:,0]) and np.array_equal(a[:,-1],b[:,-1])),"nativeLeftUnresizedRegionExact":bool(np.array_equal(donor[:,:455-l],native[t-1050:bt-1050,l:455])),"nativeRightTranslatedRegionExact":bool(np.array_equal(donor[:,485-l:],native[t-1050:bt-1050,485+168:r+168]))}
review={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","status":"geometry_pass_object_plane_pending","issue":"r11_c06 G01","sourceProposal":{"file":str(R/"G01.proposal.json"),"sha256":sha(R/"G01.proposal.json")},"candidateBox":p["candidateBox"],"worldBox":p["worldBox"],"hashes":hashes,"mechanicalChecks":checks,"changedPixels":int(d.sum()),"actualChangedBox":box(d),"viewedNativeCrops":[str(R/"G01.qa-before.png"),str(R/"G01.qa-after.png")],"visualReview":{"stairGeometry":"pass_local","reason":"Lowest stair now ends with the upper stair near tile x505; tread, front riser, vertical end and lower bevel are visually continuous. The previous premature end near x285 is corrected.","paperProjectionAndContactShadow":"pending","paperBoxInTile":box(red),"paperReason":"The red scrap previously read as a flat object on the ground. In the proposal it lies in the middle of the extended vertical riser while retaining a flat diamond-like quadrilateral and lower-right shadow. Its support plane and contact shadow do not convincingly establish whether it rests on a tread or adheres to the face; object placement is not accepted.","material":"not_closed_by_this_geometry_review; surrounding dense repetitive stone remains a separate issue"},"mergeRecommendation":"May merge as a provisional local geometry improvement while retaining G01-object-plane as an explicit open visual issue. Do not label the whole G01 repair or whole tile formally accepted.","formalTileAccepted":False,"newImageGenerationCalls":0,"sourceArtworkModified":False}
save("G01-independent-qa.json",review)
# Inventory native exterior neighbors within the current city production tree.
city=S.parent;contract=read(city/"production-contract.json")
allfiles=list(city.rglob("*"))
imagefiles=[x for x in allfiles if x.is_file() and x.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]
boundaries=[]
for c in range(1,9):
 tile=f"r09_c{c:02d}";neighbor=f"r08_c{c:02d}"
 hits=[str(x) for x in imagefiles if neighbor in str(x)]
 boundaries.append({"tile":tile,"edge":"north","neighbor":neighbor,"neighborZone":"northwest","tileAddressedImageFiles":hits,"availableNativeOrFullNeighbor":bool(hits),"status":"needs_neighbor_artwork_and_cross_zone_native_visual_review" if not hits else "files_exist_unreviewed"})
for r0 in range(9,17):
 tile=f"r{r0:02d}_c08";neighbor=f"r{r0:02d}_c09"
 hits=[str(x) for x in imagefiles if neighbor in str(x)]
 boundaries.append({"tile":tile,"edge":"east","neighbor":neighbor,"neighborZone":"southeast","tileAddressedImageFiles":hits,"availableNativeOrFullNeighbor":bool(hits),"status":"needs_neighbor_artwork_and_cross_zone_native_visual_review" if not hits else "files_exist_unreviewed"})
for r0 in range(9,17):boundaries.append({"tile":f"r{r0:02d}_c01","edge":"west","neighbor":None,"status":"world_canvas_boundary_review_against_approved_layout"})
for c in range(1,9):boundaries.append({"tile":f"r16_c{c:02d}","edge":"south","neighbor":None,"status":"world_canvas_boundary_review_against_approved_layout"})
refkeys=[("layoutReference","layoutSha256"),("detailStyleReference","detailSha256"),("primaryStyleReference","primaryStyleSha256")]
refs=[]
for key,hkey in refkeys:
 f=Path(contract[key]);refs.append({"role":key,"file":str(f),"exists":f.exists(),"sha256":sha(f) if f.exists() else None,"matchesContract":sha(f)==contract[hkey] if f.exists() else False})
standards={
"createdAtUtc":datetime.now(timezone.utc).isoformat(),"sourceContract":{"file":str(city/"production-contract.json"),"sha256":sha(city/"production-contract.json")},
"scope":{"tiles":64,"rows":[9,16],"columns":[1,8],"acceleratedSouthwestExclusions":[],"internalSharedEdges":112,"internalFourTileJunctions":49,"crossZoneEdgeSegments":16,"worldCanvasBoundarySegments":16},
"approvedReferenceVerification":refs,
"acceptanceGates":[
{"id":"provenance","requirement":"Real native detail, verified source hashes and dimensions, prompts and approved references; preserve original tool receipts. Actual model/quality remain null when undisclosed. Config targets are not evidence."},
{"id":"assembly","requirement":"Each delivered tile is 4096x4096 fully covered at native resolution; source 1254 crops/1024 core and 115 halo are verified, no enlarged overview or seed pixels presented as final. Context crop must equal tile, masks replay exactly and preserve outside pixels."},
{"id":"layout","requirement":"Match approved v9 layout at correct world coordinates and scale. Preserve buildings, routes, steps, corners, stone/wood edge geometry and sparse prop placement. Do not add roofs, cracks, branches or objects to conceal a seam."},
{"id":"internal_visual","requirement":"Inspect all 16 patch areas, internal joins and intersections using actual-size crops, plus whole-tile material view. Reject broken geometry, duplicated outlines, accidental branches/stubs, guide fragments, repeated texture bands or implausible prop support/shadows. Numerical continuity alone never passes visual QA."},
{"id":"material","requirement":"Natural pale grey/blue-grey stone and approved near-view illustration style. Consistent light direction, scale, texture density and wood/stone colors across patches and tiles. Repetitive scaly texture and broad brightness/color bands remain open even when joins are pixel-continuous."},
{"id":"shared_edges","requirement":"Visually review 112 interior 4096-pixel shared edges and 49 four-tile junctions at native scale. An edge pass refers to both current source hashes; re-review changed strips after repair. Both sides and outer halos must be coherent."},
{"id":"cross_zone","requirement":"Review 16 SW-to-NW/SE boundary segments against recorded actual neighboring native artwork; approved overview can guide placement but cannot substitute for missing native neighbors."},
{"id":"world_boundary","requirement":"Review 16 true exterior canvas segments against approved layout; preserve short north/south exit indication where applicable, without extending exterior panorama. No imaginary outside tile is required."},
{"id":"formal","requirement":"Formal tile acceptance requires all applicable evidence, internal layout/material/prop checks and neighboring edges passed. Local geometry pass, full pixel coverage, exact hash or low seam error alone is insufficient."}
],
"externalNeighborAvailability":{"searchRoot":str(city),"tileAddressedNeighborImagesFound":sum(len(x.get("tileAddressedImageFiles",[])) for x in boundaries),"availableNeighborSegments":sum(bool(x.get("availableNativeOrFullNeighbor")) for x in boundaries),"limitations":"Availability inventory covers saved tile-addressed artwork in current main-city production; excludes unrelated older map variants and scaled overview as native neighbor evidence.","segments":boundaries},
"currentReadiness":{"fullCandidates":4,"formalAccepted":0,"fourCurrentSharedEdges":{"pass":2,"pending":2},"eightCurrent2x2OuterSegments":"all pending complete neighbors and visual review"},
"scopeExclusions":"No client/runtime/capacity work. No old AGENTS gating applied. Restored network is not a present blocker."
}
save("acceptance-and-boundary-readiness.json",standards)
print(json.dumps({"G01":checks,"paperBox":box(red),"boundaryNeighborSegmentsWithFiles":standards["externalNeighborAvailability"]["availableNeighborSegments"],"refs":refs},ensure_ascii=False))

