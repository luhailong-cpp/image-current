"""Check exported animation counts/timing without generating any character pixels."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
errors=[];rows=[]
for action,count,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
 for direction in ['E','W']:
  for suffix,factor in [('normal',1),('slow',4)]:
   p=ROOT/'preview'/f'{action}-{direction}-{suffix}.webp'
   im=Image.open(p); durations=[]
   for n in range(im.n_frames):
    im.seek(n);im.load();durations.append(im.info.get('duration'))
   passed=im.n_frames==count and im.size==(512,512) and durations==[ms*factor]*count
   row={'file':p.relative_to(ROOT).as_posix(),'frames':im.n_frames,'size':list(im.size),'durationMs':durations,'passed':passed}
   rows.append(row)
   if not passed:errors.append(row)
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':not errors,'errors':errors,'animations':rows,'browserReview':'See visual-review.json for actual normal/slow/step interaction; this script only checks saved animation metadata.'}
(ROOT/'records/preview-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'animations':len(rows),'errors':len(errors)}))
