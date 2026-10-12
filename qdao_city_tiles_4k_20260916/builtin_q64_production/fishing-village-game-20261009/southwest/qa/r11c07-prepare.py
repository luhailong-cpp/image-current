import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json
from PIL import Image
z=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('r11c07_production',z/'production.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
original=p.write
def write(path,obj):
 if Path(path).name in ['progress.json','index.json','ledger.json']:return
 original(path,obj)
p.write=write
patch=sys.argv[1];version=sys.argv[2] if len(sys.argv)>2 else 'v1';stem=f'r11_c07_{patch}_{version}';f=z/'native'/f'{stem}.request.json';assert not f.exists(),f
p.prepare('r11_c07',patch,version)
d=json.loads(f.read_text(encoding='utf-8-sig'));target=d['coordinates']['globalContextBox'];targetpath=Path(d['references'][0]['path']);im=Image.open(targetpath).convert('RGB')
refs=[{'path':(z/'qa/block2x2-r09r10c06c07-v2-r10_c07-context-native.png').as_posix(),'globalContextBox':[24461,36749,28787,41075],'role':'effective north context after internally and externally reviewed native seams'},{'path':(z/'qa/repair-r11_c06-internal-v2-context-native.png').as_posix(),'globalContextBox':[20365,40845,24691,45171],'role':'effective west context after internal native repairs'}]
extra=z/'qa/r11c07-neighbor-overrides.json'
if extra.exists():refs+=json.loads(extra.read_text(encoding='utf-8-sig'))
for a in refs:
 box=a['globalContextBox'];inter=[max(target[0],box[0]),max(target[1],box[1]),min(target[2],box[2]),min(target[3],box[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
 src=Image.open(a['path']).convert('RGB');sb=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];db=[inter[0]-target[0],inter[1]-target[1],inter[2]-target[0],inter[3]-target[1]];im.paste(src.crop(sb),tuple(db[:2]));d['overlaps'].append({**a,'sha256':p.sha(a['path']),'globalOverlapBox':inter,'sourceBox':sb,'targetBox':db})
im.save(targetpath)
der=json.loads(Path(str(targetpath)+'.derivation.json').read_text(encoding='utf-8-sig'));der['sha256']=p.sha(targetpath);der['effectiveNeighborOverrides']=d['overlaps'][len(der['nativeSources']):];p.write(Path(str(targetpath)+'.derivation.json'),der)
d['references']=d['references'][:4];p.write(f,d);print(json.dumps({'stem':stem,'context':str(targetpath)}))
