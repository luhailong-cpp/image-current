from pathlib import Path
from PIL import Image
import json,hashlib
b=Path(__file__).resolve().parents[1]
s=b/'r04_c11/candidate/r04_c11-4096-candidate-v3.png'
box=[900,3000,1700,4096]
Image.open(s).crop(box).save(b/'qa/root-final-net-native.png')
(b/'qa/root-final-net-derivation.json').write_text(json.dumps({'source':str(s),'sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'cropBox':box,'operation':'unscaled native crop'},indent=2),encoding='utf-8')
