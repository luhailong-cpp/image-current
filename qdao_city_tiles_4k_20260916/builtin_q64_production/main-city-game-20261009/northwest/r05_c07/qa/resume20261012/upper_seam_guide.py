import json
from pathlib import Path
from PIL import Image
t=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c07');target=t/'layout-only/s01_02_seam02.edit-guide.png';assert not target.exists()
im=Image.open(t/'native/s01_02.png').convert('RGB');im.paste(Image.open(t/'native/s01_01.png').convert('RGB').crop((1024,0,1254,1254)),(0,0));im.save(target)
(t/'layout-only/s01_02_seam02.edit-guide.png.derivation.json').write_text(json.dumps({'operation':'LAYOUT/EDIT GUIDE ONLY: current s01_02 with LEFT230 exact native neighbor samples from s01_01 right230','noFinalArt':True,'sourceResampled':False,'parts':[{'file':str(t/'native/s01_02.png'),'box':[0,0,1254,1254]},{'file':str(t/'native/s01_01.png'),'box':[1024,0,1254,1254],'paste':[0,0]}]},indent=2)+'\n',encoding='utf-8')
print(target)

