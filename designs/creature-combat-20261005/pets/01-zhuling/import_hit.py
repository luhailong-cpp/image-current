"""Persist an actual builtin AI output; uniform whole-canvas export, never pose creation."""
from pathlib import Path
from PIL import Image
import json, hashlib, sys
ROOT=Path(__file__).resolve().parent
direction, number, source=sys.argv[1:4]
action=sys.argv[4] if len(sys.argv)>4 else 'hit'
assert direction in ('E','W') and action in ('hit','attack') and 1<=int(number)<=(6 if action=='hit' else 12)
stem=f'{int(number):02}'
src=Path(source)
out=ROOT/'runtime'/action/direction/(stem+'.png')
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src).convert('RGBA')
assert im.width==im.height
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
native_size=im.size
# A single fixed transform for every direction and action, no per-frame alignment.
canvas=Image.new('RGBA',(1024,1024))
canvas.alpha_composite(im.resize((820,820),Image.Resampling.LANCZOS),(102,102))
canvas.save(out)
receipt_path=ROOT/'records'/action/direction/(stem+'.receipt.json')
receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
cfg=json.loads((ROOT.parents[3]/'config'/'image-generation.json').read_text(encoding='utf-8'))
record={'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'generatedAt':receipt['returnedAt'],'format':'PNG','width':1024,'height':1024,'nativeWidth':native_size[0],'nativeHeight':native_size[1],
 'tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,
 'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,
 'unverifiedReason':receipt['unverifiedReason'],'prompt':f'prompts/{action}/{direction}/{stem}.txt',
 'references':[{'path':p,'role':('direction identity' if i==0 else 'opposite identity' if i==1 else 'main painterly finish')} for i,p in enumerate(receipt['submittedParameters']['referenced_image_paths'])],
 'evidence':{'receipt':receipt_path.relative_to(ROOT).as_posix(),'metadataKeys':list(Image.open(src).info)},
 'derivedFrom':{'originalPath':str(src),'sha256':source_sha,'nativeWidth':native_size[0],'nativeHeight':native_size[1]},
 'operation':{'type':'uniform whole canvas scale and transparent padding','resizedCanvas':[820,820],'offset':[102,102],'outputCanvas':[1024,1024],'perFrameAlignment':False},
 'visualStatus':'pending final sequence review'}
out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':record['sha256'],'native':native_size,'alphaBBox':canvas.getbbox()},ensure_ascii=False))
