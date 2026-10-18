from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/row4-x1024-cross-20261013';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fs=[T/'native/s04_01_native01.png',T/'native/s04_02_native01.png'];parts=[([512,0,1139,1254],[0,0]),([115,0,742,1254],[627,0])]
im=Image.new('RGB',(1254,1254))
for f,(box,xy) in zip(fs,parts):im.paste(Image.open(f).convert('RGB').crop(box),xy)
im.save(D/'edit-target.png')
im.crop((490,470,810,800)).save(D/'before-detail.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','worldBox':[12685,31629,13939,32883],'originInTile':[397,2957],'formalSourceCoreY':[115,1139],'contextOnlyOutsideCoreY':True,'sources':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':xy} for f,(box,xy) in zip(fs,parts)],'resampled':False,'sha256':sha(D/'edit-target.png')},indent=2),encoding='utf-8')
