from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
R=T/'qa/local-repair-resume2-20261013'
base=T/'qa/core-baseline/31b09711d96a1bf993b7/r06_c15-core-baseline.candidate.png'
out=R/'upperroof-target-v1.png'
box=[680,400,1934,1654]
assert not out.exists()
Image.open(base).crop(box).save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(R/'upperroof-target-v1.json').write_text(json.dumps({'file':str(out),'sha256':sha(out),'crop':box,'source':str(base),'sourceSha256':sha(base),'operation':'integer crop only'},indent=2)+'\n',encoding='utf-8')
