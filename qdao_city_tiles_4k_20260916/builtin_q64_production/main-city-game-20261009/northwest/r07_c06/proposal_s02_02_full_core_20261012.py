from PIL import Image
from pathlib import Path
import hashlib,json
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');out=r/'qa/s02_02_orphanfix03-full-core-proposal01';out.mkdir(exist_ok=False)
base=r/'candidate/r07_c06-candidate-native-roi-v04.png';src=r/'native/s02_02_orphanfix03.png'
c=Image.open(base).convert('RGB');d=Image.open(src).convert('RGB');c.paste(d.crop((115,115,1139,1139)),(1024,1024));c.save(out/'proposal-candidate-4096.png')
crops=[]
for name,box in [('v-r2-c1',(896,1024,1152,2048)),('v-r2-c2',(1920,1024,2176,2048)),('h-r1-c2',(1024,896,2048,1152)),('h-r2-c2',(1024,1920,2048,2176))]:
 p=out/(name+'.png');c.crop(box).save(p);crops.append(dict(name=name,box=list(box),file=str(p),actuallyViewed=False))
for xcol,x in [(1,1024),(2,2048)]:
 for yrow,y in [(1,1024),(2,2048)]:
  box=(x-160,y-160,x+160,y+160);name='j-r'+str(yrow)+'-c'+str(xcol);p=out/(name+'.png');c.crop(box).save(p);crops.append(dict(name=name,box=list(box),file=str(p),actuallyViewed=False))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'proposal-proof.json').write_text(json.dumps(dict(status='full-core-proposal-pending-eight-affected-joins',baseCandidate=dict(file=str(base),sha256=sha(base)),native=dict(file=str(src),sha256=sha(src)),sourceROI=[115,115,1139,1139],candidateROI=[1024,1024,2048,2048],nativeWorldBox=[21389,25485,22643,26739],proposal=dict(file=str(out/'proposal-candidate-4096.png'),sha256=sha(out/'proposal-candidate-4096.png')),crops=crops,sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,formalAccepted=False),indent=2),encoding='utf-8')
