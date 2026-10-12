from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
DIRS=['N','NE','E','SE','S','SW','W','NW']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports=[]
for direction in DIRS:
 p=ROOT/f'audit/run-{direction}-paired-ground-review.json'
 if not p.exists():raise ValueError(f'Missing current paired-position review: {direction}')
 d=read(p)
 orders=d.get('supportOrder') or {s['foot']:[x['frames'] for x in s['positions']] for s in d.get('segments',[])}
 if not orders:orders={str(i):s['pairs'] for i,s in enumerate(d.get('intendedSegments',[]))}
 if len(orders)!=2:raise ValueError(f'{direction}: expected two support legs')
 coverage=[]
 for foot,pairs in orders.items():
  if len(pairs)!=4 or any(len(pair)!=2 for pair in pairs):raise ValueError(f'{direction}/{foot}: expected four two-frame positions')
  ids=[int(i) for pair in pairs for i in pair]
  if any(ids[i+1]!=(ids[i]%16)+1 for i in range(7)):raise ValueError(f'{direction}/{foot}: contact frames are not consecutive')
  coverage.extend(ids)
 if sorted(coverage)!=list(range(1,17)):raise ValueError(f'{direction}: support coverage must contain each frame once')
 frames=d.get('frames',[])
 if len(frames)!=16:raise ValueError(f'{direction}: expected16 actual reviewed frames')
 for row in frames:
  slot=row.get('slot') or f"run/{direction}/{int(row['frame']):02d}"
  file=ROOT/(row.get('file') or f'runtime/{slot}.png')
  if sha(file)!=row.get('sha256'):raise ValueError(f'Stale paired-position review: {slot}')
 reports.append({'direction':direction,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'review':d})
out={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'latestRequirement':'同一支撑脚连续着地，沿行进与透视方向逐步改变相对位置；每两张独立姿态一个位置段，再与另一脚交替。','frameMs':75,'cycleMs':1200,'framesPerRun':16,'pairDurationMs':150,'reviewedCurrentFrames':128,'sourceHashesCurrent':True,'reviews':reports,'dynamicVisualAcceptance':False,'clientIntegrated':False}
(ROOT/'audit/eight-direction-paired-grounding.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reviewedCurrentFrames':128,'directions':len(reports),'sourceHashesCurrent':True,'dynamicVisualAcceptance':False}))
