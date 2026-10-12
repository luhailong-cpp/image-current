from pathlib import Path
import json, importlib.util
import numpy as np
from PIL import Image
from repair import Q,W,R,read,write,sha,base,BOXES

ns=base(); m=ns['m']; pair=ns['pair']; pid=ns['ids'];
eastfile=R/'tiles/r03_c03.candidate-repair-v5.png'; eastid=R/'tiles/r03_c03.source-id-repair-v5.png'; em=read(R/'tiles/r03_c03.repair-v5.assembly.json')
contextbase=pair.copy();contextids=pid.copy()
east=np.array(Image.open(eastfile).convert('RGB')); ei=np.array(Image.open(eastid)); pair[:,4096:]=east;pid[:,4096:]=ei+50
sources={s['sourceId']:{'file':s['file'],'globalNativeBox':[8192+v for v in s['nativeBox']],'sha256':s['sha256']}for s in em['sources']}
up=R/'native/r03_c03_e3_door_u_v01.png';lo=R/'native/r03_c03_e3_door_l_v01.png';u=np.array(Image.open(up).convert('RGB'));l=np.array(Image.open(lo).convert('RGB'))
for sid,p in [(201,up),(202,lo)]:
    r=read(str(p)+'.generation.json');assert sha(p)==r['sha256'];sources[sid]={'file':str(p),'globalNativeBox':r['globalNativeBox'],'sha256':r['sha256'],'generationRecord':str(p)+'.generation.json'}
g,gi,mid=m.append_hard(u.transpose(1,0,2),np.full((1254,1254),201,np.uint8).T,l.transpose(1,0,2),np.full((1254,1254),202,np.uint8).T,'upper-lower-true230')
g=g.transpose(1,0,2);gi=gi.T
Image.fromarray(g).save(Q/'door-group.true230.png');Image.fromarray(gi).save(Q/'door-group.true230.source-id.png')
x,y=7408-4096,8781-8192;old=pair[y:y+2278,x:x+1254].copy()
# Existing physical timber joints define selection; every selected pixel remains native.
# Complete lower right plank pair and complete right post are repaired, with lamp/roof left from v5.
def curved_cut(x0,x1,points,radius):
 xx=np.arange(x0,x1);cen=np.rint(np.interp(xx,[p[0] for p in points],[p[1] for p in points])).astype(int)
 yy=cen[:,None]+np.arange(-radius,radius+1)[None,:];lx=xx[:,None]-7408;ly=yy-8781
 off,cost=m.minimum_vertical_seam(old[ly,lx],g[ly,lx]);return xx,cen+off-radius,cost
px,PT,ptc=curved_cut(8192,8347,[(8192,9703),(8202,9688),(8212,9668),(8222,9643),(8232,9611),(8240,9608),(8270,9599),(8347,9575)],0)
_,PB,pbc=curved_cut(8192,8347,[(8192,10595),(8270,10578),(8347,10564)],5)
sx,ST,stc=curved_cut(8347,8575,[(8347,9167),(8360,9158),(8370,9145),(8380,9110),(8413,9107),(8416,9155),(8450,9170),(8520,9132),(8575,9097)],3)
_,SB,sbc=curved_cut(8347,8575,[(8347,10662),(8407,10685),(8435,10680),(8491,10699),(8575,10682)],12)
mask=np.zeros((2278,1254),bool)
for xx,top,bot in [(px,PT,PB),(sx,ST,SB)]:
 for gx,gt,gb in zip(xx,top,bot):mask[gt-8781:gb-8781,gx-7408]=True
