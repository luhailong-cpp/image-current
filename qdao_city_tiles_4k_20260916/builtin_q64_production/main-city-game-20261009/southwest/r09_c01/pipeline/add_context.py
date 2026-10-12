from pathlib import Path
from PIL import Image
import hashlib,json,sys
q=Path(sys.argv[1]); p=Path(sys.argv[2])
d=json.loads(q.read_text(encoding='utf-8-sig'))
assert len(d['referenced_image_paths'])==4
d['referenced_image_paths'].append(str(p))
d['references'].append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'native approved wholecity crop semantic context only; do not enlarge for final art','pixels':list(Image.open(p).size)})
q.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(str(q))
