from pathlib import Path
from PIL import Image
import json,hashlib
out=Path(__file__).parent
src=out.parent/'current-v10-native-20261013/west-segment03.png'
im=Image.open(src)
records=[]
for name,box in [('west-y2415-current-detail.png',(287,249,447,389)),('west-y2927-2956-current-detail.png',(814,249,974,389))]:
    p=out/name
    assert not p.exists()
    im.crop(box).save(p)
    records.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':str(src),'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'cropOfRotatedNativeStripLTRB':box,'nativePixelScale':1})
(out/'v10-west-known-point-crops.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,indent=2))
