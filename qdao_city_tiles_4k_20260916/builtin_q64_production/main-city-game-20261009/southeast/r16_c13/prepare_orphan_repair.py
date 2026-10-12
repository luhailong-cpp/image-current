from pathlib import Path
import json, hashlib
from PIL import Image
T=Path(__file__).resolve().parent
L=json.loads((T/'candidate/latest-assembly.json').read_text(encoding='utf-8-sig'))
C=Image.open(L['candidate']['path']).convert('RGB')
R=T/'repairs-20261012'; R.mkdir(exist_ok=True)
box=[2300,1650,3554,2904]
p=R/'two-orphan-joints-v1-target.png'; C.crop(box).save(p)
Npath=T.parent/'r15_c13/candidate/r15_c13-4k-native-halo24-v4-20261012.png'
N=Image.open(Npath).convert('RGB')
for x in (1024,2048,3072):
 im=Image.new('RGB',(900,640)); im.paste(N.crop((x-450,3776,x+450,4096)),(0,0)); im.paste(C.crop((x-450,0,x+450,320)),(0,320))
 im.save(T/'review/native-full-qa-v1'/f'north-neighbor-junction{x}.png')
print(json.dumps({'target':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'box':box}))

