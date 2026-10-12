from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
atlas=Image.new('RGB',(796,796),'white')
for i in range(4):
 for k,n in enumerate(['left','top','right','bottom']):
  im=Image.open(D/f'bench-G3-left-conditioned-v7-edge{i+1}-{n}-native.png');atlas.paste(im,(k*199,i*199))
atlas.save(D/'bench-G3-left-conditioned-v7-16-perimeters-native-atlas.png')
a=np.asarray(Image.open(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png').convert('RGB'));out=[]
for x in [519,615]:
 gold=(a[:,x,0]>240)&(a[:,x,1]>160)&(np.arange(1254)>330)&(np.arange(1254)<450);top=int(np.flatnonzero(gold)[0]);lum=a[:,x].mean(1)
 center=round(442+(x-449)*97/236);bevel=int(np.argmax(a[center-12:center+13,x,1].astype(int)+a[center-12:center+13,x,2].astype(int))+center-12)
 lowCenter=round(582+(x-449)*107/236);lower=int(lum[lowCenter-15:lowCenter+16].argmin()+lowCenter-15)
 lowFloor=710 if x==519 else760;floor=int(lum[lowFloor:lowFloor+60].argmin()+lowFloor)
 out.append({'x':x,'goldTopRow':top,'bevelRow':bevel,'darkLowerRow':lower,'deckGrooveRow':floor})
print(json.dumps(out))

