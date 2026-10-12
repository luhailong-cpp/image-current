import json
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
rows=[]
for action,count,duration in [('hit',6,40),('attack',12,30),('cast',16,45)]:
    for direction in ['E','W']:
        for speed,factor in [('normal',1),('slow',4)]:
            p=R/'preview'/f'{action}-{direction}-{speed}.png'
            im=Image.open(p); times=[]
            for i in range(im.n_frames): im.seek(i); times.append(im.info.get('duration'))
            rows.append({'file':p.relative_to(R).as_posix(),'nFrames':im.n_frames,'durationMs':times,'passed':im.n_frames==count and all(t==duration*factor for t in times)})
errors=[r['file'] for r in rows if not r['passed']]
(R/'records/apng-validation.json').write_text(json.dumps({'previews':rows,'errors':errors},indent=2),encoding='utf-8')
print(f'{len(rows)} APNG previews verified; errors={len(errors)}')
raise SystemExit(bool(errors))
