import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
O=Path(__file__).parent;S=O.parents[2]
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert("RGB"))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(y) else None
now=datetime.now(timezone.utc).isoformat()
D=S/"r11_c06/repairs-restored-20261011";path=D/"G01-object-plane.proposal.json";p=read(path)
a=arr(p["base"]["file"]);b=arr(p["proposal"]["file"]);patch=arr(p["premixed"]["file"]);mask=np.array(Image.open(p["pasteMask"]["file"]).convert("L"))>0
l,t,r,bt=p["candidateBox"];replay=a.copy();replay[t:bt,l:r]=np.where(mask[...,None],patch,a[t:bt,l:r]);change=np.any(a!=b,axis=2);out=change.copy();out[t:bt,l:r]=False
reds=lambda z:(z[:,:,0]>130)&(z[:,:,0].astype(float)>z[:,:,1]*1.4)&(z[:,:,1]<130)&(z[:,:,2]<130)
red=reds(b[t:bt,l:r]);redbox=bbox(red);redtile=[redbox[0]+l,redbox[1]+t,redbox[2]+l,redbox[3]+t]
hashes={k:{"file":p[k]["file"],"sha256":sha(p[k]["file"]),"matches":sha(p[k]["file"])==p[k]["sha256"]} for k in ["base","premixed","pasteMask","proposal"]}
checks={"hashesAllMatch":all(v["matches"] for v in hashes.values()),"maskReplayExact":bool(np.array_equal(replay,b)),"outsideROIChangedPixels":int(out.sum()),"changedPixels":int(change.sum()),"fourOuter115PixelBandsUnchanged":bool(np.array_equal(a[:115],b[:115]) and np.array_equal(a[-115:],b[-115:]) and np.array_equal(a[:,:115],b[:,:115]) and np.array_equal(a[:,-115:],b[:,-115:])),"oldRiserRedPixelsRemaining":int(reds(b[1432:1501,380:488]).sum()),"proposalBaseMatchesV3Pixels":bool(np.array_equal(a,arr(S/"integrated-20261011/v3/r11_c06.candidate.png")))}
q={"createdAtUtc":now,"reviewer":"resume_crossedge_audit","issue":"G01-object-plane","status":"local_contact_plane_pass_pending_parent_merge","proposal":{"file":str(path),"sha256":sha(path)},"candidateBox":p["candidateBox"],"worldBox":p["worldBox"],"hashes":hashes,"sourceRegions":[{"file":s["source"]["file"],"sha256":sha(s["source"]["file"]),"matches":sha(s["source"]["file"])==s["source"]["sha256"],"sourceBox":s["sourceBox"],"targetBoxInTile":s["targetBoxInTile"],"translation":s["translation"]} for s in p["sourceRegions"]],"mechanicalChecks":checks,"redPaperBoxInTile":redtile,"redPaperBoxInWorld":[redtile[0]+20480,redtile[1]+40960,redtile[2]+20480,redtile[3]+40960],"visualFinding":"The single red scrap now lies fully on the horizontal tread, with a short contact shadow and a planar projection consistent with that surface. The previous red scrap on the vertical face is removed cleanly. Stair endpoint and bevel remain coherent; no duplicate scrap visible.","mayCloseLocalIssueAfterExactMerge":True,"formalTileAccepted":False,"materialAcceptance":"not addressed; dense stone pattern still pending","evidenceViewed":[str(D/"G01-object-plane.qa-after.png"),str(D/"G01.qa-after.png")],"networkRequests":0,"newImageGenerationCalls":0}
save("G01-object-plane-independent-qa.json",q)
# first bevel proposal
D=S/"pipeline-tools/stair-short-bevels-local";path=D/"proposal.json";p=read(path)
a=arr(p["input"]);b=arr(p["premixed"]);mask=np.array(Image.open(p["copyMask"]).convert("L"))>0;alpha=np.array(Image.open(p["alpha"]).convert("L"))
native=arr(p["source"]["native"]);x0,y0,x1,y1=p["source"]["nativeCrop"];n=native[y0:y1,x0:x1]
w=alpha.astype(np.uint32)[...,None];mixed=((a.astype(np.uint32)*(255-w)+n.astype(np.uint32)*w+127)//255).astype(np.uint8)
parent=read(p["dependsOnProposal"]);pa=arr(parent["premixed"]);wx,wy,wr,wb=p["worldBox"];px,py,pr,pb=parent["worldBox"];base=pa[wy-py:wb-py,wx-px:wr-px]
checks={"dependencyHashMatches":sha(p["dependsOnProposal"])==p["dependsOnProposalSha256"],"expectedParentPremixedHashMatches":sha(parent["premixed"])==p["expectedParentPremixedSha256"],"sourceInputEqualsParentCrop":bool(np.array_equal(base,a)),"nativeHashMatches":sha(p["source"]["native"])==p["source"]["nativeSha256"],"nativeDimensions":list(Image.open(p["source"]["native"]).size),"oneToOneNativeAlphaReplayExact":bool(np.array_equal(mixed,b)),"singleCopyMaskReplayExact":bool(np.array_equal(np.where(mask[...,None],b,a),b)),"maskEqualsAlphaNonzero":bool(np.array_equal(mask,alpha>0)),"outsideMaskChangedPixels":int(np.any(a!=b,axis=2)[~mask].sum()),"changedPixels":int(np.any(a!=b,axis=2).sum())}
hashes={key:{"file":p[key],"sha256":sha(p[key]),"matches":sha(p[key])==p[key+"Sha256"]} for key in ["input","premixed","copyMask","alpha"]}
save("stair-first-bevel-independent-qa.json",{"createdAtUtc":now,"reviewer":"resume_crossedge_audit","status":"first_bevel_local_visual_pass_pending_parent_merge","proposal":{"file":str(path),"sha256":sha(path)},"worldBox":p["worldBox"],"affectedWorldBox":p["affectedWorldBox"],"hashes":hashes,"source":p["source"],"mechanicalChecks":checks,"visualFinding":"Before/after actual-size660x80 crops show that the abrupt short vertical value step around x20480/y40507 is removed. The bright bevel reads continuously without an obvious rectangle or gross new bend. This is an acceptable local improvement; uniform translation is unnecessary.","mayCloseFirstBevelLocalIssueAfterMerge":True,"secondBevelWorldY":40734,"secondBevelStatus":"unchanged_pending","northVerticalFullEdgeStatus":"pending_material_and_second_bevel","mergeOrder":"Apply after stair-combined, validating this input under copy-mask; copy premixed once, no second alpha.","formalAccepted":False,"networkRequests":0,"newImageGenerationCalls":0})
# New p02_01 geometry return
f=Path(r"C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-8d525376-9bfc-493f-8d56-b36108442454.png")
n=arr(f);gray=n.mean(axis=2);oldpath=S/"r12_c05/native/p02_01.png";old=arr(oldpath);seedpath=S/"r12_c05/refinement/p02_01.geometry-v02.native-crop-seed.png";seed=arr(seedpath)
horizontal=[{"nativeX":x,"firstLineY":int(np.argmin(gray[825:900,x])+825),"secondLineY":int(np.argmin(gray[1115:1200,x])+1115)} for x in [100,500,800,1150]]
vertical=[{"nativeY":y,"firstLineX":int(np.argmin(gray[y,260:370])+260),"secondLineX":int(np.argmin(gray[y,880:1000])+880)} for y in [1180,1220]]
diagonal=[]
sg=seed.mean(axis=2)
for y in [50,100,150,200,225]:
 start=640+y;end=min(1254,740+y+50)
 diagonal.append({"nativeY":y,"newDarkCenterX":int(np.argmin(gray[y,start:end])+start),"seedDarkCenterX":int(np.argmin(sg[y,start:end])+start)})
diff=np.abs(n[:230].astype(np.int16)-seed[:230].astype(np.int16))
Image.fromarray(n).crop((0,790,1254,1254)).save(O/"p02_01-geometry-v02-lower-native.png")
Image.fromarray(n).crop((250,250,850,750)).save(O/"p02_01-geometry-v02-material-native.png")
q={"createdAtUtc":now,"reviewer":"resume_crossedge_audit","status":"geometry_candidate_pass_material_fail","source":{"file":str(f),"sha256":sha(f),"pixels":list(Image.open(f).size)},"seed":{"file":str(seedpath),"sha256":sha(seedpath)},"contextWorldBox":[16269,45965,17523,47219],"coreWorldBox":[16384,46080,17408,47104],"geometryReview":{"firstHorizontal":"retained near y863","secondHorizontal":"restored near y1152 instead of y~960","middleCourse":"broad uninterrupted course restored, no extra strip/subdivision","transverseJoints":"two clipped lower joints remain nearx314/x938 consistent with revised exact seed","upperRightDiagonal":"large trajectory retained, no definite break seen","measurements":{"horizontal":horizontal,"vertical":vertical,"diagonalVsSeed":diagonal},"localPass":True},"worldHorizontalYRanges":[[45965+min(z["firstLineY"] for z in horizontal),45965+max(z["firstLineY"] for z in horizontal)],[45965+min(z["secondLineY"] for z in horizontal),45965+max(z["secondLineY"] for z in horizontal)]],"materialReview":{"pass":False,"finding":"Dense high-frequency cellular/crosshatched flecks and bright overlaps are stronger than the prior source. The geometry fix does not approach the approved broad quiet gray stone faces; do not adopt this output as material style seed or mark material accepted.","requiredScope":"broad stone-face material repair, preserving corrected grout geometry; not a narrow seam fix"},"top230Comparison":{"pixelExactToSeed":bool(np.array_equal(n[:230],seed[:230])),"changedPixels":int(np.any(n[:230]!=seed[:230],axis=2).sum()),"meanAbsoluteChannelDelta":float(diff.mean()),"note":"Imagegen redraw is not exact neighbor preservation. Any selected assembly must retain/restore original overlap or visually re-review the generated boundary; line continuity alone does not establish exact pixel registration."},"selectionRecommendation":"Usable as a geometry candidate or donor for corrected lower geometry, with material explicitly pending. Prefer limiting application to required region if preserving original upper border; retain provenance and review assembly seam.","formalAccepted":False,"networkRequests":0,"newImageGenerationCalls":0}
save("p02_01-geometry-v02-independent-qa.json",q)
print(json.dumps({"objectChecks":read(O/"G01-object-plane-independent-qa.json")["mechanicalChecks"],"redPaperBox":redtile,"bevelChecks":checks,"p02SourceSha256":q["source"]["sha256"],"p02Geometry":q["geometryReview"],"top230":q["top230Comparison"]},ensure_ascii=False))