# Preserve original outer post/wall geometry; actual50px wood-edge overlap.
RX,rc=m.minimum_vertical_seam(g[:,8525-7408:8575-7408],old[:,8525-7408:8575-7408]);RX+=8525-7408
mask&=(np.arange(1254)[None,:]<RX[:,None])
assert mask[10155-8781:10300-8781,8275-7408:8455-7408].all()
pair[y:y+2278,x:x+1254]=np.where(mask[...,None],g,old);pid[y:y+2278,x:x+1254]=np.where(mask,gi,pid[y:y+2278,x:x+1254])
proposal=pair[:,4096:].copy();pids=pid[:,4096:].copy();pids=np.where(pids>=201,pids,pids-50).astype(np.uint8)
pf=Q/'r03_c03.e3-proposal-v08.png';sf=Q/'r03_c03.e3-proposal-v08.source-id.png';Image.fromarray(proposal).save(pf);Image.fromarray(pids).save(sf)
assert np.array_equal(proposal[pids<201],east[pids<201])
verified=[]
for sid in np.unique(pids):
    s=sources[int(sid)];p=Path(s['file']);assert sha(p)==s['sha256'];a=np.array(Image.open(p).convert('RGB'));yy,xx=np.nonzero(pids==sid);b=s['globalNativeBox'];assert np.array_equal(proposal[yy,xx],a[yy+8192-b[1],xx+8192-b[0]]);verified.append({'sourceId':int(sid),'pixels':len(xx)})
ctx=contextbase.copy();ctxids=contextids.copy();cm=(pid>=201);ctx[cm]=pair[cm];ctxids[cm]=pid[cm]
Image.fromarray(ctx[y-200:y+2478,x-200:x+1454]).save(Q/'door-group.integrated-context-v08.png')
Image.fromarray(ctxids[y-200:y+2478,x-200:x+1454]).save(Q/'door-group.integrated-context-v08.source-id.png')
crops={'upper-lower-full230':[8192,9705,8662,10135],'door-top':[8192,9470,8420,9780],'post-top':[8290,9020,8690,9320],'west':[8170,9500,8370,10720],'east-upper':[8460,9060,8700,9920],'east-lower':[8460,9920,8700,10780],'bottom':[8210,10470,8650,10800],'E3':[8140,10000,8580,10400]}
for name,b in crops.items():
    p=Q/f'qa-v08-{name}.100pct.png';Image.fromarray(pair[b[1]-8192:b[3]-8192,b[0]-4096:b[2]-4096]).save(p)
cuts={'method':'upper/lower generated group true230 DP. Integration follows full affected plank and post structural joints, mechanically selecting native pixels only; no fixed core clip, no feather/scale/warp/color edits. Roof, lamp and other timbers remain current-v5 pixels.','nativeGroupBox':[7408,8781,8662,11059],'upperLowerCut':mid,'planks':{'x':px.tolist(),'topY':PT.tolist(),'bottomY':PB.tolist()},'post':{'x':sx.tolist(),'topY':ST.tolist(),'bottomY':SB.tolist()},'outerPostRightCutXByY':RX.tolist(),'globalOrigin':[7408,8781],'outerPostRightOverlapGlobalX':[8525,8575]}
write(Q/'e3-cuts-v08.json',cuts)
out={'status':'proposal-pending-full-native-visual-review','tile':'r03_c03','formalAccepted':False,'sharedFilesUpdated':False,'base':{'file':str(eastfile),'sha256':sha(eastfile),'sourceIdFile':str(eastid),'sourceIdSHA256':sha(eastid),'assembly':str(R/'tiles/r03_c03.repair-v5.assembly.json')},'candidate':{'file':str(pf),'sha256':sha(pf),'size':[4096,4096],'globalCoreBox':[8192,8192,12288,12288]},'sourceIdFile':str(sf),'sourceIdSHA256':sha(sf),'sources':sources,'contributions':verified,'nativePixelsVerified':16777216,'mismatchedPixels':0,'untouchedBasePixelsEqual':True,'newNativeSourceIds':[201,202],'cuts':{'file':str(Q/'e3-cuts-v08.json'),'sha256':sha(Q/'e3-cuts-v08.json')},'crops':{k:{'file':str(Q/f'qa-v08-{k}.100pct.png'),'globalBox':b}for k,b in crops.items()},'crossTileContext':{'file':str(Q/'door-group.integrated-context-v08.png'),'globalBox':[7208,8581,8862,11259],'note':'Diagnostic retains approved roof and west context; actual v5 proposal changes only complete affected right plank/post objects. Old lamp and roof preserved.'},'visualQA':'pending'}
write(Q/'e3-proposal-v08.assembly.json',out);print(json.dumps({'candidate':out['candidate'],'nativePixelsVerified':16777216,'newPixels':sum(z['pixels']for z in verified if z['sourceId']>=201)}))
