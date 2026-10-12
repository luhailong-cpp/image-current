from pathlib import Path
from PIL import Image
import numpy as np, json,hashlib
O=Path(__file__).resolve().parent
N=Image.open(O.parent/'qa-repair-native/exported-native-v1/s04_01-internal4-derived.png').convert('RGB')
S=Image.open(O.parent.parent.parent/'northwest/r05_c04/native/s01_01.png').convert('RGB')
R=Image.open(O/'raw-v4.png').convert('RGB')
assert N.size==S.size==R.size==(1254,1254)
def ramp(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def blend(a,b,w):
 w=np.floor(255*w+0.5).astype(np.uint32)[:,:,None];return ((a.astype(np.uint32)*(255-w)+b.astype(np.uint32)*w+127)//255).astype(np.uint8)
x=np.arange(1254)[None,:]+0.5;y=np.arange(1254)[:,None]+0.5
left=ramp(y,420,484);right=ramp(y,0,80);xright=ramp(x,810,870)
w=(left*(1-xright)+right*xright)*ramp(x,610,660)*(1-ramp(x,1090,1135))
A=blend(np.array(N),np.array(R),w)
Image.fromarray(np.floor(w*255+0.5).astype(np.uint8)).save(O/'stage4-raw-alpha.png')
southcanvas=np.array(N).copy();southcanvas[1024:]=np.array(S)[:230]
ws=np.broadcast_to(ramp(y,1024,1104),(1254,1254)).copy()
A=blend(A,southcanvas,ws)
Image.fromarray(np.floor(ws*255+0.5).astype(np.uint8)).save(O/'stage4-south-alpha.png')
Image.fromarray(A).save(O/'stage4-derived-native.png')
ctx=np.concatenate((A[512:1139],np.array(S)[115:742]),axis=0)
Image.fromarray(ctx).save(O/'left-join-guide-v5.png')
Image.fromarray(ctx[360:740,610:1120]).save(O/'stage4-rail-join-detail-native.png')
print('stage4 saved; raw, south and same-coordinate alpha only')
