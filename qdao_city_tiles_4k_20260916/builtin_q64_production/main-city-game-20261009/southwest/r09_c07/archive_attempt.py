import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image
p=Path(__file__).parent
r=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
s=Path(r['sourceOutputPath']);id=Path(sys.argv[1]).name.replace('.receipt.json','');dest=p/'pipeline/attempts'/f'{id}.png'
assert not dest.exists();shutil.copy2(s,dest)
data={'sourceOutput':str(s),'preservedNative':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'size':list(Image.open(dest).size),'receipt':sys.argv[1],'status':sys.argv[2]}
(dest.with_suffix('.archive.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data))
