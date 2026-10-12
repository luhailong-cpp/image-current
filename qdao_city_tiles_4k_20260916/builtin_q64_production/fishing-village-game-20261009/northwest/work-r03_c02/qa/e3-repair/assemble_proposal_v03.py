from pathlib import Path
import numpy as np
from PIL import Image
from repair import Q,W,R,read,write,sha,base
ns=base();m=ns['m'];pair=ns['pair'];pid=ns['ids'];contextbase=pair.copy();contextids=pid.copy()
ef=R/'tiles/r03_c03.candidate-repair-v5.png';eif=R/'tiles/r03_c03.source-id-repair-v5.png';em=read(R/'tiles/r03_c03.repair-v5.assembly.json')
east=np.array(Image.open(ef).convert('RGB'));ei=np.array(Image.open(eif));pair[:,4096:]=east;pid[:,4096:]=ei+50
sources={s['sourceId']:{'file':s['file'],'sha256':s['sha256'],'globalNativeBox':[8192+v for v in s['nativeBox']]}for s in em['sources']}
p=R/'native/r03_c03_e3_door_l_v02.png';r=read(str(p)+'.generation.json');a=np.array(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3) and sha(p)==r['sha256'];sources[203]={'file':str(p),'sha256':r['sha256'],'globalNativeBox':r['globalNativeBox'],'generationRecord':str(p)+'.generation.json'}
x,y=7408-4096,9805-8192;old=pair[y:y+1254,x:x+1254].copy()
L,lc=m.minimum_vertical_seam(old[:,:115],a[:,:115]);RR,rc=m.minimum_vertical_seam(a[:,1139:],old[:,1139:]);RR+=1139
T,tc=m.minimum_vertical_seam(old[:230].transpose(1,0,2),a[:230].transpose(1,0,2));B,bc=m.minimum_vertical_seam(a[1139:].transpose(1,0,2),old[1139:].transpose(1,0,2));B+=1139
ys=np.arange(1254)[:,None];xs=np.arange(1254)[None,:];mask=(xs>=L[:,None])&(xs<RR[:,None])&(ys>=T[None,:])&(ys<B[None,:]);assert mask[230:1139,115:1139].all()
pair[y:y+1254,x:x+1254]=np.where(mask[...,None],a,old);pid[y:y+1254,x:x+1254]=np.where(mask,203,pid[y:y+1254,x:x+1254])
proposal=pair[:,4096:].copy();pi=pid[:,4096:];pi=np.where(pi==203,pi,pi-50).astype(np.uint8)
pf=Q/'r03_c03.e3-proposal-v03.png';sf=Q/'r03_c03.e3-proposal-v03.source-id.png';Image.fromarray(proposal).save(pf);Image.fromarray(pi).save(sf)
assert np.array_equal(proposal[pi!=203],east[pi!=203]);assert np.array_equal(proposal[:9805-8192],east[:9805-8192])
verified=[]
for sid in np.unique(pi):
 s=sources[int(sid)];f=Path(s['file']);assert sha(f)==s['sha256'];src=np.array(Image.open(f).convert('RGB'));yy,xx=np.nonzero(pi==sid);b=s['globalNativeBox'];assert np.array_equal(proposal[yy,xx],src[yy+8192-b[1],xx+8192-b[0]]);verified.append({'sourceId':int(sid),'pixels':len(xx)})
ctx=contextbase.copy();ci=contextids.copy();cm=(pid==203);ctx[cm]=pair[cm];ci[cm]=203
cb=[7208,8581,8862,11259];Image.fromarray(ctx[cb[1]-8192:cb[3]-8192,cb[0]-4096:cb[2]-4096]).save(Q/'door-group.integrated-context-v03.png');Image.fromarray(ci[cb[1]-8192:cb[3]-8192,cb[0]-4096:cb[2]-4096]).save(Q/'door-group.integrated-context-v03.source-id.png')
crops={'north-full230':[7208,9705,8862,10135],'south':[7208,10829,8862,11159],'E3':[8140,10000,8580,10400],'west-1':[7228,9805,7588,10432],'west-2':[7228,10432,7588,11059],'east-1':[8482,9805,8842,10432],'east-2':[8482,10432,8842,11059],'tile-west-join':[7992,9705,8392,11159]}
for name,b in crops.items():Image.fromarray(pair[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096]).save(Q/f'qa-v03-{name}.100pct.png')
cuts={'method':'Full existing upper doorway retained; lower native whole-object section enters via actual old/new230 north overlap9805..10035.115 side/bottom DP hardcut, no blend or resampling. Protected central rectangle includes entire E3.','globalNativeBox':[7408,9805,8662,11059],'globalCoreBox':[7523,9920,8547,10944],'integrationProtectedBox':[7523,10035,8547,10944],'northOverlapBox':[7408,9805,8662,10035],'leftXByY':L.tolist(),'rightXByY':RR.tolist(),'topYByX':T.tolist(),'bottomYByX':B.tolist()}
cf=Q/'e3-cuts-v03.json';write(cf,cuts)
out={'status':'proposal-pending-native-review','tile':'r03_c03','formalAccepted':False,'sharedFilesUpdated':False,'base':{'file':str(ef),'sha256':sha(ef),'sourceIdFile':str(eif),'sourceIdSHA256':sha(eif),'assembly':str(R/'tiles/r03_c03.repair-v5.assembly.json')},'candidate':{'file':str(pf),'sha256':sha(pf),'size':[4096,4096],'globalCoreBox':[8192,8192,12288,12288]},'sourceIdFile':str(sf),'sourceIdSHA256':sha(sf),'sources':sources,'contributions':verified,'nativePixelsVerified':16777216,'mismatchedPixels':0,'untouchedBasePixelsEqual':True,'allPixelsNorthOf9805Unchanged':True,'newNativeSourceIds':[203],'notSelectedNewImages':['r03_c03_e3_door_u_v01','r03_c03_e3_door_l_v01'],'cuts':{'file':str(cf),'sha256':sha(cf)},'crops':{k:{'file':str(Q/f'qa-v03-{k}.100pct.png'),'globalBox':v}for k,v in crops.items()},'crossTileContext':{'file':str(Q/'door-group.integrated-context-v03.png'),'globalBox':cb,'note':'Mechanical diagnostic retains root-approved roof bridge and west context outside repair; actual east tile proposal remains exactly v5 outside source203 mask.'},'visualQA':'pending'}
write(Q/'e3-proposal-v03.assembly.json',out);print({'candidate':out['candidate'],'nativePixelsVerified':16777216,'newPixels':sum(s['pixels']for s in verified if s['sourceId']==203)})
