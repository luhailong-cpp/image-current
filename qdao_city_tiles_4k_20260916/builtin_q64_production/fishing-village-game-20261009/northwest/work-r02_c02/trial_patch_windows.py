from production import *
def uniform_filter(a,size):
 q=np.pad(a,size//2,mode='edge');z=np.pad(q,((1,0),(1,0))).cumsum(0).cumsum(1);return (z[size:,size:]-z[:-size,size:]-z[size:,:-size]+z[:-size,:-size])/(size*size)
from compose_patch import minpath
T=W/'patch-window-trials';T.mkdir(exist_ok=True);p=W/'native/r02_c02_internal_roof_joint_v01.png';src=np.asarray(Image.open(p).convert('RGB'));old=np.asarray(Image.open(W/'guides/r02_c02_internal_roof_joint_v01.target.png').convert('RGB'));yy,xx=np.indices(old.shape[:2]);raw=np.mean((src.astype(float)-old.astype(float))**2,axis=2)
for size in [15,41,81]:
 cost=uniform_filter(raw,size=size)*10+raw*.1
 for mode,bands in [('wide',[(0,180),(1000,1253),(0,500),(1000,1253)]),('outer',[(0,80),(1180,1253),(0,80),(1180,1253)])]:
  def v(band):
   z=cost.copy();z[(xx<band[0])|(xx>band[1])]=1e20;return minpath(z)
  def h(band):
   z=cost.copy();z[(yy<band[0])|(yy>band[1])]=1e20;return minpath(z.T)
  t,b,l,r=bands;top=h(t);bot=h(b);left=v(l);right=v(r);mask=(yy>=top[None,:])&(yy<=bot[None,:])&(xx>=left[:,None])&(xx<=right[:,None]);out=old.copy();out[mask]=src[mask];d=T/f'window-{size}-{mode}';d.mkdir(exist_ok=True);Image.fromarray(out).save(d/'composed.100pct.png');Image.fromarray(mask.astype(np.uint8)*255).save(d/'hard-mask.png');write(d/'record.json',{'native':str(p),'nativeSha256':sha(p),'target':str(W/'guides/r02_c02_internal_roof_joint_v01.target.png'),'targetSha256':sha(W/'guides/r02_c02_internal_roof_joint_v01.target.png'),'costWindow':size,'costUsedOnlyForHardSelection':True,'bands':bands,'mask':str(d/'hard-mask.png'),'maskSha256':sha(d/'hard-mask.png'),'status':'trial-unreviewed'})
 print(size)
