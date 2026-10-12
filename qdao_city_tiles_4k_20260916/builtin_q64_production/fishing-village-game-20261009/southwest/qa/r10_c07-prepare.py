import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json,hashlib
from PIL import Image
z=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('c07production',z/'production.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
patch=sys.argv[1];version=sys.argv[2] if len(sys.argv)>2 else 'v1';stem=f'r10_c07_{patch}_{version}'
def fresh_patch_guide(tile_id,patch_id):
 plan=json.loads((z/'coordinate-plan.json').read_text(encoding='utf-8'))
 tile=next(t for t in plan['tiles'] if t['tile']==tile_id)
 part=next(t for t in tile['patches'] if t['id']==patch_id)
 source=Path(p.CONTRACT['layoutReference'])
 bbox=[v*p.SCALE for v in part['globalContextBox']]
 output=z/'layout-only'/f'{tile_id}_{patch_id}.png'
 Image.open(source).transform((1254,1254),Image.Transform.EXTENT,bbox,resample=Image.Resampling.NEAREST).save(output)
 p.write(Path(str(output)+'.derivation.json'),{'file':output.as_posix(),'sha256':p.sha(output),'role':'layout-only mechanical crop enlarged for coordinate guidance, NEVER final native game art','operation':{'type':'coordinate crop and nearest-neighbor enlargement','sourceBoxFloat':bbox,'outputDimensions':[1254,1254]},'derivedFrom':{'path':source.as_posix(),'sha256':p.sha(source)},'globalBox':part['globalContextBox']})
p.guide=fresh_patch_guide
p.prepare('r10_c07',patch,version)
f=z/'native'/f'{stem}.request.json';d=json.loads(f.read_text(encoding='utf-8-sig'));target=d['coordinates']['globalContextBox'];targetpath=Path(d['references'][0]['path']);im=Image.open(targetpath).convert('RGB')
refs=[{'path':(z/'qa/repair-r09_c07-v1-context-native.png').as_posix(),'globalContextBox':[24461,32653,28787,36979],'role':'effective north neighbor context after internal tray repair'}]
extra=z/'qa/r10_c07-neighbor-overrides.json'
if extra.exists():refs+=json.loads(extra.read_text(encoding='utf-8-sig'))
for a in refs:
 box=a['globalContextBox'];inter=[max(target[0],box[0]),max(target[1],box[1]),min(target[2],box[2]),min(target[3],box[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
 src=Image.open(a['path']).convert('RGB');srcbox=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];destbox=[inter[0]-target[0],inter[1]-target[1],inter[2]-target[0],inter[3]-target[1]];im.paste(src.crop(srcbox),tuple(destbox[:2]));d['overlaps'].append({**a,'sha256':p.sha(a['path']),'globalOverlapBox':inter,'sourceBox':srcbox,'targetBox':destbox})
im.save(targetpath)
der=json.loads(Path(str(targetpath)+'.derivation.json').read_text(encoding='utf-8-sig'));der['sha256']=p.sha(targetpath);der['effectiveNeighborOverrides']=d['overlaps'][len(der['nativeSources']):];p.write(Path(str(targetpath)+'.derivation.json'),der)
d['references']=d['references'][:4];p.write(f,d);print(json.dumps({'stem':stem,'context':str(targetpath)}))
