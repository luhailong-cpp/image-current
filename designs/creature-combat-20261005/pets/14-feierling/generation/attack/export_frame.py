from PIL import Image
from pathlib import Path
import hashlib,json,sys,shutil
base=Path(__file__).resolve().parents[2]
meta_path=Path(sys.argv[1])
meta=json.loads(meta_path.read_text(encoding='utf-8-sig'))
source=Path(meta['nativePath'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[]
for r in meta['references']:
    p=Path(r['path']); refs.append(dict(r,sha256=sha(p)))
native_saved=meta_path.parent/(meta['frame']+'.native.png')
shutil.copy2(source,native_saved)
meta['nativeSavedPath']=str(native_saved)
out=base/'runtime'/'attack'/meta['direction']/(meta['frame']+'.png')
out.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(source) as im:
    native={'path':str(source),'sha256':sha(source),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
    rgba=im.convert('RGBA')
    if rgba.size!=(1024,1024): rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
    rgba.save(out)
    alpha=rgba.getchannel('A')
    a=alpha.histogram()
    exported={'file':str(out),'sha256':sha(out),'width':1024,'height':1024,'mode':'RGBA','alphaMinMax':alpha.getextrema(),'transparentPixels':a[0],'partialAlphaPixels':sum(a[1:255]),'opaquePixels':a[255],'alphaBBox':alpha.getbbox()}
meta.update(native=native,exported=exported,references=refs,derivedFrom={'path':str(source),'sha256':native['sha256']},operation='whole-canvas uniform resize to 1024x1024 with LANCZOS; no crop, alignment, mirroring, interpolation or pose synthesis',durationMs=30,pivot=[0.5,0.08],action='attack',actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露 model/quality；configSnapshot 为目标，不等于实际提交或返回参数',configSnapshot=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')))
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(exported,ensure_ascii=False))
