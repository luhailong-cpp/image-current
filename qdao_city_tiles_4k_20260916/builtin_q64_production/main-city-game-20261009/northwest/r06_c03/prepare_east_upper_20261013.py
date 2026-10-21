from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-upper-contour-02';d.mkdir(parents=True,exist_ok=False)
own=T/'candidate/native-repairs-20261013-v01/candidate.png';neighbor=T.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(own).crop((3469,2545,4096,3799)),(0,0));im.paste(Image.open(neighbor).crop((0,2545,627,3799)),(627,0));im.save(d/'edit-target.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'derivation.json').write_text(json.dumps(dict(source=str(own),sourceSha256=sha(own),actualEastNeighbor=dict(file=str(neighbor),sha256=sha(neighbor)),tileCropLTRB=[3469,2545,4723,3799],worldBox=[11661,23025,12915,24279],output=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),nativePixelScale=1,sourceResampled=False,sourceRecolored=False,authorizedAdoption='r06_c03 left side x<627 only; neighbor immutable.'),indent=2)+'\n')
p=ImageDraw.Draw(im);p.rectangle([525,595,626,715],outline=(255,30,40),width=2);p.ellipse([622,622,632,632],outline=(255,240,0),width=2);im.save(d/'annotation-only.png')
print(str(d/'edit-target.png'))
