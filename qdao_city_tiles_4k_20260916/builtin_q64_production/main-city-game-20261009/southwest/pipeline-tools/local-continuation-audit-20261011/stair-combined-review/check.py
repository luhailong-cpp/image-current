import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime,timezone
O=Path(__file__).parent;S=O.parents[2];D=S/"pipeline-tools/crossedge-stair-restored-20261011/stair-combined"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(D/"proposal.json");m=read(D.parent/"manifest.json")
a=np.array(Image.open(p["input"]).convert("RGB"));b=np.array(Image.open(p["premixed"]).convert("RGB"));alpha=np.array(Image.open(p["alpha"]).convert("L"));mask=np.array(Image.open(p["copyMask"]).convert("L"))>0;native=np.array(Image.open(D/"native-union.png").convert("RGB"))
orig=np.zeros_like(a);coverage=np.zeros(a.shape[:2],bool);sources=[]
for s in p["sourceCrops"]:
 im=np.array(Image.open(s["file"]).convert("RGB"));ctx=np.array(Image.open(s["context"]).convert("RGB"))
 l,t,r,bt=s["sourceCrop"];dl,dt,dr,db=s["destinationBox"];orig[dt:db,dl:dr]=im[t:bt,l:r];coverage[dt:db,dl:dr]=True
 v3=S/"integrated-20261011/v3"/(s["tile"]+".candidate.png")
 sources.append({"tile":s["tile"],"sourceHashVerified":sha(s["file"])==s["sha256"],"contextHashVerified":sha(s["context"])==s["contextSha256"],"coreMatchesContext":bool(np.array_equal(ctx[115:4211,115:4211],im)),"v3CandidateSamePixels":bool(np.array_equal(np.array(Image.open(v3).convert("RGB")),im))})
