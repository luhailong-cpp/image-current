"""只清理本角色已经退出当前引用的图片；逐图文字记录保留。"""
from pathlib import Path
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
assert ROOT.name=="20_star_formation_master_girl" and ROOT.parent.name=="characters"
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");args=p.parse_args()
sel=rd(ROOT/"selection.json");assert sel.get("status")=="offline_delivery" and len(sel["frames"])==196
manifest=rd(ROOT/"merge-manifest.json");assert manifest["exportedFrames"]==196 and len(manifest["groups"])==14
keep=set()
for f in sel["frames"]:
 image=(ROOT/f["source"]).resolve();record=ROOT/f["generationRecord"]
 assert image.is_relative_to(ROOT) and sha(image)==f["sourceSha256"]==rd(record)["sha256"]
 with Image.open(image) as im:assert im.size==(1024,1024) and im.mode=="RGBA"
 keep.add(image)
for g in manifest["groups"]:
 for suffix in ["contact","normal","slow"]:
  path=(ROOT/f"preview/{g['action']}-{g['direction']}-{suffix}.png").resolve()
  assert path.is_file(),path
  keep.add(path)
for name in ["run-eight-directions-1200ms.png","run-eight-directions-slow.png"]:
 path=(ROOT/"preview"/name).resolve();assert path.is_file();keep.add(path)
targets=[]
for image in ROOT.rglob("*"):
 if image.is_file() and image.suffix.lower() in [".png",".jpg",".jpeg",".webp",".gif"]:
  image=image.resolve();assert image.is_relative_to(ROOT),image
  if image not in keep:targets.append(image)
obsolete_html=[p.resolve() for p in (ROOT/"preview").rglob("*.html") if p.name!="index.html" or p.parent!=(ROOT/"preview")]
obsolete_html=[p for p in obsolete_html if p!=(ROOT/"preview/run-E-grounding.html").resolve()]
for p in obsolete_html:assert p.is_relative_to(ROOT)
record={"at":datetime.now(ZoneInfo("America/New_York")).isoformat(),"applied":args.apply,"authorization":"根AGENTS用户2026-09-23素材保留要求：成品与当前引用完整后删除原图、拒稿、中间图，无需图片备份；只保留逐图文字来源。","root":ROOT.as_posix(),"retainedRuntimeImages":196,"retainedPreviewImages":len(keep)-196,"removedImages":[{"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size} for p in targets],"removedObsoleteHtml":[p.relative_to(ROOT).as_posix() for p in obsolete_html],"recordsRetained":True,"gitOperations":False}
(ROOT/"provenance/image-retention-cleanup.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if args.apply:
 for image in targets:
  assert image.is_relative_to(ROOT) and image not in keep
  image.unlink()
 for p in obsolete_html:p.unlink()
 assert all(p.is_file() for p in keep)
print(json.dumps({"applied":args.apply,"runtimeKept":196,"previewsKept":len(keep)-196,"removedImages":len(targets),"removedBytes":sum(r["bytes"] for r in record["removedImages"]),"obsoleteHtml":len(obsolete_html)}))
