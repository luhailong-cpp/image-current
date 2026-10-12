from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
Q=T/'qa'/'first-row';Q.mkdir(parents=True,exist_ok=True)
out=Image.new('RGB',(4096,1024));sources=[]
for c in range(1,5):
 p=T/'native'/f'p1{c}.png';im=Image.open(p).convert('RGB');out.paste(im.crop((115,115,1139,1139)),((c-1)*1024,0));sources.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out.save(Q/'first-row.png')
montage=Image.new('RGB',(1152,1024))
for c in range(1,4):
 crop=out.crop((c*1024-192,0,c*1024+192,1024));crop.save(Q/f'v-{c}.png');montage.paste(crop,((c-1)*384,0))
montage.save(Q/'v-row1-100pct.png')
npath=T.parent/'r06_c14'/'candidates'/'r06_c14.candidate.png';north=Image.open(npath).convert('RGB')
for c in range(1,5):
 ext=Image.new('RGB',(1024,384));ext.paste(north.crop(((c-1)*1024,3904,c*1024,4096)),(0,0));ext.paste(out.crop(((c-1)*1024,0,c*1024,192)),(0,192));ext.save(Q/f'north-{c}-100pct.png')
(Q/'manifest.json').write_text(json.dumps({'selectedNative':sources,'dimensions':[4096,1024],'resized':False,'north':str(npath),'northSha256':hashlib.sha256(npath.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
p=T/'tile-progress.json';d=json.loads(p.read_text());d.update(status='row1_generated_waiting_for_required_west_p24',nativeCount=4,selectedCoreCount=4,remainingCoreCount=12,waitFor='r07_c13/native/p24.png.generation.json',nextPatch='p21');p.write_text(json.dumps(d,indent=2),encoding='utf-8')
