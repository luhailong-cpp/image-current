from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
selected={1:'run-S-01-v3',2:'run-S-02-v2',5:'run-S-05-v5',6:'run-S-06-v3',8:'run-S-08-v2',9:'run-S-09-v3',12:'run-S-12-v3',14:'run-S-14-v4'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
deletions=[]
for number,folder in selected.items():
    dest=ROOT/'generation'/folder/'native.png'
    im=Image.open(dest);im.verify()
    meta=json.loads(Path(str(dest)+'.generation.json').read_text(encoding='utf-8'))
    assert sha(dest)==meta['sha256']
    for p in (ROOT/'generation').glob(f'run-S-{number:02}*/native.png'):
        if p==dest:continue
        assert p.resolve().is_relative_to(ROOT.resolve())
        deletions.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),replacement=dest.relative_to(ROOT).as_posix(),replacementSHA=sha(dest),reason='Superseded or rejected image; current selected in-progress pose retained and verified. Text generation record retained.'))
for d in ['E','W']:
    p=ROOT/'hit-work'/f'hit-{d}-04.png';dest=ROOT/'hit-work'/f'hit-{d}-04-v2.png'
    if p.exists() and dest.exists():
        im=Image.open(dest);im.verify()
        assert Path(str(dest)+'.generation.json').exists()
        deletions.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),replacement=dest.relative_to(ROOT).as_posix(),replacementSHA=sha(dest),reason='04 recoil recovery replaces rejected forward lunge; text provenance retained.'))
log=ROOT/'revision-cleanup-20261003.json'
payload={'time':datetime.now(timezone.utc).isoformat(),'scope':'this character directory only','selectedRunS':selected,'records':deletions,'imageBackupsCreated':False}
if log.exists():
    previous=json.loads(log.read_text(encoding='utf-8'))
    payload['records']=previous['records']+deletions
log.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for row in deletions:
    target=(ROOT/row['file']).resolve()
    assert target.is_relative_to(ROOT.resolve()) and target.suffix=='.png'
    target.unlink()
    metadata=Path(str(target)+'.generation.json')
    if metadata.exists():
        record=json.loads(metadata.read_text(encoding='utf-8'))
        record['imageRetention']={'status':'superseded-image-deleted','replacement':row['replacement'],'cleanupLog':log.name}
        metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'deletedSupersededImages':len(deletions),'log':log.name}))
