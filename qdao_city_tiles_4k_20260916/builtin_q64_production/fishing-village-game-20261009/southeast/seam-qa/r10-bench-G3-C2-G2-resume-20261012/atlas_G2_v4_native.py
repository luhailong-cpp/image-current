from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parent
atlas=Image.new('RGB',(796,995),'white')
for i in range(5):
 for k,n in enumerate(['left','top','right','bottom']):
  im=Image.open(D/f'eastdeck-G2-conditioned-v4-gap{i+1}-{n}-native.png')
  atlas.paste(im,(k*199,i*199))
atlas.save(D/'eastdeck-G2-conditioned-v4-20-local-perimeters-native-atlas.png')

