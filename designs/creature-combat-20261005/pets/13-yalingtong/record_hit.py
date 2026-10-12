import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--source', required=True)
p.add_argument('--direction', required=True)
p.add_argument('--index',type=int,required=True)
p.add_argument('--edit-reference')
args=p.parse_args()
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
src=Path(args.source)
name=f'{args.index:02d}'
out=ROOT/'runtime/hit'/args.direction/f'{name}.png'
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src)
native={'width':im.width,'height':im.height,'mode':im.mode,'sha256':sha(src),'path':str(src)}
im=im.convert('RGBA')
if im.size != (1024,1024): im=im.resize((1024,1024),Image.Resampling.LANCZOS)
im.save(out)
refs=[('designs/pets-original-20260924/source/13-yalingtong-E.png','original identity E'),('designs/pets-original-20260924/source/13-yalingtong-W.png','original identity W'),('designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','primary approved style/material')]
ev=ROOT/'evidence/hit'/args.direction
ev.mkdir(parents=True,exist_ok=True)
record={'file':str(out.relative_to(ROOT)).replace('\\','/'),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[str(Path('D:/work/image')/x[0]) for x in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selectors and returned no model/quality metadata.','prompt':f'prompts/hit/{args.direction}/{name}.txt','references':[{'path':x,'role':y,'sha256':sha(Path('D:/work/image')/x)} for x,y in refs],'native':native,'operation':{'kind':'uniform full-canvas scale only' if native['width']!=1024 else 'RGBA PNG export','from':[native['width'],native['height']],'to':[1024,1024],'perFrameAlignment':False},'width':1024,'height':1024,'alphaExtrema':im.getchannel('A').getextrema(),'visualStatus':'individually inspected from generated tool image; sequence pending','evidence':f'evidence/hit/{args.direction}/{name}.receipt.json'}
if args.edit_reference:
 record['references'].append({'path':args.edit_reference,'role':'edit target; preserve all except specified repair','sha256':sha(Path(args.edit_reference))})
 record['submittedParameters']['referenced_image_paths'].append(args.edit_reference)
(ev/f'{name}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':record['file'],'native':native,'alpha':record['alphaExtrema']}))
