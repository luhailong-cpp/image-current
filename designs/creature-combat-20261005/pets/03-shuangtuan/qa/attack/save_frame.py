from pathlib import Path
from PIL import Image
import json, hashlib, shutil, re, sys
root=Path(__file__).resolve().parents[2]
direction, frame=sys.argv[1:3]
reqpath=root/'records'/'attack'/direction/(frame+'.request.json')
req=json.loads(reqpath.read_text(encoding='utf-8'))
hint=req['toolResult']['output_hint']
src=Path(re.search(r' as (.+?\.png) by default\.',hint).group(1))
native=root/'source'/'attack'/direction/(frame+'.png')
out=root/'runtime'/'attack'/direction/(frame+'.png')
native.parent.mkdir(parents=True,exist_ok=True)
out.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,native)
im=Image.open(native)
native_size=im.size
native_sha=hashlib.sha256(native.read_bytes()).hexdigest()
if im.width!=im.height: raise ValueError('Unexpected non-square native image')
if 'A' not in im.getbands(): raise ValueError('No alpha channel')
rgba=im.convert('RGBA')
if rgba.getchannel('A').getextrema()!=(0,255): raise ValueError('Unexpected alpha extrema')
if im.size==(1024,1024): shutil.copy2(native,out)
else: rgba.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
final=Image.open(out)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
receipt=root/'records'/'attack'/direction/(frame+'.receipt.json')
receipt.write_text(json.dumps({'tool':'image_gen.imagegen','startedAt':req['startedAt'],'completedAt':req['completedAt'],'returnedKeys':['image_url','output_hint'],'output_hint':hint,'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
record={'file':out.relative_to(root).as_posix(),'sha256':sha,'generatedAt':req['completedAt'],'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':req['arguments']['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露 model / quality；无可核实元数据。','prompt':req['prompt'],'references':req['references'],'evidence':[receipt.relative_to(root).as_posix(),reqpath.relative_to(root).as_posix()],'native':{'file':native.relative_to(root).as_posix(),'sha256':native_sha,'width':native_size[0],'height':native_size[1],'format':'PNG','mode':im.mode,'deleted':False},'derivedFrom':{'file':native.relative_to(root).as_posix(),'sha256':native_sha,'operation':'uniform-square-resize','scale':1024/native_size[0],'translation':[0,0],'mirrored':False,'perFrameAlignment':False},'visualQA':req['visualQA'],'event':'attack-contact' if frame=='08' else None,'durationMs':30,'pivot':[0.5,0.08]}
(root/'records'/'attack'/direction/(frame+'.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'nativeSize':native_size,'sha256':sha,'alphaExtrema':final.getchannel('A').getextrema(),'bbox':final.getchannel('A').getbbox(),'visualQA':req['visualQA']},ensure_ascii=True))
