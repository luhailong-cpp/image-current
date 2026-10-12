from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]; out=R/'review/video-axis-details';out.mkdir(exist_ok=True)
sources=[];outputs=[]
for who,base in [('06',R),('09',R.parent/'09_bamboo_archer_girl')]:
 for direction in ['S','SE','SW']:
  batches=range(4) if who=='06' else range(1)
  for batch in batches:
   ids=range(batch*4,batch*4+4) if who=='06' else [1,5,9,13]
   board=Image.new('RGB',(1700,918),(220,224,222));d=ImageDraw.Draw(board)
   selected=[]
   for idx,n in enumerate(ids):
    p=base/'runtime/run'/direction/f'{n:02}.png';im=Image.open(p).convert('RGBA')
    crop=im.crop((100,590,950,1024));x=idx%2*850;y=idx//2*459
    board.paste(crop,(x,y),crop);d.text((x+10,y+437),f'{who} {direction} {n:02} actual crop 1:1',fill='black')
    selected.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frame':n,'direction':direction,'crop':[100,590,950,1024]})
   p=out/f'{who}-{direction}-{batch}.jpg';board.save(p,quality=95);outputs.append(str(p))
   p.with_name(p.name+'.generation.json').write_text(json.dumps({'file':str(p),'derivedFrom':selected,'operation':'diagnostic crop at native1:1 only, runtime untouched','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
   sources+=selected
(out/'inputs.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(outputs))

