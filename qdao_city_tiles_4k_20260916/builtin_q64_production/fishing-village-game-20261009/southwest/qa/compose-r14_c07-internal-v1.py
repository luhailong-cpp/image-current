import sys,json,hashlib,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=Z/'qa/full-tile-r14_c07-assembly.json';j=json.loads(a.read_text())
jobs=json.loads((Z/'qa/r14_c07-localrepair-jobs-v1.json').read_text())
repairs=[]
for item in jobs:
 p=Z/f"native/{item['stem']}.png";r=Path(str(p)+'.generation.json')
 repairs.append({k:item[k] for k in ['id','tileContextBox','repairBounds','margin','source']}|{'repair':{'path':p.as_posix(),'sha256':sha(p)},'generationRecord':{'path':r.as_posix(),'sha256':sha(r)}})
m=Z/'qa/repair-r14_c07-internal-v1.manifest.json'
with m.open('x',encoding='utf-8') as f:json.dump({'schemaVersion':1,'outputPrefix':'repair-r14_c07-internal-v1','baseAssembly':{'path':a.as_posix(),'sha256':sha(a)},'expectedBaseCandidateSha256':j['output']['sha256'],'repairs':repairs},f,indent=2)
subprocess.run([sys.executable,'-B',str(Z/'qa/repair-compose.py'),'--manifest',str(m)],check=True)
trace=json.loads((Z/'qa/repair-r14_c07-internal-v1-trace.json').read_text())
with Image.open(trace['candidate']['path']) as im:
 for item in jobs:
  p=Z/f"qa/repair-r14_c07-internal-v1-{item['id']}-after-100pct.png"
  with p.open('xb') as f: im.crop(item['tileContextBox']).save(f,format='PNG')
print(json.dumps({'trace':trace['candidate'],'repairs':len(jobs)}))
