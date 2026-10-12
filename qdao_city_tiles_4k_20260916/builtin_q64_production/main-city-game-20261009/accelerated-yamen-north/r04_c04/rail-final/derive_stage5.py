from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path(__file__).resolve().parent
B=np.array(Image.open(O/'left-join-guide-v5.png').convert('RGB'))
R=np.array(Image.open(O/'raw-v5.png').convert('RGB'))
assert B.shape==R.shape==(1254,1254,3)
def ramp(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
x=np.arange(1254)[None,:]+0.5;y=np.arange(1254)[:,None]+0.5
w=ramp(x,610,660)*(1-ramp(x,1200,1254))*ramp(y,380,440)*(1-ramp(y,552,620))
alpha=np.floor(w*255+0.5).astype(np.uint32)
D=((B.astype(np.uint32)*(255-alpha[:,:,None])+R.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(alpha.astype(np.uint8)).save(O/'stage5-alpha.png')
Image.fromarray(D).save(O/'stage5-derived-context.png')
N=np.array(Image.open(O/'stage4-derived-native.png').convert('RGB'))
N[512:1139]=D[:627]
Image.fromarray(N).save(O/'stage5-derived-native.png')
Image.fromarray(D[340:760,610:1254]).save(O/'stage5-rail-join-detail-native.png')
Image.fromarray(D[467:787,115:1139]).save(O/'stage5-formal-south-boundary-native.png')
print('stage5 saved')
