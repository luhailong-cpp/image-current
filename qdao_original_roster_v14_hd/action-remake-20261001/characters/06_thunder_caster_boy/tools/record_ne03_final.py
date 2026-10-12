from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'runtime/run/NE/03.png'
items=[]
for label,q in [('old',R/'work/run_NE_03_v4.png'),('current',p)]:
 im=Image.open(q).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
 a=im.getchannel('A');values=[]
 for x in range(580,751):
  ys=[y for y in range(850,1005) if a.getpixel((x,y))>128]
  if ys:values.append(max(ys))
 values.sort();items.append({'state':label,'region':[580,850,751,1005],'medianLowerContourY':values[len(values)//2],'maxLowerContourY':max(values)})
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'run NE03 final local shin-length correction','frames':[{'file':'runtime/run/NE/03.png','sha256':sha(p),'decision':'accept current local shin/ankle correction'}],'observations':['旧03白绑腿露出长度异常增加约34px，膝部未作相应伸展；不是仅依据最低像素判断。','新图缩短该段白绑腿，上收踝靴，保留NE鞋轴、抬跟、原上身反臂和相机。','与02仍有合理蹬离/支撑位置差，未进行逐帧最低像素强贴地。'],'measurements':items,'oldRuntimeSha256':'7273e3661f7b870a19508df7e228570cedce1a5d698d6262b80ea39ff9150fb8','supersedes':'review/run_NE_front_review_20261004.json中的03旧SHA及拉长问题；其余01/02/04/05/06结论保持','clientVerified':False}
(R/'review/NE03_final_correction_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(items))
