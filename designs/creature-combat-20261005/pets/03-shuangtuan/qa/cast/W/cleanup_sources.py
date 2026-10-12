from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[3]
SCOPE=(BASE/'source/cast/W').resolve()
RECORDS=BASE/'records/cast/W'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for n in range(1,17):
    p=BASE/'runtime/cast/W'/f'{n:02d}.png'
    rec=json.loads((RECORDS/f'{n:02d}.generation.json').read_text(encoding='utf-8'))
    assert p.is_file() and sha(p)==rec['sha256'],f'Final output not verified: {p}'
images={str(p.resolve()):{'path':p.relative_to(BASE).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in SCOPE.glob('*.png')}
for path in images:
    assert Path(path).parent==SCOPE and Path(path).is_file(),f'Out of scope deletion: {path}'
def identify(value):
    p=Path(value)
    return str((p if p.is_absolute() else BASE/p).resolve())
def mark(node):
    if isinstance(node,dict):
        for key in ('file','path','sourcePath'):
            value=node.get(key)
            if isinstance(value,str) and identify(value) in images:
                info=images[identify(value)]
                node['sha256']=info['sha256']
                node['deleted']=True
                node['deletedAt']=now
                node['retentionReason']='Final runtime verified; source/intermediate image removed per project retention policy; source hash and generation evidence retained.'
        for value in list(node.values()):
            if isinstance(value,(dict,list)): mark(value)
    elif isinstance(node,list):
        for child in node: mark(child)
for p in RECORDS.glob('*.generation.json'):
    record=json.loads(p.read_text(encoding='utf-8'))
    mark(record)
    if p.stem.split('.')[0].isdigit():
        record['visualStatus']='Individual current output and full 16-frame static contact reviewed; normal/slow playback and client not verified; see qa/cast/W/static-review.json'
    p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
report={'cleanedAt':now,'scope':SCOPE.as_posix(),'finalRuntimeVerified':16,'removed':list(images.values()),'retained':'16 runtime PNGs, prompts, generation/receipt/error records, current QA and preview support; external identity/style sources and generated cache untouched'}
(Path(__file__).resolve().parent/'cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for path in images:
    Path(path).unlink()
print(json.dumps({'deleted':len(images),'finalRuntime':16,'scope':str(SCOPE)}))
