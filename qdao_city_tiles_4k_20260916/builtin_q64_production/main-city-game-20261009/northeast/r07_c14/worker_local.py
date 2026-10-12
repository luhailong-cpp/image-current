from pathlib import Path
import importlib.util, sys, json
from PIL import Image
TILE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('production',TILE.parent/'production.py')
production=importlib.util.module_from_spec(spec);spec.loader.exec_module(production)
production.TILE=TILE
production.update=lambda *a,**k:None
_original_save=production.save
def tile_save(path,data):
 path=Path(path).resolve()
 if not path.is_relative_to(TILE.resolve()):
  if path==(TILE.parent/'model-verification.json').resolve():return
  raise RuntimeError('Refusing non-tile write: '+str(path))
 _original_save(path,data)
production.save=tile_save
NORTH=TILE.parent/'r06_c14'/'candidates'/'r06_c14.candidate.png'
NORTH_SHA='609ed58611561a612eec2f87ec95b21ca0c7a3712a2ef07585368f4287b99a66'
def context(patch):
 if patch[1]=='1':
  north=Image.open(NORTH).convert('RGB')
  if north.size!=(4096,4096) or production.sha(NORTH)!=NORTH_SHA:raise RuntimeError('North stable final candidate mismatch')
 for tile,neighbor_patch,box,pos in production.context_neighbors(patch):
  src=production.selected_native(tile,neighbor_patch)
  if not src.is_file():raise RuntimeError('Wait for required native neighbor: '+str(src))
  side=Path(str(src)+'.generation.json')
  if not side.is_file():raise RuntimeError('Wait for required neighbor sidecar: '+str(side))
  record=json.loads(side.read_text(encoding='utf-8-sig'))
  if record['sha256']!=production.sha(src):raise RuntimeError('Native neighbor SHA mismatch')
 production.context(patch)
 if patch[1]=='1':
  dest=TILE/'layout-only'/f'{patch}-mixed-context.png';side=Path(str(dest)+'.generation.json')
  data=json.loads(side.read_text(encoding='utf8'));im=Image.open(dest).convert('RGB')
  left=(int(patch[2])-1)*1024-115;x0=max(left,0);x1=min(left+1254,4096)
  box=(x0,3981,x1,4096);paste=(x0-left,0)
  im.paste(north.crop(box),paste);im.save(dest)
  data['sha256']=production.sha(dest)
  data['derivedFrom'].append({'file':str(NORTH),'sha256':NORTH_SHA,'role':'north final candidate exact last115 core rows; outer115 from original native halo','crop':box,'paste':paste})
  data['operation']['northFinalCoreOverride']=True
  production.save(side,data)
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='prepare':production.prepare()
 elif cmd=='context':context(sys.argv[2])
 elif cmd=='ingest':production.ingest(sys.argv[2],sys.argv[3])
 else:raise ValueError(cmd)

