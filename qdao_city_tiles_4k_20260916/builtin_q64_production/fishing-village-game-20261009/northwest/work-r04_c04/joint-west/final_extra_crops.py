from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent;O=D/'final-v3'
a=Image.new('RGB',(8192,4096));a.paste(Image.open(O/'r04_c03.joint-proposal.png'),(0,0));a.paste(Image.open(O/'r04_c04.joint-proposal.png'),(4096,0))
items=[]
boxes=[('blue-north-final',[11648,14904,12902,15334]),('blue-west-final',[11448,15104,11878,16358]),('blue-east-final',[12672,15104,13102,16358])]
for k in range(1,4):boxes.append(('west-cross-final-'+str(k),[11968,12288+k*1024-230,12608,12288+k*1024+230]))
for name,b in boxes:
 p=O/(name+'.png');a.crop([b[0]-8192,b[1]-12288,b[2]-8192,b[3]-12288]).save(p);items.append({'file':str(p),'globalBox':b,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unscaled':True})
(O/'extra-diagnostics.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

