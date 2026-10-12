"""Same native pipeline, per-tile progress only for isolated parallel production."""
import sys,json
from pathlib import Path
import pipeline as p

if len(sys.argv)<3 or sys.argv[1] not in ('prepare','ingest','assemble'):
    raise SystemExit('Use prepare/ingest/assemble TILE ...; root controls shared progress')
tile=sys.argv[2]
p.validate_tile(tile)
def local_progress():
    selected=[]
    for patch in p.patch_ids():
        path=p.selected(p.ROOT/tile,patch)
        if path.is_file():
            selected.append({'patch':patch,**p.native_info(path)})
    have={x['patch'] for x in selected}
    order=[f's{r:02d}_{c:02d}' for r in range(4,0,-1) for c in range(1,5)]
    nxt=next((x for x in order if x not in have),None)
    data={'tile':tile,'updatedAt':p.now(),'selectedCount':len(selected),'selected':selected,'nextCoordinate':tile+'/'+nxt if nxt else None,'formalAccepted':False,'status':'candidate_pending_QA' if len(have)==16 else 'native_generation_in_progress','builtinOnly':True,'actualModel':None}
    p.replace_json(p.ROOT/tile/'worker-progress.json',data)
    return data
p.update_progress=local_progress
p.main()
