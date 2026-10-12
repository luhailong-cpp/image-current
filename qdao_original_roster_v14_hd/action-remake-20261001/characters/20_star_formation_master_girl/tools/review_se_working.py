from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1]
versions={1:3,2:3,3:2,4:2,5:2,6:2,7:2,8:2,9:4,10:1,11:1,12:1,13:2,14:1,15:1,16:1}
out=Image.new('RGB',(1400,1520),'#ebe5d7');d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
rows=[]
for i,v in versions.items():
 rel=f'generation/run/SE/{i:02}-v{v}.png';p=R/rel;im=Image.open(p).convert('RGBA');small=im.resize((350,350),Image.Resampling.LANCZOS);x=(i-1)%4*350;y=(i-1)//4*380;out.paste(small,(x,y),small);d.line((x,y+328,x+350,y+328),fill='#b97766');d.text((x+10,y+352),f'SE {i:02} v{v}',font=font,fill='#203c39')
 rows.append({'action':'run','direction':'SE','frame':i,'source':rel,'generationRecord':rel+'.generation.json','sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'status':'candidate','visualReview':'static_direction_checked_sequence_pending','dynamicReview':'not_verified'})
out.save(R/'preview/run-SE-working-contact.png')
(R/'provenance/run-SE-working-slots.json').write_text(json.dumps({'frames':rows,'review':'仅对照表，不是主选帧/完成验收'},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'run-SESW-selection.json').write_text(json.dumps({'frames':rows,'review':'SE16候选，鞋尖逐图已看，左右腿前后相位及短腾空重新定向编辑；完整动态接地仍待验收','dynamicAcceptance':False,'remaining':['04/12前掌蹬离形状继续动态复核','SE透视近远腿不同屏幕地面，不能按最低像素强贴','09领先右靴触地较低，需和08/10正常尺寸复核']},ensure_ascii=False,indent=2),encoding='utf-8')
print('SE working contact saved')

