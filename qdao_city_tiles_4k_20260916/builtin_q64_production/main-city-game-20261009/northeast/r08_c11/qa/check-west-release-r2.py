from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parents[1];s=p/'native/p41-v20261013-r2fix1.png';w=p.parent/'r08_c10/native/p44-v20261012-v2.png';im=Image.new('RGB',(300,1024));im.paste(Image.open(w).convert('RGB').crop((989,115,1139,1139)),(0,0));im.paste(Image.open(s).convert('RGB').crop((115,115,265,1139)),(150,0));o=p/'qa/p41-west-shared-r2fix1.png';assert not o.exists();im.save(o);print(str(o))
