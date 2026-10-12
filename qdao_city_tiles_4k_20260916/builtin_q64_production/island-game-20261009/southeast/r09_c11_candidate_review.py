from workflow import ROOT,sha,write,read
from PIL import Image
from pathlib import Path
import shutil
p=ROOT/'tiles/r09_c11.candidate.png';o=ROOT/'qa/r09_c11-candidate-revision02.png';shutil.copy2(p,o)
im=Image.open(p)
for name,box in [('beam',[2816,1460,3328,1972]),('stairs',[2816,3572,3328,4084])]:
 out=ROOT/'qa'/f'r09_c11-final-{name}-revision02.png';im.crop(box).save(out);write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'operation':'unscaled crop','source':p.as_posix(),'sourceSha256':sha(p),'box':box})
