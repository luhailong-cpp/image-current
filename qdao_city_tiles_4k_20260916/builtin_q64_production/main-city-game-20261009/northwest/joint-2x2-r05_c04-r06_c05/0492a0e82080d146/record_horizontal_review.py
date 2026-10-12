import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")
cur=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/joint-2x2-r05_c04-r06_c05/0492a0e82080d146")
old=z/"joint-2x2-r05_c04-r06_c05/0cc569c6ab11cf03/review-horizontal.json"
a=json.loads(old.read_text(encoding="utf-8"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldhash=sha(old)
viewed=set(["seam-y5120-segment01","seam-y5120-segment02","seam-y5120-segment04","seam-y5120-segment05","seam-y5120-segment06","seam-y5120-segment08","seam-y6144-segment01","seam-y6144-segment02","seam-y6144-segment03","seam-y6144-segment04","seam-y6144-segment05","seam-y6144-segment06","seam-y6144-segment07","seam-y6144-segment08","seam-y7168-segment06","seam-y7168-segment07"])
notes={
"seam-y6144-segment06":"The prior dangling diagonal endpoint at approximately (973,46) is gone; the upper-right grout joins a complete angled paver corner.",
"seam-y7168-segment06":"The prior isolated diagonal starting around (982,95) is gone; the right-side stone joint continues into the connected paver network.",
"seam-y7168-segment07":"Blue road body and both pale borders run continuously at unchanged width. The old lateral step and doubled curb are absent. Stone texture differences remain natural within individual pavers.",
"seam-y5120-segment05":"Material revision preserves connected upper slab boundaries; only subtle hand-painted texture variation is visible.",
"seam-y6144-segment05":"Material revision preserves whole leaf silhouettes and diagonal paver edges at the lower interface.",
"seam-y6144-segment07":"Road borders and left angled paver network remain connected; no orphan grout is visible."
}
entries=[]
for prev in a["entries"]:
 name=prev["name"];p=cur/"qa"/(name+".png");h=sha(p)
 assert sha(prev["file"])==prev["sha256"],name+" old crop changed"
 changed=h!=prev["sha256"]
 mustview=changed or prev["verdict"]=="blocking"
 assert (name in viewed)==mustview,name+" inconsistent review inventory"
 if mustview:
  e={"name":name,"file":str(p),"sha256":h,"cropLTRB":prev["cropLTRB"],"verdict":"passed","actuallyViewed":True,"inheritedFrom":None,"findings":[notes[name]] if name in notes else []}
 else:
  assert prev["verdict"]=="passed",name+" cannot inherit unpassed crop"
  e={"name":name,"file":str(p),"sha256":h,"cropLTRB":prev["cropLTRB"],"verdict":"passed","actuallyViewed":False,"inheritedFrom":{"report":str(old),"reportSha256":oldhash,"file":prev["file"],"sha256":prev["sha256"],"verdict":prev["verdict"],"priorInheritedFrom":prev.get("inheritedFrom")},"findings":prev["findings"]}
 entries.append(e)
assert len(entries)==56 and len({e["name"] for e in entries})==56
candidate=cur/"joint-8192.png"
ch=sha(candidate)
assert ch=="d8ebdea30827db955bc220563cb169f1d816d42794c5564eb784820302390b05"
report={"schemaVersion":2,"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"finish_material_review","candidate":str(candidate),"candidateSha256":ch,"jointWorldBox":a["jointWorldBox"],"scope":"All 56 horizontal native 1024x320 seam crops for joint v3","method":"16 changed crops directly viewed at original pixels; 40 exact-SHA previous passed crops inherited after verifying their stored files.","summary":{"total":56,"actuallyViewed":16,"inherited":40,"passed":56,"nonblocking":0,"blocking":0},"fixedPriorBlockers":[{"name":n,"verdict":"passed","description":notes[n]} for n in ["seam-y6144-segment06","seam-y7168-segment06"]],"roadLowerConnection":{"name":"seam-y7168-segment07","verdict":"passed","description":notes["seam-y7168-segment07"]},"entries":entries,"visualPixelScale":1,"formalAccepted":False,"qualification":"This report covers horizontal seam crops only. It does not accept the entire region or all outer cross-region boundaries.","newArtGenerated":False,"sourceFilesModified":False}
out=cur/"review-horizontal.json"
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":sha(out),"summary":report["summary"]}))

