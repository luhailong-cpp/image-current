import json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ids=[f'r10c10-south-segment-{i}' for i in range(1,5)]+[f'r11c09-east-segment-{i}' for i in range(1,5)]
ids += ['intersection-x36864-y40960']+[f'intersection-x{x}-y40960' for x in (37888,38912,39936)]+[f'intersection-x36864-y{y}' for y in (41984,43008,44032)]
ids += [f'r11c09-south-segment-{i}' for i in range(1,5)]+[f'intersection-x{x}-y45056' for x in (33792,34816,35840)]
for identifier in ids:
    path=HERE/(identifier+'.qa.json')
    d=json.loads(path.read_text(encoding='utf-8'))
    assert d['sourceComplete']
    d['visualReview']={'status':'reviewed_independent_native_geometry','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'seam_review','structuralBlockers':[],'colorOnlyRisks':[],'candidateUsable':True,'formalAccepted':False,'scope':'Exact native pixel shared-edge strip or crossing only; not whole-tile internal acceptance','observations':['Connected wood plank gaps, rail/sill contours and ground paving have no visible step across the actual shared edge and junction; no synthetic fill or geometry masking used.']}
    path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(len(ids))
