from pathlib import Path
from PIL import Image
import json,numpy as np,sys
O=Path(__file__).resolve().parent;i=int(sys.argv[1]);P=json.loads((O/'preparation.json').read_text());r=P['rois'][i-1];l,t,rr,bb=r.get('supportBox',r['roiBox'])
B=np.array(Image.open(O/f'stage{i-1}-native.png').convert('RGB'));R=np.array(Image.open(O/f'roi{i}-raw.png').convert('RGB'))
assert B.shape==R.shape==(1254,1254,3)
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
def s(v,a,b):
 z=np.clip((v-a)/(b-a),0,1);return z*z*(3-2*z)
w=s(x,l,l+16)*(1-s(x,rr-16,rr))*s(y,t,t+16)*(1-s(y,bb-16,bb))
A=np.floor(w*255+.5).astype(np.uint32);D=((B.astype(np.uint32)*(255-A[:,:,None])+R.astype(np.uint32)*A[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(A.astype('uint8')).save(O/f'roi{i}-alpha.png');Image.fromarray(((A>0)*255).astype('uint8')).save(O/f'roi{i}-support-positive-mask.png')
Image.fromarray(D).save(O/f'roi{i}-derived-context.png');Image.fromarray(D).save(O/f'stage{i}-native.png')
box=[l-60,t-60,rr+60,bb+60];before=B[box[1]:box[3],box[0]:box[2]];after=D[box[1]:box[3],box[0]:box[2]]
Image.fromarray(after).save(O/f'roi{i}-qa-detail-native.png');Image.fromarray(np.concatenate([before,after],axis=1)).save(O/f'roi{i}-qa-comparison-native.png')
assert np.array_equal(B[A==0],D[A==0])
if i<3:
 n=P['rois'][i]['roiBox'];M=np.concatenate([D,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);M[n[1]:n[3],n[0]:n[2]]=0
 Image.fromarray(M).save(O/f'roi{i+1}-mask-guide.png')
print(json.dumps({'id':i,'roi':r,'qaContextBox':box,'changedPixels':int(np.any(D!=B,axis=2).sum())}))
