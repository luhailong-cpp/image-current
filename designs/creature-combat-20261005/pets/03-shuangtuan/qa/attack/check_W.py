from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parents[2]
rows=[]
canvas=Image.new('RGB',(1536,1248),(235,239,236))
draw=ImageDraw.Draw(canvas)
for i in range(1,13):
 name=f'{i:02}'; p=root/'runtime/attack/W'/f'{name}.png'
 im=Image.open(p).convert('RGBA'); a=im.getchannel('A')
 rec=json.loads((root/'records/attack/W'/f'{name}.generation.json').read_text(encoding='utf-8'))
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 core=a.point(lambda q:255 if q>=128 else 0).getbbox()
 rows.append({'frame':name,'size':im.size,'mode':im.mode,'alphaExtrema':a.getextrema(),'coreAlpha128BBox':core,'sha256':sha,'recordMatches':rec['sha256']==sha,'promptExists':(root/rec['prompt']).exists(),'referencesExist':all(Path(r['path']).exists() for r in rec['references'])})
 thumb=im.resize((384,384),Image.Resampling.LANCZOS)
 x=((i-1)%4)*384; y=((i-1)//4)*416
 canvas.paste(thumb,(x,y),thumb)
 draw.text((x+12,y+385),f'Attack W {name} | 30 ms'+(' CONTACT' if i==8 else ''),fill=(20,30,25))
out=root/'qa/attack/W-contact-sheet.png';canvas.save(out)
result={'frames':rows,'count':len(rows),'uniqueSha256':len({r['sha256'] for r in rows}),'technicalStatus':'passed' if len(rows)==12 and all(r['recordMatches'] and r['promptExists'] and r['referencesExist'] and r['size']==(1024,1024) for r in rows) else 'failed','dynamicReview':'pending-parent','clientValidation':'not-performed'}
(root/'qa/attack/W-technical.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'contactSheet':str(out),'technicalStatus':result['technicalStatus'],'uniqueSha256':result['uniqueSha256'],'coreBoxes':[r['coreAlpha128BBox'] for r in rows]}))


