import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/'provenance'/'attack'
direction,frame=sys.argv[1:3]
receipt_path=PROV/direction/(frame+'.receipt.json')
receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
src=Path(receipt['sourcePath'])
native=PROV/'_inprogress'/direction/(frame+'.png')
native.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,native)
im=Image.open(native)
if im.width!=im.height: raise ValueError('Non-square native requires review')
if im.mode!='RGBA' or im.getextrema()[3][0]!=0: raise ValueError('Native genuine alpha missing')
canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
canvas.alpha_composite(im.resize((920,920),Image.Resampling.LANCZOS),(52,37))
dest=ROOT/'runtime'/'attack'/direction/(frame+'.png')
dest.parent.mkdir(parents=True,exist_ok=True)
canvas.save(dest)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[{'file':p,'role':role,'sha256':sha(Path(p))} for p,role in zip(receipt['submittedParameters']['referenced_image_paths'],['original E identity','original W identity','main painting/material style','approved same-direction frame for continuity'])]
record={'file':str(dest),'sha256':sha(dest),'generatedAt':receipt['completedAt'],'native':{'file':str(native),'sha256':sha(native),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format},'width':1024,'height':1024,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((PROV/'config-snapshot.json').read_text(encoding='utf-8-sig')),'submittedParameters':receipt['submittedParameters'],'actualModel':None,'actualQuality':None,'evidence':{'receipt':str(receipt_path),'returnedKeys':receipt['returnedKeys']},'unverifiedReason':'Host managed; tool exposes no model/quality selector and does not disclose actual model/quality metadata.','prompt':str(PROV/direction/(frame+'.prompt.txt')),'references':refs,'operation':{'type':'uniform-export','description':'Whole native square resized to 920x920 with Lanczos, alpha composited into transparent 1024x1024 at (52,37); no per-frame bbox alignment.'},'derivedFrom':{'file':str(native),'sha256':sha(native)},'action':'attack','direction':direction,'frame':int(frame),'durationMs':30,'pivot':[0.5,0.08],'visualReview':{'static':'inspected-tool-image','animation':'pending root review'}}
(dest.with_suffix('.png.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'native':[im.width,im.height],'mode':im.mode,'alphaExtrema':canvas.getextrema()[3],'sha256':sha(dest)}))
