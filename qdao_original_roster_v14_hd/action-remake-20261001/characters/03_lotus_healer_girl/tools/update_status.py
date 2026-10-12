from pathlib import Path
import json,re
from datetime import datetime
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent.parent
dirs=["N","NE","E","SE","S","SW","W","NW"]
slots={}
for act,ds,num in [("run",dirs,16),("hit",["E","W"],6),("attack",["E","W"],12),("cast",["E","W"],16)]:
 for d in ds:
  for f in range(1,num+1): slots[(act,d,f)]={"action":act,"direction":d,"frame":f,"nativeCandidates":[],"candidateExport":None,"status":"missing"}
for r in (B/"generation").rglob("*.png.generation.json"):
 info=json.loads(r.read_text(encoding="utf-8-sig")); p=r.with_name(r.name.removesuffix(".generation.json"))
 parts=p.relative_to(B/"generation").parts
 if len(parts)==2 and parts[0] in dirs: act,d="run",parts[0]
 elif len(parts)==3 and parts[0] in ["hit","attack","cast"]:act,d=parts[0],parts[1]
 else:continue
 match=re.match(r"(\d+)",p.name)
 if not match:continue
 key=(act,d,int(match.group(1)))
 if key in slots:
  slots[key]["nativeCandidates"].append({"file":str(p.relative_to(B)).replace(chr(92),"/"),"sha256":info["sha256"],"imageExists":p.is_file(),"generationRecord":str(r.relative_to(B)).replace(chr(92),"/")})
  if p.is_file():slots[key]["status"]="native_wip"
for sel in (B/"review").glob("*-selection.json"):
 selection=json.loads(sel.read_text(encoding="utf-8-sig"))
 for f in selection.get("frames",[]):
  key=(selection.get("action","run"),selection.get("direction",sel.stem.split("-")[-2]),f["frame"])
  if key not in slots or not f.get("file") or not (B/f["file"]).is_file():continue
  slots[key]["selectedSource"]=f["source"];slots[key]["candidateExport"]=f["file"];slots[key]["status"]="candidate_not_accepted"
groups={}
for key,s in slots.items():
 label=key[0]+"/"+key[1]
 g=groups.setdefault(label,{"target":0,"nativeOrExportPresent":0,"candidateExport":0,"accepted":0,"missing":0})
 g["target"]+=1
 g["nativeOrExportPresent"]+=s["status"]!="missing"
 g["candidateExport"]+=s["candidateExport"] is not None
 g["missing"]+=s["status"]=="missing"
result={"updatedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"target":196,"groups":groups,"presentSlots":sum(g["nativeOrExportPresent"] for g in groups.values()),"candidateExportCount":sum(g["candidateExport"] for g in groups.values()),"visualAccepted":0,"clientAccepted":0,"newGenerationRecords":len(list((B/"generation").rglob("*.png.generation.json"))),"slots":list(slots.values()),"latestUserCriterion":"Latest direct user reference is the current09 bamboo archer. Compare actual same-direction foot axes, hand action and support; retain correct lotus frames. Run default960ms=16x60ms; no old fast options. Slowing alone does not prove grounding.","note":"Native WIP may have documented defects and is not completed animation. Explicit per-group selection mappings override raw filename slots; no duplicated pose fills a slot."}
(B/"review/production-status.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
manifestPath=B/"manifest.json"
if manifestPath.exists():
 m=json.loads(manifestPath.read_text(encoding="utf-8-sig"));m["productionStatus"]="review/production-status.json"
 m["counts"]["runOtherDirectionsGeneratedThisBatch"]=sum(g["nativeOrExportPresent"] for label,g in groups.items() if label.startswith("run/") and label!="run/E")
 m["counts"]["combatGeneratedThisBatch"]=sum(g["nativeOrExportPresent"] for label,g in groups.items() if not label.startswith("run/"))
 m["counts"]["allPresentSlotsIncludingUnacceptedNativeWip"]=result["presentSlots"]
 m["counts"]["newGenerationRecords"]=result["newGenerationRecords"]
 m["status"]="revision_exported_pending_user_and_client_review" if result["candidateExportCount"]==196 else "in_progress_not_all_actions_complete"
 manifestPath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k not in ["slots","groups"]},ensure_ascii=False))

