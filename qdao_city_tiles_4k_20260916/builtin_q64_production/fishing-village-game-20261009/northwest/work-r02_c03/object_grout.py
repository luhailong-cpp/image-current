from repair_composite import *
def dpwide(cost,step=4):
 h,w=cost.shape;prev=cost[0].copy();back=np.zeros((h,w),np.int8);INF=1e18;offsets=list(range(-step,step+1));offsets.sort(key=abs)
 for y in range(1,h):
  opts=np.full((len(offsets),w),INF)
  for k,o in enumerate(offsets):
   if o>=0:opts[k,:w-o]=prev[o:]+abs(o)*0.1
   else:opts[k,-o:]=prev[:w+o]+abs(o)*0.1
  choice=np.argmin(opts,axis=0);back[y]=np.asarray(offsets)[choice];prev=cost[y]+opts[choice,np.arange(w)]
 path=np.zeros(h,np.int32);path[-1]=np.argmin(prev)
 for y in range(h-1,0,-1):path[y-1]=path[y]+back[y,path[y]]
 return path
def groutmask(src,old,bands):
 z=src.astype(float);r,g,b=z[:,:,0],z[:,:,1],z[:,:,2]
 isgrout=(r-b>10)&(r-g>2)&(r<235)&(g>65)
 # The source-boundary path runs on a complete new-source grout network.
 good=np.asarray(Image.fromarray(isgrout.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
 cost=np.where(good,1.,1000.)+np.sum((z-old.astype(float))**2,axis=2)*0.00002
 yy,xx=np.indices(good.shape)
 paths=[]
 for domain,trans in [(bands[0],True),(bands[1],True),(bands[2],False),(bands[3],False)]:
  lo,hi=domain;cc=cost.T if trans else cost
  p=dpwide(cc[:,lo:hi+1])+lo;paths.append(p)
 t,bo,l,ri=paths
 # Include two native pixels beyond the grout centerline to retain each whole edge.
 return (yy>=t[None,:]-2)&(yy<=bo[None,:]+2)&(xx>=l[:,None]-2)&(xx<=ri[:,None]+2)
def object_patch(a,ids,sources,n,key,bands,D):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];mask=groutmask(src,old,bands);old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key
 sources[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 mp=D/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(old).save(D/(n+'.result.png'));write(D/(n+'.mask.json'),{'sourceId':key,'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'sourceSelectionOnly':True,'method':'native grout object boundary, no RGB alteration','bands':bands})
if __name__=='__main__':
 D=W/'grout-test';D.mkdir(exist_ok=True);a,i,s=loadbase('internal-v1')
 # Start independently of prior paving patches.
 aa,ii,ss=loadbase('base-v1');a=aa;i=ii;s=ss
 object_patch(a,i,s,'r02_c03_paving_join_a_v01',104,[(150,460),(870,1253),(0,80),(1000,1253)],D)
 object_patch(a,i,s,'r02_c03_paving_join_b_v01',105,[(20,320),(920,1253),(0,80),(1000,1253)],D)
 finish(D,a,i,s)

