from edge_patch import *
from boxes_patch import boxes_patch
def blue_patch(a,ids,sources,n,key,D,domain=None):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];blue=lambda z:(z[:,:,2].astype(int)>z[:,:,0].astype(int)+25)&(z[:,:,2].astype(int)>z[:,:,1].astype(int)+2)
 mask=blue(old)|blue(src)
 # Include the whole ceramic object's original and repaired silhouette, including small adjacent shadow.
 mask=np.asarray(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9)))>0
 if domain:
  yy,xx=np.indices(mask.shape);l,t,r,bo=domain;mask&=(xx>=l)&(xx<r)&(yy>=t)&(yy<bo)
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key;sources[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 mp=D/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);write(D/(n+'.mask.json'),{'sourceId':key,'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'method':'whole blue ceramic union object mask expanded4 native pixels; no RGB modification'})
 Image.fromarray(old).save(D/(n+'.result.png'))
if __name__=='__main__':
 D=W/'converge-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('edge-v1')
 edge_patch(a,i,s,'r02_c03_paving_connector_a_v03',115,D,(330,520,680,665),31)
 edge_patch(a,i,s,'r02_c03_paving_connector_b_v03',116,D,(400,515,720,660),31)
 patch(a,i,s,'r02_c03_rail_continuity_v01',103,top=(0,150),bottom=(1220,1253),left=(0,100),right=(1200,1253),out=D)
 blue_patch(a,i,s,'r02_c03_blue_ridge_v01',108,D)
 blue_patch(a,i,s,'r02_r03_roof_phase_left_v01',101,D)
 blue_patch(a,i,s,'r02_r03_roof_phase_right_v01',102,D)
 finish(D,a,i,s)
 im=Image.fromarray(a)
 for j in range(4):im.crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(D/('south-'+str(j+1)+'.png'))

