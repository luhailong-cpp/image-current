from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1].resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Check exact current replacements before deleting any superseded GIF.
for d in ['N','NE','E','SE','S','SW','W','NW']:
 for name,ms in [('normal',75),('slow',300)]:
  p=ROOT/'preview/qa'/f'run-{d}-{name}.apng'
  with Image.open(p) as im:
   assert im.n_frames==16
   for i in range(16):im.seek(i);assert im.info['duration']==ms
paths=set((ROOT/'preview/qa').glob('run-*.gif'))
for folder in (ROOT/'provenance').glob('run-*'):
 if folder.is_dir():paths.update(folder.rglob('*.gif'))
html=[(p,p.read_text(encoding='utf-8-sig')) for p in ROOT.rglob('*.html')]
removed=[]
for p in sorted(paths):
 p=p.resolve();assert p.is_relative_to(ROOT) and 'runtime' not in p.parts and p.suffix=='.gif'
 for hp,text in html:assert p.name not in text,f'Active HTML reference in {hp}: {p.name}'
 removed.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
 p.unlink()
report={'atUtc':datetime.now(timezone.utc).isoformat(),'reason':'User removed old faster run preview rates. Replaced current run GIFs with exact75ms/300ms APNG. Original196 runtime PNG unchanged; historical text retained.','removed':removed}
(ROOT/'audit/cleanup-old-run-speed-previews.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'obsoleteRunGifsDeleted':len(removed),'runtimePngModified':0}))
