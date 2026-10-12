from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent.parent; T=B/'r09_c06'; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=T/'refinement/versions/resume-20261012-v02/p03_01.rejected-native.png'
layout=T/'pipeline/guides/p03_01.resume-20261012-v01.continuity-seed.png'
out=T/'pipeline/guides/p03_01.resume-20261012-v03.coordination-seed.png'
assert not out.exists()
im=Image.open(native).convert('RGB'); guide=Image.open(layout).convert('RGB'); box=(400,390,1100,1254)
im.paste(guide.crop(box),box[:2]); im.save(out)
d={'file':str(out),'sha256':sha(out),'guideOnly':True,'finalArt':False,'operation':'exact same-coordinate crop and paste, no painting/resampling/warp','base':{'file':str(native),'sha256':sha(native)},'layout':{'file':str(layout),'sha256':sha(layout)},'box':box,'nativePixelsOutsideBoxPreserved':True}
out.with_suffix('.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)
