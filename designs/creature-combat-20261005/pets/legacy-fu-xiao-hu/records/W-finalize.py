import json,hashlib,sys
from pathlib import Path
from PIL import Image
p=Path(sys.argv[1]); data=json.loads(p.read_text(encoding='utf-8-sig')); src=Path(data['sourceFile']); dest=Path(data['targetFile'])
raw=src.read_bytes(); im=Image.open(src); im.load(); native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'sha256':hashlib.sha256(raw).hexdigest()}
if data.get('type')=='frame':
    if im.size!=(1254,1254): raise RuntimeError(f'Unexpected native size {im.size}; fixed W export expects 1254')
    out=im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True,exist_ok=True); out.save(dest)
    data['derivedFrom']={'sourcePath':str(src),'sha256':native['sha256'],'native':native}
    data['operation']={'name':'uniform whole-canvas resize','sourceSize':[1254,1254],'destinationSize':[1024,1024],'filter':'Lanczos','translation':[0,0],'perFrameAlignment':False}
else: out=Image.open(dest)
data.update({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'width':out.width,'height':out.height,'format':'PNG','mode':out.mode,'native':native,'alphaRange':list(out.getchannel('A').getextrema()),'bboxAlphaNonzero':list(out.getchannel('A').getbbox()),'evidence':{'receipt':str(p),'fields':['receipt.output_hint'],'modelQualitySelectorsExposed':False}})
record=dest.with_suffix(dest.suffix+'.generation.json'); record.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'record':str(record),'size':out.size,'alpha':data['alphaRange'],'sha256':data['sha256']},ensure_ascii=False))

