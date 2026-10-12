from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent
TILE=HERE.parents[1]
BASE=TILE/'qa/core-baseline/df217b3c44d2eb2195d0/r08_c13-core-baseline.candidate.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
src=Path('C:/Users/luyua/.codex/generated_images/01a12556-0e70-7380-96c1-1af9b358adf7/exec-4df42711-a5fd-4ff7-9454-c65eed11e8ca.png')
dest=HERE/'source/road-junction-v1.png'
if not dest.exists():shutil.copy2(src,dest)
im=Image.open(dest).convert('RGB');assert im.size==(1254,1254)
mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).rectangle([250,470,999,1159],fill=255)
mask.save(HERE/'masks/road-junction-v1.png')
base=Image.open(BASE).convert('RGB')
base.paste(im,(1421,2445),mask)
base.save(HERE/'review/road-applied.png')
base.crop((1421,2445,2675,3699)).save(HERE/'review/road-after-100pct.png')
box=[2445,2190,3699,3444]
base.crop(box).save(HERE/'context/stone-cut.png')
save(HERE/'records/road-junction-v1.json',dict(sourceFile=str(dest),sourceSha256=sha(dest),toolOutput=str(src),toolOutputSha256=sha(src),actualModel=None,actualQuality=None,sourceSize=[1254,1254],sourceCrop=[0,0,1254,1254],dest=[1421,2445],mask=str(HERE/'masks/road-junction-v1.png'),maskSha256=sha(HERE/'masks/road-junction-v1.png'),maskType='binary integer rectangle; no feather/blur',maskLocalBox=[250,470,1000,1160],tileBox=[1671,2915,2421,3605],contextRecord=str(HERE/'records/road-context.json'),prompt=str(HERE/'prompts/road-junction-v1.txt'),request=str(HERE/'prompts/road-junction-v1.request.json'),receipt=str(HERE/'receipts/road-junction-v1.receipt.json'),reviewStatus='pending applied-edge inspection'))
save(HERE/'records/stone-context.json',dict(source=str(HERE/'review/road-applied.png'),sourceSha256=sha(HERE/'review/road-applied.png'),tileBox=box,worldBox=[2445+49152,2190+28672,3699+49152,3444+28672],operation='integer pixel crop; no resizing',context=str(HERE/'context/stone-cut.png'),contextSha256=sha(HERE/'context/stone-cut.png')))
print('Prepared repair and second context')

src=Path('C:/Users/luyua/.codex/generated_images/01a12556-0e70-7380-96c1-1af9b358adf7/exec-12eff10b-0667-418b-a432-de6b8e31dd3f.png')
dest=HERE/'source/stone-cut-v1.png'
if not dest.exists():shutil.copy2(src,dest)
im=Image.open(dest).convert('RGB');assert im.size==(1254,1254)
mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).rectangle([110,210,914,893],fill=255)
mask.save(HERE/'masks/stone-cut-v1.png')
base.paste(im,(2445,2190),mask)
base.save(HERE/'review/two-repairs-applied.png')
base.crop((2445,2190,3699,3444)).save(HERE/'review/stone-after-100pct.png')
base.resize((1024,1024)).save(HERE/'review/two-repairs-preview-25pct.png')
save(HERE/'records/stone-cut-v1.json',dict(sourceFile=str(dest),sourceSha256=sha(dest),toolOutput=str(src),toolOutputSha256=sha(src),actualModel=None,actualQuality=None,sourceSize=[1254,1254],sourceCrop=[0,0,1254,1254],dest=[2445,2190],mask=str(HERE/'masks/stone-cut-v1.png'),maskSha256=sha(HERE/'masks/stone-cut-v1.png'),maskType='binary integer rectangle; no feather/blur',maskLocalBox=[110,210,915,894],tileBox=[2555,2400,3360,3084],contextRecord=str(HERE/'records/stone-context.json'),prompt=str(HERE/'prompts/stone-cut-v1.txt'),request=str(HERE/'prompts/stone-cut-v1.request.json'),receipt=str(HERE/'receipts/stone-cut-v1.receipt.json'),reviewStatus='pending applied-edge inspection'))


