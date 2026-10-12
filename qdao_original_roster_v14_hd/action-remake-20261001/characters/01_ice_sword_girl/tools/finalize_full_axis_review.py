"""Bind current selections and art decisions to actual reviewed revision hashes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
approved=read(R/"review/full-axis-approved-native-20261005.json")
assert approved["passed"] and not approved["remainingRequiredRepairs"]
revision=read(R/"review/full-axis-revision-selection-20261005.json")
reviewed={f["path"]:f["sha256"] for f in approved["reviewedDrafts"] if f["passed"]}
assert len(reviewed)==len(revision["changes"])
for f in revision["changes"]:
 assert sha(R/f["file"])==f["sha256"] and reviewed[f["source"]]==f["nativeSha256"]
prior=read(R/"review/manifest-before-full-axis-20261005.json")
changes={f["file"]:f for f in revision["changes"]}
for sequence in prior["sequences"]:
 for frame in sequence["frames"]:
  if frame["path"] not in changes:assert sha(R/frame["path"])==frame["sha256"],frame["path"]
assert 196-len(changes)==revision["unchangedFrameCount"]
evidence=[]
for rel in approved["coverageReports"]:
 path=R/rel;assert path.exists()
 evidence.append({"file":rel,"sha256":sha(path)})
now=datetime.now(timezone.utc).isoformat();records=[]
for p in sorted((R/"review").glob("*selection.json")):
 s=read(p)
 if s.get("action") not in ["run","hit","attack","cast"]:continue
 s.update(finalReviewClosedAt=now,finalFullAxisReview="review/full-axis-final-review-20261005.json",remainingRequiredImageRepairs=[],offlineArtworkReviewComplete=True)
 if (s["action"],s["direction"]) in {(f["action"],f["direction"]) for f in revision["changes"]}:
  s["dynamicArtAccepted"]=False
 write(p,s)
 records.append({"selection":p.relative_to(R).as_posix(),"selectionSha256":sha(p),"action":s["action"],"direction":s["direction"],"offlineArtworkReviewComplete":True})
assert len(records)==14
closure={"reviewedAt":now,"passed":True,"reviewType":"actual_sprite_and_neighbor_visual_review","scope":"196 current selected sprites: full leg movement-plane, shoulder/elbow/wrist/grip review. Correct frames retained; specific intermediate arm poses revised.",
"frameCount":196,"revisedFrames":len(changes),"unchangedFrameCount":revision["unchangedFrameCount"],"remainingRequiredRepairs":[],
"revision":{"file":"review/full-axis-revision-selection-20261005.json","sha256":sha(R/"review/full-axis-revision-selection-20261005.json")},
"approvedNative":{"file":"review/full-axis-approved-native-20261005.json","sha256":sha(R/"review/full-axis-approved-native-20261005.json")},
"coverageEvidence":evidence,"clientIntegrated":False,"clientRuntimeVerified":False,"userAcceptanceClaimed":False,
"limitations":["Sequential actual-image art review and automated browser timing/order checks are distinct; this record does not claim a fresh human-rated live temporal playback.","Transparent sprites have no calibrated world floor; no client foot-lock or no-slip guarantee.","Normal knee flexion, heel lift and perspective sole visibility are not treated as outward foot yaw."]}
write(R/"review/full-axis-final-review-20261005.json",closure)
write(R/"review/final-artwork-review.json",{"reviewedAt":now,"status":"complete","scope":closure["scope"],"sequences":records,"priorArtReview":"review/final-artwork-review-before-full-axis-20261005.json","fullAxisRevision":"review/full-axis-revision-selection-20261005.json","fullAxisFinalReview":"review/full-axis-final-review-20261005.json","clientIntegrated":False,"clientRuntimeVerified":False,"userAcceptanceClaimed":False})
print(json.dumps({"reviewClosed":True,"revisedFrames":len(changes),"sequences":14}))
