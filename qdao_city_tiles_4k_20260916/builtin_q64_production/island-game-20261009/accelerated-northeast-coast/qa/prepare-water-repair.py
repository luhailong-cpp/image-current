from pathlib import Path
from PIL import Image,ImageFilter
import sys,json
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast')
import coast_work as c
src=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/native/r01_c13_p03_02_v3.png')
im=Image.open(src).convert('RGB')
box=(950,760,1254,1110)
im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(24)),box)
dest=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast/guides/r01_c13_p03_02_v4.local-repaint-guide.png')
im.save(dest)
c.write(dest.with_suffix('.png.derivation.json'),{'operation':'blur target defect area in guide only; final will be newly generated','source':str(src),'box':box,'finalPixels':False})
c.prepare('r01_c13_p03_02_v4',[],str(dest))

