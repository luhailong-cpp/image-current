from pathlib import Path
import json,hashlib,shutil,sys
from PIL import Image
import numpy as np
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;id=sys.argv[1];src=Path(sys.argv[2]);base=id.split('.')[0]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=read(D/'prompts'/f'{id}.request.json');old=read(D/'native'/f'{base}.png.generation.json')
for ref in req['references']:assert sha(ref['file'])==ref['sha256']
im=Image.open(src);assert im.size==(1254,1254);dest=D/'native'/f'{id}.png';assert not dest.exists();shutil.copyfile(src,dest)
old.update(id=id,file=str(dest),sha256=sha(dest),sourceOutput=str(src),sourceOutputSha256=sha(src),generatedAtUtc=datetime.now(timezone.utc).isoformat(),mode=im.mode,pngMetadata=dict(im.info),prompt=req['promptFile'],promptSha256=req['promptSha256'],request=str(D/'prompts'/f'{id}.request.json'),references=req['references'],receipt=str(D/'receipts'/f'{id}.receipt.json'),previousRepairNative=req['previousRepairNative'],visualQa='pending',selected=False,fixedBandMeasurements={})
new=np.array(im.convert('RGB'));orig=np.array(Image.open(req['targetOriginal']['file']).convert('RGB'));prev=np.array(Image.open(req['previousRepairNative']['file']).convert('RGB'))
for k,a,b in [('top230VsPreviousRepair',new[:230],prev[:230]),('bottom230VsOriginal',new[1024:],orig[1024:])]:
 diff=np.abs(a.astype(np.int16)-b.astype(np.int16));old['fixedBandMeasurements'][k]={'pixelExact':bool(np.array_equal(a,b)),'meanAbsoluteChannelDifference':float(diff.mean()),'differentPixels':int(np.count_nonzero(np.any(a!=b,axis=2)))}
(D/'native'/f'{id}.png.generation.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':id,'file':str(dest),'sha256':sha(dest),'bands':old['fixedBandMeasurements']},indent=2))
