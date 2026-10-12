from pathlib import Path
from PIL import Image
import os,json,hashlib,sys
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent; REV=sys.argv[1] if len(sys.argv)>1 else 'v13'; p=R/f'tiles/r08_c12.candidate-{REV}.png'; im=Image.open(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[]
for axis in ['h','v']:
 for seam in range(1,4):
  for seg in range(4):
   b=[seg*1024,seam*1024-128,(seg+1)*1024,seam*1024+128] if axis=='h' else [seam*1024-128,seg*1024,seam*1024+128,(seg+1)*1024]
   q=R/'qa'/f'r08_c12.{REV}-{axis}{seam}-s{seg+1}.png';im.crop(b).save(q);files.append({'file':str(q),'sha256':sha(q),'sourceCrop':b,'operation':'exact native crop, no resize'})
(R/f'qa/r08_c12.{REV}-seam-evidence.json').write_text(json.dumps({'source':str(p),'sourceSha256':sha(p),'crops':files},indent=2),encoding='utf-8')
print(len(files))

