from pathlib import Path
from PIL import Image
import json, hashlib, sys
root=Path(__file__).resolve().parents[1]
for job_path in sys.argv[1:]:
 job=json.loads(Path(job_path).read_text(encoding='utf-8'))
 n=job['frame']; stem=f'{n:02d}'
 source=Path(job['sourcePath'])
 im=Image.open(source); native_size=list(im.size); native_mode=im.mode
 source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
 if im.width != im.height: raise RuntimeError('Non-square source requires review')
 scaled=im.convert('RGBA').resize((960,960),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(1024,1024),(0,0,0,0)); out.alpha_composite(scaled,(32,6))
 path=root/'runtime'/'cast'/'W'/f'{stem}.png'; path.parent.mkdir(parents=True,exist_ok=True); out.save(path)
 rgba=out.getchannel('A')
 record={**job,'file':str(path.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','durationMs':45,'pivot':[0.5,0.08],'groundAnchor':[512,942],'event':'cast' if n==10 else None,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':job['references']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具无 model/quality 选择器且结果未披露，目标不冒充实际参数。','native':{'path':str(source),'width':native_size[0],'height':native_size[1],'mode':native_mode,'sha256':source_sha},'derivedFrom':{'path':str(source),'sha256':source_sha},'operation':{'type':'uniform-full-canvas-resize-and-pad','resizedCanvas':[960,960],'destinationCanvas':[1024,1024],'offset':[32,6],'crop':False,'perFrameAlignment':False},'alpha':{'extrema':list(rgba.getextrema()),'bbox':list(rgba.getbbox())},'visualReview':{'status':'pending','notes':None}}
 rec=root/'records'/'W-cast'/f'{stem}.generation.json'; rec.parent.mkdir(parents=True,exist_ok=True); rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'frame':n,'file':str(path),'sha256':record['sha256'],'native':native_size,'alphaBBox':record['alpha']['bbox']}))

