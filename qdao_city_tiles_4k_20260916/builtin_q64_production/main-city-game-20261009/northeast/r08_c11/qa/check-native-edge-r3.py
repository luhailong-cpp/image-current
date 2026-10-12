from pathlib import Path
from PIL import Image
import json,sys,hashlib
p=Path(__file__).resolve().parents[1]
patch,tag=sys.argv[1:3];q=p/'qa';sel=json.loads((p/'selected-native.json').read_text(encoding='utf-8-sig'));fn=p/'native'/sel[patch];im=Image.open(fn).convert('RGB');pr,pc=int(patch[1]),int(patch[2]);manifest=[]
for d,dr,dc,a,b,pos,size in [('east',0,1,(939,115,1139,1139),(115,115,315,1139),(200,0),(400,1024)),('south',1,0,(115,939,1139,1139),(115,115,1139,315),(0,200),(1024,400))]:
 r,c=pr+dr,pc+dc;nt=p
 if c==5:nt=p.parent/f'r{int(p.name[1:3]):02}_c{int(p.name[5:7])+1:02}';c=1
 if r==5:nt=p.parent/f'r{int(p.name[1:3])+1:02}_c{int(p.name[5:7]):02}';r=1
 sf=nt/'selected-native.json'
 if not sf.exists():continue
 ns=json.loads(sf.read_text(encoding='utf-8-sig'));neighbor=f'p{r}{c}'
 if neighbor not in ns:continue
 nf=nt/'native'/ns[neighbor]
 if not nf.exists():continue
 out=q/f'{patch}-{d}-join-{tag}.png';assert not out.exists()
 ci=Image.new('RGB',size);ci.paste(im.crop(a),(0,0));ci.paste(Image.open(nf).convert('RGB').crop(b),pos);ci.save(out)
 manifest.append({'file':str(out),'native':str(fn),'nativeSha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'neighbor':str(nf),'neighborSha256':hashlib.sha256(nf.read_bytes()).hexdigest(),'operation':'integer native core edge crop paste; no scaling'})
out=q/f'{patch}-edge-evidence-{tag}.json';assert not out.exists();out.write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))
