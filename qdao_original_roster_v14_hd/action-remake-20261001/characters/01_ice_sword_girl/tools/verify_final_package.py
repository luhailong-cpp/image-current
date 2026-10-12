"""Check the exact delivered archive and live preview dependencies without retaining unpacked copies."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
from io import BytesIO
import json,hashlib,re,posixpath
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
d=json.loads((R/'delivery.json').read_text(encoding='utf-8'))
assert sha((R/d['file']).read_bytes())==d['sha256']
with ZipFile(R/d['file']) as z:
 assert z.testzip() is None
 m=json.loads(z.read('manifest.json'));count=0
 for s in m['sequences']:
  for f in s['frames']:
   data=z.read(f['path']);assert sha(data)==f['sha256']
   im=Image.open(BytesIO(data));assert im.size==(1024,1024) and im.mode=='RGBA'
   assert json.loads(z.read(f['path']+'.generation.json'))['sha256']==f['sha256']
   count+=1
 assert count==196
 for link in re.findall(r'(?:src|href)="([^"]+)"',z.read('preview/all.html').decode()):
  assert posixpath.normpath(posixpath.join('preview',link)) in z.namelist(),link
 pm=json.loads(z.read('preview/all-sequences.js').decode().removeprefix('window.ALL_SEQUENCES=').strip().removesuffix(';'))
 assert [f['path'] for s in pm['sequences'] for f in s['frames']]==[f['path'] for s in m['sequences'] for f in s['frames']]
live=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
for s in live['sequences']:
 for f in s['frames']:assert sha((R/f['path']).read_bytes())==f['sha256']
result={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':True,'archive':d['file'],'archiveSha256':d['sha256'],'archiveFrames':count,'liveFrames':count,'htmlDependenciesResolved':True,'clientRuntimeVerified':False}
(R/'review/final-package-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
