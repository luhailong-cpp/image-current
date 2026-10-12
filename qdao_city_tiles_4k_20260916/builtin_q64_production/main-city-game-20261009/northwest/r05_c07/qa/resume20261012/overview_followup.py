from PIL import Image
from pathlib import Path
import json
t=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c07');im=Image.open(t/'candidate/r05_c07-candidate-localcut-374432b8ed07.png')
out=t/'qa/resume20261012/overview-followup';out.mkdir(exist_ok=False)
for name,box in [('upper-left-seam',[850,280,1280,560]),('lower-left-seam',[850,630,1280,890]),('bottom-road-join',[910,3350,1210,3650])]:
 im.crop(box).save(out/(name+'.png'))
print(out)

