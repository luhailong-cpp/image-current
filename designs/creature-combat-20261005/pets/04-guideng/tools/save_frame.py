from pathlib import Path
import sys, json, hashlib
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
record_path = Path(sys.argv[1]).resolve()
assert record_path.is_relative_to(BASE)
r = json.loads(record_path.read_text(encoding='utf-8-sig'))
source = Path(r['nativeFile'])
dest = BASE / r['file']
assert dest.resolve().is_relative_to(BASE)
dest.parent.mkdir(parents=True, exist_ok=True)
im = Image.open(source)
r['nativeWidth'],r['nativeHeight'] = im.size
r['nativeFormat'],r['nativeMode'] = im.format, im.mode
r['nativeSha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
rgba=im.convert('RGBA')
if rgba.size != (1024,1024):
    assert rgba.width == rgba.height, 'Non-square source requires review, no adaptive crop'
    rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
r['operation'] = {'type':'full-canvas-uniform-resize','from':[im.width,im.height],'to':[1024,1024],'filter':'Lanczos','perFrameAlignment':False}
rgba.save(dest)
r['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
r['width'],r['height'],r['format'],r['mode']=1024,1024,'PNG','RGBA'
alpha=rgba.getchannel('A')
r['alphaExtrema']=alpha.getextrema()
r['alphaBBox']=alpha.getbbox()
r['derivedFrom']={'path':str(source),'sha256':r['nativeSha256'],'record':str(record_path.relative_to(BASE)).replace('\\','/')}
record_path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dest),'native':im.size,'alpha':r['alphaExtrema'],'bbox':r['alphaBBox'],'sha256':r['sha256']},ensure_ascii=False))
