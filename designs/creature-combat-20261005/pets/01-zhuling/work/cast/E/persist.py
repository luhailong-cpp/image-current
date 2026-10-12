import json,sys,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(r'D:/work/image/designs/creature-combat-20261005/pets/01-zhuling')
frame=sys.argv[1]
receipt_path=ROOT/'records/cast/E'/f'{frame}.receipt.json'
receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
src=Path(sys.argv[2]); im=Image.open(src); im.load()
native={'path':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode}
if im.width!=im.height: raise ValueError('non-square native output')
out=ROOT/'runtime/cast/E'/f'{frame}.png'; out.parent.mkdir(parents=True,exist_ok=True)
scaled=im.convert('RGBA').resize((820,820),Image.Resampling.LANCZOS)
outim=Image.new('RGBA',(1024,1024),(0,0,0,0))
outim.paste(scaled,(102,102))
outim.save(out)
alpha=outim.getchannel('A')
refs=[]
for i,path in enumerate(receipt['referenced_image_paths']):
 p=Path(path)
 refs.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'purpose':['E identity and direction','W supplementary identity only','primary painterly style/material','previous accepted frame continuity'][min(i,3)]})
record={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'generatedAt':receipt['completedAt'],'action':'cast','direction':'E','frame':int(frame),'durationMs':45,'pivot':[0.5,0.08],'event':'release' if int(frame)==10 else None,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','native':native,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path(r'D:/work/image/config/image-generation.json').read_text()),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':receipt['referenced_image_paths'],'promptFile':str(ROOT/'prompts/cast/E'/f'{frame}.txt')},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in tool exposes no model/quality selectors and discloses neither actual model nor actual quality. Prompt target and official page are not result evidence.','evidence':{'receipt':str(receipt_path),'outputHint':receipt['output_hint']},'prompt':str(ROOT/'prompts/cast/E'/f'{frame}.txt'),'references':refs,'derivedFrom':native,'operation':'fixed transform for every frame: native complete canvas uniformly resampled to 820x820 LANCZOS, placed at (102,102) in 1024 transparent canvas; no per-frame alignment/crop/mirror/animation interpolation','alphaExtrema':alpha.getextrema(),'alphaBBox':alpha.getbbox(),'visualStatus':receipt.get('visualStatus','pending'),'visualNotes':receipt.get('visualNotes',[])}
path=ROOT/'records/cast/E'/f'{frame}.generation.json'; path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'nativeSize':im.size,'alphaExtrema':alpha.getextrema(),'bbox':alpha.getbbox(),'sha256':record['sha256']},ensure_ascii=False))
