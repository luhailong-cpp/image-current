from pathlib import Path
import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;R=W.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sources=read(W/'plan.json')['northBoundary'];a=np.asarray(Image.open(sources[0]['file']).convert('RGB'));ids=np.ones((1254,1254),dtype=np.uint8);seams=[]
for i,e in enumerate(sources[1:],2):
 a,ids,s=m.append_hard(a,ids,np.asarray(Image.open(e['file']).convert('RGB')),np.ones((1254,1254),dtype=np.uint8)*i,f'north-col{i-1}-to-{i}');seams.append(s)
p=W/'guides/r04_c03.north-band.png';Image.fromarray(a[1024:1254]).save(p);Image.fromarray(ids[1024:1254]).save(W/'guides/r04_c03.north-band-ids.png')
record={'file':str(p),'sha256':sha(p),'nativeSize':[4326,230],'globalNativeBox':[8077,12173,12403,12403],'sources':sources,'method':'same row-native exact minimum-error hard cuts used by r03 tile assembler; no blending/scaling','paths':seams}
Path(str(p)+'.derivation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'file':str(p),'sha256':sha(p)}))
