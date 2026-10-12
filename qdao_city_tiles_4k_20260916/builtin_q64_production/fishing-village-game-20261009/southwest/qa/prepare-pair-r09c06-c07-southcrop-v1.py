import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
src=Q/'pair-r09c06-c07-v1-context-native.png';box=[3650,3072,4904,4326];dst=Q/'pair-r09c06-c07-southfloor-source-native-v1.png';assert not dst.exists();im=Image.open(src);im.crop(box).save(dst)
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
Path(str(dst)+'.derivation.json').write_text(json.dumps({'source':ref(src),'crop':ref(dst),'contextBox':box,'globalContextBox':[24015,35725,25269,36979],'dimensions':[1254,1254],'nativePixelsResampled':False},indent=2)+'\n')

