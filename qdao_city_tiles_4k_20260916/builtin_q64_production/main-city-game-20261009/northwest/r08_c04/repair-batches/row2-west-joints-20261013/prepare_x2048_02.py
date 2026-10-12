from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
B=Path(__file__).resolve().parent;D=B/'joint-x2048-02';D.mkdir(exist_ok=False)
src=B/'joint-x2048-01/upper-trial.png';shutil.copyfile(src,D/'edit-target.png')
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((620,260,800,432),outline=(0,220,230),width=2);d.line([(650,289),(752,389)],fill=(0,220,230),width=3);im.save(D/'locator-only.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'input-provenance.json').write_text(json.dumps({'worldBox':[13709,29581,14963,30835],'target':str(D/'edit-target.png'),'sha256':sha(D/'edit-target.png'),'derivedFrom':str(src),'sourceBase':str(B/'joint-x2048-01/edit-target.png'),'sourceOverlay':str(B/'joint-x2048-01/native.png'),'overlayROI':[487,271,699,538],'pixelResampled':False,'locatorOnly':'cyan suggested short diagonal joint, never production'},indent=2))

