from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
if json.loads((ROOT/"selection.json").read_text(encoding="utf-8-sig")).get("status")=="offline_delivery":
 raise SystemExit("正式交付后保留源记录不可变；已补录的参考SHA不再被历史图片清理状态覆盖。")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cache={};changed=[]
for p in (ROOT/"generation").rglob("*.generation.json"):
 r=json.loads(p.read_text(encoding="utf-8-sig"))
 refs=r.get("references",[])
 for entry in refs:
  if not isinstance(entry,dict):continue
  name=entry.get("path",entry.get("file"))
  if not name:continue
  path=Path(name);path=path if path.is_absolute() else ROOT/path
  norm=path.as_posix()
  role=("已确认画法/材质参考" if "/designs/" in norm else "本角色身份参考" if "q_daoist_character_pack" in norm else "用户认可的同方向靴轴/步态参考，仅姿态，不转移身份或持物" if "09_bamboo_archer_girl" in norm else "本角色旧朝向/身份/姿态参考" if "recovery-" in norm else "本角色原生编辑目标或相邻关键姿态")
  entry["reviewedRole"]=role
  if path.is_file():
   if norm not in cache:
    with Image.open(path) as im:cache[norm]={"sha256":sha(path),"width":im.width,"height":im.height,"mode":im.mode}
   entry["observedFileEvidenceBeforeCleanup"]=cache[norm]
  else:entry["observedFileEvidenceBeforeCleanup"]={"available":False,"reason":"当前路径不存在；保持原记录，不补造SHA"}
 r["referenceMetadataVerifiedAt"]=datetime.now(ZoneInfo("America/New_York")).isoformat()
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 changed.append(p.relative_to(ROOT).as_posix())
out={"records":len(changed),"uniqueReferencesHashed":len(cache),"files":changed,"scope":"补录参考文件SHA和真实用途；不修改生成时间、实际调用参数或未确认型号质量"}
(ROOT/"provenance/reference-evidence-enrichment.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"records":len(changed),"uniqueReferencesHashed":len(cache)}))
