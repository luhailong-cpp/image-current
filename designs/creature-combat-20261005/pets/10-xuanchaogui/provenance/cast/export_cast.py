import json,sys,hashlib
from pathlib import Path
from PIL import Image
base=Path(__file__).resolve().parents[2]
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
src=Path(job['source']); im=Image.open(src)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d,n=job['direction'],job['frame']; stem=f'{d}{n:02d}'
out=base/'runtime'/'cast'/d/f'{n:02d}.png'
source_info={'file':str(src),'sha256':sha(src),'width':im.width,'height':im.height,'mode':im.mode}
assert im.width==im.height
assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
native=job|{'sourceImage':source_info,'file':str(out),'sha256':sha(out),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','durationMs':45,'pivot':[0.5,0.08],'stageFootPoint':[512,942],'event':'release' if n==10 else None,'operation':{'name':'whole_canvas_uniform_resize','from':[im.width,im.height],'to':[1024,1024],'crop':None,'translation':[0,0]},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'unverifiedReason':'宿主管理，工具未披露型号/质量选择器或返回值','alphaExtrema':list(Image.open(out).getchannel('A').getextrema())}
record_path=base/'provenance'/'cast'/f'{stem}.generation.json'
refs=[{'path':p,'sha256':sha(p),'role':['identity E front-three-quarter','identity W rear-three-quarter','primary painting/material style'][i] if i<3 else 'animation continuity / fixed composition'} for i,p in enumerate(job['references'])]
source_record=job|{'file':str(src),'sha256':source_info['sha256'],'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'actualModel':None,'actualQuality':None,'submittedParameters':native['submittedParameters']|{'referenced_image_paths':job['references'],'prompt':job['prompt']},'unverifiedReason':native['unverifiedReason'],'references':refs,'evidence':{'receipt':f'provenance/cast/{stem}.job.json','output_hint':job['receipt']['output_hint'],'returnedFields':['image_url','output_hint']},'nativeRetention':'host-managed generation output, no duplicate source in delivery directory'}
record_path.write_text(json.dumps(source_record,ensure_ascii=False,indent=2),encoding='utf-8')
sidecar=native|{'file':str(out.relative_to(base)).replace(chr(92),'/'),'derivedFrom':{'path':str(src),'sha256':source_info['sha256'],'generationRecord':str(record_path.relative_to(base)).replace(chr(92),'/')},'references':refs,'evidence':source_record['evidence'],'visualStatus':'individual-frame-reviewed; sequence review pending','alphaBBox':list(Image.open(out).getchannel('A').getbbox())}
Path(str(out)+'.generation.json').write_text(json.dumps(sidecar,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sourceSize':[im.width,im.height],'sha256':native['sha256']}))
