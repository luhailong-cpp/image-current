from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
keys=['03-v4','03-v5','03-v6','13-v1','13-v2','14-v1']
rows=[];tiles=[]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
for key in keys:
 p=b/'sources/new'/f'run-SE-{key}.png';im=Image.open(p).convert('RGBA');aa=im.getchannel('A').point(lambda a:255 if a>128 else 0);bb=aa.getbbox()
 # These six native cels have a boot as the lowest foreground object.
 row={'source':p.relative_to(b).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'soleBottomNativeY':bb[3]-1,'soleBottomExportY':round(49+(bb[3]-1)*940/1254,2),'generationRecord':f'provenance/generation/run-SE-{key}.json'};rows.append(row)
 tile=Image.new('RGB',(384,430),(224,231,237));sm=im.resize((352,352),Image.Resampling.LANCZOS);tile.paste(sm,(16,40),sm);d=ImageDraw.Draw(tile);d.text((7,6),f'SE {key} soleY={bb[3]-1}',font=font,fill=(22,49,65));tiles.append(tile)
sheet=Image.new('RGB',(1152,860));[sheet.paste(im,((i%3)*384,(i//3)*430))for i,im in enumerate(tiles)];sheet.save(b/'audit/run-SE-local-grounding-fixes.png')
d={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_w','scope':'Only SE03 and SE13; did not modify SE selection/runtime','reviewed':rows,'recommendations':{'frame03':'run-SE-03-v6.png','frame13_14':'Inspect swap: use former run-SE-14-v1 as frame13 early flight and run-SE-13-v2 as frame14 apex; root decides based full arm/cloth motion'},'reason':{'03v5':'Bent supporting knee; sole1209->1152, preserved hands, but shoe still too profile/horizontal-right.','03v6':'Only shoe yaw repainted into front-threequarter pointing down-right/SE; unchanged leg spacing; selected local candidate.','13v2':'Bent leading left knee; sole1179->1129, fan/arms preserved, both feet airborne. Existing14v1 sole1145 lower; consider true phase reorder, not translating either image.'},'actualModel':None,'actualQuality':None,'configurationTarget':'GPT Image 2.5 Sunburst / max','client':'not integrated'}
(b/'audit/run-SE-local-grounding-fixes.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=True))

