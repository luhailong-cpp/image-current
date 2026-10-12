from PIL import Image
from pathlib import Path
import json, hashlib
B=Path(__file__).resolve().parent.parent
f=B/'tiles/r08_c11.candidate-v01.png'
o=B/'qa/r08_c11-v01-sol/preview-only-1600.png'
assert not o.exists()
Image.open(f).resize((1600,1600),Image.Resampling.LANCZOS).save(o)
print(json.dumps({'previewOnly':str(o),'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'usableAsFinalArt':False}))
