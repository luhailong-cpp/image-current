"""Finalize native same-coordinate south seam repair; no resize/warp/spatial filtering."""
import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=ROOT/'continuation-20261011';OLD=HERE/'merged-south-v1';OUT=HERE/'merged-south-v3';OUT.mkdir(exist_ok=True)
d=p.read(OLD/'strip-derivation.json');base=np.array(Image.open(d['base']['file']).convert('RGB'));src=np.array(Image.open(OLD/'source-index.png'))
gen=base.copy();raws={r['index']:np.array(Image.open(r['file']).convert('RGB')) for r in d['sources']}
# Preserve horizontal seam choice in repaired band; extend row1000 source IDs below the return seam.
ids=src.copy();ids[1000:]=src[1000][None,:]
for r in d['sources']:
 L=r['contextStripBox'][0];mask=ids[:,L:L+1254]==r['index'];gen[:,L:L+1254][mask]=raws[r['index']][mask]
yy,xx=np.indices((1254,4096));bottom=np.array(d['bottomSeamPath']);top=np.array(d['topSeamPath'])
t=np.clip((yy-(bottom[None,:]-64))/128,0,1);w=1-t*t*(3-2*t)
def edge(a):
 a=a.astype(float);gx=np.max(np.abs(a[:,2:]-a[:,:-2]),2);gy=np.max(np.abs(a[2:]-a[:-2]),2);z=np.zeros(a.shape[:2]);z[:,1:-1]=gx;z[1:-1]=np.maximum(z[1:-1],gy);return z
seed=np.maximum(edge(base),edge(gen))>65
padded=np.pad(seed,2,mode='constant');strong=np.zeros_like(seed)
for dy in range(5):
 for dx in range(5):strong|=padded[dy:dy+1254,dx:dx+4096]
