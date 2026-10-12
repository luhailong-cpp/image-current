import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,shutil,datetime
Z=Path(__file__).resolve().parents[1]
p=Z/'native/r08_c05_p01_01_v1.png.generation.json'
bak=Z/'qa/r08_c05_p01_01_v1-generation-before-rejection.json';assert not bak.exists();shutil.copyfile(p,bak)
a=json.loads(p.read_text(encoding='utf-8'));a['status']='rejected';a['rejectionReason']='Invented boats, fish and pier outside approved layout in upper-right. Retained source only; do not use as overlap anchor.';a['reviewedAtUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8')
src=(Z/'qa/r08c05-production.py').read_text(encoding='utf-8').replace('Fish-market stock must be fish inside existing trays/tubs, never folded cloth merchandise. ','')
out=Z/'qa/r08c05-production-v2.py';assert not out.exists();out.write_text(src,encoding='utf-8')

