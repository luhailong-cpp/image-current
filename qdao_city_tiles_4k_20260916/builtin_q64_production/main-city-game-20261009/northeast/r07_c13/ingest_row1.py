"""Ingest owned first-row native, with explicit request stem for retained retries."""
from pathlib import Path
import json,hashlib,shutil,sys,importlib.util
from datetime import datetime,timezone
from PIL import Image
HERE=Path(__file__).resolve().parent;ZONE=HERE.parent
patch,stem,source=sys.argv[1:];assert patch in ['p11','p12','p13','p14'] and (stem==patch or stem.startswith(patch+'-'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
dest=HERE/'native'/f'{patch}.png';assert not dest.exists()
im=Image.open(source);im.load();assert im.format=='PNG' and im.size==(1254,1254) and im.mode in ('RGB','RGBA')
if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
request=HERE/'prompts'/f'{stem}.request.json';prompt=HERE/'prompts'/f'{stem}.prompt.txt';receipt=HERE/'receipts'/f'{stem}.receipt.json'
req=read(request);txt=prompt.read_text(encoding='utf-8');assert txt in [req['prompt'],req['prompt']+'\n'];read(receipt)
refs=[{'file':v,'sha256':sha(v),'role':role} for v,role in zip(req['referenced_image_paths'],req['referenceRoles'])];assert len(refs) in (4,5)
coord=next(v for v in read(HERE/'coordinates.json')['patches'] if v['id']==patch)
spec=importlib.util.spec_from_file_location('row1_production_readonly',ZONE/'production.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
shutil.copy2(source,dest);assert sha(dest)==sha(source)
record={'file':str(dest),'sha256':sha(dest),'generatedAt':datetime.now(timezone.utc).isoformat(),'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','tool':'image_gen','route':'builtin','sourceOutputPath':source,'sourceOutputByteIdentical':True,'configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image_gen did not disclose actual model/quality.','prompt':str(prompt),'request':str(request),'references':refs,'evidence':str(receipt),'coordinates':coord,'dimensionsMatch1254Plan':True,'resized':False,'requestVariant':stem,'status':'native-candidate-awaiting-row-seam-review'}
Path(str(dest)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'patch':patch,'requestVariant':stem,'file':str(dest),'sha256':sha(dest),'nativeSize':[1254,1254]},ensure_ascii=False))
