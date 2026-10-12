from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
z=Path(__file__).resolve().parent
src=z/'r10_c09/processed/colorpass/r10_c09-colorpass-candidate.png'
dst=z/'r10_c09/repair-inputs/cloth-seam-v1.png'
dst.parent.mkdir(exist_ok=True)
box=[1180,420,2434,1674]
im=Image.open(src)
im.crop(box).save(dst)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data={'file':str(dst),'sha256':sha(dst),'createdAt':datetime.now(timezone.utc).isoformat(),'classification':'unscaled crop of native-detail composite for AI seam edit','source':{'file':str(src),'sha256':sha(src)},'tile':'r10_c09','tileBox':box,'globalBox':[32768+box[0],36864+box[1],32768+box[2],36864+box[3]],'dimensions':[1254,1254],'operation':'integer crop only','resampling':False,'nativeSourceManifest':str(z/'colorpass-selected.json'),'status':'AI edit input, not additional native detail'}
dst.with_suffix('.png.derivation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(dst))

