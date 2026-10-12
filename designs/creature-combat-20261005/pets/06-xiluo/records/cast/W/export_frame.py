from pathlib import Path
from PIL import Image
import json,hashlib,sys,datetime
base=Path(__file__).resolve().parents[3]
receipt=Path(sys.argv[1])
meta=json.loads(receipt.read_text(encoding='utf-8'))
num=meta['frame']
src=Path(meta['nativePath'])
im=Image.open(src); im.load()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
native={'path':str(src),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'sha256':sha(src)}
out=base/'runtime'/'cast'/'W'/f'{num:02}.png'
canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
canvas.alpha_composite(im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS),(0,-13))
canvas.save(out)
finished=Image.open(out)
alpha=finished.getchannel('A')
record={
'file':str(out.relative_to(base)).replace('\\','/'),'sha256':sha(out),'generatedAt':meta['generatedAt'],
'tool':'image_gen.imagegen','route':'builtin','action':'cast','direction':'W','frame':num,'durationMs':45,
'width':1024,'height':1024,'format':'PNG','mode':'RGBA','native':native,
'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),
'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':meta['references']},
'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有 model/quality 选择器，返回仅含 image_url/output_hint，未披露可确认型号质量。',
'prompt':meta.get('prompt',f'prompts/cast/W/{num:02}.txt'),'references':meta['references'],
'evidence':{'receipt':str(receipt.relative_to(base)).replace('\\','/'),'output_hint':meta['output_hint']},
'derivedFrom':{'path':str(src),'sha256':native['sha256']},
'operation':{'type':'uniform_whole_canvas_export','sourceSize':[im.width,im.height],'targetSize':[1024,1024],'scale':1024/1254,'offset':[0,-13],'interpolation':'LANCZOS','directionRuleFixed':True,'perFrameAlignment':False},
'pivot':[0.5,0.08],'anchorTopLeft':[512,942],'dynamicReview':'pending',
'alphaExtrema':list(alpha.getextrema()),'alphaBBox':list(alpha.getbbox()),'visualReview':meta['visualReview'],
'nativeCleanup':'native output retained until parent final reference/cleanup audit; no image backup created',
'gameIntegration':'not tested'}
(base/'records'/'cast'/'W'/f'{num:02}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':num,'native':native,'export':str(out),'sha256':record['sha256'],'alpha':record['alphaExtrema'],'bbox':record['alphaBBox']},ensure_ascii=False))
