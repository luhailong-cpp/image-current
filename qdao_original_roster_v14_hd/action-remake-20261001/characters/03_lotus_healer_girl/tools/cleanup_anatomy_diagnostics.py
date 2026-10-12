"""Remove explicitly obsolete diagnostic images after current exports and audits are complete."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
assert B==Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl")
plan=read(B/"review/anatomy-revision-decisions-20261005.json")
assert plan["status"]=="verified_ready_for_retention"
assert read(B/"review/anatomy-current-coverage-20261005.json")["slots"]==196
names=["09-archer-N-reference.png","09-archer-NW-reference.png","attack-W-contact.png","cast-W-contact.png","hit-E-contact.png","hit-W-contact.png","run-E-continuous-support-contact.jpg","run-S-paired-final-contact.jpg","run-S-paired-trial.apng"]
names+=["video-axis-20261004/continuous-"+n+".jpg" for n in ["012","060","108","156","204","252","300","348","390"]]
rows=[]
for name in names:
    p=(B/"review"/name).resolve()
    assert p.is_relative_to(B/"review") and p.suffix in [".png",".jpg",".apng"]
    if not p.exists(): continue
    assert not p.is_symlink()
    rows.append(dict(path=p.relative_to(B).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reason="Superseded contact/APNG or reproducible read-only reference extraction; current14 preview contact sheets, selected masters, exports and all text provenance retained."))
record=dict(checkedAt=datetime.now(timezone.utc).isoformat(),root=B.as_posix(),deleted=[],complete=False)
log=B/"review/anatomy-obsolete-media-cleanup-20261005.json"
assert not log.exists()
for row in rows:
    p=B/row["path"]; assert hashlib.sha256(p.read_bytes()).hexdigest()==row["sha256"]
    p.unlink();record["deleted"].append(row)
    log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
record["complete"]=True
log.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(deleted=len(rows),complete=True)))

