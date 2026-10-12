from pathlib import Path
import json,hashlib,argparse
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args()
ip=Z/'guides'/f'{a.stem}.input.json';d=json.loads(ip.read_text(encoding='utf8'))
src=Z/'native'/f'{a.stem}.png';im=Image.open(src).convert('RGB')
o=Z/'qa'/f'{a.stem}_quick_native_v1';o.mkdir(exist_ok=False)
items=[]
for n in d.get('neighbor',[]):
 ni=Image.open(n['path']).convert('RGB');di=n['direction']
 if di=='top':
  out=Image.new('RGB',(1024,512));out.paste(ni.crop((115,883,1139,1139)),(0,0));out.paste(im.crop((115,115,1139,371)),(0,256))
 elif di=='left':
  out=Image.new('RGB',(512,1024));out.paste(ni.crop((883,115,1139,1139)),(0,0));out.paste(im.crop((115,115,371,1139)),(256,0))
 elif di=='right':
  out=Image.new('RGB',(512,1024));out.paste(im.crop((883,115,1139,1139)),(0,0));out.paste(ni.crop((115,115,371,1139)),(256,0))
 else:continue
 path=o/f'{di}_native_join.png';out.save(path)
 items.append({'direction':di,'path':path.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'neighbor':n['path'],'neighborSha256':hashlib.sha256(Path(n['path']).read_bytes()).hexdigest(),'imageSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scale':1,'seamLocalCoordinate':256})
(o/'index.json').write_text(json.dumps({'stem':a.stem,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'quick native layout and adjacent edge review; not whole-tile closure','mechanicalOnly':True,'items':items},indent=2)+'\n')
print(json.dumps(items))

