import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest");cur=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70")
old=z/"joint-2x2-r05_c04-r06_c05/0492a0e82080d146/review-horizontal.json"
a=json.loads(old.read_text(encoding="utf-8"));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldhash=sha(old)
viewed=set(["seam-y5120-segment01","seam-y5120-segment04","seam-y5120-segment05","seam-y5120-segment06","seam-y5120-segment07","seam-y5120-segment08","seam-y6144-segment04","seam-y6144-segment05","seam-y6144-segment06","seam-y6144-segment08"])
notes={"seam-y5120-segment05":"Upper paving boundaries remain whole and connected after fix04.","seam-y5120-segment07":"Paver grout remains connected. Tiny local bevel-width variation near (791,246) is not a broken joint and is nonblocking.","seam-y6144-segment05":"Lower foliage silhouettes and diagonal floor joints remain continuous after fix04.","seam-y6144-segment06":"The repaired upper-right angled grout still joins a complete paver corner; prior open endpoint does not recur."}
entries=[]
for prev in a["entries"]:
 name=prev["name"];p=cur/"qa"/(name+".png");h=sha(p)
 assert sha(prev["file"])==prev["sha256"],name+" old crop changed"
 changed=h!=prev["sha256"]
 assert (name in viewed)==changed,name+" inconsistent viewed inventory"
 if changed:e={"name":name,"file":str(p),"sha256":h,"cropLTRB":prev["cropLTRB"],"verdict":"passed","actuallyViewed":True,"inheritedFrom":None,"findings":[notes[name]] if name in notes else []}
 else:
  assert prev["verdict"]=="passed"
  e={"name":name,"file":str(p),"sha256":h,"cropLTRB":prev["cropLTRB"],"verdict":prev["verdict"],"actuallyViewed":False,"inheritedFrom":{"report":str(old),"reportSha256":oldhash,"file":prev["file"],"sha256":prev["sha256"],"verdict":prev["verdict"],"priorInheritedFrom":prev.get("inheritedFrom")},"findings":prev["findings"]}
 entries.append(e)
assert len(entries)==56 and len({e["name"] for e in entries})==56
candidate=cur/"joint-8192.png";ch=sha(candidate)
assert ch=="6aaa59bce371a91818e4c77270e03c01cb1fecbfd7a27e354208fa2bb24ea474"
r={"schemaVersion":2,"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"finish_material_review","candidate":str(candidate),"candidateSha256":ch,"jointWorldBox":a["jointWorldBox"],"scope":"All 56 horizontal native 1024x320 seam crops for fix04 joint","method":"10 changed crops directly viewed at original pixels; 46 exact-SHA prior passed crops inherited after verifying stored files.","summary":{"total":56,"actuallyViewed":10,"inherited":46,"passed":56,"nonblocking":0,"blocking":0},"fixedPriorBlockers":a["fixedPriorBlockers"],"roadLowerConnection":a["roadLowerConnection"],"entries":entries,"visualPixelScale":1,"formalAccepted":False,"qualification":"Horizontal seams only. The old fix01 west-pair defect is vertical and excluded from this review. This does not accept the whole region or outer boundaries.","newArtGenerated":False,"sourceFilesModified":False}
out=cur/"review-horizontal.json"
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":sha(out),"summary":r["summary"]}))

