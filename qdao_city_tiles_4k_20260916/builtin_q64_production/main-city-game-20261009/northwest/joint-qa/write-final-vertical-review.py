from pathlib import Path
import json,hashlib,datetime
z=Path(r"D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009\northwest")
d=z/"joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70"
old=z/"joint-2x2-r05_c04-r06_c05/0492a0e82080d146/review-vertical.json"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((d/"joint-assembly.json").read_text(encoding="utf-8-sig"))
prior={e["name"]:e for e in json.loads(old.read_text(encoding="utf-8-sig"))["entries"]}
notes={
"seam-x1024-segment05":"Native-scale view: blossom petals, stems, bamboo highlight and adjacent roof remain continuous, without clipped forms or exposed assembly line.",
"seam-x4096-segment05":"Native-scale view: both paving joints and their bevel/shadow edges remain continuous across the source boundary.",
"seam-x4096-segment06":"Native-scale view: repaired blue paving middle joint is now continuous with gradual tonal transition; the small red paper diamond is whole. Border mitre, diagonal paving and foliage connect cleanly. Previous microrepair blocker resolved.",
"seam-x5120-segment05":"Native-scale view: paving joint geometry is continuous; shallow stone grain varies naturally without a geometric break or abrupt false band.",
"seam-x5120-segment06":"Native-scale view: blue paving seams, curb edges and diagonal stone joints align; no false color stripe or clipping at the revised source edge.",
"seam-x7168-segment06":"Native-scale view: straight and mitred stone joints align through the intersection, with continuous bevels and no duplicate grout branch."
}
entries=[]
for q in m["qa"]:
    n=q["name"]
    if not n.startswith("seam-x"):continue
    assert q["sha256"]==sha(Path(q["file"]))
    e={k:q[k] for k in ("name","file","sha256","cropLTRB")}
    e["nativePixelScale"]=1
    if n in notes:
        e.update(verdict="passed",actuallyViewed=True,inheritedFrom=None,viewMode="original native 1024x320 QA crop; rotated 90 degrees without resampling",findings=[notes[n]])
    else:
        p=prior[n]
        assert p["sha256"]==q["sha256"] and p["verdict"] in ("passed","nonblocking"),n
        e.update(verdict=p["verdict"],actuallyViewed=False,inheritedFrom={"file":p["file"],"sha256":p["sha256"],"report":str(old),"reportSha256":sha(old),"originalActuallyViewed":p["actuallyViewed"],"priorInheritance":p.get("inheritedFrom")},findings=p["findings"])
    entries.append(e)
assert len(entries)==56 and sum(e["actuallyViewed"] for e in entries)==6
out={"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"reviewer":"root","candidate":m["output"],"status":"passed_no_blocking_vertical_seam_defects","entries":entries,"summary":{"total":56,"directlyViewed":6,"identicalHashInherited":50,"passed":sum(e["verdict"]=="passed" for e in entries),"nonblocking":sum(e["verdict"]=="nonblocking" for e in entries),"blocking":0},"scope":"Vertical native source seams within current 2x2 only; outer neighboring tiles remain pending."}
p=d/"review-vertical.json"; p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":str(p),"sha256":sha(p),"summary":out["summary"]}))

