import json, hashlib, re
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
out=R/'review/run-diagonal';out.mkdir(parents=True,exist_ok=True)
for d in ('SE','SW'):
 chosen={}
 for p in (R/'staging/run'/d).glob('*.png'):
  m=re.fullmatch(r'(\d\d)(?:-v(\d+))?\.png',p.name)
  if m:
   n,v=int(m[1]),int(m[2] or 0)
   if n not in chosen or v>chosen[n][0]:chosen[n]=(v,p)
 sheet=Image.new('RGB',(1200,1304),(58,66,75));dr=ImageDraw.Draw(sheet);records=[]
 for n,(_,p) in sorted(chosen.items()):
  im=Image.open(p).convert('RGBA');a=im.getchannel('A');edge=sum(v>8 for v in list(a.crop((0,0,im.width,1)).getdata())+list(a.crop((0,im.height-1,im.width,im.height)).getdata())+list(a.crop((0,0,1,im.height)).getdata())+list(a.crop((im.width-1,0,im.width,im.height)).getdata()))
  q=im.resize((300,300),Image.Resampling.LANCZOS);x=((n-1)%4)*300;y=((n-1)//4)*326
  sheet.paste(q,(x,y),q);dr.text((x+10,y+301),f'{d} {n:02d} {p.name}',fill='white')
  records.append({'index':n,'path':str(p.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'record':str(p.relative_to(R)).replace('\\','/')+'.generation.json','size':im.size,'edgePixelsAlphaGT8':edge,'status':'candidate_pending_sequence_review'})
 sheet.save(out/f'{d}-contact.jpg',quality=94)
 (out/f'{d}-selection.json').write_text(json.dumps({'direction':d,'count':len(records),'reviewStatus':'candidate','frames':records},ensure_ascii=False,indent=2),encoding='utf-8')
 print(d,len(records),[(r['index'],r['edgePixelsAlphaGT8']) for r in records if r['edgePixelsAlphaGT8']])

