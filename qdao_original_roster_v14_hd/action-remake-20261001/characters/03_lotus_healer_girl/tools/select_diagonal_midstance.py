from pathlib import Path
from datetime import datetime
import json,hashlib
from PIL import Image
B=Path(__file__).resolve().parents[1]
stamp=datetime.now().astimezone().isoformat()
rows=[]
for d,stem,phase in [
 ("SE","03-midstance-v2","近右支撑腿收至身体下方，鞋底保持原地面高度，鞋尖按东南行进轴；远左腿回收。原有正确持物与上身保留。"),
 ("SW","03-midstance-v1","近左支撑腿收至身体下方，鞋底保持原地面高度，鞋尖顺西南行进轴；远右腿回收。原有正确持物与上身保留。")]:
 p=B/f"review/run-{d}-sequence-input.json";data=json.loads(p.read_text(encoding="utf-8-sig"));f=data["frames"][2]
 src=B/f"generation/{d}/{stem}.png";h=hashlib.sha256(src.read_bytes()).hexdigest();im=Image.open(src)
 row=dict(frame=3,direction=d,source=str(src.relative_to(B)),sourceSha256=h,replacedSource=f["source"],observedPhase=phase,reviewedAt=stamp,status="selected_current_candidate",visualAcceptance=False)
 f.update(source=row["source"],sourceSha256=h,observedPhase=phase,issues=["中支撑脚已向身下收，减小03到04变化；保留原生画布，尚无客户端位移验证。"],alphaGt8Bounds=list(im.getchannel("A").point(lambda v:255 if v>8 else 0).getbbox()))
 data["updatedAt"]=stamp;p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 src.with_name(src.stem+".review.json").write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding="utf-8");rows.append(row)
matrix=B/"review/run-SE-SW-continuous-support-matrix.md"
text=matrix.read_text(encoding="utf-8")
for row in rows:
 lines=text.splitlines()
 for i,line in enumerate(lines):
  if line.startswith("|"+row["direction"]+"03|"):
   lines[i]="|"+row["direction"]+"03|"+Path(row["source"]).name+"|"+row["observedPhase"]+"|本轮局部收支撑脚，原生画布与地面高度保留|"
 text="\n".join(lines)+"\n"
matrix.write_text(text,encoding="utf-8")
(B/"review/diagonal-midstance-review.json").write_text(json.dumps(dict(updatedAt=stamp,frames=rows),ensure_ascii=False,indent=2),encoding="utf-8")
print("Updated SE/SW03 local midstance selection; other15slots unchanged per direction.")
