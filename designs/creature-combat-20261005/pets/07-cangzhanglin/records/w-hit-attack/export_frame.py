import json, hashlib, sys
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[2]
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
source=Path(job['source'])
dest=root/job['file']
im=Image.open(source).convert('RGBA')
native={'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
assert im.width==im.height, native
assert im.getchannel('A').getextrema()[0]==0
out=Image.new('RGBA',(1024,1024),(0,0,0,0))
out.alpha_composite(im.resize((960,960),Image.Resampling.LANCZOS),(32,6))
dest.parent.mkdir(parents=True,exist_ok=True)
out.save(dest)
job.update({'native':native,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','alphaExtrema':list(out.getchannel('A').getextrema()),'alphaBBox':list(out.getbbox()),'operation':{'kind':'uniform_full_canvas_scale_and_pad','inputCanvas':[im.width,im.height],'scaledCanvas':[960,960],'outputCanvas':[1024,1024],'offset':[32,6],'resampling':'LANCZOS','perFrameAlignment':False},'pivot':[0.5,0.08],'anchorTopLeft':[512,942]})
job['configSnapshot']=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
job['references']=[{'path':r,'role':role,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r,role in job['references']]
record=root/job['record']
record.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'native':native,'sha256':job['sha256'],'alphaBBox':job['alphaBBox']},ensure_ascii=False))
