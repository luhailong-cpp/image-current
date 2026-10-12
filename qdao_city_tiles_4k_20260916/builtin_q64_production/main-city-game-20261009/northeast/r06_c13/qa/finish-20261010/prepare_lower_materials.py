from pathlib import Path
from PIL import Image
import json,hashlib
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
basepath=HERE/'inputs/base-with-north-repairs.png';im=Image.open(basepath).convert('RGB')
for case,origin in [('roof-left-upper-v1',[49549,22300]),('roof-left-lower-v1',[49549,23322])]:
    x,y=origin;crop=[x-49152,y-20480,x-49152+1254,y-20480+1254]
    path=HERE/'inputs'/f'{case}.png';assert not path.exists();im.crop(crop).save(path)
    rec={'id':case,'context':str(path),'sha256':sha(path),'contextWorldBox':[x,y,x+1254,y+1254],'editContextBox':[400,20,860,1234],'composition':[{'file':str(basepath),'sha256':sha(basepath),'crop':crop,'paste':[0,0]}],'operation':'exact native/candidate pixel crop; no resize'}
    (HERE/'records'/f'{case}.input.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(path)
