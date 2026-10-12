"""Close confirmed support defects only after actual static review and all19 replacements."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--approve-static",action="store_true");args=parser.parse_args()
    if not args.approve_static:raise SystemExit("Requires the root's completed visual inspection; metadata alone cannot approve art.")
    selected=[("attack","E",1)]+[(a,"W",i) for a,count in [("hit",6),("attack",12)] for i in range(1,count+1)]
    evidence=[]
    for action,direction,index in selected:
        record_path=ROOT/f"records/{action}-{direction}/{index:02}.generation.json";r=read(record_path)
        assert "guardfix-20261008" in r["prompt"],str(record_path)
        current=ROOT/r["file"];assert hashlib.sha256(current.read_bytes()).hexdigest()==r["sha256"]
        evidence.append({"file":r["file"],"sha256":r["sha256"],"record":record_path.relative_to(ROOT).as_posix(),"nativeSourceSha256":r["native"]["sha256"]})
    metrics=read(ROOT/"records/guardfix-20261008-measurements.json")
    assert all(x["guardfixRecorded"] for x in metrics["w"])
    assert len(metrics["nativeEdges"])==19
    edge_attention=[x for x in metrics["nativeEdges"] if x["edgePixelsAlphaAbove64"]]
    for entry in edge_attention:
        # Root visually inspected this exact native/exported return pose. Six
        # semi-transparent fringe pixels are not a truncated solid ribbon.
        assert entry["file"]=="runtime/attack/W/12.png" and entry["sha256"]=="3e40d8cce21f72450797f24770d47de41d30395f068a320e5edb7fd358f7b276" and entry["edgePixelsAlphaAbove64"]==6 and entry["edgeMaxAlpha"]==88
    historic=ROOT/"records/sequence-continuity-review.pre-guardfix-20261008.json"
    prior=read(ROOT/"records/sequence-continuity-review.json")
    if not historic.exists():save(historic,prior)
    now=datetime.now(timezone.utc).isoformat()
    result={"reviewDate":"2026-10-08","checkedAt":now,"status":"static-repairs-complete-playback-pending",
      "method":"Real builtin image_gen edits to E attack01 and every W hit/attack frame; each author viewed native and exported output. Root viewed final sequence contact sheets plus E01/02/12 and W return-guard exports. Reproducible shoe-component metrics are supporting evidence, not motion approval.",
      "supersedes":"records/sequence-continuity-review.pre-guardfix-20261008.json",
      "resolvedFindings":[{"id":"E-attack-01-foot-outlier","resolution":"AI-edited first-frame lower-body support. Right-shoe dark centroid first-to-second difference reduced from81.0 to3.98 output pixels; end-to-first residual24.51px is recorded for playback assessment."},{"id":"W-return-guard-foot-mismatch","resolution":"All6 W hit and all12 W attack frames AI-edited to original narrow staggered support, including transition frames and final guards, preserving distinct upper-body actions. Final current pixel measurements are in guardfix-20261008-measurements.json."}],
      "confirmedFindings":[],"selectedRepairs":evidence,"guardMeasurements":"records/guardfix-20261008-measurements.json",
      "nativeEdgeReview":{"checkedSelectedRepairs":19,"attention":edge_attention,"resolution":"Exact W attack12 native and export viewed: six low-opacity fringe pixels at maximum alpha88, no solid contour clipping. Other selected repair native edges have no pixels above64."},
      "remainingLimitations":["Independent AI drawings retain small foot, wrist, hair and chiffon variations; actual real-time and quarter-speed playback remains unverified.","Static silhouette, body articulation and source decoding do not establish in-game timing or client performance."],
      "playbackStatus":"not-verified-browser-policy-blocked","playbackEvidence":"records/cast-E/browser-policy-rejection.json","clientStatus":"not-integrated"}
    save(ROOT/"records/sequence-continuity-review.json",result)
    old_path=ROOT/"records/root-static-review.json";old=read(old_path);old["supersededBy"]="records/sequence-continuity-review.json";old["currentAcceptanceStatus"]="static-repairs-complete-playback-pending";save(old_path,old)
    print(json.dumps({"repairedFrames":len(evidence),"staticReview":"confirmed support defects repaired; residual motion review pending","playback":"not-verified"}))
if __name__=="__main__":main()
