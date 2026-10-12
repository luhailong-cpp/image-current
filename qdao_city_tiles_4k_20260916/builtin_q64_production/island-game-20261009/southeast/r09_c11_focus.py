from PIL import Image
from workflow import ROOT,sha,write
from pathlib import Path
for name,box in [('r09_c11-p23v03-p24v01',(0,550,512,1062)),('r09_c11-p43v03-p44',(0,500,512,1012))]:
 p=ROOT/'qa'/f'{name}.hard-seam-100pct.png';o=ROOT/'qa'/f'{name}.focus.png';Image.open(p).crop(box).save(o);write(Path(str(o)+'.generation.json'),{'file':o.as_posix(),'sha256':sha(o),'operation':'unscaled crop','source':p.as_posix(),'sourceSha256':sha(p),'crop':box})
