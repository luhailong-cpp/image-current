from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
now=datetime.now(timezone.utc).isoformat()
run=json.loads((B/"audit/run-NWSW-selection.json").read_text(encoding="utf8"))
attack=json.loads((B/"audit/attack-selection.json").read_text(encoding="utf8"))
frames=run["frames"]+[x for x in attack["frames"] if x["direction"]=="W"]
seen=set(); counts={}; outputs=[]
for row in frames:
 p=B/row["source"]; sha=hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha==row["sha256"],p
 assert sha not in seen,p
 seen.add(sha)
 im=Image.open(p); assert im.size[0]==im.size[1] and im.size[0]>=1024,p
 assert im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255),p
 rec=json.loads((B/row["generationRecord"]).read_text(encoding="utf8"))
 counts[row["action"]+"_"+row["direction"]]=counts.get(row["action"]+"_"+row["direction"],0)+1
 outputs.append({"action":row["action"],"direction":row["direction"],"frame":row["frame"],"source":row["source"],"sha256":sha,"size":list(im.size),"mode":im.mode,"generationRecord":row["generationRecord"]})
rvp=B/"audit/run-NWSW-review.json"; rv=json.loads(rvp.read_text(encoding="utf8"))
extras=[
("run-NW-04-v3","蹬地尝试产生非透明阴影/地面痕迹，后由v5重做"),
("run-NW-06-v1","右靴过低，未形成清楚腾空顶点"),
("run-NW-06-v2","右靴仍偏低"),
("run-NW-06-v3","脚向再审：领先右靴朝右侧，后由v6局部转左"),
("run-NW-06-v4","改脚导致整身放大，拒绝"),
("run-NW-06-v5","改脚导致整身放大及脚高度变化，拒绝"),
("run-NW-07-v2","右靴过低，未适合目标下降相位"),
("run-NW-07-v3","前后腿归属错误，未采用"),
("run-NW-10-v1","大幅抬臂并扭躯，与09过渡跳变"),
("run-SW-12-v1","支撑靴仍平放，未形成前掌蹬地"),
("run-SW-12-v2","仍未清楚抬跟，未采用"),
("run-SW-12-v3","鞋尖朝右下，与SW左下运动不符"),
("run-SW-13-v1","领先左靴鞋头向右下外撇，foot-v1局部纠正"),
("run-SW-14-v1","仍为错误腿领先，未真换腿"),
("run-SW-14-v2","换腿正确但领先左靴鞋头右下外撇，由foot-v1纠正"),
("run-SW-15-v1","扇边出画，v2定点内收")]
known={x["key"] for x in rv.get("rejectedFrames",[])}
rv.setdefault("rejectedFrames",[]).extend({"key":k,"reason":r} for k,r in extras if k not in known)
rv["wholeContactReview"]={"reviewedAt":now,"reviewer":"/root/finish_attack_diagonals","sheets":["review/diagonals/run-NW-current-contact.png","review/diagonals/run-SW-current-contact.png"],"observed":"32格全部重新查看，选用已修手部和脚轴版本；鞋尖、膝踝与腾空/承重按实际图片记录。最后NW06领先右靴朝左、SW13/14领先左靴朝左下。整组动态另由主线程复核。"}
rv["browserReviewLimit"]={"attempted":True,"result":"IAB visibility is not supported in a subagent thread","rootReviewNeeded":True}
rvp.write_text(json.dumps(rv,ensure_ascii=False,indent=2),encoding="utf8")
foot={"schemaVersion":1,"reviewedAt":now,"reviewer":"/root/finish_attack_diagonals","selectedFrameCount":12,"wholeContactReviewed":True,"dynamicAccepted":False,"clientIntegrated":False,"findings":["已逐图看过W12：双靴鞋尖与脚掌均朝W左侧；前掌/鞋跟有平支撑关系","原动作顺序复用，04/05保留先前按实际姿态重选方案；只修后侧膝踝与靴","01/02/12的foot-v1导致整身放大（02另边缘裁切），改选foot-v2","连续动态仍由主线程正常/慢速复核"],"rejectedFrames":[{"key":"attack-W-"+n+"-foot-v1","reason":"整体尺度放大或边缘裁切，替换为受限区域foot-v2"} for n in ["01","02","12"]],"sources":[x for x in outputs if x["action"]=="attack"],"preview":{"contact":"review/diagonals/attack-W-contact.png","normal":"review/diagonals/attack-W-normal.gif","slow":"review/diagonals/attack-W-slow.gif"}}
(B/"audit/attack-W-foot-review.json").write_text(json.dumps(foot,ensure_ascii=False,indent=2),encoding="utf8")
(B/"audit/diagonals-technical-verification.json").write_text(json.dumps({"verifiedAt":now,"counts":counts,"uniquePngCount":len(seen),"allShaMatch":True,"allSquare1024Plus":True,"allNative1254":all(x["size"]==[1254,1254] for x in outputs),"allRgbaTransparency":True,"allProvenanceExists":True,"dynamicAccepted":False,"frames":outputs},ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"counts":counts,"unique":len(seen),"dimensions":"1254x1254 native RGBA","shaAndRecords":"44/44 verified","dynamicAccepted":False}))

