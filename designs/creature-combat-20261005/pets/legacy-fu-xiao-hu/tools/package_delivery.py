"""Verify the unchanged accepted frames and assemble a portable delivery package."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/'manifest.json');v=read(ROOT/'records/visual-review.json')
assert m['actualFrameCount']==68 and len(m['frames'])==68
assert read(ROOT/'records/source-audit.json')['passed']
assert read(ROOT/'records/preview-audit.json')['passed']
assert v['passed']
rows=[];pixels=set()
for f in m['frames']:
 p=ROOT/f['file'];h=sha(p)
 assert h==f['sha256']==v['frameSHA256'][f['file']]
 im=Image.open(p);im.load()
 assert im.size==(1024,1024) and im.mode=='RGBA'
 assert im.getchannel('A').getextrema()==(0,255)
 bbox=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
 assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<1024 and bbox[3]<1024
 pixel=hashlib.sha256(im.tobytes()).hexdigest()
 assert pixel not in pixels
 pixels.add(pixel);rows.append({'file':f['file'],'sha256':h})
assert len(list((ROOT/'runtime').rglob('*.png')))==68
report={'checkedOnUserDate':'2026-10-08','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'passed':True,'frameCount':68,'framesUnchangedSinceVisualReview':True,'normalAndSlowAnimationsVerified':12,'clientIntegration':'not-performed','frames':rows}
(ROOT/'records/delivery-recheck-20261008.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
out=ROOT/'delivery';out.mkdir(exist_ok=True)
archive=out/'fu-xiao-hu-combat-68frames.zip'
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not p.is_relative_to(out) and '__pycache__' not in p.parts)
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'fu-xiao-hu-combat/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in rows:assert hashlib.sha256(z.read('fu-xiao-hu-combat/'+row['file'])).hexdigest()==row['sha256']
receipt={'file':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'entries':len(files),'runtimeFrames':68,'zipCRC':'passed','archivedRuntimeSHA256':'68/68 matched','checkedOnUserDate':'2026-10-08'}
(out/'package-check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'SHA256SUMS.txt').write_text(receipt['sha256']+'  '+archive.name+'\n',encoding='utf-8')
print(json.dumps(receipt))
