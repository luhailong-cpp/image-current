from pathlib import Path
from PIL import Image
import json,hashlib,argparse
Z=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--stem',required=True);a.add_argument('--source',required=True);a.add_argument('--previous-input',required=True);a.add_argument('--original-guide-last',action='store_true');v=a.parse_args()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=Z/'native'/f'{v.source}.png'
gen=Path(str(base)+'.generation.json')
g=read(gen);assert g['sha256']==sha(base)
old=read(Z/'guides'/f'{v.previous_input}.input.json')
refs=old['inputs'].copy()
if v.original_guide_last: refs[-1]=old['inputs'][0]
refs[0]={'path':base.as_posix(),'sha256':sha(base),'nativeSize':list(Image.open(base).size),'role':'native AI artwork edit target; keep framing and correct specified complete-object geometry and joint boundaries','generationRecord':{'path':gen.as_posix(),'sha256':sha(gen)}}
rec={k:x for k,x in old.items() if k not in ['versionStem','attempt','inputs','editTarget','imageGenReferencedImagePaths']}
rec.update(versionStem=v.stem,attempt=v.stem.split('_')[-1],inputs=refs,editTarget=refs[0],imageGenReferencedImagePaths=[r['path'] for r in refs])
for name,data in [(f'{v.stem}.input.json',rec),(f'{v.stem}.references.json',refs)]:
 p=Z/'guides'/name
 with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'stem':v.stem,'references':[r['path'] for r in refs]}))

