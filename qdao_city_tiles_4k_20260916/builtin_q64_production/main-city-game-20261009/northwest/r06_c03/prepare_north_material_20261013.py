from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;d=T/'repair-batches/north-glaze-material-01';d.mkdir(parents=True,exist_ok=False)
own=T/'candidate/native-repairs-20261013-v02/candidate.png';neighbor=T.parent/'r05_c03/candidate/r05_c03-candidate-hard-80982c249bee.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(neighbor).crop((1900,3469,3154,4096)),(0,0));im.paste(Image.open(own).crop((1900,0,3154,627)),(0,627));im.save(d/'edit-target.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'derivation.json').write_text(json.dumps(dict(source=str(own),sourceSha256=sha(own),actualNorthNeighbor=dict(file=str(neighbor),sha256=sha(neighbor)),tileCropLTRB=[1900,-627,3154,627],worldBox=[10092,19853,11346,21107],output=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),nativePixelScale=1,sourceResampled=False,sourceRecolored=False,authorizedAdoption='r06_c03 bottom half y>=627 only; finished north neighbor immutable.'),indent=2)+'\n')
p=ImageDraw.Draw(im);p.line([(0,627),(1253,627)],fill=(255,30,40),width=2);im.save(d/'annotation-only.png')
print(str(d/'edit-target.png'))
