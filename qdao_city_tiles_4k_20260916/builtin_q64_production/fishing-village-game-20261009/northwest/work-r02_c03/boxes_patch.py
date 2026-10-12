from repair_composite import *
def boxes_patch(a,ids,sources,n,key,boxes,D,pad=45):
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x,y=b[0]-8077,b[1]-3981;src=np.asarray(Image.open(p));old=a[y:y+1254,x:x+1254];cost=np.sum((old.astype(np.int32)-src.astype(np.int32))**2,axis=2,dtype=np.int64)+1;mask=np.zeros((1254,1254),bool)
 for box in boxes:
  l,t,r,bo=box;c=cost[t:bo,l:r];h,ww=c.shape
  lt,_=minimum_path(c,0,pad);rt,_=minimum_path(c,ww-pad-1,ww-1);tt,_=minimum_path(c.T,0,pad);bt,_=minimum_path(c.T,h-pad-1,h-1);yy,xx=np.indices(c.shape);mask[t:bo,l:r]|=(xx>=lt[:,None])&(xx<rt[:,None])&(yy>=tt[None,:])&(yy<bt[None,:])
 old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=key;sources[str(key)]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
 mp=D/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(old).save(D/(n+'.result.png'));write(D/(n+'.mask.json'),{'sourceId':key,'globalNativeBox':b,'pixels':int(mask.sum()),'file':str(mp),'sha256':sha(mp),'boxes':boxes,'padding':pad,'method':'local defect hard source selector; no final RGB modification'})
if __name__=='__main__':
 D=W/'precise-v1';D.mkdir(exist_ok=True);a,i,s=loadbase('base-v1')
 patch(a,i,s,'r02_c03_rail_continuity_v01',103,top=(0,150),bottom=(1200,1253),left=(0,150),right=(1200,1253),out=D)
 boxes_patch(a,i,s,'r02_c03_paving_precise_a_v02',111,[(140,460,470,750),(870,420,1240,840)],D)
 boxes_patch(a,i,s,'r02_c03_paving_join_a_v01',104,[(405,425,785,745)],D)
 boxes_patch(a,i,s,'r02_c03_paving_join_b_v01',105,[(350,405,780,785)],D)
 boxes_patch(a,i,s,'r02_c03_paving_precise_c_v02',113,[(110,400,475,780)],D)
 boxes_patch(a,i,s,'r02_c03_paving_precise_d_v02',114,[(520,400,850,745),(940,480,1238,850)],D)
 boxes_patch(a,i,s,'r02_c03_blue_ridge_v01',108,[(380,360,970,740)],D)
 finish(D,a,i,s)

