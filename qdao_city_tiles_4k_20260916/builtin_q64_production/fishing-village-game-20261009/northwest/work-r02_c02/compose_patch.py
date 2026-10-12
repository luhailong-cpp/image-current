from production import *
from datetime import datetime,timezone
from PIL import ImageFilter
def minpath(cost):
 h,w=cost.shape;prev=cost[0].copy();back=np.zeros((h,w),np.int8);inf=1e30;offsets=np.array([0,-1,1,-2,2,-3,3,-4,4,-5,5],np.int8)
 for y in range(1,h):
  vals=[]
  for d in offsets:
   v=np.roll(prev,-int(d));v[:max(0,-int(d))]=inf
   if d>0:v[-int(d):]=inf
   vals.append(v)
  vals=np.stack(vals);z=np.argmin(vals,axis=0);back[y]=offsets[z];prev=cost[y]+vals[z,np.arange(w)]
 line=np.empty(h,int);line[-1]=np.argmin(prev)
 for y in range(h-1,0,-1):line[y-1]=line[y]+back[y,line[y]]
 return line
def hard_region(src,old,bands):
 cost=np.mean((src.astype(float)-old.astype(float))**2,axis=2)+0.05
 # Selection cost only: favor contours agreeing across a local neighborhood.
 edge=lambda q:(q.min(axis=2)<155)&((q.max(axis=2).astype(int)-q.min(axis=2).astype(int))>45)
 mismatch=(edge(src)!=edge(old)).astype(np.uint8)*255;near=np.asarray(Image.fromarray(mismatch).filter(ImageFilter.MaxFilter(17)));cost+=near.astype(float)*500
 cost=np.asarray(Image.fromarray(cost.astype(np.float32)).filter(ImageFilter.BoxBlur(5))) if False else cost
 yy,xx=np.indices(cost.shape);t,b,l,r=bands
 def vertical(band):
  z=cost.copy();z[(xx<band[0])|(xx>band[1])]=1e20;return minpath(z)
 def horizontal(band):
  z=cost.copy();z[(yy<band[0])|(yy>band[1])]=1e20;return minpath(z.T)
 top=horizontal(t);bot=horizontal(b);left=vertical(l);right=vertical(r);return (yy>=top[None,:])&(yy<=bot[None,:])&(xx>=left[:,None])&(xx<=right[:,None])
def proof(rgb,ids,sources,origin,path):
 assert not (ids==0).any();rows=[]
 for k in np.unique(ids):
  z={s['sourceId']:s for s in sources}[int(k)];assert sha(z['file'])==z['sha256'];im=np.asarray(Image.open(z['file']).convert('RGB'));yy,xx=np.nonzero(ids==k);sx=xx+origin[0]-z['globalNativeBox'][0];sy=yy+origin[1]-z['globalNativeBox'][1];valid=(sx>=0)&(sx<1254)&(sy>=0)&(sy<1254);assert valid.all();mis=int(np.any(rgb[yy,xx]!=im[sy,sx],axis=1).sum());assert mis==0;rows.append({'sourceId':int(k),'pixels':int(len(xx)),'mismatches':0,'sha256':sha(z['file'])})
 j={'pixels':int(ids.size),'mismatches':0,'uncovered':0,'invalidCoordinates':0,'contributions':rows,'nativeScaleResampled':False,'feathered':False,'painted':False};write(path,j);return j
def compose(base,out,n,bands):
 D=W/out;D.mkdir(exist_ok=True);assert not (D/'r02_c02.candidate.png').exists();bm=read(W/base/'full.assembly.json');a=np.asarray(Image.open(bm['candidate']['file']).convert('RGB')).copy();ids=np.asarray(Image.open(bm['sourceIdMap']['file'])).copy();s=bm['sources'].copy();p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');src=np.asarray(Image.open(p).convert('RGB'));b=g['globalNativeBox'];x=b[0]-3981;y=b[1]-3981;old=a[y:y+1254,x:x+1254];mask=hard_region(src,old,bands);gy,gx=np.indices(mask.shape);mask&=(gx+b[0]>=4096)&(gx+b[0]<8192)&(gy+b[1]>=4096)&(gy+b[1]<8192);k=max(z['sourceId'] for z in s)+1;old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=k;s.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None,'nativeScaleResampled':False});mp=D/(n+'.hard-mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp)
 patch={'name':n,'sourceId':k,'globalNativeBox':b,'hardMask':str(mp),'hardMaskSha256':sha(mp),'pixels':int(mask.sum()),'bands':bands,'resampled':False,'feathered':False,'painted':False};Image.fromarray(old).save(D/(n+'.composed.100pct.png'));Image.fromarray(a).save(D/'full-context.png');Image.fromarray(ids).save(D/'full-source-id.png');pr=proof(a,ids,s,[3981,3981],D/'full-source-proof.json');tile=a[115:4211,115:4211];ti=ids[115:4211,115:4211];Image.fromarray(tile).save(D/'r02_c02.candidate.png');Image.fromarray(ti).save(D/'r02_c02.source-id.png');tpr=proof(tile,ti,s,[4096,4096],D/'r02_c02.source-proof.json')
 im0=np.asarray(Image.open(bm['candidate']['file']).convert('RGB'));outside=np.ones(ids.shape,bool);outside[115:4211,115:4211]=False;assert np.array_equal(a[outside],im0[outside])
 common={**bm,'sources':s,'seams':bm.get('seams',[]),'patches':bm.get('patches',[])+[patch],'baseAssembly':{'file':str(W/base/'full.assembly.json'),'sha256':sha(W/base/'full.assembly.json')},'candidate':{'file':str(D/'full-context.png'),'sha256':sha(D/'full-context.png')},'sourceIdMap':{'file':str(D/'full-source-id.png'),'sha256':sha(D/'full-source-id.png')},'proof':{'file':str(D/'full-source-proof.json'),'sha256':sha(D/'full-source-proof.json'),'pixels':pr['pixels'],'mismatches':0},'status':'native-patch-candidate-awaiting-visual-review','createdAtUtc':datetime.now(timezone.utc).isoformat(),'outsideOwnCoreChangedPixels':0};write(D/'full.assembly.json',common)
 tm={**read(W/base/'r02_c02.assembly.json'),'sources':s,'patches':common['patches'],'candidate':{'file':str(D/'r02_c02.candidate.png'),'sha256':sha(D/'r02_c02.candidate.png')},'sourceIdMap':{'file':str(D/'r02_c02.source-id.png'),'sha256':sha(D/'r02_c02.source-id.png')},'proof':{'file':str(D/'r02_c02.source-proof.json'),'sha256':sha(D/'r02_c02.source-proof.json'),'pixels':tpr['pixels'],'mismatches':0},'fullAssembly':{'file':str(D/'full.assembly.json'),'sha256':sha(D/'full.assembly.json'),'crop':[115,115,4211,4211]},'status':common['status']};write(D/'r02_c02.assembly.json',tm);print(json.dumps({'candidate':tm['candidate'],'patchPixels':patch['pixels'],'proofPixels':tpr['pixels'],'mismatches':0,'outsideOwnCoreChangedPixels':0}))
if __name__=='__main__':compose(sys.argv[1],sys.argv[2],sys.argv[3],json.loads(sys.argv[4]))
