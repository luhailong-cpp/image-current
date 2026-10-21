from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-gold-material-01';d.mkdir(parents=True,exist_ok=False)
own=T/'candidate/native-repairs-20261013-v03/candidate.png';neighbor=T.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(own).crop((3469,1900,4096,3154)),(0,0));im.paste(Image.open(neighbor).crop((0,1900,627,3154)),(627,0));im.save(d/'edit-target.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'derivation.json').write_text(json.dumps(dict(source=str(own),sourceSha256=sha(own),actualEastNeighbor=dict(file=str(neighbor),sha256=sha(neighbor)),tileCropLTRB=[3469,1900,4723,3154],worldBox=[11661,22380,12915,23634],output=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),nativePixelScale=1,sourceResampled=False,sourceRecolored=False,authorizedAdoption='r06_c03 left side x<627 only; neighbor immutable.'),indent=2)+'\n')
print(str(d/'edit-target.png'))
