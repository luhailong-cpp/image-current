from PIL import Image,ImageDraw
from pathlib import Path
import json
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
keys=['run-NW-07-v3','run-NW-08-v2','run-NW-09-v5']
sheet=Image.new('RGB',(1254,610),(218,222,223)); d=ImageDraw.Draw(sheet)
data=[]
for i,k in enumerate(keys):
 im=Image.open(b/'staging'/(k+'.png')).convert('RGBA')
 mask=im.getchannel('A').crop((410,940,605,1180)).point(lambda v:255 if v>100 else 0)
 box=mask.getbbox();bottom=940+box[3]-1
 data.append({'key':k,'lowerLeftLandingSoleApproxNativeY':bottom,'region':[410,940,605,1180],'method':'Alpha>100 bottom in visually identified LOWER-LEFT landing-boot region, not whole-character lowest pixel. Display used only for measurement; no original pixels altered.'})
 full=im.resize((400,400))
 sheet.paste(full,(i*418+9,22),full)
 crop=im.crop((400,880,900,1220));crop.thumbnail((400,180));sheet.paste(crop,(i*418+9,428),crop)
 d.text((i*418+9,4),k+'   landing sole y='+str(bottom),fill='black')
 d.line((i*418+5,22+bottom*400/1254,i*418+410,22+bottom*400/1254),fill=(110,75,15),width=1)
sheet.save(b/'review/reference09-NW-07-09-correction.png')
(b/'review/reference09-NW-07-09-measurement.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data))

