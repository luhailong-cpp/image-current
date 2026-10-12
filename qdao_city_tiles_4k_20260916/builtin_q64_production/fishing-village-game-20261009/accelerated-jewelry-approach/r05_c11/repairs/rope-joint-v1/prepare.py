from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=B/'r05_c11/qa/internal-unrepaired/partial-native.png';box=[1421,950,2675,2204]
Image.open(p).crop(box).save(D/'target-native.png')
(D/'target.derivation.json').write_text(json.dumps({'tileBox':box,'source':str(p),'sourceSha256':sha(p),'dimensions':[1254,1254],'resampling':False,'targetSha256':sha(D/'target-native.png')},indent=2))
