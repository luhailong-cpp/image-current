from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parents[1];out=p/'qa/p44-east-shared-r2.png';assert not out.exists()
new=p/'native/p44-v20261013-r2.png';other=p.parent/'r08_c12/native/p41-v20261012.png'
a=Image.open(new).convert('RGB').crop((989,115,1139,1139));b=Image.open(other).convert('RGB').crop((115,115,265,1139));im=Image.new('RGB',(300,1024));im.paste(a,(0,0));im.paste(b,(150,0));im.save(out)
print(str(out))
