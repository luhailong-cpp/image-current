from pathlib import Path
import json, importlib.util
import numpy as np
from PIL import Image
from repair import Q,W,R,read,write,sha,base,BOXES

ns=base(); m=ns['m']; pair=ns['pair']; pid=ns['ids'];
eastfile=R/'tiles/r03_c03.candidate-repair-v5.png'; eastid=R/'tiles/r03_c03.source-id-repair-v5.png'; em=read(R/'tiles/r03_c03.repair-v5.assembly.json')
east=np.array(Image.open(eastfile).convert('RGB')); ei=np.array(Image.open(eastid)); pair[:,4096:]=east;pid[:,4096:]=ei+50
sources={s['sourceId']:{'file':s['file'],'globalNativeBox':[8192+v for v in s['nativeBox']],'sha256':s['sha256']}for s in em['sources']}
up=R/'native/r03_c03_e3_door_u_v01.png';lo=R/'native/r03_c03_e3_door_l_v01.png';u=np.array(Image.open(up).convert('RGB'));l=np.array(Image.open(lo).convert('RGB'))
for sid,p in [(201,up),(202,lo)]:
    r=read(str(p)+'.generation.json');assert sha(p)==r['sha256'];sources[sid]={'file':str(p),'globalNativeBox':r['globalNativeBox'],'sha256':r['sha256'],'generationRecord':str(p)+'.generation.json'}
g,gi,mid=m.append_hard(u.transpose(1,0,2),np.full((1254,1254),201,np.uint8).T,l.transpose(1,0,2),np.full((1254,1254),202,np.uint8).T,'upper-lower-true230')
g=g.transpose(1,0,2);gi=gi.T
Image.fromarray(g).save(Q/'door-group.true230.png');Image.fromarray(gi).save(Q/'door-group.true230.source-id.png')
x,y=7408-4096,8781-8192;old=pair[y:y+2278,x:x+1254].copy()
L,lc=m.minimum_vertical_seam(old[:,:115],g[:,:115]);RR,rc=m.minimum_vertical_seam(g[:,1139:],old[:,1139:]);RR+=1139
T,tc=m.minimum_vertical_seam(old[:115].transpose(1,0,2),g[:115].transpose(1,0,2))
B,bc=m.minimum_vertical_seam(g[2163:].transpose(1,0,2),old[2163:].transpose(1,0,2));B+=2163
ys=np.arange(2278)[:,None];xs=np.arange(1254)[None,:];mask=(xs>=L[:,None])&(xs<RR[:,None])&(ys>=T[None,:])&(ys<B[None,:])
assert mask[115:2163,115:1139].all()
pair[y:y+2278,x:x+1254]=np.where(mask[...,None],g,old);pid[y:y+2278,x:x+1254]=np.where(mask,gi,pid[y:y+2278,x:x+1254])
proposal=pair[:,4096:].copy();pids=pid[:,4096:].copy();pids=np.where(pids>=201,pids,pids-50).astype(np.uint8)
pf=Q/'r03_c03.e3-proposal-v01.png';sf=Q/'r03_c03.e3-proposal-v01.source-id.png';Image.fromarray(proposal).save(pf);Image.fromarray(pids).save(sf)
assert np.array_equal(proposal[pids<201],east[pids<201])
verified=[]
for sid in np.unique(pids):
    s=sources[int(sid)];p=Path(s['file']);assert sha(p)==s['sha256'];a=np.array(Image.open(p).convert('RGB'));yy,xx=np.nonzero(pids==sid);b=s['globalNativeBox'];assert np.array_equal(proposal[yy,xx],a[yy+8192-b[1],xx+8192-b[0]]);verified.append({'sourceId':int(sid),'pixels':len(xx)})
Image.fromarray(pair[y-200:y+2478,x-200:x+1454]).save(Q/'door-group.integrated-context.png')
Image.fromarray(pid[y-200:y+2478,x-200:x+1454]).save(Q/'door-group.integrated-context.source-id.png')
crops={'upper-lower-full230':[7408,9705,8662,10135],'north':[7208,8681,8862,9011],'south':[7208,10829,8862,11159],'E3-before-location':[8140,10000,8580,10400]}
for side,cx in [('west',7408),('east',8662)]:
    for j in range(3):crops[f'{side}-{j+1}']=[cx-180,8781+j*760,cx+180,min(11059,8781+(j+1)*760)]
for name,b in crops.items():
    p=Q/f'qa-{name}.100pct.png';Image.fromarray(pair[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096]).save(p)
cuts={'method':'upper/lower true230 DP hardcut then 4 outer115 DP halos, entire1024x2048 group core protected; no feather,rescale,warp or color edits','globalNativeGroupBox':[7408,8781,8662,11059],'globalCoreGroupBox':[7523,8896,8547,10944],'upperLowerCut':mid,'outerCut':{'leftXByY':L.tolist(),'rightXByY':RR.tolist(),'topYByX':T.tolist(),'bottomYByX':B.tolist()},'maskGlobalOrigin':[7408,8781]}
write(Q/'e3-cuts.json',cuts)
out={'status':'proposal-pending-full-native-visual-review','tile':'r03_c03','formalAccepted':False,'sharedFilesUpdated':False,'base':{'file':str(eastfile),'sha256':sha(eastfile),'sourceIdFile':str(eastid),'sourceIdSHA256':sha(eastid),'assembly':str(R/'tiles/r03_c03.repair-v5.assembly.json')},'candidate':{'file':str(pf),'sha256':sha(pf),'size':[4096,4096],'globalCoreBox':[8192,8192,12288,12288]},'sourceIdFile':str(sf),'sourceIdSHA256':sha(sf),'sources':sources,'contributions':verified,'nativePixelsVerified':16777216,'mismatchedPixels':0,'untouchedBasePixelsEqual':True,'newNativeSourceIds':[201,202],'cuts':{'file':str(Q/'e3-cuts.json'),'sha256':sha(Q/'e3-cuts.json')},'crops':{k:{'file':str(Q/f'qa-{k}.100pct.png'),'globalBox':b}for k,b in crops.items()},'crossTileContext':{'file':str(Q/'door-group.integrated-context.png'),'globalBox':[7208,8581,8862,11259],'note':'Diagnostic with existing west tile/roof context, current east v5 and same native repair group. Shared west tile is not overwritten.'},'visualQA':'pending'}
write(Q/'e3-proposal-v01.assembly.json',out);print(json.dumps({'candidate':out['candidate'],'nativePixelsVerified':16777216,'newPixels':sum(z['pixels']for z in verified if z['sourceId']>=201)}))
