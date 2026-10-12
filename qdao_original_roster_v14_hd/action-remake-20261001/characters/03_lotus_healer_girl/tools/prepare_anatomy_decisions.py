"""Create an explicit decision ledger only after root has viewed every selected edit."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
choices=[
("E",11,"11-anatomy-v1","近解剖右肩通过前景袖接灯，远左手托瓶；原腿相位保持。"),
("W",3,"03-anatomy-v2","右灯臂收向身侧中间位，左瓶与原支撑相位保持。"),
("W",4,"04-anatomy-v1","右灯臂回收，衔接03与05，近左瓶与原腿保持。"),
("N",3,"03-anatomy-v1","右脚中段支撑、左腿回收；右灯臂恢复胸侧连续高度。"),
("N",7,"07-anatomy-v2","北向原腿支撑相位保持；左掌仅托瓶腹，右手持灯。"),
("N",8,"08-anatomy-v2","北向原末支撑相位保持；左掌仅托瓶腹，右手持灯。"),
("N",9,"09-anatomy-v1","北向换步相位保持；左掌仅托瓶腹，右手持灯。"),
("N",10,"10-anatomy-v3","北向压缩承重相位保持；左掌仅托瓶腹，旧颈握手移除。"),
("NE",3,"03-anatomy-v1","东北支撑鞋收窄，脚掌朝向随膝踝，保持原弯腿相位。"),
("NE",4,"04-anatomy-v2","东北支撑鞋收窄且灯瓣完整；保留原腿弯曲相位。"),
("NE",8,"08-anatomy-v2","东北末支撑鞋收窄，保持旧头顶和足底高度范围。"),
("SE",2,"02-anatomy-v1","东南前支撑鞋收正至踝下，另一腿屈膝回收。"),
("SE",3,"03-anatomy-v1","东南中段支撑鞋收正，右灯手经过身侧中间位。"),
("SE",4,"04-anatomy-v1","东南后段支撑鞋收正至踝下，另一腿上抬。"),
("SE",11,"11-anatomy-v1","东南另一半圈支撑鞋收正，右灯手保持腰侧过渡。"),
("SE",12,"12-anatomy-v1","东南后段支撑鞋收正，右灯左瓶与原屈膝保持。"),
("SW",2,"02-anatomy-v1","西南支撑鞋收正至踝下，保留原受重弯曲。"),
("SW",3,"03-anatomy-v3","西南左瓶右灯经身侧中间摆位，原支撑腿保持。"),
("SW",4,"04-anatomy-v1","西南后支撑鞋收正，保留另一条上抬腿。"),
("SW",10,"10-anatomy-v1","西南另一半圈支撑鞋收正至踝下，原腿相位保持。"),
]
rows=[]
for d,n,stem,phase in choices:
    seq=read(B/f"review/run-{d}-sequence-input.json"); old=seq["frames"][n-1]
    src=B/f"generation/{d}/{stem}.png"; meta=read(src.with_name(src.name+".generation.json"))
    review=src.with_name(stem+".review.json")
    if not review.exists(): review=B/f"review/{d}-{stem}.json"
    audit=read(review); assert audit.get("status")!="rejected"
    assert sha(src)==meta["sha256"]
    issues=[s for s in audit.get("issues",[]) if "未写input" not in s and "not write" not in s]
    rows.append(dict(action="run",direction=d,frame=n,source=src.relative_to(B).as_posix(),sourceSha256=sha(src),replaces=old["source"],replacesSha256=sha((B/old["source"]).resolve()),review=review.relative_to(B).as_posix(),prompt=meta["prompt"],observedPhase=phase,issues=issues,rootActuallyViewed=True,userAccepted=False,clientAccepted=False))
selected={(B/f["source"]).resolve() for p in (B/"review").glob("*-sequence-input.json") for f in read(p).get("frames",[])}
selected-= {(B/r["replaces"]).resolve() for r in rows}
selected|= {(B/r["source"]).resolve() for r in rows}
retired=sorted(p.relative_to(B).as_posix() for p in (B/"generation").rglob("*.png") if p.resolve() not in selected)
plan=dict(schemaVersion=1,status="ready_for_selection",criterion="Direct user:60ms/frame,960ms/cycle; same-direction bamboo archer reference, grounded support, no outward foot yaw, natural knee flexion, right lamp and left bottle.",timing=dict(frameMs=60,cycleMs=960),decisions=rows,retiredSources=retired,reviewMethod="Every listed replacement actually viewed at native size by root and generating reviewer; retained sources covered by three source-SHA-bound audits. Full-cycle browser follow-up required after export.",limitations=["Clothing occludes some hip/shoulder connections; no claimed full hidden skeletal proof.","Artwork review is separate from client sliding, contact and skill-event validation.","Some hand travel and drawing registration variation remains; no per-frame image shifts used."],generationRoute="builtin image_gen",actualModel=None,actualQuality=None,userAccepted=False,clientAccepted=False)
p=B/"review/anatomy-revision-decisions-20261005.json"
assert not p.exists()
p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(selectedCandidates=len(rows),retireAfterExport=len(retired))))
