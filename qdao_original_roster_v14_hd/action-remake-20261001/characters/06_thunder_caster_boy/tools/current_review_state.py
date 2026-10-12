"""Never reuse visual conclusions after any reviewed runtime PNG changes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
def current_review():
 p=R/'review/CURRENT_REVIEW.json'
 if not p.exists():return None
 data=json.loads(p.read_text(encoding='utf-8-sig'))
 if not data.get('localWorkComplete'):return None
 timing=json.loads((R/'animation-timing.json').read_text(encoding='utf-8-sig'))['run']
 if data.get('runTiming',{}).get('frameMs')!=timing['frameMs'] or data.get('runTiming',{}).get('cycleMs')!=timing['cycleMs']:return None
 frames=data.get('frames',[])
 expected={f'runtime/{a}/{d}/{n:02d}.png' for a,dirs,count in [('run',['N','NE','E','SE','S','SW','W','NW'],16),('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16)] for d in dirs for n in range(count)}
 if len(frames)!=196 or {f['file'] for f in frames}!=expected:return None
 for f in frames:
  q=R/f['file']
  if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=f['sha256']:return None
 return data
