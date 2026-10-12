from pathlib import Path
import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;T=O.parent;Q=O/'qa-native-final';Q.mkdir(exist_ok=True);E=O/'exported-native-v3';E.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('p',T.parent/'pipeline.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def ref(f):
 f=Path(f);v={'file':str(f),'sha256':sha(f)}
 if f.suffix=='.png':
  with Image.open(f) as im:v.update(width=im.width,height=im.height,mode=im.mode,format=im.format)
 return v
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def dump(f,v):Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgb(f):return np.array(Image.open(f).convert('RGB'))
base03=p.selected(T,'s03_01');B=rgb(base03);R=rgb(O/'raw-v4.png')
alph=np.zeros((1254,1254),dtype=np.uint8);alph[1024:]=np.array(Image.open(O/'stage4-raw-alpha.png'))[:230]
A=B.copy();w=alph[1024:].astype(np.uint32)[:,:,None]
A[1024:]=((B[1024:].astype(np.uint32)*(255-w)+R[:230].astype(np.uint32)*w+127)//255).astype(np.uint8)
Image.fromarray(alph).save(O/'upper-overlap-alpha.png');Image.fromarray(A).save(O/'upper-overlap-derived-native.png')
prov=read(O/'derivation-manifest-v2.json')
prov['steps'].append({'name':'independent upper-overlap composite on actual s03_01 base',
 'base':ref(base03),'raw':ref(O/'raw-v4.png'),'rawWorldBox':[12173,15245,13427,16499],
 'alpha':ref(O/'upper-overlap-alpha.png'),'destinationWorldBox':[12173,14221,13427,15475],
 'weight':'Same stage4-raw-alpha values shifted by +1024 destination rows; zero outside rows 1024..1253.',
 'purpose':'Blend against the actual s03_01 selected base instead of copying partly blended s04_01 pixels across its base-texture discontinuity.',
 'sourceMapping':'destination(x,y) uses raw-v4(x,y-1024); identical world coordinate',
 'derived':ref(O/'upper-overlap-derived-native.png'),'actualImagegenCallsAdded':0})
P=O/'derivation-manifest-v3.json';dump(P,prov)
exports=[]
for patch in ['s03_01','s04_01']:
 prior=read(O/f'exported-native-v2/{patch}-rail-connector-derived.png.generation.json')
 base=p.selected(T,patch);arr=A if patch=='s03_01' else rgb(O/'alternative8-native.png');diff=np.any(arr!=rgb(base),axis=2);ys,xs=np.where(diff)
 f=E/f'{patch}-rail-connector-derived.png';idx=E/f'{patch}-source-index.png'
 Image.fromarray(arr).save(f);Image.fromarray(diff.astype(np.uint8)).save(idx)
 source=O/('upper-overlap-derived-native.png' if patch=='s03_01' else 'alternative8-native.png')
 rec={**prior,**ref(f),'baseNative':p.native_info(base),'derivationManifest':ref(P),
 'derivedSource':ref(source),'derivedSourceWorldBox':p.coords('r04_c04',patch)['worldBoxWithHalo'],
 'sourceIndexFile':str(idx),'sourceIndexSha256':sha(idx),'changedPixels':int(diff.sum()),'copiedPixels':int(diff.sum()),
 'changedNativeBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'localVisualVerdict':'pending final QA'}
 dump(f.with_suffix('.png.generation.json'),rec);p.native_info(f)
 exports.append({'patch':patch,**ref(f),'record':str(f)+'.generation.json','coordinates':rec['coordinates'],'baseNative':rec['baseNative'],'changedNativeBox':rec['changedNativeBox']})
arrays={};sources=[]
for patch in p.patch_ids():
 f=p.selected(T,patch)
 if patch in ['s03_01','s04_01']:f=E/f'{patch}-rail-connector-derived.png'
 arrays[int(patch[1:3])-1,int(patch[4:6])-1]=rgb(f);sources.append({'patch':patch,**p.native_info(f),'coordinates':p.coords('r04_c04',patch)})
im,paths=p.assemble_arrays(arrays,'minimum-error');im.save(Q/'candidate-minimum-error.png');out=np.array(im)
for name,box in [('rail-full-join-native',(450,2800,1100,4096)),('internal-x1024-bottom-native',(864,3072,1184,4096)),('stair-detail-native',(950,3870,1220,4050)),('upper-join-detail-native',(800,2930,1000,3120))]:im.crop(box).save(Q/(name+'.png'))
for c in [1,2,3,4]:
 im.crop(((c-1)*1024,2912,c*1024,3232)).save(Q/f'internal-y3072-segment{c:02d}-native.png')
 sf=T.parent.parent/f'northwest/r05_c04/native/s01_{c:02d}.png';sa=rgb(sf)
 Image.fromarray(np.concatenate([out[-320:,(c-1)*1024:c*1024],sa[115:435,115:1139]],axis=0)).save(Q/f'external-south-segment{c:02d}-native.png')
base=rgb(O/'qa-native/baseline-minimum-error.png');diff=np.any(out!=base,axis=2);ys,xs=np.where(diff)
Image.fromarray((diff*255).astype(np.uint8)).save(Q/'candidate-change-mask.png')
manifest=read(O/'candidate-ready-manifest.json')
manifest.update(derivationManifest=ref(P),exports=exports,sources=sources,candidate=ref(Q/'candidate-minimum-error.png'),assemblyPaths=paths,
 changedTileBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedTilePixels=int(diff.sum()),
 qaImages=[{**ref(f),'visualVerdict':'pending actual view'} for f in sorted(Q.glob('*native.png'))],
 localVisualVerdict='pending final QA of corrected upper overlap',status='pending_final_visual_QA')
dump(O/'candidate-final-manifest.json',manifest)
print(json.dumps({'exports':exports,'manifest':str(O/'candidate-final-manifest.json')},ensure_ascii=False))
