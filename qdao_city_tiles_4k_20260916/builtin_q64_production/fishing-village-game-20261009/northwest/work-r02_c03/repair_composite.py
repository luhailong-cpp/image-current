from production import *
sys.path.insert(0,str(B))
from apply_r03_c03_repairs import minimum_path
from PIL import ImageFilter
def patch(a,ids,sources,n,key,top=(0,180),bottom=(1074,1254),left=(0,180),right=(1074,1254),mode='all',out=None):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');s={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 b=s['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];assert old.shape==src.shape
 cost=np.sum((old.astype(np.int32)-src.astype(np.int32))**2,axis=2,dtype=np.int64)+1
 edge=lambda q:((q.min(axis=2)<175)&((q.max(axis=2).astype(int)-q.min(axis=2).astype(int))<90))
 mismatch=(edge(old)!=edge(src)).astype(np.uint8)*255
 proximity=np.asarray(Image.fromarray(mismatch).filter(ImageFilter.MaxFilter(13)))
 cost=cost+proximity.astype(np.int64)*300
 # Wider local error guides hard source selection only; RGB pixels are never filtered.
 lc,_=minimum_path(cost,left[0],min(1253,left[1]));rc,_=minimum_path(cost,right[0],min(1253,right[1]));tc,_=minimum_path(cost.T,top[0],min(1253,top[1]));bc,_=minimum_path(cost.T,bottom[0],min(1253,bottom[1]));yy,xx=np.indices(cost.shape);mask=(xx>=lc[:,None])&(xx<rc[:,None])&(yy>=tc[None,:])&(yy<bc[None,:])
 if mode=='blue':
  blue=lambda im:(im[:,:,2].astype(int)>im[:,:,0].astype(int)+25)&(im[:,:,2].astype(int)>im[:,:,1].astype(int)+2)
  mask&=(blue(old)|blue(src))
 if mode=='roof':
  blue=lambda im:(im[:,:,2].astype(int)>im[:,:,0].astype(int)+25)&(im[:,:,2].astype(int)>im[:,:,1].astype(int)+2)
  bl=blue(old)|blue(src);lo=np.where(bl,yy,1254).min(axis=0);hi=np.where(bl,yy,-1).max(axis=0);mask&=(yy>=lo[None,:])&(yy<=hi[None,:]+8)
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key;sources[str(key)]=s
 if out:
  mp=out/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);write(out/(n+'.mask.json'),{'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'sourceId':key,'mode':mode,'margins':{'left':left,'right':right,'top':top,'bottom':bottom}})
  for side,bb in [('north',[x,y-100,x+1254,y+280]),('south',[x,y+974,x+1254,y+1354]),('west',[x-100,y,x+280,y+1254]),('east',[x+974,y,x+1354,y+1254])]:
   bb=[max(0,bb[0]),max(0,bb[1]),min(a.shape[1],bb[2]),min(a.shape[0],bb[3])];Image.fromarray(a).crop(bb).save(out/(n+'.'+side+'.png'))
  Image.fromarray(old).save(out/(n+'.result.png'))
 return mask
def finish(D,a,ids,sources):
 D.mkdir(exist_ok=True);p=D/'full-pair.png';ip=D/'source-id.png';Image.fromarray(a).save(p);Image.fromarray(ids).save(ip);checks=[]
 for k in np.unique(ids):
  s=sources[str(k)];src=np.asarray(Image.open(s['file']));yy,xx=np.nonzero(ids==k);b=s['globalNativeBox'];sx=xx+8077-b[0];sy=yy+3981-b[1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(a[yy,xx],src[sy,sx]);checks.append({'sourceId':int(k),'pixels':int(len(yy)),'mismatches':0})
 tile=Image.fromarray(a[115:4211,115:4211]);tile.save(D/'r02_c03.candidate.png');Image.fromarray(ids[115:4211,115:4211]).save(D/'r02_c03.source-id.png')
 write(D/'assembly.json',{'globalBox':[8077,3981,12403,9331],'candidate':{'file':str(p),'sha256':sha(p)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'proof':{'pixels':int(ids.size),'mismatches':0,'contributions':checks},'status':'candidate-pending-full-visual-review','formalAccepted':False})
 preview=tile.copy();preview.thumbnail((1536,1536),Image.Resampling.LANCZOS);preview.save(D/'overview-preview-only.png');print(json.dumps({'pixels':int(ids.size),'mismatches':0,'sources':len(checks),'candidate':str(D/'r02_c03.candidate.png')}))
def loadbase(d):
 m=read(W/d/'assembly.json');return np.asarray(Image.open(m['candidate']['file'])).copy(),np.asarray(Image.open(m['sourceIdMap']['file'])).copy(),m['sources'].copy()
if __name__=='__main__':
 D=W/'repairs-v1';D.mkdir(exist_ok=True);a,ids,sources=loadbase('base-v1')
 patch(a,ids,sources,'r02_r03_roof_phase_left_v01',101,left=(115,230),right=(1100,1254),mode='blue',out=D)
 patch(a,ids,sources,'r02_r03_roof_phase_right_v01',102,left=(0,230),right=(1120,1254),mode='blue',out=D)
 finish(D,a,ids,sources)

