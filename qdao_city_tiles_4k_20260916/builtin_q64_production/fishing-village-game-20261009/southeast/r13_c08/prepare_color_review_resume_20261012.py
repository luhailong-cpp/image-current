from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent
Q=T/'qa/full-native-resume-20261012-v1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
sp=T/'selected-patches.json'
s=json.loads(sp.read_text(encoding='utf-8-sig'))
m=json.loads((Q/'manifest.json').read_text(encoding='utf-8-sig'))
assert len(s['patches'])==16
can=Q/'candidate-4096.png'
a=np.asarray(Image.open(can).convert('RGB'))
assert a.shape==(4096,4096,3)
for src in m['sources']:
    p=T/s['patches'][src['patch']]
    assert p.resolve()==Path(src['file']).resolve() and sha(p)==src['sha256']
    n=np.asarray(Image.open(p).convert('RGB'))
    assert n.shape==(1254,1254,3)
    x,y=src['destination']
    assert np.array_equal(a[y:y+1024,x:x+1024],n[115:1139,115:1139])
ids=[p.stem for p in Q.glob('*.png') if p.name not in ['candidate-4096.png','preview-QA-1024.png']]
assert len(ids)==33
review=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile=s['tile'],candidate=str(can),candidateSha256=sha(can),
    reviewedAtNativeResolution=True,geometryPassed=True,internalReady=False,formalAccepted=False,
    materialStatus='bounded color candidate required; water facet density checked separately after color pass',
    observations=['All 24 seam strips and 9 crossings inspected at native resolution. Rock contours, foam and caustic lines continue without geometric step.',
      'Water hue and caustic density variation remains especially p23-p24 and crossing-r1-c3; RGB correction may address hue only and must not conceal a texture discrepancy.'],
    sources=m['sources'],evidence=[dict(id=i,file=str(Q/(i+'.png')),sha256=sha(Q/(i+'.png'))) for i in sorted(ids)],
    exact4096CoreReplay=True,sourceResampling=False,sourceBlur=False,sourcePixelBlending=False)
rp=Q/'root-native-geometry-review.json'
assert not rp.exists();write(rp,review)
snapshot=T/'qa/selection-before-full-native-registration-20261012.json'
assert not snapshot.exists();snapshot.write_bytes(sp.read_bytes())
s.update(candidate=str(can),candidateSha256=sha(can),status='full_native_geometry_passed_material_review_pending',
    internalReady=False,formalAccepted=False,geometryReview=str(rp),materialPending=True)
write(sp,s)
backup=T/'native-selected-before-color.json'
assert not backup.exists();backup.write_bytes(sp.read_bytes())
code=(T.parent/'r12_c09/color_match_tile.py').read_text(encoding='utf-8-sig')
code=code.replace("processed/colorpass'","processed/colorpass-resume-20261012-v1'").replace('r12_c09','r13_c08')
code=code.replace('correctionLimit=40.0','correctionLimit=24.0').replace('-40, 40','-24, 24').replace('(med - 40)','(med - 24)').replace('(med + 40)','(med + 24)')
code=code.replace('<= 40.00001','<= 24.00001').replace('<= 40','<= 24').replace('exceeds 80','exceeds 48')
code=code.replace("ZONE/'colorpass-selected.json'","ZONE/'colorpass-selected-resume-20261012-v1.json'")
code=code.replace('current sources need color equalization only','geometry reviewed; color and texture acceptance remains pending native visual review')
script=T/'color_match_tile_resume_20261012.py'
assert not script.exists();script.write_text(code,encoding='utf-8')
print(json.dumps(dict(tile=s['tile'],geometryEvidenceCount=len(ids),exactCoreReplay=True,candidate=str(can),colorScript=str(script)),ensure_ascii=False))
