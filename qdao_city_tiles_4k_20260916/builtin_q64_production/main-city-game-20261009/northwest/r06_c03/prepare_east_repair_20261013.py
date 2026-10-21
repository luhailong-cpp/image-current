from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-row4-contours-01';d.mkdir(parents=True,exist_ok=False)
own=T/'candidate/native-repairs-20261013-v01/candidate.png';neighbor=T.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(own).crop((3469,2842,4096,4096)),(0,0));im.paste(Image.open(neighbor).crop((0,2842,627,4096)),(627,0));im.save(d/'edit-target.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(d/'derivation.json').write_text(json.dumps(dict(source=str(own),sourceSha256=sha(own),actualEastNeighbor=dict(file=str(neighbor),sha256=sha(neighbor)),tileCropLTRB=[3469,2842,4723,4096],worldBox=[11661,23322,12915,24576],output=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),nativePixelScale=1,sourceResampled=False,sourceRecolored=False,sourcePieces=[dict(file=str(own),sourceBox=[3469,2842,4096,4096],targetBox=[0,0,627,1254]),dict(file=str(neighbor),sourceBox=[0,2842,627,4096],targetBox=[627,0,1254,1254])],authorizedAdoption='r06_c03 left side only. Never mutate neighbor.'),indent=2)+'\n')
print(str(d/'edit-target.png'))
