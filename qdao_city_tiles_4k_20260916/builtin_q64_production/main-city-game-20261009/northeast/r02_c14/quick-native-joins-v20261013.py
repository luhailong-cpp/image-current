from pathlib import Path
from PIL import Image
import json,hashlib,sys
T=Path(__file__).resolve().parent
sel=json.loads((T/'selected-native.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for pair in sys.argv[1:]:
 a,b=pair.split(':');fa=T/'native'/sel.get(a,a+'.png');fb=T/'native'/sel.get(b,b+'.png')
 sources=[{'file':str(f),'sha256':sha(f)} for f in [fa,fb]]
 sig=hashlib.sha256(json.dumps(sources).encode()).hexdigest()[:16]
 Q=T/'qa'/'quick-native-joins'/sig;Q.mkdir(parents=True,exist_ok=True)
 out=Q/(a+'-'+b+'.png')
 if not out.exists():
  ca=Image.open(fa).convert('RGB').crop((115,115,1139,1139));cb=Image.open(fb).convert('RGB').crop((115,115,1139,1139))
  if a[1]==b[1]:
   win=Image.new('RGB',(384,1024));win.paste(ca.crop((832,0,1024,1024)),(0,0));win.paste(cb.crop((0,0,192,1024)),(192,0))
  else:
   win=Image.new('RGB',(1024,384));win.paste(ca.crop((0,832,1024,1024)),(0,0));win.paste(cb.crop((0,0,1024,192)),(0,192))
  win.save(out);(Q/'sources.json').write_text(json.dumps({'sources':sources,'operation':'integer 1:1 native core seam crops only'},indent=2))
 print(out)
