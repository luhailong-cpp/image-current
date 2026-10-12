from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parents[1]; Z=T.parent
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
sel=read(T/'selected-native.json'); west=Z/'r08_c14'; ws=read(west/'tile-progress.json');wc=Path(ws['candidate']);assert h(wc)==ws['candidateSha256']
wim=Image.open(wc).convert('RGB');out=T/'qa/left-column-v20261012';out.mkdir(exist_ok=True)
sources=[{'file':str(wc),'sha256':h(wc)}];arts=[]
for r in range(1,5):
 p=T/'native'/sel[f'p{r}1'];im=Image.open(p).convert('RGB');s=Image.new('RGB',(384,1024));s.paste(wim.crop((3904,(r-1)*1024,4096,r*1024)),(0,0));s.paste(im.crop((115,115,307,1139)),(192,0));f=out/f'west-r{r}-100pct.png';s.save(f);sources.append({'file':str(p),'sha256':h(p)});arts.append({'file':str(f),'sha256':h(f),'worldBox':[57152,28672+(r-1)*1024,57536,28672+r*1024]})
north=Z/'r07_c15';nsel=read(north/'selected-native.json');np=north/'native'/nsel['p41'];im=Image.open(np).convert('RGB');s=Image.new('RGB',(1024,384));s.paste(im.crop((115,947,1139,1139)),(0,0));p=T/'native'/sel['p11'];s.paste(Image.open(p).convert('RGB').crop((115,115,1139,307)),(0,192));f=out/'north-c1-100pct.png';s.save(f);sources.append({'file':str(np),'sha256':h(np)});arts.append({'file':str(f),'sha256':h(f),'worldBox':[57344,28480,58368,28864]})
(out/'manifest.json').write_text(json.dumps({'sources':sources,'artifacts':arts,'operation':'integer native crop/paste only; no resized source; current west candidate and selected north p41','formalAcceptedCount':0},indent=2)+'\n',encoding='utf8')
print(out)

