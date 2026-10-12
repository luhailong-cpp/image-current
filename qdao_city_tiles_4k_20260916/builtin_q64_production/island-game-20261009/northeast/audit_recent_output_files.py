from native_work import *
import re
records=[read(p) for p in (ZONE/'native').glob('*.png.generation.json')]
known={r['sha256'] for r in records};dirs=set()
for r in records:
 if r['id'].startswith(('r03_c11','r04_c14','r05_c12','r05_c13')):
  p=Path(r.get('evidence',{}).get('originalToolPath',''))
  if p.parent.exists():dirs.add(p.parent)
out=[]
for d in sorted(dirs):
 unknown=[]
 for p in sorted(d.glob('*.png'),key=lambda p:p.stat().st_mtime,reverse=True)[:12]:
  h=sha(p)
  if h not in known:unknown.append({'file':p.as_posix(),'sha256':h,'modifiedUtc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'size':list(Image.open(p).size)})
 out.append({'directory':d.as_posix(),'unknownRecentPngs':unknown})
write(ZONE/'qa/recent-unregistered-output-audit-20261011.json',{'scannedAtUtc':now(),'scope':'only tool-output dirs already evidenced by this zone active tile generation records; latest12 PNG perdir','directories':out})
print(json.dumps(out))

