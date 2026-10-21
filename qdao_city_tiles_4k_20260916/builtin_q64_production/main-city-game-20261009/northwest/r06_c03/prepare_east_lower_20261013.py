from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-lower-contours-02';d.mkdir(parents=True,exist_ok=False)
cp=json.loads((T/'current-fullqa-checkpoint-20261013.json').read_text());own=Path(cp['candidate']['file']);neighbor=T.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(own).crop((3469,2842,4096,4096)),(0,0));im.paste(Image.open(neighbor).crop((0,2842,627,4096)),(627,0));im.save(d/'edit-target.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'derivation.json').write_text(json.dumps(dict(source=str(own),sourceSha256=sha(own),actualEastNeighbor=dict(file=str(neighbor),sha256=sha(neighbor)),tileCropLTRB=[3469,2842,4723,4096],worldBox=[11661,23322,12915,24576],output=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),nativePixelScale=1,sourceResampled=False,sourceRecolored=False,authorizedAdoption='r06_c03 left side x<627 only; neighbor immutable.'),indent=2)+'\n')
im.crop((400,550,850,1030)).save(d/'before-detail.png')
p=ImageDraw.Draw(im);p.rectangle([350,565,626,1010],outline=(255,30,40),width=3);p.line([627,550,627,1030],fill=(255,240,0),width=2);im.save(d/'annotation-only.png')
print(str(d/'edit-target.png'))
