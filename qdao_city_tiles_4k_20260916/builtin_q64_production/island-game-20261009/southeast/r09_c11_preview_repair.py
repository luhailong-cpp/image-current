from pathlib import Path
from PIL import Image
import sys
from workflow import ROOT,sha,write
name=sys.argv[1]
target=ROOT/'guides'/f'{name}.native-seam-target.png';result=ROOT/'native'/f'{name}.png'
a=Image.open(target).convert('RGB');b=Image.open(result).convert('RGB');a.paste(b.crop((371,115,883,1139)),(371,115))
o=ROOT/'qa'/f'{name}.hard-insert.png';a.save(o)
write(Path(str(o)+'.generation.json'),{'file':o.as_posix(),'sha256':sha(o),'operation':'native hard replacement center512x1024 only, no blending/resampling','crop':[371,115,883,1139],'derivedFrom':[{'file':p.as_posix(),'sha256':sha(p)} for p in [target,result]]})
