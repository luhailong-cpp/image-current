from pathlib import Path
import json,sys,subprocess,hashlib
from PIL import Image
B=Path(__file__).resolve().parent.parent;R=B/'records'
n=sys.argv[1];src=Path(sys.argv[2]);out=B/'runtime/attack/W'/f'{n}.png'
for suffix,kind in [('.generation.json','export'),('.native.generation.json','native')]:
 p=out.with_suffix('.png'+suffix); d=json.loads(p.read_text(encoding='utf8'))
 d['disposition']='rejected: returned to guard prematurely; replaced by repair1'
 d['replacedBy']=f'runtime/attack/W/{n}.png'
 if kind=='native':
  d['prompt']=f'records/attack-W-{n}-candidate.prompt.txt'
  d['evidence']['toolReceipt']=f'records/attack-W-{n}-candidate.receipt.json'
 else:d['derivedFrom']['generationRecord']=f'records/attack-W-{n}-candidate.native.json'
 (R/f'attack-W-{n}-candidate.{kind}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
for ext in ['prompt.txt','receipt.json']:
 p=R/f'attack-W-{n}.{ext}';q=R/f'attack-W-{n}-candidate.{ext}'
 assert p.resolve().parent==R.resolve() and q.resolve().parent==R.resolve()
 if p.exists():p.rename(q)
subprocess.run([sys.executable,str(B/'tools/import_frame.py'),'--input',str(src),'--output',f'runtime/attack/W/{n}.png','--receipt',f'records/attack-W-{n}-repair1.receipt.json','--prompt',f'records/attack-W-{n}-repair1.prompt.txt'],check=True)
im=Image.open(out);assert im.mode=='RGBA' and im.size==(1024,1024)
print('replacement and candidate text saved',n,hashlib.sha256(out.read_bytes()).hexdigest())

