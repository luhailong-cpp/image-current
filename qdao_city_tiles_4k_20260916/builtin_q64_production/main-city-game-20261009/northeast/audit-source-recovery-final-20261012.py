from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;O=Z/'qa/model-pause-final-20261012';O.mkdir(parents=True,exist_ok=True)
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[];dirs=set();hashes={};issues=[]
for f in Z.rglob('*.generation.json'):
 try:
  j=json.loads(f.read_text(encoding='utf-8-sig'))
  if not j.get('route','').startswith('builtin'):continue
  target=Path(j['file'])
  if not target.resolve().is_relative_to(Z):continue
  src=Path(j['sourceOutputPath']);dirs.add(src.parent)
  hashes[j['sha256']]=str(target)
  generated=j.get('generatedAt',j.get('createdAt',j.get('generatedAtUtc','')))
  if target.is_file() and h(target)!=j['sha256']:issues.append({'file':str(target),'issue':'workspace native hash mismatch'})
  if generated and generated[:10]>='2026-10-12':
   ok=src.is_file() and h(src)==j['sha256'];records.append({'native':str(target),'sha256':j['sha256'],'source':str(src),'sourceByteMatch':ok})
   if not ok:issues.append({'file':str(src),'issue':'source missing or mismatch'})
 except (OSError,ValueError,KeyError) as e:issues.append({'record':str(f),'issue':str(e)})
orphans=[]
for d in dirs:
 if not d.is_dir():continue
 for p in d.glob('*.png'):
  if datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).date().isoformat()<'2026-10-12':continue
  hh=h(p)
  if hh not in hashes:orphans.append({'file':str(p),'sha256':hh})
r={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'recentNativeRecords':len(records),'nativeSources':records,'unmirroredRecentOutputFiles':orphans,'issues':issues,'conclusion':'No image generation performed; source recovery audit only.'}
(O/'source-recovery.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'recentNativeRecords':len(records),'unmirroredRecentOutputFiles':orphans,'issues':issues}))
