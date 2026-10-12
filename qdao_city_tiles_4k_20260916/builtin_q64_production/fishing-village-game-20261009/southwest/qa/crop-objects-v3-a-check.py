import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import hashlib,json
Z=Path(__file__).resolve().parents[1];p=Z/'qa/repair-r09_c06-objects-v3-context-native.png';im=Image.open(p);box=[375,75,1629,1329];a=im.crop(box);out=Z/'qa/repair-r09_c06-objects-v3-a-full-after-100pct.png';assert not out.exists();a.save(out)
print(json.dumps({'file':out.as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'contextBox':box,'source':p.as_posix()}))
