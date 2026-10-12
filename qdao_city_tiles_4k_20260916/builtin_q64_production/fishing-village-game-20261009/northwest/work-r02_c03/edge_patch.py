from repair_composite import *
def edge_patch(a,ids,sources,n,key,D,domain=(0,0,1254,1254),radius=21):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];f=old.astype(int);z=src.astype(int)
 grout=lambda q:(q[:,:,0]-q[:,:,2]>7)&(q[:,:,0]-q[:,:,1]>1)&(q[:,:,0]<243)&(q[:,:,1]>65)&(q.max(axis=2)-q.min(axis=2)<95)
 geom=grout(f)|grout(z);mask=np.asarray(Image.fromarray(geom.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(radius)))>0;yy,xx=np.indices(mask.shape);l,t,r,bo=domain;mask&=(xx>=l)&(xx<r)&(yy>=t)&(yy<bo)
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key;sources[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 mp=D/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(old).save(D/(n+'.result.png'));write(D/(n+'.mask.json'),{'sourceId':key,'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'domain':domain,'method':'hard native geometry pixel selection around both old and corrected grout; no blend or RGB synthesis'})
if __name__=='__main__':
 D=W/'edge-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
 edge_patch(a,i,s,'r02_c03_paving_precise_a_v02',111,D,(0,420,1254,1000),31)
 edge_patch(a,i,s,'r02_c03_paving_precise_b_v02',112,D,(0,370,1254,900),31)
 edge_patch(a,i,s,'r02_c03_paving_precise_c_v02',113,D,(0,350,1254,980),31)
 edge_patch(a,i,s,'r02_c03_paving_precise_d_v02',114,D,(0,440,1254,980),31)
 finish(D,a,i,s)

