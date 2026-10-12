from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parent.parent
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
notes=load(B/"review/ew-continuous-attempt-notes.json")
notes["notes"]["E/04-v8"]="选为中支撑候选（parent实际对看v5/v6/v8后确认）：足轴正确，支持位约695承上03更合适；远摆腿通过时重叠遮挡，底1202相对固定1164低38px，未宣称配准齐平。"
(B/"review/ew-continuous-attempt-notes.json").write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding="utf-8")
allrows=[]; groups={}
for direction in ("E","W"):
 p=B/f"review/run-{direction}-sequence-input.json";d=load(p);rows=[]
 for f in d["frames"]:
  source=Path(f["source"]);g=load(str(source)+".generation.json")
  im=Image.open(source)
  row={"slot":f["slot"],"source":source.as_posix(),"sha256":sha(source),"hashMatchesInput":sha(source)==f["sourceSha256"],
  "hashMatchesGeneration":sha(source)==g["sha256"],"native":list(im.size),"mode":im.mode,"alphaExtrema":list(im.getchannel("A").getextrema()),
  "durationMs":f["durationMs"],"supportFoot":f["supportFoot"],"positionPair":f["positionPair"],
  "promptExists":(B/g["prompt"]).is_file() if not Path(g["prompt"]).is_absolute() else Path(g["prompt"]).is_file(),
  "generationRecordExists":True,"actualModel":g.get("actualModel"),"actualQuality":g.get("actualQuality")}
  # Historical E01 prompt is relative to its own role generation record's BASE, not this batch.
  if not row["promptExists"] and direction=="E" and f["slot"]==1:
   historicalBase=source.parents[2]
   row["promptExists"]=(historicalBase/g["prompt"]).is_file()
  assert row["hashMatchesInput"] and row["hashMatchesGeneration"] and row["native"]==[1254,1254] and row["mode"]=="RGBA"
  assert f["durationMs"]==75
  rows.append(row);allrows.append(row)
 assert len(rows)==16 and len(set(r["sha256"] for r in rows))==16
 first="right" if direction=="E" else "left"
 assert all(r["supportFoot"]==first for r in rows[:8])
 assert all(r["supportFoot"]!=first for r in rows[8:])
 assert [r["positionPair"] for r in rows]==[1,1,2,2,3,3,4,4]*2
 groups[direction]={"input":p.as_posix(),"inputSha256":sha(p),"frames":rows,"events":d["events"],"totalDurationMs":sum(r["durationMs"] for r in rows)}
out={"schemaVersion":1,"checkedAt":datetime.now(timezone.utc).isoformat(),"groups":groups,
"checks":{"totalSources32":len(allrows)==32,"all32HashesUnique":len(set(r["sha256"] for r in allrows))==32,"allNative1254Rgba":True,"allSourceHashesMatch":True,"all75ms":True,"both1200ms":True,"8plus8FootMetadataCorrect":True,"fourPairsEachHalf":True},
"inspectionLimits":["技术检查不是动态/客户端验收。","支撑脚和动作相位来自实际原图视检，不由alpha最低点自动分类。","鞋点x是人工中心约测，y在已辨认支撑鞋ROI量取；没有平移或逐帧归一化。","E04仍存在+38px诊断偏低与摆腿遮挡；E14/15幅度偏小。","E13原始receipt恢复绑定为视觉高置信推断，非服务端披露确认；已单列恢复证据。"],
"visualAccepted":False,"clientAccepted":False,"globalBuildRun":False,"sharedPreviewModified":False}
(B/"review/ew-continuous-technical-verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
q=B/"review/support-repair-queue-20261004.json";j=load(q);j["status"]="completed_recorded; some attempts rejected, final input is source of truth";j["completedAt"]=out["checkedAt"];q.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out["checks"]))
