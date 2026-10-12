from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib,sys
b=Path(__file__).resolve().parents[1];e=b/'extension-20261011';q=e/'qa';q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
versions={'r03_c10':4,'r03_c11':2,'r04_c10':2,'r04_c11':3,'r05_c10':int(sys.argv[1]) if len(sys.argv)>1 else 1,'r05_c11':int(sys.argv[2]) if len(sys.argv)>2 else 1}
old=read(b/'delivery/candidate-manifest.json');oldsha={x['tile']:x['sha256'] for x in old['sources']}
canvas=Image.new('RGB',(8192,12288));sources=[]
for t,v in versions.items():
 p=b/t/'candidate'/f'{t}-4096-candidate-v{v}.png';im=Image.open(p).convert('RGB');assert im.size==(4096,4096)
 if t in oldsha:assert sha(p)==oldsha[t],f'Preserved candidate changed: {t}'
 x=(int(t[5:7])-10)*4096;y=(int(t[1:3])-3)*4096
 canvas.paste(im,(x,y));sources.append({'tile':t,'version':v,'file':str(p),'sha256':sha(p),'dimensions':[4096,4096],'regionPasteAt':[x,y],'globalCoreBox':[36864+x,8192+y,40960+x,12288+y]})
region_version=int(sys.argv[3]) if len(sys.argv)>3 else 1
out=e/f'jewelry-approach-six-8192x12288-candidate-v{region_version}.png'
assert not out.exists(),f'Preserve existing candidate; choose a new version: {out}'
canvas.save(out)
preview=canvas.copy();preview.thumbnail((1366,2048));preview.save(e/'six-tile-preview.png')
for y in range(0,12288,1024):canvas.crop((3968,y,4224,y+1024)).save(q/f'vertical-y{y}.png')
for y in [4096,8192]:
 for x in range(0,8192,1024):canvas.crop((x,y-128,x+1024,y+128)).save(q/f'horizontal-y{y}-x{x}.png')
for y in [4096,8192]:canvas.crop((3584,y-512,4608,y+512)).save(q/f'four-way-y{y}.png')
checks=[]
for s in sources:
 x,y=s['regionPasteAt'];crop=canvas.crop((x,y,x+4096,y+4096));tile=Image.open(s['file']).convert('RGB');checks.append({'tile':s['tile'],'exactPixelPasteVerified':ImageChops.difference(crop,tile).getbbox() is None})
manifest={'updatedAt':datetime.now(timezone.utc).isoformat(),'map':'fishing-village','coordinates':list(versions),'globalPixelBox':[36864,8192,45056,20480],'sources':sources,'regionCandidate':{'file':str(out),'sha256':sha(out),'dimensions':[8192,12288],'operation':'unscaled native pixel paste of six4096 candidates'},'preview':str(e/'six-tile-preview.png'),'priorFourUnchanged':True,'assemblyChecks':checks,'nativePixelsResized':False,'internalAndRegionQA':'pending','formalAcceptedCount':0,'exteriorSeamsReviewed':False,'actualModel':None,'actualQuality':None,'paidApiUsed':False}
(e/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(out),'sha256':manifest['regionCandidate']['sha256'],'qaCrops':30,'pixelPasteVerified':all(x['exactPixelPasteVerified'] for x in checks)}))
