from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');S=T/'repairs/north-caps-v1-20261012/N3';D=T/'repairs/north-cap-thin-v3-20261012';D.mkdir()
target=D/'target-native-1254.png';target.write_bytes((S/'target-native-1254.png').read_bytes())
mask=np.zeros((1254,1254),dtype='uint8');mask[627:707,330:650]=255;mp=D/'edit-mask-1254.png';Image.fromarray(mask).save(mp)
refs=json.loads((S/'request.json').read_text())['referenced_image_paths'][:3]
prompt='Use case: precise-object-edit. LAST image is the fixed actual 1254 x 1254 native close crop; the upper 627 rows are immutable old-neighbor core. The blue inlay is clipped at the horizontal boundary y627. Add only a thin complete horizontal dark grout and pale bevel cap across this existing blue cut at y630..640, connecting its existing left and right diagonal blue borders exactly. Keep the blue stone width and ALL existing diagonal borders unchanged. Do not round, taper or narrow the blue strip. Do not reroute grout or repaint any large slab. The repair is just a closed stone edge about 10 pixels thick at the cut; do not redesign pavement. Second-last image white mask local x330..650 y627..707 permits this tiny edit; black region is immutable. First three references define material only. Same lighting, color and crop; no zoom, warp, resize or new objects. Return actual native 1254 x 1254 PNG.'
req={'prompt':prompt,'referenced_image_paths':refs+[str(mp),str(target)],'transparent_background':False}
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
(D/'request.json').write_text(json.dumps(req,indent=2));(D/'prompt.txt').write_text(prompt);(D/'preparation.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourcePreparation':rec(S/'preparation.json'),'base':json.loads((S/'preparation.json').read_text())['base'],'origin':[2250,-627],'applyBox':[2580,0,2900,80],'references':[rec(p) for p in req['referenced_image_paths']],'request':rec(D/'request.json'),'nativeSize':[1254,1254],'noResize':True},indent=2))
print(str(D))

