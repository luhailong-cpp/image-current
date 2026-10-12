import sys,json
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;OUT=HERE/'merged-south-v1';OUT.mkdir(exist_ok=True)
base=np.array(Image.open(HERE/'south-conflict-base-strip-native.png').convert('RGB'));assembled=base.copy();source=np.zeros((1254,4096),np.uint8);records=[]
starts=[0,947,1895,2842];raws=[]
for i,L in enumerate(starts,1):
 d=HERE/f'south-segment{i:02d}';f=d/('raw-v2.png' if i==4 else 'raw-v1.png');a=np.array(Image.open(f).convert('RGB'));raws.append(a)
 rec={'index':i,'file':str(f),'sha256':p.sha(f),'generationRecord':str(f)+'.generation.json','contextStripBox':[L,0,L+1254,1254],'worldBox':[16384+L,11376,16384+L+1254,12630]};records.append(rec)
 if i==1:assembled[:,:1254]=a;source[:,:1254]=i
 else:
  oldend=starts[i-2]+1254;overlap=oldend-L
  path=p.minimum_seam(assembled[650:1200,L:oldend],a[650:1200,:overlap]);full=np.pad(path,(650,54),mode='edge')
  x=np.arange(1254)[None,:];mask=x>=full[:,None]
  assembled[:,L:L+1254][mask]=a[mask];source[:,L:L+1254][mask]=i
  rec['leftSeamPath']=full.tolist();rec['leftOverlapPixels']=overlap
top=p.minimum_seam(base[635:705].transpose(1,0,2),assembled[635:705].transpose(1,0,2))+635
bottom=p.minimum_seam(base[1090:1200].transpose(1,0,2),assembled[1090:1200].transpose(1,0,2))+1090
y=np.arange(1254)[:,None];m=(y>=top[None,:])&(y<bottom[None,:]);final=base.copy();final[m]=assembled[m];source[~m]=0
info=p.save_png(OUT/'derived-strip-native.png',Image.fromarray(final));sm=p.save_png(OUT/'source-index.png',Image.fromarray(source))
manifest={'nativeStrip':info,'sourceIndex':sm,'sourceIndexMeaning':'0=unchanged original two-candidate native crop; 1..4=recorded raw source at identical world coordinate. Binary source selection; no blend, resize, warp, or blur.','sources':records,'base':{'file':str(HERE/'south-conflict-base-strip-native.png'),'sha256':p.sha(HERE/'south-conflict-base-strip-native.png')},'topSeamPath':top.tolist(),'bottomSeamPath':bottom.tolist(),'worldBox':[16384,11376,20480,12630],'formalAccepted':False}
p.put_json(OUT/'strip-derivation.json',manifest)
originalDelivery=p.read(ROOT/'delivery-20261011-v1/delivery-manifest.json');outputs=[]
for tile,srcY,endY,tileY in [('r03_c05',0,912,3184),('r04_c05',912,1254,0)]:
 t=next(v for v in originalDelivery['tiles'] if v['tile']==tile);f=Path(t['candidate']);arr=np.array(Image.open(f).convert('RGB'));prev=arr.copy();tilemask=np.zeros((4096,4096),bool);part=m[srcY:endY];arr[tileY:tileY+endY-srcY][part]=final[srcY:endY][part];tilemask[tileY:tileY+endY-srcY]=part
 dest=OUT/tile;dest.mkdir(exist_ok=True);composite=p.save_png(dest/'integrated-candidate-native.png',Image.fromarray(arr));support=p.save_png(dest/'combined-support.png',Image.fromarray(tilemask.astype('uint8')*255));exports=[];sel=p.read(ROOT/tile/'pipeline-selection.json')
 for patch in p.patch_ids():
  co=p.coords(tile,patch);tb=co['tileWorldBox'];b=co['worldBoxWithHalo'];L,T=b[0]-tb[0],b[1]-tb[1];x0,y0,x1,y1=max(0,L),max(0,T),min(4096,L+1254),min(4096,T+1254);mm=tilemask[y0:y1,x0:x1]
  if not mm.any():continue
  old=p.selected(ROOT/tile,patch);o=np.array(Image.open(old).convert('RGB'));before=o.copy();o[y0-T:y1-T,x0-L:x1-L][mm]=arr[y0:y1,x0:x1][mm];nm=np.zeros((1254,1254),bool);nm[y0-T:y1-T,x0-L:x1-L]=mm
  png=dest/(patch+'-derived.png');pi=p.save_png(png,Image.fromarray(o));mi=p.save_png(dest/(patch+'-source-support.png'),Image.fromarray(nm.astype('uint8')*255))
  rec={'kind':'native_same_coordinate_strip_derivation',**pi,'width':1254,'height':1254,'format':'PNG','opaque':True,'baseNative':p.native_info(old),'coordinates':co,'sourceSupport':mi,'stripDerivation':str(OUT/'strip-derivation.json'),'stripDerivationSHA256':p.sha(OUT/'strip-derivation.json'),'resizedAfterGeneration':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None,'verifiedOutsideSupportUnchanged':bool(np.array_equal(o[~nm],before[~nm])),'formalAccepted':False}
  p.put_json(Path(str(png)+'.generation.json'),rec);exports.append({'patch':patch,'file':str(png),'relativePath':str(png.relative_to(ROOT/tile)) if png.is_relative_to(ROOT/tile) else None})
 p.put_json(dest/'integration-manifest.json',{'tile':tile,'baseCandidate':{'file':str(f),'sha256':p.sha(f)},'baseSelection':sel,'integratedComposite':composite,'combinedSupport':support,'exports':exports,'stripDerivation':str(OUT/'strip-derivation.json'),'contextsInApplicationOrder':records,'verifiedOutsideSupportUnchanged':bool(np.array_equal(arr[~tilemask],prev[~tilemask])),'formalAccepted':False})
 outputs.append({'tile':tile,'candidate':composite,'manifest':str(dest/'integration-manifest.json'),'exports':exports})
qa=[]
for row in [700,912,1140]:
 for i in range(4):
  q=p.save_png(OUT/f'qa-y{row}-segment{i+1:02d}.png',Image.fromarray(final[max(0,row-110):min(1254,row+110),i*1024:(i+1)*1024]));qa.append(q)
for x in [1100,2050,3000]:qa.append(p.save_png(OUT/f'qa-vertical-x{x}.png',Image.fromarray(final[620:1220,x-160:x+160])))
p.put_json(OUT/'qa-index.json',qa);p.put_json(OUT/'output-index.json',outputs)
print(json.dumps({'out':str(OUT),'outputs':outputs,'qaCount':len(qa)}))
