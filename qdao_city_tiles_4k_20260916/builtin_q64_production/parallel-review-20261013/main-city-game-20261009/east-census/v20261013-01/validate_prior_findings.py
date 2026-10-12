"""Carry forward prior visual verdicts only where current checked pixels are identical."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
from PIL import Image,ImageChops
sys.stdout.reconfigure(encoding="utf-8")
OUT=Path(__file__).resolve().parent
R=Path(r"D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009")
T={x["tile"]:x for x in json.loads((OUT/"current-tiles.json").read_text(encoding="utf-8"))}
S=R/"southeast";N=R/"northeast"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def file(p,expected=None):
 d={"path":str(p),"sha256":sha(p)}
 if expected:d.update(recordedSha256=expected,hashMatchesRecord=(d["sha256"]==expected))
 return d
def current(t):return T[t]["currentCandidate"]["path"]
def equal_crop(pa,ba,pb,bb=None):
 with Image.open(pa) as a,Image.open(pb) as b:
  ac=a.crop(ba).convert("RGB");bc=b.crop(bb or ba).convert("RGB")
  equal=ac.size==bc.size and ImageChops.difference(ac,bc).getbbox() is None
 return {"pathA":str(pa),"boxA":ba,"pathB":str(pb),"boxB":bb or ba,"pixelsIdentical":equal}

checks=[]
# Whole candidate hash changed, but saved full-width 627px seam windows can prove an existing review remains valid.
p=N/"r07_c13/qa/north-final-20261011/report.json";d=read(p);crops=[]
for w in d["windows"]:
 crops.append({"evidence":file(w["file"],w["sha256"]),
   "north":equal_crop(current("r06_c13"),w["northSourceBoxHalfOpen"],w["file"],[0,0,1254,627]),
   "south":equal_crop(current("r07_c13"),w["southSourceBoxHalfOpen"],w["file"],[0,627,1254,1254])})
valid=all(x["evidence"]["hashMatchesRecord"] and x["north"]["pixelsIdentical"] and x["south"]["pixelsIdentical"] for x in crops)
checks.append({"pair":["r06_c13","r07_c13"],"id":"north-final-existing-review","priorVisualVerdict":"no-P2/full-edge geometry pass with P3 material watch","currentEvidenceValid":valid,"status":"prior_visual_review_reusable_pixel_identity_verified" if valid else "new_current_review_required","priorReport":file(p),"comparisons":crops,"wholeCandidateHashChangeDoesNotInvalidateUnchangedCheckedPixels":valid})

# r14c15 latest north-only repair and r14c14 far-east north-only repair leave the W01..W04 checked areas untouched.
p=S/"r14_c15/review/assembly-c162322cbdcca7cb2291/visual-qa-v3-3f0ba6b3.json";d=read(p);old_child=d["candidate"]
for f in d["externalCoreJoins"]["remainingFindings"]:
 if not f["id"].startswith("W"):continue
 x0,y0,x1,y1=f["boxInChildRelativeCoordinates"]
 a=equal_crop(current("r14_c15"),[0,y0,x1,y1],old_child["path"])
 b=equal_crop(current("r14_c14"),[4096+x0,y0,4096,y1],f["neighbor"]["path"])
 valid=a["pixelsIdentical"] and b["pixelsIdentical"]
 checks.append({"pair":["r14_c14","r14_c15"],"id":f["id"],"priorVisualVerdict":"failed" if f["id"]!="W04" else "material_watch_with_geometry_repair","boxInChildRelativeCoordinates":f["boxInChildRelativeCoordinates"],"description":f["description"],"currentEvidenceValid":valid,"status":"current_FAIL_inherited_exact_pixels" if valid and f["id"]!="W04" else ("current_material_watch_inherited_exact_pixels" if valid else "new_current_review_required"),"priorReport":file(p),"oldChild":file(old_child["path"],old_child["sha256"]),"oldNeighbor":file(f["neighbor"]["path"],f["neighbor"]["sha256"]),"comparisons":[a,b]})
checks.append({"pair":["r13_c15","r14_c15"],"id":"N01","boxInChildRelativeCoordinates":[214,-70,252,90],"priorVisualVerdict":"failed","status":"old_failure_superseded_by_current_local_repair_pass; full_north_review_pending","currentEvidenceValid":False,"currentLocalRepairQA":file(S/"r14_c15/repairs/north-board-joint-20261012-v1/root-visual-qa-20261013.json")})

# r15c14 internal repairs do not touch outer failure regions; verify both old child and old neighbor pixels.
p=S/"r15_c14/review/assembly-c7fe4d0fb7016f67422f/visual-qa.json";d=read(p);old_child=d["candidate"]
for f in d["findings"]:
 if not f["id"].startswith(("N","W")):continue
 direction="north" if f["id"].startswith("N") else "west"
 nt="r14_c14" if direction=="north" else "r15_c13"
 nb=d["neighborSources"][direction]["candidate"]
 x0,y0,x1,y1=f["box"]
 a=equal_crop(current("r15_c14"),[x0,y0,x1,y1],old_child["path"])
 # Match an equally broad immutable true-core context on the adjacent side.
 nbbox=[x0,4096-max(y1,150),x1,4096] if direction=="north" else [4096-max(x1,150),y0,4096,y1]
 b=equal_crop(current(nt),nbbox,nb["path"])
 valid=a["pixelsIdentical"] and b["pixelsIdentical"]
 checks.append({"pair":[nt,"r15_c14"],"id":f["id"],"priorVisualVerdict":"failed" if f["id"].endswith("01") else "visible_material_discontinuity","boxInChildRelativeCoordinates":f["box"],"description":f["description"],"currentEvidenceValid":valid,"status":"current_FAIL_inherited_exact_pixels" if valid and f["id"].endswith("01") else ("current_material_failure_inherited_exact_pixels" if valid else "new_current_review_required"),"priorReport":file(p),"oldChild":file(old_child["path"],old_child["sha256"]),"oldNeighbor":file(nb["path"],nb["sha256"]),"comparisons":[a,b]})

groups=[
 {"id":"ne-r05-r08-c13-c14","tiles":[f"r{r:02d}_c{c:02d}" for r in range(5,9) for c in (13,14)],"count":8,"allCompleteNativeCandidates":True,"priority":"reuse_valid_existing_review","newChecks":"Only any gap left by hash/pixel validation; both 2x2 groups plus row6/7 boundary already have source-based evidence. No four-zone boundary is in this local group."},
 {"id":"se-r13-r14-c13-c16","tiles":[f"r{r:02d}_c{c:02d}" for r in (13,14) for c in range(13,17) if f"r{r:02d}_c{c:02d}" in T],"count":7,"allCompleteNativeCandidates":True,"priority":"current_true_core_joints_and_corner","newChecks":"Common r13/14 c13/14 junction; r13c14/r14c14 unresolved north x2842/2874; current full r13c15/r14c15 north; r14c14/r14c15 W01/W02/W03 remain valid FAIL. r14c16 missing, so east-lower boundary is missing-neighbor."},
 {"id":"se-r14-r16-c13-c14","tiles":["r14_c13","r14_c14","r15_c13","r15_c14","r16_c13"],"count":5,"allCompleteNativeCandidates":True,"priority":"current_true_core_joints_and_unreviewed_r16c13","newChecks":"r15c14 N01/N02 and W01/W02 failures remain valid if exact crop checks pass; r14c13/r15c13 north local pass needs whole-edge decision; r15c13/r16c13 and r16c13 internal QA still pending; r16c14 missing."}
]
for g in groups:
 g["sources"]={t:T[t]["currentCandidate"] for t in g["tiles"]}

boundaries=[
 {"boundary":"NW/NE c08/c09 rows1..8","completePairs":[],"missingEastSideCompleteSources":[f"r{r:02d}_c09" for r in range(1,9)]},
 {"boundary":"NE/SE r08/r09 columns9..16","completePairs":[],"missingSouthSideCompleteSources":[f"r09_c{c:02d}" for c in range(9,17)],"availableNorthCompleteSources":["r08_c13","r08_c14"],"northPartialSources":["r08_c10","r08_c12","r08_c15"]},
 {"boundary":"SW/SE c08/c09 rows9..16","completePairs":[],"missingEastSideCompleteSources":[f"r{r:02d}_c09" for r in range(9,17)]}
]
for fn,obj in (("prior-finding-pixel-validation.json",checks),("adjacent-review-groups.json",groups),("four-zone-boundaries.json",boundaries)):
 with (OUT/fn).open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2)
print(json.dumps({"finishedAtUtc":datetime.now(timezone.utc).isoformat(),"checks":[{k:v for k,v in x.items() if k in ("pair","id","currentEvidenceValid","status")} for x in checks],"groups":[{"id":x["id"],"count":x["count"]} for x in groups]},ensure_ascii=False,indent=2))
