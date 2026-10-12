from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
im=Image.open(D/'output/r11_c05.repaired.candidate.png')
boxes={'G01-dangling-y2795':[790,2630,1250,3060],'G02-G03-dangling-y3158-y3290':[940,3030,1400,3450],'G04-notch-y3642':[830,3500,1180,3800],'G05-notch-y4000':[900,3840,1230,4096],'G06-horizontal-dangling':[1950,1990,2360,2360],'G07-notch-y2350':[780,2180,1190,2550],'T01-second-row-color-x3072':[2790,1024,3280,1610]}
Q=D/'qa/issues';Q.mkdir(parents=True,exist_ok=True);crops={}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for k,b in boxes.items():
 p=Q/(k+'.png');im.crop(b).save(p,optimize=True);crops[k]={'path':str(p),'sha256':sha(p),'coreBox':b,'pixels':[b[2]-b[0],b[3]-b[1]],'resampled':False}
north=SW/'r10_c05/repairs/output/r10_c05.repaired.candidate.png'
assert sha(north)=='f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'
a=np.array(Image.open(north).convert('RGB'))[-256:]
b=np.array(im.convert('RGB'))[:256]
joined=np.concatenate([a,b],axis=0)
for c in range(4):
 p=D/'qa'/f'north-boundary-c{c+1}.png';Image.fromarray(joined[:,c*1024:(c+1)*1024]).save(p,optimize=True)
 crops[f'north-c{c+1}']={'path':str(p),'sha256':sha(p),'tileXRange':[c*1024,(c+1)*1024],'crossTileY':[-256,256],'joinAtY':256,'resampled':False}
(D/'qa/issue-evidence.json').write_text(json.dumps(crops,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'evidence':str(D/'qa/issue-evidence.json'),'northOriginalHashVerified':True,'count':len(crops)}))

