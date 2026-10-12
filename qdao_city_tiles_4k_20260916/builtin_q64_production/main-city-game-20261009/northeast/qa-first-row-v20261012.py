from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
T=Z/'r07_c15';O=T/'qa'/'first-row-v20261012';O.mkdir(exist_ok=True,parents=True)
fs=[T/'native'/f'p1{c}-v20261012.png' for c in range(1,5)]
row=Image.new('RGB',(4096,1024))
for c,f in enumerate(fs):row.paste(Image.open(f).convert('RGB').crop((115,115,1139,1139)),(c*1024,0))
for k in range(1,4):
    f=O/f'seam-p1{k}-p1{k+1}.png';assert not f.exists();row.crop((1024*k-256,0,1024*k+256,1024)).save(f)
p=O/'row-preview.png';assert not p.exists();row.resize((1536,384),Image.Resampling.LANCZOS).save(p)
(O/'sources.json').write_text(json.dumps({'sourceFiles':[{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in fs],'operation':'integer 1024px core crops; seam crops native pixels; preview alone resized; not final artwork','complete4kCandidate':False},indent=2),encoding='utf-8')
print(str(O))
