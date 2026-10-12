from PIL import Image
import numpy as np,json
from production import W,B,read,write,sha
D=W/'joint-v2';D.mkdir(exist_ok=True)
m=read(W/'joint-stage/joint.assembly.json')
a=np.asarray(Image.open(m['file']).convert('RGB')).copy();ids=np.asarray(Image.open(m['sourceIdMap'])).copy();sources=m['sources'];origin=(12173,3981)
def path(cost,step=3):
 h,w=cost.shape;prev=cost[:,0].copy();back=np.zeros((h,w),np.int8)
 for x in range(1,w):
  ar=np.stack([np.roll(prev,k) for k in range(-step,step+1)])
  for k in range(-step,step+1):
   if k<0:ar[k+step,k:]=1e12
   elif k>0:ar[k+step,:k]=1e12
  ix=ar.argmin(0);back[:,x]=ix-step;prev=ar.min(0)+cost[:,x]
 y=int(prev.argmin());p=np.zeros(w,int)
 for x in range(w-1,-1,-1):p[x]=y;y-=int(back[y,x])
 return p
def ring(old,new,bands=(150,150,150,150),minedge=4):
 cost=np.abs(old.astype(float)-new.astype(float)).mean(2)+.05
 # Discourage crossing mismatched high-contrast stone joints or object edges.
 cost=cost+np.max(np.abs(old.astype(float)-new.astype(float)),2)*.35
 def joint(z):
  z=z.astype(float);return (z[:,:,0]>z[:,:,1]+13)&(z[:,:,1]>z[:,:,2]+7)
 j1,j2=joint(old),joint(new)
 bad=j1^j2
 bad=np.maximum.reduce([np.roll(np.roll(bad,dy,0),dx,1) for dy in range(-3,4) for dx in range(-3,4)])
 cost+=bad*2000
 h,w=cost.shape;yy,xx=np.indices((h,w));mask=np.ones((h,w),bool)
 t,r,b,l=bands
 if t: mask &= yy>=path(cost[minedge:t,:])+minedge
 if b: mask &= yy<=path(cost[h-b:h-minedge,:])+h-b
 if l: mask &= xx>= (path(cost[:,minedge:l].T)+minedge)[:,None]
 if r: mask &= xx<= (path(cost[:,w-r:w-minedge].T)+w-r)[:,None]
 return mask
def add(n,bands,custom=None):
 global sources
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');gb=g['globalNativeBox'];x=gb[0]-origin[0];y=gb[1]-origin[1];src=np.asarray(Image.open(p).convert('RGB'));old=a[y:y+1254,x:x+1254]
 mask=ring(old,src,bands)
 if custom:mask=custom(mask,src,old)
 ks=[s['sourceId'] for s in sources if s['file']==str(p)]
 k=ks[0] if ks else max(s['sourceId'] for s in sources)+1
 if not ks:sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':gb,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None})
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=k;Image.fromarray(mask.astype(np.uint8)*255).save(D/(n+'.hard-mask.png'))
 return {'id':n,'sourceId':k,'pixels':int(mask.sum())}
def main():
 changes=[]
 changes.append(add('r02_c04_rail_span_right_v02',(180,70,70,160)))
 changes.append(add('r02_c04_paving_south_west_v02',(300,180,300,400)))
 changes.append(add('r02_c04_paving_south_mid_v02',(250,120,250,120)))
 def greenonly(mask,src,old):
  return mask & (src[:,:,1].astype(float)>src[:,:,2]*1.3) & (src[:,:,1].astype(float)>src[:,:,0]*.87) & (old[:,:,1].astype(float)>old[:,:,2]*1.3) & (old[:,:,1].astype(float)>old[:,:,0]*.87)
 # The complete-span native now covers this foliage; do not isolate individual leaves by RGB.
 changes.append(add('r02_c04_foliage_left_v01',(180,180,180,180)))
 changes.append(add('r02_c04_foliage_right_upper_v01',(160,160,160,160)))
 changes.append(add('r02_c04_foliage_right_lower_v01',(160,160,160,160)))
 changes.append(add('r02_c04_rail_post_full_anchor_v01',(130,70,70,80)))
 changes.append(add('r02_c04_west_fence_span_v01',(190,180,170,220),lambda z,s,o: z & (np.indices(z.shape)[0]<(.58*np.indices(z.shape)[1]+450)) & (np.indices(z.shape)[0]>(.48*np.indices(z.shape)[1]+120)) & (np.indices(z.shape)[1]>115)))
 def flooronly(mask,src,old):
  yy,xx=np.indices(mask.shape);miny=np.where(xx<570,.65*xx+210,np.where(xx<810,800,.5*(xx-810)+750));cost=np.abs(src.astype(float)-old.astype(float)).mean(2)+.01;cost[(yy<miny)|(yy>miny+145)]=1e8;curve=path(cost,step=10);return mask & (yy>=curve)
 changes.append(add('r02_c04_hedge_post_foot_v01',(50,80,100,70),flooronly))
 # Preserve the complete native post shaft/cap/foot after adjacent rail repairs.
 p=W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png';src=np.asarray(Image.open(p));sid=next(s['sourceId'] for s in sources if s['sha256']==sha(p));yy,xx=np.indices((1254,1254));z=src.astype(float);wood=(z[:,:,0]>z[:,:,1]+22)&(z[:,:,1]>z[:,:,2]+13);body=(xx>=574)&(xx<=798)&(yy>=197)&(yy<=1155);cap=(((xx-683)/119)**2+((yy-163)/83)**2<=1);mask=wood&(body|cap);x=15245-origin[0];y=7453-origin[1];a[y:y+1254,x:x+1254][mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=sid;Image.fromarray(mask.astype(np.uint8)*255).save(D/'whole-post-wood-exact.mask.png')
 Image.fromarray(a).save(D/'joint.context.png');Image.fromarray(ids).save(D/'joint.source-id.png');m.update(file=str(D/'joint.context.png'),sourceIdMap=str(D/'joint.source-id.png'),sources=sources,patches=changes,previousAssembly=str(W/'joint-stage/joint.assembly.json'));write(D/'joint.assembly.json',m)
 for n,b in [('foliage-left-v01',[12750,4700,14004,5954]),('foliage-right-upper-v01',[14650,4700,15904,5954]),('foliage-right-lower-v01',[14650,5750,15904,7004])]:
  pass # Keep generation-reference target bytes immutable.
 for n,b in [('south-west',[12288,7700,13542,8954]),('south-middle',[13288,7700,14542,8954]),('south-east',[14500,7800,15754,9054]),('post-east',[15245,7453,16499,8707])]:
  Image.fromarray(a).crop((b[0]-origin[0],b[1]-origin[1],b[2]-origin[0],b[3]-origin[1])).save(W/'qa'/(n+'.v2.100pct.png'))
 Image.fromarray(a[115:4211,115:4211]).resize((1024,1024),Image.Resampling.LANCZOS).save(W/'qa/r02_c04.joint-v2.preview-only.png')
 print(json.dumps(changes))
if __name__=='__main__':main()

