from pathlib import Path
import json,hashlib,subprocess,sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
wr=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
groups={"run":(["N","NE","E","SE","S","SW","W","NW"],16,75),"hit":(["E","W"],6,40),"attack":(["E","W"],12,30),"cast":(["E","W"],16,45)}
sel=rd(ROOT/"selection.json")
if sel.get("status")=="offline_delivery":
 print("已完成正式交付；保留当前selection/STATUS，不再合并历史在制选表。重建使用build_delivery.py --rebuild。")
 sys.exit(0)
key=lambda f:(f["action"],f["direction"],int(f["frame"]))
rows={key(f):f for f in sel["frames"]}
files=["run-selection.json","hit-selection.json","hit-W-selection.json","attack-selection.json","cast-selection.json","attack-E-foot-selection.json","attack-W-foot-selection.json","cast-W-selection.json","cast-foot-selection.json","run-foot-selection.json","run-W-selection.json","run-W-continuation-selection.json","run-NS-selection.json","run-NENW-selection.json","run-SESW-selection.json"]
files += ["run-SW-selection.json", "cast-W-continuity-selection.json", "run-NW-selection.json"]
used=[]
for name in files:
 path=ROOT/name
 if not path.exists():continue
 d=rd(path); fs=d.get("frames",[])
 if isinstance(fs,dict):fs=[dict(v,action=d["action"],direction=d["direction"],frame=int(n)) for n,v in fs.items()]
 for f in fs:
  f=dict(f,frame=int(f["frame"]))
  k=key(f)
  if str(f.get("status","")).startswith(("rejected","needs_")):
   rows.pop(k,None);continue
  source=ROOT/f["source"];record=ROOT/f["generationRecord"]
  assert source.exists() and record.exists(),f
  digest=sha(source)
  if f.get("sourceSha256"):assert f["sourceSha256"]==digest,source
  rows[k]=dict(f,sourceSha256=digest)
 used.append({"file":name,"sha256":sha(path),"count":len(fs)})
sel["frames"]=sorted(rows.values(),key=key);sel["lastMergedAt"]=datetime.now(ZoneInfo("America/New_York")).isoformat()
sel["selectionInputs"]=used
wr(ROOT/"selection.json",sel)
state={"character":ROOT.name,"updatedAt":sel["lastMergedAt"],"expected":196,"selectedCandidates":len(rows),"generatedAttemptPNGsPresent":len(list((ROOT/"generation").rglob("*.png"))),"finalVisualPassed":0,"runtimeExported":0,"complete":False,"clientIntegration":"not_integrated","clientValidation":"not_run","groups":[],"slots":[]}
for action,(directions,count,duration) in groups.items():
 for d in directions:
  available=[i for i in range(1,count+1) if (action,d,i) in rows]
  state["groups"].append({"action":action,"direction":d,"required":count,"selectedCandidates":len(available),"frames":available,"missing":[i for i in range(1,count+1) if i not in available],"durationMs":duration,"dynamicAcceptance":False})
  state["slots"] += [{"action":action,"direction":d,"frame":i,"candidate":rows.get((action,d,i)),"finalVisualPassed":False,"runtimeExported":False} for i in range(1,count+1)]
state["pendingIssues"]=["当前候选已按实际PNG与动作独立选表合并，图片齐全不等于动态通过。","跑步正常1×统一1200ms/圈、每帧75ms、无额外尾帧停留；客户端未接入。","脚向定向修复采用局部AI重绘；已正确帧保留。逐帧复核见provenance。","缺失跑步方向保持空槽，旧walk仅作身份及朝向参考。","客户端未接入、未运行；固定整画布导出，没有最低脚贴地。"]
wr(ROOT/"STATUS.json",state)
lines=["# 星阵少女动作续作状态","",f"更新：{state['updatedAt']}。候选{len(rows)}/196；最终视觉及完整动态未通过，正式runtime导出0，客户端未接入。","","|动作|方向|候选/目标|缺帧|","|---|---|---:|---|"]
for g in state["groups"]:lines.append(f"|{g['action']}|{g['direction']}|{g['selectedCandidates']}/{g['required']}|"+",".join(f"{i:02}" for i in g["missing"])+"|")
lines+=["","逐图版本、质量、SHA、真实提示词与参考用途见generation同名generation.json；新配置目标为GPT Image 2.5 Sunburst/max，实际model/quality未披露均为null。","","[预览](preview/index.html) · [八方向跑步预览](preview/run-E-grounding.html) · [合并交接](MERGE_HANDOFF.md)",""]+["- "+x for x in state["pendingIssues"]]
(ROOT/"STATUS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"selected":len(rows),"inputs":used},ensure_ascii=False))
