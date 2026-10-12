"""Bind retained audited source hashes and newly viewed edits to the current196 exports."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
audits={}
for p in (B/"review").glob("anatomy-audit-*-20261005.json"):
    a=read(p)
    groups=a.get("groups") or [dict(frames=a["frames"])]
    for g in groups:
        for f in g["frames"]:
            key=(f.get("action","run"),f.get("direction",g.get("direction")),f.get("slot",f.get("frame")))
            assert key not in audits
            audits[key]=(f,p.relative_to(B).as_posix())
plan=read(B/"review/anatomy-revision-decisions-20261005.json")
edits={(r["action"],r["direction"],r["frame"]):r for r in plan["decisions"]}
overview=read(B/"review/all-actions-selection.json"); rows=[]
for g in overview["groups"]:
    for f in g["frames"]:
        key=(g["action"],g["direction"],f["frame"])
        prior,record=audits[key]
        if key in edits:
            decision=edits[key]; assert f["sourceSha256"]==decision["sourceSha256"]
            assert prior["sourceSha256"]==decision["replacesSha256"]
            inspection=decision["review"]
        else:
            assert f["sourceSha256"]==prior["sourceSha256"]
            inspection=record
        assert sha((B/f["source"]).resolve())==f["sourceSha256"]
        assert sha(B/f["file"])==f["sha256"]
        rows.append(dict(action=key[0],direction=key[1],frame=key[2],source=f["source"],sourceSha256=f["sourceSha256"],export=f["file"],exportSha256=f["sha256"],inspection=inspection,replaced=key in edits,durationMs=f["durationMs"]))
assert len(rows)==len(audits)==196
result=dict(checkedAt=datetime.now(timezone.utc).isoformat(),overviewSha256=sha(B/"review/all-actions-selection.json"),slots=196,replaced=len(edits),retained=196-len(edits),runFrameMs=60,runCycleMs=960,rows=rows,method="Hash-bound visual review coverage; original audits retain their historical75ms timing, current playback is60ms.",userAccepted=False,clientAccepted=False)
(B/"review/anatomy-current-coverage-20261005.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ["slots","replaced","retained","runFrameMs","runCycleMs"]}))

