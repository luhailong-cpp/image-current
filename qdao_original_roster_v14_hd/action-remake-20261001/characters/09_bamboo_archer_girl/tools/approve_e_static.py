import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for a,n in [("hit",6),("attack",12),("cast",16)]:
 for f in range(1,n+1):
  p=ROOT/"runtime"/a/"E"/f"{f:02d}.png"
  note={"hit":"最新01/02/04/05/06已重新绘制固定承重脚，03为峰值；双腿、双手与完整长弓、无箭的受击姿态可读。","attack":"取箭→搭弦→加深拉距→07释放→收势可读；04–06单箭尾/右指/弦顶点相连，07后无箭。","cast":"取箭、拉弦05–09、10释放、11展开及12–16收势可读；05/06已修拉距，12已修收势过渡，13已重画恢复与14相符的长弓。"}[a]
  rows.append({"slot":f"{a}/E/{f:02d}","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"status":"passed","staticAnatomy":"passed","evidence":note,"footOrientation":"两靴鞋尖均朝角色前方偏右，弓步屈膝随各自脚轴；未见左靴向左、右靴向右的横向外八分叉。战斗支撑站姿不套用跑步相位。","reviewBasis":"根逐图与接触表实际查看，并行只读50帧审阅audit/root-review-20261003.md；最新脚尖核查见audit/feet-*-E-current.jpg及完整preview/qa接触表，未使用其他角色自动判通过；cast13以最终63345b7c版本为准。","dynamicApproval":False})
sequences=[{"sequence":f"{a}/E","status":"needs_review","frameSha256":[r["sha256"] for r in rows if r["slot"].startswith(a+"/")],"evidence":"单帧静态审查通过；整段时序、根位、正常尺寸连续性仍须实播核验。浏览器本地file导航被策略阻止，未绕过，也没有冒充已完成浏览器或客户端动态验收。"} for a in ["hit","attack","cast"]]
(ROOT/"review-parts/combat-E.json").write_text(json.dumps({"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"frames":rows,"sequences":sequences},ensure_ascii=False,indent=2),encoding="utf-8")
print("E combat 34 static approvals recorded for exact current hashes; dynamic pending.")

