"""Archive a builtin receipt without depending on unrelated global model settings."""
from pathlib import Path
import argparse,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--stem',required=True);a=ap.parse_args()
rp=Z/'receipts'/f'{a.stem}.receipt.json';r=json.loads(rp.read_text(encoding='utf-8-sig'))
assert r['tool']=='image_gen.imagegen' and r['route']=='builtin'
src=Path(r['generatedFile']);dst=Z/'native'/f'{a.stem}.png';gp=Path(str(dst)+'.generation.json')
assert not gp.exists()
im=Image.open(src);assert im.size==(1254,1254) and im.format=='PNG'
prompt=Path(r['submitted']['promptFile']);assert prompt.is_file()
refs=json.loads((Z/'guides'/f'{a.stem}.references.json').read_text(encoding='utf-8-sig'));refs=refs if isinstance(refs,list) else refs['inputs']
assert r['submitted']['referenced_image_paths']==[x['path'] for x in refs]
for x in refs:assert sha(x['path'])==x['sha256']
if dst.exists():assert sha(src)==sha(dst)
else:shutil.copy2(src,dst)
d=dict(file=dst.as_posix(),sha256=sha(dst),generatedAt=datetime.now(timezone.utc).isoformat(),nativeWidth=1254,nativeHeight=1254,format='PNG',sourceOutputPath=src.as_posix(),sourceOutputSha256=sha(src),tool='image_gen.imagegen',route='builtin',configSnapshot=None,submittedParameters=dict(model=None,quality=None,transparent_background=False),actualModel=None,actualQuality=None,unverifiedReason='Builtin tool does not disclose model/quality; no global-config claim.',prompt=prompt.as_posix(),promptSha256=sha(prompt),references=refs,evidence=dict(receipt=rp.as_posix()),resizedAfterGeneration=False,finalArtUpscaled=False,status='candidate_pending_native_visual_and_seam_QA')
with gp.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(file=dst.as_posix(),sha256=sha(dst),record=gp.as_posix())))

