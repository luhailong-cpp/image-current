from repair_composite import *
from object_grout import dpwide
def smart_patch(a,ids,sources,n,key,bands,D,mode='all'):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];f=old.astype(float);z=src.astype(float)
 grout=lambda q:(q[:,:,0]-q[:,:,2]>9)&(q[:,:,0]-q[:,:,1]>2)&(q[:,:,0]<240)&(q[:,:,1]>65)
 e1,e2=grout(f),grout(z);bad=np.asarray(Image.fromarray((e1!=e2).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
 cost=np.sum((f-z)**2,axis=2)*.05+bad.astype(float)*1e7+1
 # Follow a broad hard source-selection path, avoiding unmatched geometric edges.
 paths=[]
 for domain,trans in [(bands[0],True),(bands[1],True),(bands[2],False),(bands[3],False)]:
  lo,hi=domain;cc=cost.T if trans else cost;paths.append(dpwide(cc[:,lo:hi+1],step=3)+lo)
 t,bo,l,ri=paths;yy,xx=np.indices(cost.shape);mask=(yy>=t[None,:])&(yy<bo[None,:])&(xx>=l[:,None])&(xx<ri[:,None])
 if mode=='roof':
  blue=lambda q:(q[:,:,2]>q[:,:,0]+25)&(q[:,:,2]>q[:,:,1]+2)
  bl=blue(f)|blue(z);lo=np.where(bl,yy,1254).min(axis=0);hi=np.where(bl,yy,-1).max(axis=0);mask&=(yy>=lo[None,:])&(yy<=hi[None,:]+8)
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key
 sources[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 mp=D/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(old).save(D/(n+'.result.png'));write(D/(n+'.mask.json'),{'sourceId':key,'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'sourceSelectionOnly':True,'method':'native hard seam avoids unmatched geometry; no RGB alteration','bands':bands,'mode':mode})
if __name__=='__main__':
 D=W/'smart-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
 patch(a,i,s,'r02_c03_rail_continuity_v01',103,top=(0,150),bottom=(1200,1253),left=(0,150),right=(1200,1253),out=D)
 for n,key,bands in [('paving_join_a',104,[(250,400),(800,1050),(0,115),(1000,1253)]),('paving_join_b',105,[(100,360),(900,1180),(0,115),(1000,1253)]),('paving_join_c',106,[(100,350),(900,1190),(0,300),(1000,1253)]),('paving_join_d',107,[(300,470),(900,1190),(0,300),(1000,1253)])]:
  smart_patch(a,i,s,'r02_c03_'+n+'_v01',key,bands,D)
 finish(D,a,i,s)