w=alpha.astype(np.uint32)[...,None];replay=((a.astype(np.uint32)*(255-w)+native.astype(np.uint32)*w+127)//255).astype(np.uint8)
copied=np.where(mask[...,None],b,a)
changed=np.any(a!=b,axis=2);yy,xx=np.where(changed);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
checks={"manifestProposalHashMatches":sha(D/"proposal.json")==m["proposals"][0]["sha256"],"manifestVisualQAHashMatches":sha(D/"visual-qa.json")==m["visualQA"]["sha256"],"inputHashMatches":sha(p["input"])==p["inputSha256"],"premixedHashMatches":sha(p["premixed"])==p["premixedSha256"],"alphaHashMatches":sha(p["alpha"])==p["alphaSha256"],"copyMaskHashMatches":sha(p["copyMask"])==p["copyMaskSha256"],"sourceInputReplayExact":bool(coverage.all() and np.array_equal(orig,a)),"nativeAlphaReplayExact":bool(np.array_equal(replay,b)),"singleCopyMaskReplayExact":bool(np.array_equal(copied,b)),"copyMaskEqualsAlphaNonzero":bool(np.array_equal(mask,alpha>0)),"outsideMaskChangedPixels":int(changed[~mask].sum()),"woodRows0to194Unchanged":bool(np.array_equal(a[:195],b[:195])),"rightContextFromX915Unchanged":bool(np.array_equal(a[:,915:],b[:,915:])),"last50RowsUnchanged":bool(np.array_equal(a[-50:],b[-50:])),"changedPixels":int(changed.sum()),"maskPixels":int(mask.sum()),"actualChangedWorldBox":[p["worldBox"][0]+bbox[0],p["worldBox"][1]+bbox[1],p["worldBox"][0]+bbox[2],p["worldBox"][1]+bbox[3]],"sourceChecks":sources}
protected=[]
for band in p["protectedOriginalBevelWorldBands"]:
 y0=band[1]-p["worldBox"][1];y1=band[3]-p["worldBox"][1]
 protected.append({"worldBox":band,"exactSourcePixelsPreserved":bool(np.array_equal(a[y0:y1],b[y0:y1])),"alphaZero":bool((alpha[y0:y1]==0).all())})
gens=[]
for g in p["generations"]:
 d=read(g["file"]);gens.append({"record":g["file"],"recordHashVerified":sha(g["file"])==g["sha256"],"nativeFile":d["file"],"nativeSha256":sha(d["file"]),"nativeHashVerified":sha(d["file"])==d["sha256"],"pixels":list(Image.open(d["file"]).size),"actualModel":d.get("actualModel"),"actualQuality":d.get("actualQuality")})
cropmeta=[]
for wy in [40507,40734]:
 cy=wy-p["worldBox"][1];box=[427,cy-70,827,cy+70]
 for label,arr in [("before",a),("after",b)]:
  f=O/f"bevel-{wy}-{label}.png";Image.fromarray(arr).crop(box).save(f)
  cropmeta.append({"file":str(f),"worldBox":[19853+box[0],39320+box[1],19853+box[2],39320+box[3]],"resized":False})
q={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","status":"accept_as_provisional_improvement_not_complete_edge_pass","sourceProposal":{"file":str(D/"proposal.json"),"sha256":sha(D/"proposal.json")},"visualReview":{"viewed":["input.png","premixed.png","top-before.png","top-after.png","middle-before.png","middle-after.png","bottom-before.png","bottom-after.png"],"improvement":"Long artificial vertical color divider at world x20480 is substantially reduced through most stair faces and tread surfaces. Stair count and large horizontal geometry remain coherent.","geometry":"No new gross staircase geometry defect seen in proposal. Two inherited protected bevel bands still show clear localized height/color discontinuities.","material":"Local cross-edge color transition improves, while dense scalloped/crosshatched stone material remains inconsistent with approved calm broad stone faces. Mild texture-density changes persist around the sparse mask perimeter."},"mechanicalChecks":checks,"protectedOriginalBands":protected,"nativeProvenance":gens,"remainingIssues":[{"id":"STAIR-BEVEL-40507","priority":"P2","scope":"local_geometry_and_color","worldInspectionBox":[20280,40437,20680,40577],"finding":"Inherited short bevel-color/height discontinuity at x20480 within protected original strip y40499-40516; still visible after material patch.","nextStep":"Keep pending; future tiny native geometry repair should align bevel across the tile boundary and preserve surrounding stair level."},{"id":"STAIR-BEVEL-40734","priority":"P2","scope":"local_geometry_and_color","worldInspectionBox":[20280,40664,20680,40804],"finding":"Clear short bright-edge offset at x20480 within protected original strip y40726-40743, visually roughly3-4px. It is preserved baseline, not a new improvement.","nextStep":"Keep pending; repair the short bright bevel/join when generation becomes available, without moving the whole step."},{"id":"STAIR-MATERIAL-GLOBAL","priority":"P1","scope":"broad_existing_surface_style","worldBox":p["worldBox"],"finding":"Dense overlapping scaly/woven marks remain over stair stone; local color smoothing does not meet approved quiet material reference.","nextStep":"Coordinate material treatment with adjacent stone surfaces after a representative style pilot; do not mark this native return as a complete material fix."},{"id":"STAIR-MASK-PERIMETER","priority":"P2","scope":"local_material","affectedWorldBox":p["affectedWorldBox"],"finding":"Some mild density transitions remain near left/right sparse mask edges; re-review within merged4K context.","nextStep":"Assess after parent integration; do not create extra artificial joints to hide it."}],"mergeRecommendation":{"mayMergeAsImprovement":True,"sourceCompatibility":"Both affected v3 source candidates remain pixel-identical to recorded v2, independently verified.","method":"Validate source input under copy-mask, then copy premixed exactly once where mask is nonzero; no second alpha blend.","retainPendingEdge":"north_vertical","formalAccepted":False},"cropEvidence":cropmeta,"networkRequests":0,"newImageGenerationCalls":0,"sourceArtworkModified":False}
(O/"qa-review.json").write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(O/"report.txt").write_text("Can merge as a provisional improvement. Long x20480 color divider is substantially reduced. Exact mask/source replay passes. Both affected v3 tiles equal the recorded v2 sources. Keep north_vertical pending: protected bevels near world y40507 and y40734 retain short height/color joins; dense scaly/woven material remains global and sparse mask perimeter has mild density transitions. Copy premixed once through copy-mask, with source validation. No network or generation was used.\n",encoding="utf-8")
print(json.dumps({"checks":checks,"protected":protected,"native":gens},ensure_ascii=False))

