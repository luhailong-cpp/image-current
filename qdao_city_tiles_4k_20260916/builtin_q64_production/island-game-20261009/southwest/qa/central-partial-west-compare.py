from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path.cwd();P='central-partial-r11c04-rows12-resume-v01'
b=[14225,42730,14445,43008]
rows=[]
for name,path,origin in [('candidate',R/'qa'/f'{P}-native.png',[12288,40960]),('s02_02',R/'native/r11_c04_s02_02_v01.png',[13197,41869]),('s02_03',R/'native/r11_c04_s02_03_v01.png',[14221,41869])]:
    p=R/'qa'/f'{P}-west-compare-{name}.png'
    Image.open(path).crop((b[0]-origin[0],b[1]-origin[1],b[2]-origin[0],b[3]-origin[1])).save(p)
    rows.append({'source':name,'path':str(p),'sourcePath':str(path),'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'globalBox':b,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'qa'/f'{P}-west-compare.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))

