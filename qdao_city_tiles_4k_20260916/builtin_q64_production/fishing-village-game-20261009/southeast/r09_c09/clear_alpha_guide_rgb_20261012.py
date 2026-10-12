from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for stem in ['canopy-cross-r2-c2-v3','ridge-cross-r3-c3-v4']:
 old=R/'repairs'/f'{stem}-alpha-hole-guide.png';record=json.loads(Path(str(old)+'.derivation.json').read_text())
 image=Image.open(record['source']).convert('RGBA');draw=ImageDraw.Draw(image)
 for b in record['holes']:draw.rectangle([b[0],b[1],b[2]-1,b[3]-1],fill=(255,255,255,0))
 new=R/'repairs'/f'{stem}-empty-alpha-hole-guide.png';image.save(new)
 record.update(file=str(new),sha256=sha(new),operation='exact source RGB outside repair holes; repair hole RGB cleared white and alpha zero; mechanical input only; no resampling')
 Path(str(new)+'.derivation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
 requestpath=R/'repairs'/f'{stem}.request.json';request=json.loads(requestpath.read_text())
 request['referenced_image_paths'][0]=str(new);request['referenceEvidence'][0].update(path=str(new),sha256=sha(new))
 requestpath.write_text(json.dumps(request,indent=2),encoding='utf-8')
 print(str(new))

