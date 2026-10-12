from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent;T=Z/'r07_c15';Q=T/'qa/model-pause-20261012';Q.mkdir(exist_ok=True,parents=True)
W=Z/'r07_c14/candidates/r07_c14.candidate.png'
for r in range(1,5):
 n=T/'native'/f'p{r}1-v20261012.png';o=Q/f'west-shared-row{r}.png';assert not o.exists()
 im=Image.new('RGB',(512,1024));im.paste(Image.open(W).convert('RGB').crop((3840,(r-1)*1024,4096,r*1024)),(0,0));im.paste(Image.open(n).convert('RGB').crop((115,115,371,1139)),(256,0));im.save(o)
source=T/'qa/core-baseline/cc4957ad3118e1d860b7/partial-core-baseline.rgba.png';o=Q/'partial-preview-not-complete.png';assert not o.exists();Image.open(source).resize((1536,1536),Image.Resampling.LANCZOS).save(o)
(Q/'qa-crop-provenance.json').write_text(json.dumps({'westCandidate':{'file':str(W),'sha256':hashlib.sha256(W.read_bytes()).hexdigest()},'nativeFirstColumn':[{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((T/'native').glob('p?1-v20261012.png'))],'operation':'shared windows integer native crops/paste noresampling; partialpreview alone resized and is not final art','partialPreviewSource':str(source)},indent=2),encoding='utf-8')
