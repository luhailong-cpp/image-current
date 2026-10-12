from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[2];T=B/'r05_c11';D=T/'qa/internal-unrepaired';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.new('RGB',(4096,4096),(100,100,100));selected={}
for r in range(1,5):
 for c in range(1,5):
  p=T/'records'/f'p{r}{c}.selection.json'
  if not p.exists():continue
  rec=json.loads(p.read_text());native=Path(rec['file']);src=Image.open(native);assert src.size==(1254,1254)
  im.paste(src.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));selected[(r,c)]={'file':str(native),'sha256':sha(native),'nativeDimensions':list(src.size)}
im.save(D/'partial-native.png');preview=im.copy();preview.thumbnail((1254,1254));preview.save(D/'preview.png')
crops=[]
for r in range(1,5):
 for c in range(1,4):
  if (r,c) not in selected or (r,c+1) not in selected:continue
  box=[c*1024-256,(r-1)*1024,c*1024+256,r*1024];p=D/f'v-p{r}{c}-p{r}{c+1}.png';im.crop(box).save(p);crops.append({'file':str(p),'sha256':sha(p),'tileBox':box})
for r in range(1,4):
 for c in range(1,5):
  if (r,c) not in selected or (r+1,c) not in selected:continue
  box=[(c-1)*1024,r*1024-256,c*1024,r*1024+256];p=D/f'h-p{r}{c}-p{r+1}{c}.png';im.crop(box).save(p);crops.append({'file':str(p),'sha256':sha(p),'tileBox':box})
(D/'manifest.json').write_text(json.dumps({'selected':list(selected.values()),'cropCount':len(crops),'crops':crops,'nativeDimensions':[4096,4096],'resampling':False,'previewOnlyResized':True},indent=2))
print(json.dumps({'coreCount':len(selected),'cropCount':len(crops)}))
