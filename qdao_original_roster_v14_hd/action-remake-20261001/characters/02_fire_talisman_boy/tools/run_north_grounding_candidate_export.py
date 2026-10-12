import argparse,datetime,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('key')
a=p.parse_args()
reqpath=R/'records'/f'{a.key}.request.json'
receiptpath=R/'records'/f'{a.key}.receipt.json'
req=json.loads(reqpath.read_text(encoding='utf-8'))
receipt=json.loads(receiptpath.read_text(encoding='utf-8'))
hint=receipt.get('output_hint','')
matches=re.findall(r'as (.*?[.]png) by default',hint)
if not matches: raise RuntimeError('No exact native path from output_hint')
src=Path(matches[0])
assert src.is_file()
slot=req['slot'].split('/')
outdir=R/'work'/'grounding-v2'/'north'/slot[1]
outdir.mkdir(parents=True,exist_ok=True)
native=outdir/f'{a.key}.native.png'
out=outdir/f'{a.key}.png'
assert not out.exists(), 'Do not overwrite existing candidate'
shutil.copy2(src,native)
im=Image.open(native)
assert im.width>=1024 and im.height>=1024 and im.width==im.height
assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={**req,'status':'candidate_exported_pending_visual_root_review','generatedAt':receipt['receivedAt'],'file':str(out),'sha256':sha(out),'width':1024,'height':1024,'format':'PNG','native':{'file':str(native),'hostPath':str(src),'sha256':sha(src),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具返回仅image_url/output_hint，未披露实际型号/质量。','evidence':{'request':str(reqpath),'receipt':str(receiptpath),'output_hint':hint},'operation':'whole square canvas LANCZOS resize to 1024; no bbox scaling, translation, mirroring or interpolation of poses'}
for ref in record['references']:
 ref['sha256']=sha(Path(ref['path']))
out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':record['sha256'],'nativeSize':list(im.size),'nativeSha256':sha(native)}))

