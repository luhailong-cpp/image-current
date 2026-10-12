from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
names=['candidates/run-E-01-needs-handedness-correction.png','candidates/run-E-02-needs-handedness-correction.png','candidates/run-E-03-earlier-phase-mismatch.png','candidates/run-E-04-wide-bow-swing.png','e-full-preview.png','e-half-preview.png']
checks=list((ROOT/'selection').glob('*.json'))+list((ROOT/'preview').rglob('*.html'))+[ROOT/'preview/data.js']
selected=json.loads((ROOT/'selection/run-north.json').read_text(encoding='utf-8-sig'))['frames']
for i in range(1,17):
 p=ROOT/'runtime/run/E'/f'{i:02d}.png'
 row=next(r for r in selected if r['direction']=='E' and r['frame']==i)
 record=ROOT/row['generationRecord']
 assert p.is_file() and record.is_file(),str(p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
 assert hashlib.sha256(record.read_bytes()).hexdigest()==row['generationRecordSha256'],str(record)
 for check in ['E-contact-current.png','E-legs-inspection-current.png']:
  assert (ROOT/'provenance/run-north'/check).is_file(),check
deleted=[]
for name in names:
 p=(ROOT/'provenance/run-north'/name).resolve()
 assert p.is_relative_to(ROOT.resolve()) and p.suffix=='.png' and 'runtime' not in p.parts,str(p)
 if not p.exists():continue
 for check in checks:
  if check.is_file():
   data=check.read_text(encoding='utf-8-sig')
   assert name not in data and p.name not in data, f'Current reference: {check}'
 deleted.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reason':'rejected or superseded; current runtime and current previews verified present'})
 p.unlink()
# Inventory is informational; remove obsolete image entries immediately, then full rescan.
mf=ROOT/'manifest.json'
if mf.exists():
 data=json.loads(mf.read_text(encoding='utf-8-sig'))
 old={row['file'] for row in deleted}
 inv=data.get('pngInventory')
 if isinstance(inv,list):data['pngInventory']=[x for x in inv if x.get('file') not in old]
 elif isinstance(inv,dict):data['pngInventory']={k:v for k,v in inv.items() if k not in old}
 mf.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'audit/cleanup-rejected-20261003.json').write_text(json.dumps({'atUtc':datetime.now(timezone.utc).isoformat(),'deleted':deleted,'generationTextRecordsRetained':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'deleted':len(deleted)}))
