from pathlib import Path
from PIL import Image, ImageChops
import json, hashlib, io
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
Q=T/'qa'/'final-review'; Q.mkdir(exist_ok=True)
R=T/'qa'/'native-repairs'
B=T/'qa'/'core-baseline'/'c283fdfb38adab68f261'/'r05_c14-core-baseline.candidate.png'
C=T/'candidates'/'r05_c14.candidate.png'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def imsha(im):
 b=io.BytesIO(); im.save(b,format='PNG'); return hashlib.sha256(b.getvalue()).hexdigest()
im=Image.open(B).convert('RGB'); chain=[]
for m in ['m01','m02','m03','m04','m05']:
 d=json.loads((R/(m+'-integration.json')).read_text())
 assert imsha(im)==d['input']['sourceSha256'],m+' input chain hash'
 native=Path(d['native']); mask=Path(d['mask'])
 assert sha(native)==d['nativeSha256'] and sha(mask)==d['maskSha256']
 origin=tuple(d['input']['origin']); before=im.copy()
 im.paste(Image.open(native).convert('RGB'),origin,Image.open(mask))
 assert imsha(im)==d['outputSha256'],m+' output chain hash'
 expanded=Image.new('L',(4096,4096),0); expanded.paste(Image.open(mask),origin)
 unchanged=ImageChops.difference(before,im); unchanged.paste((0,0,0),(0,0,4096,4096),expanded.point(lambda n:255 if n else 0))
 assert unchanged.getbbox() is None
 chain.append({'repair':m,'inputSha256':d['input']['sourceSha256'],'outputSha256':d['outputSha256'],'allPixelsOutsideMaskUnchanged':True,'record':str(R/(m+'-integration.json'))})
final=Image.open(C).convert('RGB'); assert ImageChops.difference(im,final).getbbox() is None
art=[]
for axis in ['vertical','horizontal']:
 for n in range(1,4):
  center=n*1024
  for seg in range(4):
   box=(center-192,seg*1024,center+192,(seg+1)*1024) if axis=='vertical' else (seg*1024,center-192,(seg+1)*1024,center+192)
   path=Q/f'{axis}-{n}-{seg+1}-100pct.png'; final.crop(box).save(path); art.append({'file':str(path),'crop':box,'sha256':sha(path)})
for r in range(1,4):
 for c in range(1,4):
  x,y=c*1024,r*1024; path=Q/f'intersection-{r}-{c}-100pct.png'; final.crop((x-450,y-450,x+450,y+450)).save(path)
west=Image.open(T.parent/'r05_c13'/'candidates'/'r05_c13.candidate.png').convert('RGB')
for row in range(4):
 crop=Image.new('RGB',(384,1024)); crop.paste(west.crop((3904,row*1024,4096,(row+1)*1024)),(0,0)); crop.paste(final.crop((0,row*1024,192,(row+1)*1024)),(192,0)); crop.save(Q/f'west-external-row{row+1}-100pct.png')
# Native 1:1 montage panels: 3 vertical seams side by side, 3 horizontal seams stacked.
for seg in range(1,5):
 v=Image.new('RGB',(1152,1024)); h=Image.new('RGB',(1024,1152))
 for n in range(1,4):
  v.paste(Image.open(Q/f'vertical-{n}-{seg}-100pct.png'),((n-1)*384,0))
  h.paste(Image.open(Q/f'horizontal-{n}-{seg}-100pct.png'),(0,(n-1)*384))
 v.save(Q/f'v-montage-row{seg}-100pct.png'); h.save(Q/f'h-montage-col{seg}-100pct.png')
proof={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r05_c14','candidate':str(C),'candidateSha256':sha(C),'pixels':[4096,4096],'replayPixelIdentical':True,'nativePatchesSelected':16,'nativeGenerationRecords':len(list((T/'native').glob('*.generation.json'))),'repairChain':chain,'operations':'integer core crops plus native source overlays, no resizing/blur/warp','actualModel':None,'actualQuality':None,'allCurrentReferencesCheckedByBaseline':True,'historicalMissingStyleReferences':2}
(Q/'source-replay.json').write_text(json.dumps(proof,indent=2)+'\n')
(T/'candidates'/'r05_c14.candidate.png.generation.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))

