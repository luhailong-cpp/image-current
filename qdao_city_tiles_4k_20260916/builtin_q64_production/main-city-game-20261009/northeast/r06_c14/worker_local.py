from pathlib import Path
import importlib.util, sys, json
from PIL import Image
TILE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('production',TILE.parent/'production.py')
production=importlib.util.module_from_spec(spec); spec.loader.exec_module(production)
production.TILE=TILE
production.update=lambda *a, **k: None
_original_save=production.save
def tile_save(path,data):
    path=Path(path).resolve()
    if not path.is_relative_to(TILE.resolve()):
        if path== (TILE.parent/'model-verification.json').resolve(): return
        raise RuntimeError('Refusing non-tile write: '+str(path))
    _original_save(path,data)
production.save=tile_save
def context(patch):
    if patch[1]=='1':
        checked_north=Image.open(TILE.parent/'r05_c14'/'candidates'/'r05_c14.candidate.png').convert('RGB')
        if checked_north.size!=(4096,4096): raise RuntimeError('North candidate dimensions mismatch')
    for neighbor_tile, neighbor_patch, box, pos in production.context_neighbors(patch):
        source=production.selected_native(neighbor_tile,neighbor_patch)
        if not source.is_file(): raise RuntimeError('Wait for missing native neighbor: '+str(source))
    production.context(patch)
    if patch[1]=='1':
        candidate=TILE.parent/'r05_c14'/'candidates'/'r05_c14.candidate.png'
        if not candidate.is_file(): raise RuntimeError('North final candidate required')
        dest=TILE/'layout-only'/f'{patch}-mixed-context.png'
        record=Path(str(dest)+'.generation.json')
        data=json.loads(record.read_text(encoding='utf-8'))
        im=Image.open(dest).convert('RGB')
        north=Image.open(candidate).convert('RGB')
        if north.size!=(4096,4096): raise RuntimeError('North candidate dimensions mismatch')
        left=(int(patch[2])-1)*1024-115
        x0=max(left,0); x1=min(left+1254,4096)
        box=(x0,3981,x1,4096); paste=(x0-left,0)
        im.paste(north.crop(box),paste); im.save(dest)
        data['sha256']=production.sha(dest)
        data['derivedFrom'].append({'file':str(candidate),'sha256':production.sha(candidate),'role':'North accepted working candidate exact last 115 core rows; remaining outer 115 comes from original native halo','crop':box,'paste':paste})
        data['operation']['northFinalCoreOverride']=True
        production.save(record,data)
if __name__=='__main__':
    command=sys.argv[1]
    if command=='prepare': production.prepare()
    elif command=='context': context(sys.argv[2])
    elif command=='ingest': production.ingest(sys.argv[2],sys.argv[3])
    else: raise ValueError('Unknown command')

