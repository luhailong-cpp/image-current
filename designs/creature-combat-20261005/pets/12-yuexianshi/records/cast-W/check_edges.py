from pathlib import Path
from PIL import Image
import json
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/12-yuexianshi')
result=[]
for n in range(1,17):
 rec=json.loads((root/'records/cast-W'/f'{n:02}.generation.json').read_text(encoding='utf-8'))
 p=Path(rec['derivedFrom']['path'])
 im=Image.open(p); a=im.getchannel('A')
 strong=a.point(lambda v:255 if v>64 else 0)
 edge=[a.crop((0,0,1,a.height)).getextrema()[1],a.crop((a.width-1,0,a.width,a.height)).getextrema()[1],a.crop((0,0,a.width,1)).getextrema()[1],a.crop((0,a.height-1,a.width,a.height)).getextrema()[1]]
 result.append({'frame':n,'nativeAlphaBBox':a.getbbox(),'nativeAlphaGt64BBox':strong.getbbox(),'nativeEdgeMaxAlpha_LRTB':edge,'sha256':rec['sha256']})
(root/'records/cast-W/edge-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

