from pathlib import Path
import importlib.util,json,hashlib,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prep',ROOT/'tools/repair-ground-contact.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
maps={
 'E':{1:('new',16,2),2:('old',1),3:('old',2),4:('old',3),5:('new',5,3),6:('new',6,3),7:('old',4),8:('new',8,4),9:('new',8,3),10:('old',9),11:('old',10),12:('old',11),13:('new',13,3),14:('new',14,3),15:('old',12),16:('new',16,3)},
 'SE':{**{i:('old',i) for i in [1,2,3,4,5,9,10,11,12]},6:('new',6,5),7:('new',7,4),8:('new',8,4),13:('new',13,4),14:('new',14,7),15:('new',15,6),16:('new',16,6)}
}
for d in sys.argv[1:]:
 rows=[]
 for n in range(1,17):
  s=maps[d][n]
  if s[0]=='new': p=mod.prepare(d,s[1],s[2])['reviewFile']
  else:p=f'final/run/{d}/{s[1]:02}.png'
  meta=load(ROOT/(p+'.generation.json'))
  rows.append({'action':'run','direction':d,'targetFrame':n,'sourceFile':p,'sourceGenerationRecord':p+'.generation.json','sha256':sha(ROOT/p),'nativeSha256':meta['source']['sha256'],'supportLeg':'RIGHT' if n<=8 else 'LEFT','positionSegment':((n-1)%8)//2+1,'pairOrdinal':(n-1)%2+1,'visualNotes':'pending visual review; source mapping only'})
 assert len({r['sha256'] for r in rows})==16
 dest=ROOT/f'provenance/ground-contact-20261004/position-selection-{d}-root.json';dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for typ in ['full','feet']:
  w,h=(300,320) if typ=='full' else (300,150)
  sheet=Image.new('RGB',(w*4,h*4),'#d9e5e8');draw=ImageDraw.Draw(sheet)
  for i,r in enumerate(rows):
   im=Image.open(ROOT/r['sourceFile']);x=i%4*w;y=i//4*h
   if typ=='feet':im=im.crop((200,725,925,1010))
   im.thumbnail((w,h-20),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+20),im)
   draw.text((x+5,y+3),f'{d}{i+1:02} {r["supportLeg"]} P{r["positionSegment"]}.{r["pairOrdinal"]}',fill='#182c32')
  sheet.save(ROOT/f'provenance/ground-contact-20261004/root-position-{d}-{typ}.jpg',quality=95)
 print(d,len(rows))
