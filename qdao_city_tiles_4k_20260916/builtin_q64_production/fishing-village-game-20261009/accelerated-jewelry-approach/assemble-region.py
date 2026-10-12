from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
versions={'r03_c10':4,'r03_c11':2,'r04_c10':2,'r04_c11':3}
d=ROOT/'delivery';d.mkdir(exist_ok=True);q=ROOT/'qa/region-seams';q.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(8192,8192));sources=[]
for t,v in versions.items():
 p=ROOT/t/'candidate'/f'{t}-4096-candidate-v{v}.png';tile=Image.open(p);assert tile.size==(4096,4096)
 x=(int(t[5:7])-10)*4096;y=(int(t[1:3])-3)*4096
 im.paste(tile,(x,y));sources.append({'tile':t,'file':str(p),'sha256':sha(p),'dimensions':list(tile.size),'regionPasteAt':[x,y],'globalCoreBox':[36864+x,8192+y,40960+x,12288+y]})
out=d/'jewelry-approach-8192-candidate-v2.png';im.save(out)
prev=im.copy();prev.thumbnail((2048,2048));prev.save(d/'jewelry-approach-preview-2048.png')
for y in range(0,8192,1024):im.crop((3968,y,4224,y+1024)).save(q/f'vertical-y{y}.png')
for x in range(0,8192,1024):im.crop((x,3968,x+1024,4224)).save(q/f'horizontal-x{x}.png')
im.crop((3584,3584,4608,4608)).save(q/'center-four-way-native.png')
manifest={'updatedAt':datetime.now(timezone.utc).isoformat(),'map':'fishing-village','coordinates':list(versions),'globalPixelBox':[36864,8192,45056,16384],'sources':sources,'regionCandidate':{'file':str(out),'sha256':sha(out),'dimensions':[8192,8192],'operation':'unscaled integer pixel paste of four native-composed4096 candidates'},'preview':{'file':str(d/'jewelry-approach-preview-2048.png'),'classification':'downsampled preview only, not final artwork'},'nativePatchLayout':'4x4 1024-core per formal tile; each builtin original measured1254 with115pxhalo','nativePixelsResized':False,'formalAcceptedCount':0,'regionInternalSeamReview':'in_progress','externalRegionSeams':'not_available_for_review','actualModel':None,'actualQuality':None,'paidApiUsed':False}
(d/'candidate-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'nativeRegion':str(out),'preview':manifest['preview']['file'],'nativeSeamCrops':17,'sources':sources}))
