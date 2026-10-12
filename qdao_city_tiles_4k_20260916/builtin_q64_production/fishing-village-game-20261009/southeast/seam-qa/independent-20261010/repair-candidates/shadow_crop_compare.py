from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
for prefix,box in [('S1-hull-shadow',(560,250,1040,1110)),('S2-stone-shadow',(850,500,1080,830))]:
 for suffix in ['input-100pct','v1']:
  im=Image.open(HERE/(prefix+'-'+suffix+'.png'))
  im.crop(box).save(HERE/(prefix+'-'+suffix+'-focus.png'))
