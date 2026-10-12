from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
B=Path(__file__).resolve().parents[1]
choices={1:'run-SE-01-v2',2:'run-SE-02-v1',3:'run-SE-03-v6',4:'run-SE-04-v1',5:'run-SE-05-v2',6:'run-SE-06-v4',7:'run-SE-06-v2',8:'run-SE-08-v4',9:'run-SE-09-v2',10:'run-SE-10-v2',11:'run-SE-11-v1',12:'run-SE-12-v1',13:'run-SE-14-v1',14:'run-SE-13-v2',15:'run-SE-15-v2',16:'run-SE-16-v1'}
notes={1:'左前腿足跟落地姿势，近右扇跨胸前摆，远左空手后摆。',2:'左腿压缩承重，右后靴上抬，右扇开始回收。',3:'左髋下支撑、右膝通过；v4移除v3胸前多余扇，仅保留右手扇。',4:'左后腿伸展至脚尖，右膝前抬，右扇后摆、左空手前摆。',5:'v2修正左右腿连接；右腿前抬、左脚刚蹬离，双靴分离。',6:'v3修正第三靴并弯右膝；短腾空峰值，左腿后折。',7:'原06v2重选为下降，右靴比峰值更低；保留原始来源名，不复制来源。',8:'从正确09接触图局部弯膝修为预触地；右靴接近地面，左腿在后。',9:'右足跟接触；右扇后摆，左拳前摆，正确右腿来自近右髋。',10:'右腿屈膝承重，扇逐步降回腰前；左脚后折。',11:'右髋下支撑、左膝通过，两靴清楚。',12:'右后脚尖推蹬、左膝前抬，右扇向前、左空手后摆。',13:'左领先早腾空，右后腿折起，右扇前摆。',14:'左领先腾空峰值，两靴分离，右扇跨胸前摆。',15:'v2纠正右扇后摆跳变，保持前摆且左空手后摆；左靴下降。',16:'左靴向落地点展开，右后腿收起，准备回01。'}
notes.update({6:'v4降低过高腾空幅度，保留两靴和SE鞋头方向；为低幅短腾空峰值。',3:'v6修正过低支撑鞋底，鞋尖朝右下SE，左髋下支撑、右膝通过；单扇保持。',8:'v4修正前右靴外撇，鞋头转向右下SE；提前接触，左腿在后。',9:'v2右足跟接触，鞋头朝右下SE，不再朝左外撇；右扇后摆左拳前摆。',10:'v2右腿屈膝承重，鞋头朝右下SE，左脚后折。',13:'原14v1重选为左领先早腾空，低于新14峰值；保留来源与扇手。',14:'原13v2修正腾空高度并屈左膝，重选为短腾空峰值，鞋头朝右下SE。'})
frames=[];metrics=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);sheet=Image.new('RGB',(1280,1416),(227,232,236))
for n,key in choices.items():
 rel=f'sources/new/{key}.png';p=B/rel
 im=Image.open(p).convert('RGBA');box=im.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
 assert im.size==(1254,1254) and all(v>0 for v in box[:2]) and box[2]<1254 and box[3]<1254,(key,box)
 row=dict(action='run',direction='SE',frame=n,source=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),accepted=True,nativeSingleFrame=True,generationRecord=f'provenance/generation/{key}.json',review=dict(reviewer='root',reviewedAt=datetime.now(timezone.utc).isoformat(),notes=notes[n]+' 已逐图核对两手两脚及单扇；静态候选，完整动态接地仍须组审。'),event={1:'left_heel_contact',2:'left_load',4:'left_toeoff',6:'flight_peak',8:'right_early_contact',9:'right_heel_contact',10:'right_load',12:'right_toeoff',14:'flight_peak',16:'left_precontact'}.get(n))
 frames.append(row);metrics.append({'frame':n,'source':rel,'soleNativeY':box[3]-1,'note':notes[n]})
 x=(n-1)%4*320;y=(n-1)//4*354;d=ImageDraw.Draw(sheet);d.text((x+8,y+4),f'{n:02} {key} y={box[3]-1}',font=font,fill='#173d49');sm=im.resize((310,310));sheet.paste(sm,(x+5,y+30),sm)
(B/'audit/run-SE-selection.json').write_text(json.dumps(dict(frames=frames),ensure_ascii=False,indent=2),encoding='utf-8')
(B/'audit/run-SE-static-review.json').write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),selected=16,frames=metrics,rejected=['run-SE-06-v1: three boots','run-SE-08-v1: three boots','run-SE-08-v2: canvas edge and wrong leading-hip linkage','run-SE-07-v1: wrong leading leg','run-SE-07-v2: edge and foot too low','run-SE-03-v3: two fans','run-SE-15-v1: arm discontinuity'],groundingAcceptance='pending_dynamic_review',client='not_integrated'),ensure_ascii=False,indent=2),encoding='utf-8')
sheet.save(B/'audit/run-SE-selection-contact.png')
print(json.dumps(metrics,ensure_ascii=True))
