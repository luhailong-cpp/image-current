from pathlib import Path
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent
B=np.array(Image.open(O/'stage5-derived-context.png').convert('RGB'))
R=np.array(Image.open(O/'raw-v7.png').convert('RGB'))
def ramp(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
w=ramp(x,600,640)*(1-ramp(x,1040,1100))*ramp(y,400,440)*(1-ramp(y,619,627))
alpha=np.floor(w*255+.5).astype(np.uint32)
D=((B.astype(np.uint32)*(255-alpha[:,:,None])+R.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(alpha.astype(np.uint8)).save(O/'alternative7-alpha.png')
Image.fromarray(D).save(O/'alternative7-context.png')
N=np.array(Image.open(O/'stage5-derived-native.png').convert('RGB'));N[512:1139]=D[:627]
Image.fromarray(N).save(O/'alternative7-native.png')
Image.fromarray(D[330:820,580:1130]).save(O/'alternative7-join-detail-native.png')
Image.fromarray(D[467:787,115:1139]).save(O/'alternative7-formal-boundary-native.png')
print('Alternative saved; design change must be disclosed.')
