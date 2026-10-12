import json,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=R/'candidate/r11_c09-native-candidate-4096.png'
out=R/'layout-only/joint-p32-p33-native-crop.png'
box=[1421,1741,2675,2995]
Image.open(src).crop(tuple(box)).save(out)
m=json.loads((R/'candidate/manifest.json').read_text(encoding='utf-8'))
d={'file':str(out),'sha256':sha(out),'classification':'native repair input only, no layout pixels','operation':'exact unscaled 1254 crop from native candidate','outputDimensions':[1254,1254],'source':str(src),'sourceSha256':sha(src),'sourceBox':box,'globalBox':[34189,42701,35443,43955],'candidateSourcesSnapshot':m['sources'],'sourceCandidateSha256':m['candidateSha256']}
out.with_suffix('.png.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out))

