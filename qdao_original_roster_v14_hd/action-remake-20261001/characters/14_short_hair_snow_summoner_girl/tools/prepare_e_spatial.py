from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
sheet=Image.new('RGB',(1400,1100),(225,230,227));draw=ImageDraw.Draw(sheet)
inputs={}
for n in range(1,17):
 p=R/'run/E'/f'{n:02d}.png';m=read(Path(str(p)+'.generation.json'))
 original=Path(m['derivedFrom']['generationRecord']);native=read(original)
 source=native['evidence'].get('toolReturnedPath') or native['evidence'].get('hostPath')
 if not Path(source).exists():source=str(R/m['derivedFrom']['file'])
 inputs[str(n)]={'native':source,'formal':str(p),'sourceRoot':m['registrationTransform']['sourceRoot'],'nativeRecord':str(original),'sha256':m['sha256']}
 im=Image.open(p).convert('RGBA').crop((110,550,870,1024))
 im.thumbnail((350,250))
 x=(n-1)%4*350;y=(n-1)//4*275
 sheet.paste(im,(x,y),im);draw.text((x+10,y+254),f'E{n:02d}',fill=(20,40,30))
sheet.save(R/'run/staging/root-E-spatial-before.jpg',quality=94)
(R/'audit/root-E-spatial-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
req={'text':'直脚着地两帧，再旁边点两帧，再旁边点两帧，再旁边点俩帧，依次类推','recordedAt':datetime.now(timezone.utc).isoformat(),'status':'clarified_four_spatial_pairs_per_support_foot_in_progress','supersedes':'Earlier center4/adjacent2 and minimum4 criterion','meaning':'Each foot remains in contact across four progressively changing relative positions, each position rendered as2 distinct poses. Forward landing, body over foot, early rear support, rear toe-off. No lateral turnout, duplicate art, interpolation or whole-character shift.','cycleMs':1200,'frameDurationMs':75,'pairDurationMs':150,'segments':[{'frames':[1,2],'support':'first_support_foot','position':'P1 forward landing, nearly straight natural knee'},{'frames':[3,4],'support':'first_support_foot','position':'P2 under hip, body passes support'},{'frames':[5,6],'support':'first_support_foot','position':'P3 slightly behind body, sustained support'},{'frames':[7,8],'support':'first_support_foot','position':'P4 rear toe-off, front part of sole stays in contact'},{'frames':[9,10],'support':'opposite_support_foot','position':'P1 forward landing'},{'frames':[11,12],'support':'opposite_support_foot','position':'P2 under hip'},{'frames':[13,14],'support':'opposite_support_foot','position':'P3 slightly behind body'},{'frames':[15,16],'support':'opposite_support_foot','position':'P4 rear toe-off'}],'supportLegsByDirection':'Direction agents must bind physical legs using actual images'}
(R/'audit/spatial-contact-requirement.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'inputs':len(inputs),'rule':req['status']},ensure_ascii=False))
