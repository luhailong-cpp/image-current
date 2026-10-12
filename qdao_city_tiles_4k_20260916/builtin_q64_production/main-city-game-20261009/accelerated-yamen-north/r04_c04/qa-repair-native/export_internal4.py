"""Export repair patches without mutating selection/progress. Native coordinates only."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
ROOT=D.parents[1]
sys.path.insert(0,str(ROOT))
import pipeline as p
T=D.parent
OUT=D/'exported-native-v1'
OUT.mkdir(exist_ok=True)
def read(x): return json.loads(Path(x).read_text(encoding='utf-8-sig'))
def put(x,d): Path(x).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(x): return hashlib.sha256(Path(x).read_bytes()).hexdigest()
repairs=[]
for name in ['f1-door-groove','f2-rail-tone','f3-stair-tone','f4-stair-tone']:
 m=read(D/name/'manifest.json')
 repairs.append((m,np.array(Image.open(m['derivedFile']).convert('RGB')),np.array(Image.open(m['alphaFile']))))
sources={pid:p.selected(T,pid) for pid in p.patch_ids()}
put(OUT/'source-selection-used.json',{k:{'file':str(v),'sha256':sha(v)} for k,v in sources.items()})
arrays={}; basearrays={}; exports={}; records=[]
for pid,src in sources.items():
 inf=p.native_info(src); geo=p.coords('r04_c04',pid)
 world=geo['worldBoxWithHalo']; x0,y0=world[0]-12288,world[1]-12288
 a=np.array(Image.open(src).convert('RGB')); old=a.copy(); index=np.zeros((1254,1254),dtype=np.uint8); applied=[]
 for i,(m,pixels,alpha) in enumerate(repairs,1):
  bx,by,br,bb=m['contextTileBox']; l=max(x0,bx); t=max(y0,by); r=min(x0+1254,br); b=min(y0+1254,bb)
  if l>=r or t>=b: continue
  crop=(slice(t-by,b-by),slice(l-bx,r-bx)); dst=(slice(t-y0,b-y0),slice(l-x0,r-x0)); mask=alpha[crop]>0
  if not mask.any(): continue
  a[dst][mask]=pixels[crop][mask]; index[dst][mask]=i
  applied.append({'repair':m['patchId'],'manifest':str(D/m['patchId']/'manifest.json'),'manifestSha256':sha(D/m['patchId']/'manifest.json'),'contextWorldBox':m['contextWorldBox'],'alphaFile':m['alphaFile'],'alphaHash':m['alphaHash'],'rawFile':m['rawFile'],'rawHash':m['rawHash'],'derivedFile':m['derivedFile'],'derivedHash':m['derivedHash'],'copiedPixels':int(mask.sum()),'binaryDestinationMaskValue':i})
 r,c=int(pid[1:3])-1,int(pid[4:6])-1
 basearrays[r,c]=old; arrays[r,c]=a
 if not applied: continue
 dest=OUT/(pid+'-internal4-derived.png'); Image.fromarray(a).save(dest)
 maskfile=OUT/(pid+'-repair-source-index.png'); Image.fromarray(index).save(maskfile)
 changed=np.any(a!=old,axis=2); yy,xx=np.where(changed)
 col2coreunchanged=bool(np.array_equal(a[115:1139,115:1139],old[115:1139,115:1139])) if c==1 else None
 assert c!=1 or col2coreunchanged
 rec={'schemaVersion':1,'kind':'native_multi_source_alpha_derivation','tile':'r04_c04','patch':pid,'file':str(dest),'sha256':sha(dest),'width':1254,'height':1254,'format':'PNG','mode':'RGB','opaque':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None,'baseNative':inf,'coordinates':geo,'repairs':applied,'sourceIndexFile':str(maskfile),'sourceIndexSha256':sha(maskfile),'sourceIndexMeaning':'0=latest selected native; 1..4=already composited repair context copied at identical world coordinates. Per-source alpha masks are separately preserved. Do not apply alpha again.','changedPixels':int(changed.sum()),'changedNativeBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'verifiedOutsideRepairMaskUnchanged':bool(np.array_equal(a[index==0],old[index==0])),'col2CoreByteIdenticalToLatestSelection':col2coreunchanged,'operation':'Same-world-coordinate copy from recorded alpha composites, no resizing/warping/blur. This is a multi-source derivation, not raw native generation.','formalAccepted':False}
 put(str(dest)+'.generation.json',rec); put(str(dest)+'.derivation.json',rec)
 p.native_info(dest); exports[pid]=str(dest.relative_to(T)); records.append(rec)
base,basepaths=p.assemble_arrays(basearrays,'minimum-error'); final,paths=p.assemble_arrays(arrays,'minimum-error')
base.save(OUT/'latest-selected-base-4096.png'); final.save(OUT/'internal4-derived-candidate-4096.png')
for m,_,_ in repairs: final.crop(m['contextTileBox']).save(OUT/(m['patchId']+'-assembled-context.png'))
put(OUT/'integration-manifest.json',{'tile':'r04_c04','selectionNotModified':True,'sharedProgressNotModified':True,'sources':{k:{'file':str(v),'sha256':sha(v)} for k,v in sources.items()},'exports':exports,'selectorArguments':['r04_c04']+[k+'='+v for k,v in exports.items()],'candidate':str(OUT/'internal4-derived-candidate-4096.png'),'candidateSha256':sha(OUT/'internal4-derived-candidate-4096.png'),'baseCandidate':str(OUT/'latest-selected-base-4096.png'),'baseCandidateSha256':sha(OUT/'latest-selected-base-4096.png'),'seamPaths':paths,'records':records,'localVisualQA':'pending final assembled context review','externalSouthSegment1':'FAIL retained; not addressed by these internal repairs','formalAccepted':False})
print(json.dumps({'exports':exports,'candidate':str(OUT/'internal4-derived-candidate-4096.png')},indent=2))
