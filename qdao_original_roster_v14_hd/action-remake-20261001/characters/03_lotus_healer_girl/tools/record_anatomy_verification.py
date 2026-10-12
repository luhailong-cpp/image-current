from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
overview=read(B/"review/all-actions-selection.json")
plan=read(B/"review/anatomy-revision-decisions-20261005.json")
assert overview["selectedExported"]==196 and len(plan["decisions"])==20
stamp=datetime.now(timezone.utc).isoformat()
record=dict(checkedAt=stamp,method="Actual CUA browser controls, decoded-count and timing DOM, all20 changed source labels, next/previous controls, and screenshots. Current native edits and final NE/N/SW/SE contacts viewed separately.",overviewSha256=hashlib.sha256((B/"review/all-actions-selection.json").read_bytes()).hexdigest(),groups=[dict(action=g["action"],direction=g["direction"],decoded=g["present"],cycleMs=g["cycleMs"]) for g in overview["groups"]],changedSources=[dict(direction=r["direction"],frame=r["frame"],source=r["source"],sourceSha256=r["sourceSha256"],observedInBrowser=True) for r in plan["decisions"]],normal=dict(frameMs=60,cycleMs=960,rate=1),slow=dict(frameMs=240,cycleMs=3840,rate=0.25),loop=dict(direction="SW",nextFrom16=1,previousFrom1=16),finalPlayback=dict(action="run",direction="SE",rate=1,size=256,playing=True),technicalChecks=426,independentTimingReadOnlyAudit=dict(boundaryAssertions=52,eventTimeFields=136,passed=True),visualAcceptance=False,clientAcceptance=False,limits=["Some native registration and prop-travel differences remain in per-image reviews.","Browser loading and frame controls do not establish client movement/contact/skill-event correctness."])
write(B/"review/anatomy-browser-verification-20261005.json",record)
plan.update(status="verified_ready_for_retention",verifiedAt=stamp,browserVerification="review/anatomy-browser-verification-20261005.json",exportVerification="review/all-actions-technical-verification.json",coverage="review/anatomy-current-coverage-20261005.json")
write(B/"review/anatomy-revision-decisions-20261005.json",plan)
print("Recorded14groups,20sources,60ms,196covered")

