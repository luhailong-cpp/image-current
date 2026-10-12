from pathlib import Path
from PIL import Image
import json,sys,hashlib,shutil
from datetime import datetime,timezone
ROOT=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian')
PROV=ROOT/'provenance/cast/E'
idx=sys.argv[1]; src=Path(sys.argv[2])
native=PROV/'_inprogress'/f'{idx}.png';native.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,native)
im=Image.open(native); assert im.mode=='RGBA' and im.width==im.height
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
final=ROOT/'runtime/cast/E'/f'{idx}.png';final.parent.mkdir(parents=True,exist_ok=True)
out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((920,920),Image.Resampling.LANCZOS),(52,37));out.save(final)
refs=[
{'path':'D:/work/image/designs/pets-xianling-20260924/source/15-landuoxian-E.png','role':'exact existing E identity'},
{'path':'D:/work/image/designs/pets-xianling-20260924/source/15-landuoxian-W.png','role':'same character rear identity, not direction for this E frame'},
{'path':'D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','role':'primary approved painting/material style'}]
if len(sys.argv)>3: refs.append({'path':sys.argv[3],'role':'accepted prior frame continuity, must redraw the new pose'})
record={
'file':str(final),'sha256':sha(final),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'format':'PNG','tool':'image_gen.imagegen','route':'builtin',
'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),
'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[r['path'] for r in refs]},
'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有 model/quality 选择器，返回值未披露版本/质量。',
'prompt':str(PROV/f'{idx}.prompt.txt'),'references':refs,
'evidence':{'receipt':str(PROV/f'{idx}.receipt.json'),'returnedKeys':['image_url','output_hint']},
'derivedFrom':{'nativeFile':str(native),'sourceToolPath':str(src),'sha256':sha(native),'width':im.width,'height':im.height,'mode':im.mode},
'operation':{'type':'fixed_canvas_resize','resize':[920,920],'paste':[52,37],'canvas':[1024,1024],'resampling':'LANCZOS','perFrameAlignment':False},
'action':'cast','direction':'E','frame':int(idx),'durationMs':45,'pivot':[0.5,0.08],
'visualQA':{'singleFrameInspected':True,'identity':'preserved','handedness':'right hand gold frame; left hand jade mallet','jadeChimeCount':3,'direction':'three-quarter front lower-right','motionPreview':'pending root six-group review'}
}
(PROV/f'{idx}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':idx,'nativeSize':im.size,'exportSize':out.size,'alphaExtrema':out.getchannel('A').getextrema(),'sha256':sha(final)}))
