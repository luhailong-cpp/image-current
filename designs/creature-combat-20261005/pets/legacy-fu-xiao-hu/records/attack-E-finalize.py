from pathlib import Path
import json, hashlib, sys, shutil
from datetime import datetime, timezone
from PIL import Image
B=Path(__file__).resolve().parent.parent
n=sys.argv[1]; src=Path(sys.argv[2]); native=B/'records'/'attack-E-native'/f'{n}.png'; out=B/'runtime'/'attack'/'E'/f'{n}.png'
shutil.copy2(src,native)
im=Image.open(native); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
refs=['D:/work/image/qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png','D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png',str(B/'design'/'E-reference.png')]
if int(n)>1: refs.append(str(B/'records'/'attack-E-native'/f'{int(n)-1:02}.png'))
receipt=json.loads((B/'records'/f'attack-E-{n}.receipt.json').read_text(encoding='utf-8'))
record={'file':str(native.relative_to(B)).replace('\\','/'),'sha256':h(native),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':refs},'actualModel':None,'actualQuality':None,'evidence':{'receipt':f'records/attack-E-{n}.receipt.json','sourcePath':str(src),'toolOutputHint':receipt.get('output_hint')},'unverifiedReason':'宿主管理，工具未披露 model/quality，无可核实元数据。','prompt':f'records/attack-E-{n}.prompt.txt','references':[{'path':v,'role':r} for v,r in zip(refs,['original identity','primary approved painterly style','fixed E camera identity','previous native frame'])]}
rec=B/'records'/f'attack-E-{n}.generation.json'; rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
im.convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS).save(out)
d={'file':str(out.relative_to(B)).replace('\\','/'),'sha256':h(out),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','derivedFrom':{'path':record['file'],'sha256':record['sha256'],'generationRecord':str(rec.relative_to(B)).replace('\\','/')},'operation':{'kind':'uniform-full-canvas-resize','sourceSize':[im.width,im.height],'targetSize':[1024,1024],'resampler':'LANCZOS','translation':[0,0],'crop':None},'action':'attack','direction':'E','frame':int(n),'durationMs':30,'pivot':[0.5,0.08],'anchor':[512,942]}
out.with_suffix('.png.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':n,'source':im.size,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'output':str(out)}))

