import argparse,json,shutil,subprocess,sys,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('receipt');args=p.parse_args()
rp=(ROOT/args.receipt).resolve();assert rp.is_relative_to(ROOT/'sources')
r=json.loads(rp.read_text(encoding='utf-8'))
dest=(ROOT/r['draftPath']).resolve();assert dest.is_relative_to(ROOT/'drafts') and r['action'] in ('hit','attack','cast')
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():raise RuntimeError('Refuse overwrite '+str(dest))
shutil.copyfile(r['output']['toolReturnedPath'],dest)
im=Image.open(dest);im.load()
if min(im.size)<1024 or im.mode!='RGBA':raise RuntimeError('Native size or RGBA check failed; keep actual output for review')
r['output'].update({'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'nativeFrameSize':list(im.size),'mode':im.mode,'alphaExtrema':list(im.getchannel('A').getextrema())})
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'tools/record_frame.py'),r['draftPath'],args.receipt,r['promptFile']],check=True)
print(json.dumps({'file':str(dest),'nativeFrameSize':list(im.size),'actualModel':None,'actualQuality':None}))

