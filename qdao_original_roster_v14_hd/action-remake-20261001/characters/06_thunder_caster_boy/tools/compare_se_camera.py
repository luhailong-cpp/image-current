from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[1]
paths=['work/run_SE_06_contactpair_v2.png','work/run_SE_07_v4.png','work/run_SE_08_contactpair_v2.png','work/run_SE_09_contactpair_v2.png','work/run_SE_06_camerafinal_v2.png','work/run_SE_07_camerafinal_v2.png','work/run_SE_08_contactpair_v2.png','work/run_SE_09_contactpair_v2.png']
b=Image.new('RGB',(1600,840),(210,218,215));d=ImageDraw.Draw(b)
for i,p in enumerate(paths):
 im=Image.open(R/p).convert('RGBA').resize((400,400),Image.Resampling.LANCZOS);x=i%4*400;y=i//4*420;b.paste(im,(x,y),im);d.text((x+5,y+400),p.split('/')[-1],fill='black')
p=R/'review/SE_camera_candidates.png';b.save(p)
p.with_name(p.name+'.generation.json').write_text(json.dumps({'derivedFrom':[{'file':f,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest()} for f in paths],'operation':'full canvas400 fixedgrid comparison only','actualModel':None,'actualQuality':None},ensure_ascii=False),encoding='utf-8')
