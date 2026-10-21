from PIL import Image
from pathlib import Path
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north')
p=b/'versions/right-r04c14-p23-repair-guide-v003/r04_c14/guides/p23-REPAIR-GUIDE-only.png'
p.parent.mkdir(parents=True,exist_ok=True)
a=Image.open(b/'versions/right-r04c14-p23-native-v002/r04_c14/native/p23.png').convert('RGB')
s=Image.open(b/'versions/right-r04c14-p33-native-v001/r04_c14/native/p33.png').convert('RGB')
a.paste(s.crop((0,0,1254,230)),(0,1024));a.save(p)
print(p)

