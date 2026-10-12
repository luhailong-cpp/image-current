from pathlib import Path
import json,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
tile,patch,nextpatch=sys.argv[1:4];T=Z/tile
assert T.parent==Z and tile not in json.loads((Z/'reserved-tiles-20261013.json').read_text())['reservedTiles']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
selection=read(T/'selected-native.json')
existing=[k for k,v in selection.items() if (T/'native'/v).exists()]
record=read(Path(str(T/'native'/selection[patch])+'.generation.json'))
p=read(T/'tile-progress.json')
p.update({'selectedCoreCount':len(existing),'remainingCoreCount':16-len(existing),'updatedAt':datetime.now(timezone.utc).isoformat(),'nextPatch':None if nextpatch=='none' else nextpatch,'inflightGeneration':None,'lastSaved':{'file':record['file'],'sha256':record['sha256'],'nativeSize':record['nativeSize']},'status':'native_saved_layout_checked_full_tile_QA_pending'})
(T/'tile-progress.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tile':tile,'selectedCoreCount':len(existing),'nextPatch':p['nextPatch'],'lastSavedSha256':record['sha256']}))
