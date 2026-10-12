from pathlib import Path
from PIL import Image
import os,json
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
a=Image.open(R/'native/r08_c11_p34_v01.png').convert('RGB');b=Image.open(R/'native/r08_c11_p44_v01.png').convert('RGB')
for cut in [1024,1082,1196,1254]:
 out=Image.new('RGB',(1254,2278));out.paste(a.crop((0,0,1254,cut)),(0,0));out.paste(b.crop((0,cut-1024,1254,1254)),(0,cut));out.crop((115,883,1139,1395)).save(Q/f'r08_c11-p34-p44-cut{cut}.png')
print('Saved four native-scale same-coordinate hard-cut trials, main images unchanged.')
