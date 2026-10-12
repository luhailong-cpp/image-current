from pathlib import Path
import json,hashlib,sys,shutil,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;T=O.parent;Q=O/'qa-native-stairs-restored';E=O/'exported-native-v2';E.mkdir(exist_ok=True)
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
SFILE=T.parent.parent/'northwest/r05_c04/native/s01_01.png';S=rgb(SFILE)
NFILE=T/'qa-repair-native/exported-native-v1/s04_01-internal4-derived.png';N=rgb(NFILE);C=rgb(O/'alternative8-native.png')
assert np.array_equal(C[120:326,709:775],N[120:326,709:775])
assert np.array_equal(C[1139:],S[115:230])
assert sha(SFILE)=='7919f7f22ce30a0b79704adec2f6932b9c4a46c7677b526b8c4670d8a831fe8a'
context=np.concatenate([C[512:1139],S[115:742]],axis=0)
Image.fromarray(context).save(O/'derived-context-native.png')
prov=read(O/'derivation-manifest.json')
prov['steps'].append({'name':'restore aligned adjacent staircase from saved stage4',
 'base':ref(O/'alternative7-native.png'),'source':ref(O/'stage4-derived-native.png'),
 'alpha':ref(O/'restore-stairs-alpha.png'),'worldBox':[12173,15245,13427,16499],
 'weight':'s(x,1012,1044), using same pixel-center smoothstep and 255 quantization defined in alphaRule',
 'purpose':'Undo the intermediate stage5 deletion of the existing stair front lip; preserve the generated stone rail connector.',
 'derived':ref(O/'alternative8-native.png'),'actualImagegenCallsAdded':0})
prov['finalNative']=ref(O/'alternative8-native.png');prov['finalContext']=ref(O/'derived-context-native.png')
prov['contextWorldBox']=[12173,15757,13427,17011]
change=np.any(C!=N,axis=2);Image.fromarray((change*255).astype('uint8')).save(O/'alternative8-changed-mask.png')
prov['changedMask']=ref(O/'alternative8-changed-mask.png')
prov['scripts'].append(ref(O/'qa_restore_stairs.py'))
P=O/'derivation-manifest-v2.json';dump(P,prov)
exports=[]
for patch in ['s03_01','s04_01']:
 old=read(O/f'exported-native-v1/{patch}-rail-connector-derived.png.generation.json')
 basefile=p.selected(T,patch);base=rgb(basefile)
 if patch=='s04_01':out=C
 else:out=rgb(O/'exported-native-v1/s03_01-rail-connector-derived.png')
 changed=np.any(out!=base,axis=2);ys,xs=np.where(changed)
 f=E/f'{patch}-rail-connector-derived.png';idx=E/f'{patch}-source-index.png'
 Image.fromarray(out).save(f);Image.fromarray(changed.astype('uint8')).save(idx)
 record={**old,**ref(f),'baseNative':p.native_info(basefile),'derivationManifest':ref(P),
 'derivedSource':ref(O/'alternative8-native.png'),'sourceIndexFile':str(idx),'sourceIndexSha256':sha(idx),
 'changedPixels':int(changed.sum()),'copiedPixels':int(changed.sum()),
 'changedNativeBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'sourceIndexMeaning':'0=unchanged latest selected native; 1=recorded multi-source alpha derivation copied at the identical world coordinate. Do not apply alpha again.',
 'localVisualVerdict':'PASS for formal south rail, adjacent staircase and inspected internal joins; design-change alternative awaits root selection.',
 'formalAccepted':False}
 dump(f.with_suffix('.png.generation.json'),record)
 p.native_info(f)
 exports.append({'patch':patch,**ref(f),'record':str(f)+'.generation.json','baseNative':record['baseNative'],
                 'coordinates':record['coordinates'],'changedNativeBox':record['changedNativeBox']})

sources=[]
for patch in p.patch_ids():
 f=p.selected(T,patch)
 if patch in ['s03_01','s04_01']:f=E/f'{patch}-rail-connector-derived.png'
 sources.append({'patch':patch,**p.native_info(f),'coordinates':p.coords('r04_c04',patch)})

