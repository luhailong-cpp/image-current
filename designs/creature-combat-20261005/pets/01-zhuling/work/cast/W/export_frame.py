from pathlib import Path
from PIL import Image
import json,hashlib,sys,datetime
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/01-zhuling')
frame=sys.argv[1]; source=Path(sys.argv[2])
record_path=root/'records/cast/W'/f'{frame}.generation.json'
rec=json.loads(record_path.read_text(encoding='utf-8'))
im=Image.open(source); native={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
rawsha=hashlib.sha256(source.read_bytes()).hexdigest()
out=root/'runtime/cast/W'/f'{frame}.png'
assert im.width==im.height
scaled=im.convert('RGBA').resize((820,820),Image.Resampling.LANCZOS)
im=Image.new('RGBA',(1024,1024),(0,0,0,0))
im.alpha_composite(scaled,(102,102))
im.save(out)
a=im.getchannel('A'); hist=a.histogram()
rec.update({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native':native,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','sourcePath':str(source),'sourceSha256':rawsha,'operation':'whole-canvas uniform Lanczos resize to 1024; no crop, translation or per-frame registration' if native['width']!=1024 else 'preserve generated RGBA; no registration','alphaExtrema':a.getextrema(),'alphaBBox':a.getbbox(),'transparentPixelCount':hist[0],'partialAlphaPixelCount':sum(hist[1:255]),'clientValidation':'not performed'})
rec['operation']='whole native canvas uniformly resized to 820x820 with Lanczos, alpha-composited at (102,102) on 1024x1024 transparent canvas; same transform for every frame, no bbox/foot alignment'
rec['exportTransform']={'nativeCanvasResize':[820,820],'canvas':[1024,1024],'offset':[102,102]}
rec['configSnapshot']=json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
record_path.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':frame,'native':native,'output':str(out),'sha256':rec['sha256'],'bbox':rec['alphaBBox'],'alpha':rec['alphaExtrema']}))
