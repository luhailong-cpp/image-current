import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, argparse, copy
from PIL import Image
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B/'tools'))
import batch_pipeline as p

ap=argparse.ArgumentParser()
ap.add_argument('--col',type=int,choices=[2,3],required=True)
ap.add_argument('--attempt',type=int,choices=[3,4],required=True)
ap.add_argument('--target',required=True)
ap.add_argument('--prompt-file',required=True)
ap.add_argument('--west')
a=ap.parse_args()
stem=f'r02_c02_s04_{a.col:02d}_a{a.attempt:02d}'
old=p.read_json(B/f'guides/r02_c02_s04_{a.col:02d}_a02.input.json')
data=copy.deepcopy(old)
for name in [f'guides/{stem}.input.json',f'guides/{stem}.references.json',f'guides/{stem}.layout-with-native.png',f'prompts/{stem}.txt',f'native/{stem}.png']:
 assert not (B/name).exists(),name
assert Path(a.target).name.startswith(f'r02_c02_s04_{a.col:02d}_')
assert Path(a.target).is_relative_to(B/'native')
guide=Image.open(old['guide']['path']).convert('RGB')
if a.col==3:
 assert a.west,'Corrected west required'
 wp=p.safe_path(a.west)
 assert wp.name.startswith('r02_c02_s04_02_') and wp.is_relative_to(B/'native')
 box,co,dep=p.coordinate_evidence(wp)
 assert box==[5005,7053,6259,8307]
 wi=Image.open(wp).convert('RGB')
 guide.paste(wi.crop((1024,0,1254,1254)),(0,0))
 n={**p.file_record(wp,'west corrected native neighbor'),**p.dimensions(wp),'direction':'west','globalBox':box,'coordinateEvidence':co,'sourceProvenanceDependencies':dep,'sourceCrop':[1024,0,1254,1254],'destination':[0,0],'resized':False}
 data['neighbors']=[n if x['direction']=='west' else x for x in old['neighbors']]
gr=p.save_image(B/f'guides/{stem}.layout-with-native.png',guide)
target=p.file_record(a.target,'IMAGE 1 native edit target; preserve correct pixels outside specified repair region')
refs=[target,{**gr,'role':'IMAGE 2 geometry-only target guide, sharp fixed south/west overlap strips; blurred pixels forbidden in final'},p.file_record(B/'qa/c02-geometry-review/v01/approved-pommel-layout-nearest20x-QA-ONLY.png','IMAGE 3 approved pommel identity and silhouette only, enlarged layout crop, not final pixels')]
pr=p.save_bytes(B/f'prompts/{stem}.txt',Path(a.prompt_file).read_bytes())
rf=p.save_json(B/f'guides/{stem}.references.json',{'schemaVersion':1,'stem':stem,'inputs':refs,'imageGenReferencedImagePaths':[r['path'] for r in refs]})
_,authority=p.authority()
data.update({'createdAtUtc':p.now(),'versionStem':stem,'stem':stem,'attempt':f'a{a.attempt:02d}','inputs':refs,'imageGenReferencedImagePaths':[r['path'] for r in refs],'inputCount':3,'referenceMode':'precise_native_object_edit','guide':gr,'referencesFile':rf,'prompt':pr,'authority':authority,'editTarget':target,'preparationDescription':'New immutable input for targeted AI edit; original artifacts unchanged. Geometry guide uses unresampled neighbor overlap; not final source.'})
inp=p.save_json(B/f'guides/{stem}.input.json',data)
print(json.dumps({'input':inp,'stem':stem,'referenced_image_paths':data['imageGenReferencedImagePaths']}))
