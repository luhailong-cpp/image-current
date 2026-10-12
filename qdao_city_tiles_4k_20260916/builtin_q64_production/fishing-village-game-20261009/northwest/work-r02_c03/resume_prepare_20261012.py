from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone

B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest')
W=B/'work-r02_c03'
D=W/'resume-20261012-v1'
D.mkdir(exist_ok=True)
Q=D/'qa-before';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,a:Path(p).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(W/'converge-v1/r02_c03.candidate.png')
pair=Image.open(W/'converge-v1/full-pair.png')
nb=[8589,7750,9843,9004]
target=D/'r02_r03_roof_connector_v02.target.png'
pair.crop([nb[0]-8077,nb[1]-3981,nb[2]-8077,nb[3]-3981]).save(target)
write(str(target)+'.derivation.json',{'file':str(target),'sha256':sha(target),'globalNativeBox':nb,'source':str(W/'converge-v1/full-pair.png'),'sourceSha256':sha(W/'converge-v1/full-pair.png'),'sourceCropBox':[nb[0]-8077,nb[1]-3981,nb[2]-8077,nb[3]-3981],'resampled':False,'role':'actual edit target at blue roof connector'})
for r in range(4):
 for c in range(4):
  im.crop((c*1024,r*1024,(c+1)*1024,(r+1)*1024)).save(Q/f'core-{r+1}-{c+1}.png')
south=Image.open(B/'delivery-2x2/stage-v4/r03_c03.png')
for j in range(4):
 joint=Image.new('RGB',(1024,600));joint.paste(im.crop((j*1024,3796,(j+1)*1024,4096)),(0,0));joint.paste(south.crop((j*1024,0,(j+1)*1024,300)),(0,300));joint.save(Q/f'south-current-{j+1}.png')
 pair.crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(Q/f'south-proposed-{j+1}.png')
for name,boxes in [('north',[(i*1024,0,(i+1)*1024,256) for i in range(4)]),('south',[(i*1024,3840,(i+1)*1024,4096) for i in range(4)]),('west',[(0,i*1024,256,(i+1)*1024) for i in range(4)]),('east',[(3840,i*1024,4096,(i+1)*1024) for i in range(4)])]:
 for i,b in enumerate(boxes):im.crop(b).save(Q/f'{name}-{i+1}.png')
print(json.dumps({'target':str(target),'globalNativeBox':nb,'qa':str(Q)},ensure_ascii=False))
