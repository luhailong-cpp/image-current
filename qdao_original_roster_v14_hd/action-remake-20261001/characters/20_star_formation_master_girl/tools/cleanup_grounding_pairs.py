"""Remove only superseded grounding4 image files after current final runtime is verified."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,argparse,re
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
arg=argparse.ArgumentParser();arg.add_argument("--apply",action="store_true");a=arg.parse_args()
state=rd(ROOT/"STATUS.json");assert state["offlineMaterialComplete"] is True
sel=rd(ROOT/"selection.json");assert len(sel["frames"])==196
for row in sel["frames"]:
 p=(ROOT/row["source"]).resolve()
 assert p.is_relative_to(ROOT/"runtime") and sha(p)==row["sourceSha256"]
 rec=rd(ROOT/row["generationRecord"]);assert rec["sha256"]==row["sourceSha256"]
 with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=="RGBA"
for page in [ROOT/"preview/index.html",ROOT/"preview/run-E-grounding.html"]:
 assert not re.search(r'''(?:src|href)=["'][^"']*grounding4/''',page.read_text(encoding="utf-8"))
manifest=rd(ROOT/"merge-manifest.json")
assert all(f["runtime"].startswith("runtime/") for f in manifest["files"])
out=ROOT/"provenance/grounding-pairs-image-cleanup.json"
assert not out.exists(),"Preserve earlier cleanup inventory; do not overwrite."
target=(ROOT/"grounding4").resolve();assert target.is_relative_to(ROOT) and target.name=="grounding4"
images=[p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in [".png",".jpg",".jpeg",".webp",".gif"]]
rows=[]
for p in images:
 absolute=p.resolve();assert absolute.is_relative_to(target)
 rows.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"reason":"最终runtime已确认且动态预览只依赖runtime；按用户偏好删除原生、拒稿、导出中间与审核临时图，保留来源文字。"})
record={"time":datetime.now(timezone.utc).isoformat(),"applied":a.apply,"files":rows,"count":len(rows),"bytes":sum(x["bytes"] for x in rows),"preserved":["runtime/196 PNG","preview/正式动态与联系表","全部逐图来源/提示词/回执/SHA/审核与合并文字"],"clientIntegrated":False}
if a.apply:
 (ROOT/"preview/grounding-pairs-review.html").write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=run-E-grounding.html"><a href="run-E-grounding.html">打开最终八方向跑步预览</a>',encoding="utf-8")
 for p in images:p.unlink()
 wr(out,record)
 for row in sel["frames"]:
  if row["action"]!="run":continue
  p=ROOT/row["generationRecord"];rec=rd(p)
  for obj in [rec.get("nativeOrigin",{}),rec.get("derivedFrom",{})]:
   obj["imageRetention"]="原生/中间图已清理；保留该路径、SHA与生成文字作为历史来源。"
  rec["sourceExport"]["imageRetention"]="历史输入路径；该轮旧runtime已替换或中间图已清理。"
  rec["imageCleanupRecord"]="provenance/grounding-pairs-image-cleanup.json";wr(p,rec)
  row["nativeOrigin"]=rec["nativeOrigin"]
 sel["imageCleanupRecord"]="provenance/grounding-pairs-image-cleanup.json";wr(ROOT/"selection.json",sel)
else:wr(ROOT/"provenance/grounding-pairs-image-cleanup-plan.json",record)
print(json.dumps({"applied":a.apply,"images":len(rows),"bytes":record["bytes"]}))
