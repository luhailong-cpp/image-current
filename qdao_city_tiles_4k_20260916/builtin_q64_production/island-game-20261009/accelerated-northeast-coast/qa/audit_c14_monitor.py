from pathlib import Path
from PIL import Image
import json,hashlib,re,os,uuid
from datetime import datetime,timezone
z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast');q=z/'qa/audit-c14';q.mkdir(exist_ok=True);e=q/'evidence';e.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def latest(pattern):
 choices=list((z/'native').glob(pattern));choices.sort(key=lambda p:int(re.search(r'_v(\d+)\.png$',p.name).group(1)) if re.search(r'_v(\d+)\.png$',p.name) else 1);return choices[-1] if choices else None
def atomic(p,d):
 t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
selected={(r,c):latest(f'r02_c14_p{r:02}_{c:02}*.png') for r in range(1,5) for c in range(1,5)};selected={k:v for k,v in selected.items() if v};seams=[]
for (r,c),a in selected.items():
 neighbors=[]
 if r<4 and (r+1,c) in selected:neighbors.append(('south',a,selected[r+1,c],'internal'))
 if r==4:
  b=z.parent/'northeast/native'/f"r03_c14_p01_{c:02}{'_v2' if c==4 else ''}.png";neighbors.append(('south',a,b,'external_south'))
 if c>1 and (r,c-1) in selected:neighbors.append(('east',selected[r,c-1],a,'internal'))
 if c==1:
  b=latest(f'r02_c13_p{r:02}_04*.png')
  if b:neighbors.append(('east',b,a,'external_west'))
 for side,left,right,scope in neighbors:
  imA=Image.open(left).convert('RGB');imB=Image.open(right).convert('RGB');assert imA.size==imB.size==(1254,1254)
  key=left.stem+'__'+right.stem;out=e/f'{key}-{side}-100pct.png'
  if not out.exists():
   if side=='south':
    im=Image.new('RGB',(1024,512));im.paste(imA.crop((115,883,1139,1139)),(0,0));im.paste(imB.crop((115,115,1139,371)),(0,256))
   else:
    im=Image.new('RGB',(512,1024));im.paste(imA.crop((883,115,1139,1139)),(0,0));im.paste(imB.crop((115,115,371,1139)),(256,0))
   im.save(out)
  seams.append({'key':key,'a':left.as_posix(),'aSha256':sha(left),'b':right.as_posix(),'bSha256':sha(right),'side':side,'scope':scope,'evidence':out.as_posix()})
review=q/'review.json';old=json.loads(review.read_text()) if review.exists() else {'seams':[]};reviewed={s['key'] for s in old['seams']};new=[s for s in seams if s['key'] not in reviewed]
manifest={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'selected':{f'{r},{c}':p.name for (r,c),p in selected.items()},'seams':seams}
atomic(q/'sources.json',manifest)
print(json.dumps({'selectedCount':len(selected),'selected':manifest['selected'],'unreviewed':new},ensure_ascii=False))
