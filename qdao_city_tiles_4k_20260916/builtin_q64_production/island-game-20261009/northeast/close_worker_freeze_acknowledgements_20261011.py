from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ZONE=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
for name, task, tile, last in (
    ('southeast','southeast_complete_round2','r05_c14','r05_c14_p02_01_v2'),
    ('west','west_complete_round2','r04_c11','r04_c11_p03_03'),
):
    path=ZONE/'qa'/f'migration-freeze-{name}-worker-20261011.json'
    if path.exists():
        print(json.dumps({'existingWorkerCheckpointPreserved':str(path)}))
        continue
    selection_path=ZONE/f'selection-{tile}.json'
    selection=read(selection_path)
    generation_path=ZONE/'native'/f'{last}.png.generation.json'
    generation=read(generation_path)
    image=Path(generation['file'])
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    data={
        'schemaVersion':1,
        'worker':task,
        'recordedBy':'root',
        'recordSource':'Explicit worker freeze acknowledgement delivered in root conversation, followed by root metadata/hash verification.',
        'savedAtUtc':stamp,
        'exactWorkerStopTimestamp':None,
        'stopTimeNote':'Worker explicitly reported already stopped before this record. Root subsequently interrupted the remaining bookkeeping turn; this timestamp is record time, not invented earlier stop time.',
        'state':'frozen_for_migration_root_closed_acknowledgement',
        'generationStopped':True,
        'inFlightImagegenCount':0,
        'returnedUnarchivedUniqueOutputs':[],
        'lastReturnedAndArchived':{'id':last,'native':str(image),'sha256':digest,'recordedHashMatches':digest==generation['sha256'],'generationRecord':str(generation_path),'prompt':generation.get('prompt'),'receipt':generation.get('evidence',{}).get('receipt'),'status':'saved_pending_selection'},
        'selection':{'file':str(selection_path),'snapshot':selection},
        'unselectedCoordinates':[f'{tile}_p{r+1:02d}_{c+1:02d}' for r,row in enumerate(selection['cores']) for c,value in enumerate(row) if value is None],
        'pendingWork':['Review/record the saved last candidate before selecting it; then use zone migration inventory for remaining missing coordinates.'],
        'requiredUniqueReferencesOutsideDWorkImage':[],
        'verificationEvidence':str(ZONE/'qa/migration-unsaved-output-audit-20261011.json'),
        'prohibitionsAtFreeze':['no new generation','no new artwork QA','no new composite','no Git operations','no deletion'],
    }
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checkpoint':str(path),'last':last,'hashMatches':digest==generation['sha256']}))
