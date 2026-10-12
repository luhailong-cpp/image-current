from pathlib import Path
from PIL import Image
import numpy as np,json,sys
O=Path(__file__).resolve().parent;i=int(sys.argv[1]);P=json.loads((O/'preparation.json').read_text());l,t,rr,bb=P['rois'][i-1]['roiBox']
B=np.array(Image.open(O/f'stage{i-1}-native.png').convert('RGB'));R=np.array(Image.open(O/f'roi{i}-raw.png').convert('RGB'))
lo,hi=600,670
cost=((B[lo:hi,l:rr].astype(float)-R[lo:hi,l:rr])**2).mean(axis=2).T
n,h=cost.shape;prior=cost[0].copy();back=np.zeros((n,h),dtype=np.int8)
for z in range(1,n):
 choices=np.stack([np.r_[np.inf,prior[:-1]],prior,np.r_[prior[1:],np.inf]])
 pick=np.argmin(choices,axis=0);back[z]=pick-1;prior=cost[z]+np.take_along_axis(choices,pick[None,:],axis=0)[0]
path=np.empty(n,dtype=int);path[-1]=np.argmin(prior)
for z in range(n-1,0,-1):path[z-1]=path[z]+back[z,path[z]]
path+=lo
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
def s(v,a,b):
 z=np.clip((v-a)/(b-a),0,1);return z*z*(3-2*z)
cut=np.zeros((1,1254));cut[0,l:rr]=path
w=s(x,l,l+12)*(1-s(x,rr-12,rr))*s(y,t,t+16)*(1-s(y,cut-2,cut+2))
A=np.floor(w*255+.5).astype(np.uint32);D=((B.astype(np.uint32)*(255-A[:,:,None])+R.astype(np.uint32)*A[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(A.astype('uint8')).save(O/f'roi{i}-alpha.png');Image.fromarray(((A>0)*255).astype('uint8')).save(O/f'roi{i}-support-positive-mask.png');Image.fromarray(D).save(O/f'roi{i}-derived-context.png');Image.fromarray(D).save(O/f'stage{i}-native.png')
box=[l-60,t-60,rr+60,900];before=B[box[1]:box[3],box[0]:box[2]];after=D[box[1]:box[3],box[0]:box[2]]
Image.fromarray(after).save(O/f'roi{i}-qa-detail-native.png');Image.fromarray(np.concatenate([before,after],axis=1)).save(O/f'roi{i}-qa-comparison-native.png')
(O/f'roi{i}-adaptive-path.json').write_text(json.dumps({'yPath':path.tolist(),'xRange':[l,rr],'searchYRange':[lo,hi],'lowerAlphaTransitionPixels':4})+'\n')
if i<3:
 n=P['rois'][i]['roiBox'];M=np.concatenate([D,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);M[n[1]:n[3],n[0]:n[2]]=0;Image.fromarray(M).save(O/f'roi{i+1}-mask-guide.png')
print('lower path',int(path.min()),int(path.max()))
