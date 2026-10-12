import sys,json,hashlib,re
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
receipt=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8-sig'))
src=Path(receipt['sourcePath'])
im=Image.open(src)
native={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format}
rgba=im.convert('RGBA')
if rgba.size!=(1024,1024): rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
out=ROOT/'runtime'/'attack'/job['direction']/(job['frame']+'.png')
out.parent.mkdir(parents=True,exist_ok=True)
rgba.save(out)
alpha=rgba.getchannel('A')
hist=alpha.histogram()
record={'file':str(out),'sha256':sha(out),'generatedAt':receipt['completedAt'],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':job['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**job['args']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具无 model/quality 选择器，返回未披露型号和质量。','native':native,'output':{'width':1024,'height':1024,'format':'PNG','mode':'RGBA'},'prompt':str(ROOT/'prompts'/('attack-'+job['direction']+'-'+job['frame']+'.txt')),'references':[{'path':p,'role':(job.get('referenceRoles',['original E identity and anatomy','original W identity and anatomy','approved painted jade/gold materials and finish','previous independent same-direction animation frame','frame01 same-direction closure baseline'])[i]),'sha256':sha(p)} for i,p in enumerate(job['args']['referenced_image_paths'])],'evidence':{'receipt':str(Path(sys.argv[2]).resolve()),'returnedFields':['image_url','output_hint'],'imageUrlOmitted':'data URL omitted from text receipt; source PNG SHA preserves output identity'},'derivedFrom':{'path':str(src),'sha256':sha(src),'native':native},'operation':'Full native canvas converted to RGBA and uniformly resized to 1024x1024 using Lanczos; no crop, alignment, translation, interpolation between poses, or mirroring.','action':'attack','direction':job['direction'],'frame':int(job['frame']),'durationMs':30,'pivot':[0.5,0.08],'event':'attack' if job['frame']=='07' else None,'technicalChecks':{'alphaExtrema':alpha.getextrema(),'transparentPixels':hist[0],'opaquePixels':hist[255],'partialAlphaPixels':sum(hist[1:255]),'alphaBBox':alpha.getbbox()},'visualStatus':'pending sequence review'}
out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':record['sha256'],'native':native,'checks':record['technicalChecks']},ensure_ascii=False))


