from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
groups=[('attack','E',12),('attack','W',12),('run','E',16),('run','SE',16)]
O=R/'work/full-limb-root-20261005';O.mkdir(exist_ok=True)
baseline=[]
for a,d,count in groups:
 for n in range(1,count+1):
  p=R/f'frames/{a}/{d}/{n:02}.png'
  baseline.append({'action':a,'direction':d,'frame':n,'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for start in range(1,count+1,4):
  board=Image.new('RGB',(1536,732),'#f4efdf');draw=ImageDraw.Draw(board)
  for i,n in enumerate(range(start,min(start+4,count+1))):
   im=Image.open(R/f'frames/{a}/{d}/{n:02}.png').convert('RGBA')
   # Fixed region, aspect-preserving diagnostic crop only. No formal image changes.
   crop=im.crop((0,350,1024,800)).resize((768,338),Image.Resampling.LANCZOS)
   x=(i%2)*768;y=(i//2)*366;board.paste(crop,(x,y),crop);draw.text((x+15,y+343),f'{a}/{d}/{n:02}',fill='#23443c')
  board.save(O/f'{a}-{d}-{start:02}-hands.jpg',quality=95)
(R/'reviews/full-limb-root-before-20261005.json').write_text(json.dumps({'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'frames':baseline,'reviewCrop':'uniform scale only, fixed1024x450 diagnostic region'},ensure_ascii=False,indent=2),encoding='utf-8')
review=json.loads((R/'reviews/final-review.json').read_text(encoding='utf-8'));review['knownUnresolvedArtFailures']=['2026-10-05 full limb review reopened: support shoe axes plus shoulder/elbow/wrist/grip in all196 frames; N support shoe corrections identified.'];review['fullLimbRevision']={'status':'in_progress','startedAtUtc':datetime.now(timezone.utc).isoformat()}
(R/'reviews/final-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print({'baseline':len(baseline),'reviewSheets':14})

