from pathlib import Path
import hashlib,json
from PIL import Image
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'));t=json.loads((R/'run-timing.json').read_text(encoding='utf-8'));review=json.loads((R/'review.json').read_text(encoding='utf-8'))
assert m['exported']==m['visualPassed']==m['anchor']['registeredFrames']==196
assert len(m['frames'])==len({f['sha256'] for f in m['frames']})==196
for f in m['frames']:
 p=R/f['path'];assert p.exists() and sha(p)==f['sha256']==review[f['slot']]['sha256']
 assert f['status']=='passed' and f['technicalExportValid'] and f['registrationApplied']
 meta=json.loads((R/f['generationRecord']).read_text(encoding='utf-8-sig'));assert meta['sha256']==f['sha256']
 if f['action']=='run':
  g=t['directions'][f['direction']];assert f['durationMs']==g['durationsMs'][f['frame']-1]
 else:assert f['durationMs']=={'hit':40,'attack':30,'cast':45}[f['action']]
for d,g in t['directions'].items():
 validate_contact(R,d)
 assert t['frameDurationMs']==60 and g['durationsMs']==[60]*16 and g['cycleMs']==960
 phases=json.loads((R/g['phaseReview']).read_text(encoding='utf-8'))['frames']
 assert all(p['sha256']==sha(R/'run'/d/f'{i+1:02d}.png') for i,p in enumerate(phases))
preview=json.loads((R/'preview/provenance.json').read_text(encoding='utf-8'))
assert len(preview['files'])==42
for f in preview['files']:
 assert (R/f['file']).exists()
 assert all(sha(R/s['path'])==s['sha256'] for s in f['sources'])
 if f['file'].endswith(('-normal.webp','-slow.webp')):
  im=Image.open(R/f['file']);actual=[]
  for n in range(im.n_frames):im.seek(n);im.load();actual.append(im.info.get('duration'))
  assert actual==f['durationsMs'],(f['file'],actual,f['durationsMs'])
assert all((R/'support-idle'/f'{d}.png').exists() for d in t['directions'])
(R/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in m['frames']),encoding='utf-8')
print(json.dumps({'formalFrames':196,'reviewed':196,'registered':196,'unique':196,'previewFiles':42,'runCyclesMs':{d:sum(v['durationsMs']) for d,v in t['directions'].items()},'clientValidated':False}))
