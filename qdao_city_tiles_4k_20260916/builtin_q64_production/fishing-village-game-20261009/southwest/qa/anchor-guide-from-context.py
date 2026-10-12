import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
stem,source,tile=sys.argv[1:4]
req=z/'native'/(stem+'.request.json');r=json.loads(req.read_text(encoding='utf-8-sig'));dst=Path(r['references'][0]['path'])
source=Path(source);rr,cc=int(tile[1:3]),int(tile[5:7]);srcbox=[(cc-1)*4096-115,(rr-1)*4096-115,cc*4096+115,rr*4096+115];b=r['coordinates']['globalContextBox']
inter=[max(b[0],srcbox[0]),max(b[1],srcbox[1]),min(b[2],srcbox[2]),min(b[3],srcbox[3])];assert inter[2]>inter[0] and inter[3]>inter[1]
with Image.open(source) as im,Image.open(dst) as guide:
 assert im.size==(4326,4326)
 canvas=guide.convert('RGB');canvas.paste(im.crop((inter[0]-srcbox[0],inter[1]-srcbox[1],inter[2]-srcbox[0],inter[3]-srcbox[1])),(inter[0]-b[0],inter[1]-b[1]));pending=dst.with_name(dst.stem+'.anchored.png');canvas.save(pending)
pending.replace(dst)
anchor={'path':source.as_posix(),'sha256':prod.sha(source),'globalOverlapBox':inter,'role':'current verified adjacent tile context; integer crop and paste only'}
dp=Path(str(dst)+'.derivation.json');d=json.loads(dp.read_text(encoding='utf-8'));d.update({'sha256':prod.sha(dst),'currentFinalAnchor':anchor});prod.write(dp,d)
r['currentFinalAnchor']=anchor;prod.write(req,r)
print(json.dumps(anchor))