w[strong]=(yy<bottom[None,:])[strong];w[yy<top[None,:]]=0
alpha=np.rint(w*255).astype('uint8')
def blend(a,b,m):return ((a.astype('uint32')*(255-m[...,None])+b.astype('uint32')*m[...,None]+127)//255).astype('uint8')
final=blend(base,gen,alpha)
delivery=p.read(ROOT/'delivery-20261011-v1/delivery-manifest.json');tiles=['r03_c05','r04_c05'];bases={}
for tile in tiles:
 bases[tile]=Path(next(v for v in delivery['tiles'] if v['tile']==tile)['candidate'])
pair=np.concatenate([np.array(Image.open(bases[t]).convert('RGB')) for t in tiles]);before=pair.copy();pair[3184:4438]=final
context_box=[0,3697,1254,4951];current=pair[3697:4951,:1254].copy();new=np.array(Image.open(HERE/'bottom-return01/raw-v1.png').convert('RGB'))
y,x=np.indices((1254,1254))
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
ra=np.rint(255*s(x,85,110)*(1-s(x,390,403))*s(y,400,490)*(1-s(y,710,805))).astype('uint8')
repair=blend(current,new,ra);pair[3697:4951,:1254]=repair
support=np.zeros((8192,4096),bool);support[3184:4438]=alpha>0;support[3697:4951,:1254]|=ra>0
assert np.array_equal(pair[~support],before[~support])
p.save_png(OUT/'material-alpha.png',Image.fromarray(alpha));p.save_png(OUT/'timber-repair-alpha.png',Image.fromarray(ra))
p.save_png(OUT/'source-index.png',Image.fromarray(ids));p.save_png(OUT/'derived-strip-native.png',Image.fromarray(pair[3184:4438]))
p.save_png(OUT/'timber-derived-context.png',Image.fromarray(repair))
derivation={'createdAt':p.now(),'baseDerivation':str(OLD/'strip-derivation.json'),'baseDerivationSHA256':p.sha(OLD/'strip-derivation.json'),'baseCandidates':{t:{'file':str(bases[t]),'sha256':p.sha(bases[t])} for t in tiles},'sources':d['sources'],'sourceIndex':{'file':str(OUT/'source-index.png'),'sha256':p.sha(OUT/'source-index.png'),'meaning':'0 unchanged base,1..4 source pixel at source contextStripBox; only material-alpha >0 used'},'stripPairBox':[0,3184,4096,4438],'materialAlpha':{'file':str(OUT/'material-alpha.png'),'sha256':p.sha(OUT/'material-alpha.png')},'materialFormula':'uint8 round smoothstep128px around recorded bottom seam, binary source near native color gradients >65 dilated2pixels, zero above recorded top path','timberRaw':{'file':str(HERE/'bottom-return01/raw-v1.png'),'sha256':p.sha(HERE/'bottom-return01/raw-v1.png'),'generationRecord':str(HERE/'bottom-return01/raw-v1.png.generation.json')},'timberPairBox':context_box,'timberAlpha':{'file':str(OUT/'timber-repair-alpha.png'),'sha256':p.sha(OUT/'timber-repair-alpha.png')},'timberAlphaFormula':'round(255*s(x,85,110)*(1-s(x,390,403))*s(y,400,490)*(1-s(y,710,805)))','operationOrder':['base pair','material alpha native source field at stripPairBox','timber alpha over current pair crop at timberPairBox'],'blendFormula':'(base*(255-alpha)+source*alpha+127)//255 per RGB channel','resampled':False,'spatialBlur':False,'formalAccepted':False}
p.put_json(OUT/'derivation.json',derivation)
outputs=[]
for index,tile in enumerate(tiles):
 arr=pair[index*4096:(index+1)*4096];prev=before[index*4096:(index+1)*4096];tm=support[index*4096:(index+1)*4096]
 dest=ROOT/tile/'continuation-20261011'/'south-v3';dest.mkdir(parents=True,exist_ok=True)
 composite=p.save_png(dest/'integrated-candidate-native.png',Image.fromarray(arr));sm=p.save_png(dest/'combined-support.png',Image.fromarray(tm.astype('uint8')*255));exports=[];sel=p.read(ROOT/tile/'pipeline-selection.json')
 for patch in p.patch_ids():
  co=p.coords(tile,patch);tb=co['tileWorldBox'];b=co['worldBoxWithHalo'];L,T=b[0]-tb[0],b[1]-tb[1];x0,y0,x1,y1=max(0,L),max(0,T),min(4096,L+1254),min(4096,T+1254);mm=tm[y0:y1,x0:x1]
  if not mm.any():continue
  old=p.selected(ROOT/tile,patch);o=np.array(Image.open(old).convert('RGB'));oldarr=o.copy();o[y0-T:y1-T,x0-L:x1-L][mm]=arr[y0:y1,x0:x1][mm];nm=np.zeros((1254,1254),bool);nm[y0-T:y1-T,x0-L:x1-L]=mm
  png=dest/(patch+'-derived.png');pi=p.save_png(png,Image.fromarray(o));mi=p.save_png(dest/(patch+'-source-support.png'),Image.fromarray(nm.astype('uint8')*255))
  rec={'kind':'native_same_coordinate_strip_and_context_derivation',**pi,'width':1254,'height':1254,'format':'PNG','opaque':True,'baseNative':p.native_info(old),'coordinates':co,'sourceSupport':mi,'stripDerivation':str(OUT/'derivation.json'),'stripDerivationSHA256':p.sha(OUT/'derivation.json'),'resizedAfterGeneration':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None,'verifiedOutsideSupportUnchanged':bool(np.array_equal(o[~nm],oldarr[~nm])),'formalAccepted':False}
  p.put_json(Path(str(png)+'.generation.json'),rec);exports.append({'patch':patch,'file':str(png),'relativePath':str(png.relative_to(ROOT/tile))})
 manifest={'tile':tile,'baseCandidate':{'file':str(bases[tile]),'sha256':p.sha(bases[tile])},'baseSelection':sel,'integratedComposite':composite,'combinedSupport':sm,'exports':exports,'stripDerivation':str(OUT/'derivation.json'),'contextsInApplicationOrder':d['sources']+[derivation['timberRaw']],'verifiedOutsideSupportUnchanged':bool(np.array_equal(arr[~tm],prev[~tm])),'formalAccepted':False}
 p.put_json(dest/'integration-manifest.json',manifest);outputs.append({'tile':tile,'candidate':composite,'manifest':str(dest/'integration-manifest.json'),'exports':exports})
qa=[]
for row in [700,912,1140,1280]:
 for i in range(4):
  q=p.save_png(OUT/f'qa-y{row}-segment{i+1:02d}.png',Image.fromarray(pair[3184+row-110:3184+row+110,i*1024:(i+1)*1024]));qa.append(q)
for xval in [1100,2050,3000]:qa.append(p.save_png(OUT/f'qa-vertical-x{xval}.png',Image.fromarray(pair[3804:4404,xval-160:xval+160])))
qa.append(p.save_png(OUT/'qa-timber-native.png',Image.fromarray(repair).crop((50,350,445,870))))
p.put_json(OUT/'qa-index.json',qa);p.put_json(OUT/'output-index.json',outputs)
print({'output':str(OUT),'exports':{v['tile']:len(v['exports']) for v in outputs},'outsideSupportUnchanged':True,'qaCount':len(qa)})

