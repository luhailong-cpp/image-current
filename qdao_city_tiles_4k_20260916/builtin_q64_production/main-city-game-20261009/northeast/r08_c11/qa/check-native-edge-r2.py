from pathlib import Path
from PIL import Image
import json,sys,hashlib
p=Path(__file__).resolve().parents[1];patch=sys.argv[1];q=p/'qa';sel=json.loads((p/'selected-native.json').read_text(encoding='utf-8-sig'));fn=p/'native'/sel[patch];im=Image.open(fn).convert('RGB');pr,pc=int(patch[1]),int(patch[2]);manifest=[]
for d,r,c,a,b,pos,size in [('east',pr,pc+1,(989,115,1139,1139),(115,115,265,1139),(150,0),(300,1024)),('south',pr+1,pc,(115,989,1139,1139),(115,115,1139,265),(0,150),(1024,300))]:
 if not(1<=r<=4 and 1<=c<=4):continue
 neighbor='p'+str(r)+str(c)
 if neighbor not in sel:continue
 nf=p/'native'/sel[neighbor];out=q/(patch+'-'+neighbor+'-join-r2.png');assert not out.exists()
 ci=Image.new('RGB',size);ci.paste(im.crop(a),(0,0));ci.paste(Image.open(nf).convert('RGB').crop(b),pos);ci.save(out);manifest.append({'file':str(out),'native':str(fn),'nativeSha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'neighbor':str(nf),'neighborSha256':hashlib.sha256(nf.read_bytes()).hexdigest(),'operation':'integer native core edge crop paste; no scaling'})
(q/(patch+'-edge-evidence-r2.json')).write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))
