"""Plan exact removal of this repair batch's recorded native and input images."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
CACHE=Path("C:/Users/luyua/.codex/generated_images").resolve()
INPUT=(ROOT/"repair-inputs").resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
items={}
def add(value,digest,record,kind):
    if not value or not digest:return
    p=Path(value);p=p.resolve() if p.is_absolute() else (ROOT/p).resolve()
    if not p.exists():return
    assert p.suffix.lower()==".png"
    assert (kind=="native" and p.parent.parent==CACHE and p.name.startswith("exec-")) or (kind=="input" and p.parent==INPUT)
    assert sha(p)==digest,str(p)
    key=str(p).casefold()
    if key not in items:items[key]={"path":str(p),"sha256":digest,"kind":kind,"records":[]}
    assert items[key]["sha256"]==digest
    items[key]["records"].append(record)
for p in (ROOT/"records").rglob("*guardfix-20261008*.generation.json"):
    r=read(p);rel=p.relative_to(ROOT).as_posix()
    value=r.get("file")
    if value and Path(value).is_absolute():add(value,r.get("sha256"),rel,"native")
    source=r.get("derivedFrom",{})
    if source.get("path"):add(source["path"],source.get("sha256"),rel,"native")
for p in INPUT.glob("*.input.json"):
    r=read(p);add(r["file"],r["sha256"],p.relative_to(ROOT).as_posix(),"input")
plan={"nativeCacheRoot":str(CACHE),"inputRoot":str(INPUT),"count":len(items),"items":list(items.values()),"policy":"User final-assets-only retention; remove recorded inputs/candidates only after final runtime and references verified. Keep all source text."}
(ROOT/"cleanup-guardfix-plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"planned":len(items),"native":sum(x["kind"]=="native" for x in items.values()),"inputs":sum(x["kind"]=="input" for x in items.values()),"action":"plan-only"}))
