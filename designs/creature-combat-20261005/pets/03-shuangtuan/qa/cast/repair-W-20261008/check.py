from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan');Q=B/'qa/cast/repair-W-20261008'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
sheet=Image.new('RGB',(1600,1744),(219,229,219));d=ImageDraw.Draw(sheet)
for n in range(1,17):
    f=f'{n:02d}';p=B/f'runtime/cast/W/{f}.png';im=Image.open(p);a=im.getchannel('A');rec=json.loads((B/f'records/cast/W/{f}.generation.json').read_text(encoding='utf-8-sig'))
    edges=list(a.crop((0,0,1024,1)).getdata())+list(a.crop((0,1023,1024,1024)).getdata())+list(a.crop((0,0,1,1024)).getdata())+list(a.crop((1023,0,1024,1024)).getdata())
    rows.append({'frame':n,'file':p.relative_to(B).as_posix(),'sha256':sha(p),'size':im.size,'mode':im.mode,'alphaExtrema':a.getextrema(),'alphaBBox':a.getbbox(),'edgeMaxAlpha':max(edges),'generationShaMatches':rec['sha256']==sha(p)})
    x=((n-1)%4)*400;y=((n-1)//4)*436
    tile=Image.new('RGBA',(384,384),(64,80,74,255));tile.alpha_composite(im.resize((384,384),Image.Resampling.LANCZOS));sheet.paste(tile.convert('RGB'),(x+8,y+8));d.text((x+12,y+400),f'W {f} / 45ms'+(' RELEASE' if n==11 else ''),fill=(20,40,25))
sheet.save(Q/'current-W-contact.png')
out={'scope':'cast W 01-16','frameCount':len(rows),'uniqueSha256':len(set(x['sha256'] for x in rows)),'technicalPass':all(x['size']==(1024,1024) and x['mode']=='RGBA' and x['alphaExtrema']==(0,255) and x['generationShaMatches'] for x in rows),'frames':rows,'dynamicPlayback':'not performed by repair subagent; root executor rebuilding final SHA-bound video'}
(Q/'technical.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in rows),encoding='utf-8')
print(json.dumps({'technicalPass':out['technicalPass'],'unique':out['uniqueSha256'],'edgeMax':[(x['frame'],x['edgeMaxAlpha']) for x in rows],'contact':str(Q/'current-W-contact.png')},ensure_ascii=False))
