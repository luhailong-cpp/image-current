from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent
src=T/'native/s04_02_resume01.png';w=T/'native/s04_01_curbfix01.png';n=T/'native/s03_02_resume01.png'
im=Image.open(src).convert('RGB');im.paste(Image.open(w).convert('RGB').crop((1024,0,1139,1254)),(0,0));im.paste(Image.open(n).convert('RGB').crop((115,1024,1254,1139)),(115,0))
f=T/'layout-only/s04_02_curbfix01.exact-boundary-guide.png';im.save(f)
p.write_json(f.with_suffix('.png.derivation.json'),{'gameArt':False,'base':{'file':str(src),'sha256':p.sha(src)},'west':{'file':str(w),'sha256':p.sha(w),'sourceCropLTRB':[1024,0,1139,1254],'pasteXY':[0,0]},'north':{'file':str(n),'sha256':p.sha(n),'sourceCropLTRB':[115,1024,1254,1139],'pasteXY':[115,0]},'nativePixelScale':1,'sourceResampled':False},replace=False)

