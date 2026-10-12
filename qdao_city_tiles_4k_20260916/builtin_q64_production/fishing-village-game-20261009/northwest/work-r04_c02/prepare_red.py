from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent.parent;W=B/'work-r04_c02';idx=json.loads((B/'current-artifacts.json').read_text(encoding='utf-8-sig'));box=[6800,11850,8054,13104];im=Image.new('RGB',(1254,1254));der=[]
for tile in ['r03_c02','r04_c02']:
 ap=B/idx[tile]['assembly'];a=json.loads(ap.read_text(encoding='utf-8-sig'));gb=a['globalCoreBox'];p=B/idx[tile]['candidate'];src=Image.open(p);z=[max(gb[0],box[0]),max(gb[1],box[1]),min(gb[2],box[2]),min(gb[3],box[3])]
 if z[2]>z[0] and z[3]>z[1]:im.paste(src.crop((z[0]-gb[0],z[1]-gb[1],z[2]-gb[0],z[3]-gb[1])),(z[0]-box[0],z[1]-box[1]));der.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'assembly':str(ap),'intersection':z})
p=W/'guides/red-cloth-whole-v01.native-target.png';im.save(p);p.with_suffix('.derivation.json').write_text(json.dumps({'globalNativeBox':box,'sources':der,'method':'exact native source-proven candidate crops, no scaling'},indent=2),encoding='utf-8')
