import argparse, hashlib, json, re, shutil
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('request')
p.add_argument('receipt')
p.add_argument('output')
a=p.parse_args()
request_path=(ROOT/a.request).resolve()
receipt_path=(ROOT/a.receipt).resolve()
out=(ROOT/a.output).resolve()
for path in (request_path,receipt_path,out):
    if not path.is_relative_to(ROOT): raise ValueError('Outside character scope')
req=json.loads(request_path.read_text(encoding='utf-8-sig'))
receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
hint=receipt.get('output_hint','')
paths=re.findall(r'[A-Za-z]:[^\r\n]*?\.png',hint)
if not paths: raise RuntimeError('Tool receipt has no PNG path')
src=Path(paths[-1].split(' as ')[-1])
out.parent.mkdir(parents=True,exist_ok=True)
if not out.exists(): shutil.copy2(src,out)
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
if sha(src)!=sha(out):raise RuntimeError('Source-copy SHA mismatch')
im=Image.open(out); im.load()
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
params=req.get('submittedParameters',req)
references=[{'path':r,'sha256':sha(r),'role':'primary approved style' if '/designs/' in r else 'identity/direction/pose reference'} for r in params.get('referenced_image_paths',[])]
record={'file':str(out),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'userTimezone':'America/New_York','generatedAtMeaning':'received/copied time','width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{**params,'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未披露实际型号和质量。','evidence':{'toolResult':str(receipt_path),'hostPath':str(src),'hostSHA256':sha(src)},'prompt':str(request_path),'references':references,'reviewStatus':'pending_sequence_review','nativeHD':min(im.size)>=1024,'operation':'verbatim copy of native tool output'}
Path(str(out)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out),'size':im.size,'mode':im.mode,'alpha':im.getextrema()[-1]},ensure_ascii=False))

