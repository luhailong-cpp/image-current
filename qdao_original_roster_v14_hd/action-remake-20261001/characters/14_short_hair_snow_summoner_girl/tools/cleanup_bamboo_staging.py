"""Delete reviewed process bitmaps only; keep per-image textual evidence. Dry-run unless --apply."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');a.add_argument('--record',default='audit/bamboo-cleanup.json');a.add_argument('--staging',choices=['run','hit','attack','cast'],default='run');args=a.parse_args()
S=(R/args.staging/'staging').resolve()
assert R.resolve() in S.parents and S.name=='staging' and S.parent==R.resolve()/args.staging
retention=(R/args.record).resolve()
assert retention.parent==R.resolve()/'audit' and retention.suffix=='.json'
record_path=retention.relative_to(R).as_posix()
if args.apply and retention.exists():raise FileExistsError('Use a fresh cleanup record; prior deletion history must remain immutable: '+str(retention))
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(R/'manifest.json')
candidates=[]
for p in S.rglob('*'):
 if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'} and p.is_file():
  assert not p.is_symlink() and S in p.resolve().parents
  candidates.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
if not args.apply:
 print(json.dumps({'dryRun':True,'count':len(candidates),'bytes':sum(x['bytes'] for x in candidates),'files':[x['file'] for x in candidates]},ensure_ascii=False))
 raise SystemExit(0)
assert m['exported']==m['visualPassed']==196,'Unfinished artwork review: cleanup refused'
reviews=read(R/'review.json')
for f in m['frames']:
 p=R/f['path']
 assert sha(p)==f['sha256']==reviews[f['slot']]['sha256']
 assert reviews[f['slot']]['visualStatus']=='passed' and S not in p.resolve().parents
pvs=read(R/'preview/provenance.json')
assert len(pvs['files'])==42
for preview in pvs['files']:
 assert (R/preview['file']).exists()
 assert all(sha(R/x['path'])==x['sha256'] for x in preview['sources'])
paths={x['file']:x for x in candidates}
for direction in ['N','NE','E','SE','S','SW','W','NW']:
 cp=R/'audit'/f'contact-{direction}-review.json';contact=read(cp)
 assert contact['status']=='passed_offline_four_spatial_pairs'
 historical=[]
 for evidence in contact.get('visualEvidence',[]):
  if evidence in paths:
   historical.append({'file':evidence,'sha256':paths[evidence]['sha256'],'bitmapDisposition':'removed_after_final_delivery_verification','retentionRecord':record_path})
 if historical:
  contact['reviewedProcessEvidence']=contact.get('reviewedProcessEvidence',[])+historical
  contact['visualEvidence']=[f'preview/run-{direction}-sheet.jpg']
  save(cp,contact)
for f in m['frames']:
 mp=R/f['generationRecord'];o=read(mp);origin=o.get('derivedFrom',{})
 source=Path(origin.get('file',''));source=source if source.is_absolute() else R/source
 source=source.resolve()
 if S in source.parents and source.relative_to(R).as_posix() in paths:
  assert sha(source)==origin['sha256']
  origin['bitmapRemovedAfterFinalVerification']=True
  origin['bitmapDisposition']='final1024 game export retained; process bitmap removed per user2026-09-23 policy; textual generation evidence retained'
  origin['retentionRecord']=record_path
  save(mp,o)
for entry in candidates:
 p=R/entry['file'];record=Path(str(p)+'.generation.json')
 if record.exists():
  o=read(record);o['bitmapDisposition']={'status':'removed_after_final_delivery_verification','retentionRecord':record_path,'removedSha256':entry['sha256']};save(record,o)
record={'recordedAt':datetime.now(timezone.utc).isoformat(),'scope':str(S),'reason':'user2026-09-23 keep game-final images and textual provenance only','formalShaVerified':196,'previewFilesVerified':42,'removedCount':len(candidates),'removedBytes':sum(x['bytes'] for x in candidates),'files':candidates,'hostCacheTouched':False,'otherCharactersTouched':False}
save(retention,record)
for entry in candidates:
 p=(R/entry['file']).resolve()
 assert S in p.parents and sha(p)==entry['sha256']
 p.unlink()
assert not any(p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'} for p in S.rglob('*'))
print(json.dumps({'removedCount':len(candidates),'formalFramesRetained':196,'textEvidenceRetained':True}))
