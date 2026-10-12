from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,os
from datetime import datetime,timezone
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base,pid,revision=sys.argv[1:];base=R/'tiles'/base;repair=R/'native'/f'{pid}.png'
q=read(R/'prompts'/f'{pid}.request.json');x,y=q['nativeTileBox'][:2];box=[x+115,y+115,x+1139,y+1139]
im=Image.open(base).convert('RGB');native=Image.open(repair).convert('RGB');assert im.size==(4096,4096) and native.size==(1254,1254)
im.paste(native.crop((115,115,1139,1139)),box[:2]);out=R/'tiles'/f'r08_c12.candidate-{revision}.png';assert not out.exists();im.save(out)
assert np.array_equal(np.array(im.crop(box)),np.array(native.crop((115,115,1139,1139))))
prior=read(Path(str(base)+'.generation.json'))
rec={'file':str(out),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':4096,'height':4096,'operation':'native1024 repair core hard overlay over exact native4096 base; no resize/blend/warp','base':str(base),'baseSha256':sha(base),'baseRecord':str(base)+'.generation.json','contributions':prior.get('contributions',[]),'repairOverlays':prior.get('repairOverlays',[])+[{'file':str(repair),'sha256':sha(repair),'sourceCrop':[115,115,1139,1139],'destination':box[:2],'destinationBox':box,'record':str(repair)+'.generation.json'}],'allContributionsPixelExact':True,'fullCoverage':True,'actualModel':None,'actualQuality':None,'status':'candidate_pending_native_overlay_perimeter_review'}
write(Path(str(out)+'.generation.json'),rec)
x0,y0,x1,y1=box
for name,crop in {'left':[x0-128,y0,x0+128,y1],'right':[x1-128,y0,x1+128,y1],'top':[x0,y0-128,x1,y0+128],'bottom':[x0,y1-128,x1,y1+128]}.items():
 if min(crop)>=0 and crop[2]<=4096 and crop[3]<=4096:
  p=R/'qa'/f'r08_c12.{revision}-overlay-{name}.png';im.crop(crop).save(p)
for r in range(1,4):
 for c in range(1,4):im.crop((c*1024-256,r*1024-256,c*1024+256,r*1024+256)).save(R/'qa'/f'r08_c12.junction_{r}{c}-{revision}.png')
im.resize((1024,1024),Image.Resampling.LANCZOS).save(R/'qa'/f'r08_c12.preview-{revision}.png')
print(json.dumps({'file':str(out),'sha256':sha(out),'overlay':box,'pixelExact':True}))

