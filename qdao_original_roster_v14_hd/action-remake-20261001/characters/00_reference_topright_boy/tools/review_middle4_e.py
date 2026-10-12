"""Create native-source selection and diagnostic contact sheets, never alter source art."""
import json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'review/grounding-fourframes/E-middle4-plan.json').read_text(encoding='utf-8'))
replacements={3:'middle4-03-v3',11:'middle4-11-v2',12:'middle4-12-v2',13:'middle4-13-v4',14:'middle4-14-v3'}
for row in rows:
    if row['frame'] in replacements: row['source']='generation/run/E/'+replacements[row['frame']]+'.png'
    p=R/row['source'];row['sourceSha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    row['status']='candidate_middle4_side2_static_review_pending'
    row['observation']='沿跑向前侧2→身体下方中段4→后侧2，每帧75ms；原生独立姿态，待整段静态复查。'
assert len(set(x['sourceSha256'] for x in rows))==16
(R/'generation/run/E/selection-middle4-side2-20261004.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
canvas=Image.new('RGB',(1024,1120),'#eeeae2');draw=ImageDraw.Draw(canvas)
details=Image.new('RGB',(1600,880),'#eeeae2');dd=ImageDraw.Draw(details)
for i,row in enumerate(rows):
    im=Image.open(R/row['source']).convert('RGBA');export=Image.new('RGBA',(1024,1024));export.alpha_composite(im.resize((901,901),Image.Resampling.LANCZOS),(61,106));tile=export.resize((240,240),Image.Resampling.LANCZOS)
    x=(i%4)*256;y=(i//4)*280;canvas.paste(tile,(x+8,y),tile);draw.text((x+6,y+240),f'{i+1:02d} {row["supportFoot"]} {row["position"]}',fill='#153e37')
    crop=im.crop((250,825,1030,1215)).resize((390,195),Image.Resampling.LANCZOS);x=(i%4)*400;y=(i//4)*220;details.paste(crop,(x,y+20),crop);dd.text((x+4,y+3),f'{i+1:02d} {row["source"].split("/")[-1]}',fill='#153e37')
canvas.save(R/'review/grounding-fourframes/E-middle4-contact.jpg',quality=94)
details.save(R/'review/grounding-fourframes/E-middle4-lower.jpg',quality=95)
print('16 unique native source candidates; contacts refreshed')