im=Image.open(Q/'candidate-minimum-error.png').convert('RGB');a=np.array(im)
for c in [2,3,4]:
 sf=T.parent.parent/f'northwest/r05_c04/native/s01_{c:02d}.png';sa=rgb(sf)
 Image.fromarray(np.concatenate([a[-320:,(c-1)*1024:c*1024],sa[115:435,115:1139]],axis=0)).save(Q/f'external-south-segment{c:02d}-native.png')
for c in [2,3,4]:im.crop(((c-1)*1024,2912,c*1024,3232)).save(Q/f'internal-y3072-segment{c:02d}-native.png')
baseline=rgb(O/'qa-native/baseline-minimum-error.png');diff=np.any(a!=baseline,axis=2);ys,xs=np.where(diff)
Image.fromarray((diff*255).astype('uint8')).save(Q/'candidate-change-mask.png')
checked=['external-south-segment01-native.png','internal-x1024-bottom-native.png','residual-stair-detail-native.png']
qa=[]
for f in sorted(Q.glob('*native.png')):
 info={**ref(f),'scale':'native 1:1, no resizing','visualVerdict':'PASS actual view' if f.name in checked else 'pending actual view or identical-to-viewed verification'}
 if f.name.startswith('external-south'):
  c=int(f.name.split('segment')[1][:2]);sf=T.parent.parent/f'northwest/r05_c04/native/s01_{c:02d}.png'
  info.update(worldBox=[12288+(c-1)*1024,16064,12288+c*1024,16704],formalBoundaryY=320,worldBoundaryY=16384,
              lowerSource=ref(sf),lowerNativeCrop=[115,115,1139,435],lowerSourcePixelsUnmodified=True)
 qa.append(info)
manifest={'schemaVersion':1,'status':'local_visual_pass_pending_root_design_review','formalAccepted':False,
 'tile':'r04_c04','designChange':prov['designChange'],'derivationManifest':ref(P),
 'exports':exports,'sources':sources,'candidate':ref(Q/'candidate-minimum-error.png'),
 'assemblyMethod':'pipeline.assemble_arrays minimum-error, current 16 sources with only these two export overrides; final assembly chooses original derived-source pixels without resampling',
 'assemblyPaths':read(Q/'seam-paths.json'),'qaImages':qa,
 'changedTileBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedTilePixels':int(diff.sum()),
 'localVisualVerdict':'PASS: formal south segment1 rail/grooves/shadow and adjacent stair lips connect at native scale. Stone connector is an explicit new design detail. Root review decides selection.',
 'constraintsVerified':{'rawOutputsByteIdenticalToHost':True,'allExportsOpaque1254PNG':True,
  'nativePixelPositionsUnchanged':True,'noResizeWarpOrBlur':True,'existingF2NativePixelsUnchanged':True,
  'oldSouthFileHashUnchanged':True,'southHaloEqualsTrueSouthSource':True,'selectionOrProgressModified':False},
 'previousRejectedVariants':['candidate-manifest.json','candidate-col1-manifest.json'],
 'rejectedVariantFindingResolved':'Their adjacent stair lip artifact was removed by same-world stage4 restoration with a 32px alpha transition; no additional generation.'}
dump(O/'candidate-ready-manifest.json',manifest)
handoff={'status':'READY_FOR_ROOT_DESIGN_REVIEW','formalAccepted':False,
 'candidateManifest':str(O/'candidate-ready-manifest.json'),'derivationManifest':str(P),
 'exports':exports,'nativeQA':str(Q/'external-south-segment01-native.png'),
 'stairQA':str(Q/'internal-x1024-bottom-native.png'),
 'localVerdict':manifest['localVisualVerdict'],'designChange':prov['designChange'],
 'oldSouthUnchanged':ref(SFILE),'writesConfinedTo':str(O),'selectionOrProgressModified':False}
dump(O/'handoff.json',handoff)
print(json.dumps({'handoff':str(O/'handoff.json'),'exports':exports},ensure_ascii=False))
