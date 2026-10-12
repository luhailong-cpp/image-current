from pathlib import Path
import argparse,json,hashlib
from PIL import Image
import assemble_tile
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tile',required=True);p.add_argument('--version',required=True);p.add_argument('--prepare-manifest',action='store_true');a=p.parse_args()
def info(p):return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
s=Z/'west-current-selection-20261012.json';sel=json.loads(s.read_text(encoding='utf-8-sig'));partial=next(x for x in sel['partialTiles'] if x['tileId']==a.tile)
if a.prepare_manifest:
 stems=partial['selectedNativeStems'];assert len(stems)==16
 matrix=[]
 for r in range(1,5):
  row=[]
  for c in range(1,5):
   stem=next(x for x in stems if x.startswith(f'{a.tile}_s{r:02d}_{c:02d}_'))
   im=Z/'native'/(stem+'.png');g=im.with_suffix('.png.generation.json');rec=json.loads(g.read_text(encoding='utf-8-sig'));assert info(im)['sha256']==rec['sha256']
   row.append(dict(path=im.as_posix(),generationRecord=g.as_posix(),sha256=info(im)['sha256']))
  matrix.append(row)
 path=Z/f'{a.tile}.candidate-{a.version}.manifest.json';assert not path.exists();path.write_text(json.dumps(dict(schemaVersion=1,tileId=a.tile,nativePixels=1254,corePixels=1024,haloPixels=115,patchMatrix=matrix),indent=2)+'\n',encoding='utf8');print(str(path))
else:
 base=Z/f'tiles/{a.tile}_candidate-{a.version}_4096.png';record=base.with_suffix('.native-repair.json')
 if not record.exists():record=base.with_suffix('.assembly.json')
 q=Z/f'qa/{a.tile}_{a.version}_internal_review';q.mkdir(exist_ok=False)
 qa=assemble_tile.save_qa(q,Image.open(base).convert('RGB'));index=q/'qa_index.json';index.write_text(json.dumps(qa,indent=2)+'\n',encoding='utf8')
 sel['currentTile']=dict(tileId=a.tile,candidate=info(base),record=info(record),internalClosurePassed=False,qaIndex=info(index),status='full_native_candidate_pending33_QA',formalAccepted=False)
 s.write_text(json.dumps(sel,indent=2)+'\n',encoding='utf8');print(json.dumps(sel['currentTile']))

