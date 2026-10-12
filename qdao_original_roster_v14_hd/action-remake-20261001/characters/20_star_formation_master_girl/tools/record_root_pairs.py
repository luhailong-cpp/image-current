from pathlib import Path
import json,hashlib,datetime
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
groups=[]
for d in ["E","NW"]:
 p=R/f"grounding4/{d}/selected.json";rows=json.loads(p.read_text(encoding="utf-8-sig"))
 for s in rows:
  s["visualStaticReviewed"]=True
  s.setdefault("requestedSlot",int(Path(s["exportFile"]).name[:2]))
  s["selectionReason"]="实看髋膝踝连接、支撑鞋与另一脚离地姿态后选入相位；原请求槽位不替代实际图像判定。"
 p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 groups.append({"direction":d,"selected":rows,"staticReviewed":True,"normalDynamicReviewed":False,"continuousSupport":[{"foot":"right","frames":list(range(1,9))},{"foot":"left","frames":list(range(9,17))}],"positionPairs":[{"frames":[n,n+1],"position":["front_landing","under_hip","behind_hip","rear_push"][((n-1)%8)//2]} for n in range(1,17,2)]})
record={"time":datetime.datetime.now(datetime.timezone.utc).isoformat(),"groups":groups,"scope":"本角色E/NW独立静态复核；动态待统一预览","method":"实看完整与靴区联系表，保持1024画布；不按最低像素对齐。不复制/镜像/插值。","requestedVersusSelected":"NW若干原请求左腿图实际返回右腿，按实图放入正确右腿半圈；保留原提示词、requestedSlot和SHA。NW15/16-v1/v2错误腿序及14-v3退稿未按原槽位使用。","rejectedExamples":{"E":["04-pairs-v1接地点过低","07-pairs-v1接地点过低","08-pairs-v2双脚近同地面过伸","12-pairs-v1过伸","13-pairs-v2腾空","15-pairs-v2腾空","04-v1在新06槽出现摆腿回缩，改用06-pairs-v2"],"NW":["15/16-pairs-v2仍右支撑，不计入左半圈","14-pairs-v3返回鞋位过左下，不入选"]},"provenanceLimitation":"NW05/06/07/08/11第一批工具会话中断，原生输出按主机文件/上身姿态关联；关联推断未确认已逐图记入回执。没有伪造模型/质量实际值。","clientIntegrated":False}
(R/"provenance/grounding-pairs-E-NW.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("E/NW static selected")

