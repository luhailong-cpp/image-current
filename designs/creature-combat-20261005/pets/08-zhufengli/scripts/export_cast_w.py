import json, hashlib, sys
from pathlib import Path
from PIL import Image

base = Path(__file__).resolve().parents[1]
idx = int(sys.argv[1]); tag = f'cast-W-{idx:02d}'
receipt_path = base/'receipts'/f'{tag}.json'
r = json.loads(receipt_path.read_text(encoding='utf-8'))
src = Path(r['sourcePath']); data = src.read_bytes()
im = Image.open(src); original_mode = im.mode; original_size = list(im.size)
im = im.convert('RGBA').resize((1024,1024), Image.Resampling.LANCZOS)
dst = base/'runtime'/'cast'/'W'/f'{idx:02d}.png'; dst.parent.mkdir(parents=True,exist_ok=True)
im.save(dst)
sha = hashlib.sha256(dst.read_bytes()).hexdigest()
alpha = im.getchannel('A'); counts = alpha.histogram()
refs=[]
roles=['Original E identity reference; ignore magenta background','Original W identity, rear camera, costume and anatomy reference','Approved painted jade and gold materials/style reference','Previous W cast frame for continuity']
for j,p in enumerate(r['submittedParameters']['referenced_image_paths']):
    pp=Path(p); refs.append({'path':p,'role':roles[j] if j<len(roles) else 'continuity reference','sha256':hashlib.sha256(pp.read_bytes()).hexdigest()})
record={'file':str(dst),'sha256':sha,'generatedAt':r['generatedAt'],'width':1024,'height':1024,'format':'PNG','mode':'RGBA','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':r['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposed no model/quality selectors and returned no model/quality metadata.','prompt':str(base/'prompts'/f'{tag}.txt'),'references':refs,'evidence':{'receipt':str(receipt_path),'returnedFields':['image_url','output_hint'],'outputHint':r['outputHint']},'derivedFrom':{'path':str(src),'sha256':hashlib.sha256(data).hexdigest(),'nativeWidth':original_size[0],'nativeHeight':original_size[1],'nativeMode':original_mode,'sourceRetention':'Host output retained pending final QA; no workspace duplicate original.'},'operation':{'type':'whole-canvas-resize','outputSize':[1024,1024],'filter':'LANCZOS','crop':None,'perFrameFootRealignment':False},'animation':{'action':'cast','direction':'W','frame':idx,'durationMs':45,'pivot':[0.5,0.08],'event':'cast' if idx==9 else None},'technical':{'alphaExtrema':alpha.getextrema(),'transparentPixels':counts[0],'partialAlphaPixels':sum(counts[1:255]),'opaquePixels':counts[255],'alphaBBox':alpha.getbbox()},'visualReview':{'status':'reviewed-individual','notes':r.get('visualNotes','')}}
(dst.with_name(dst.name+'.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':idx,'path':str(dst),'sha256':sha,'nativeSize':original_size,'alphaExtrema':alpha.getextrema(),'bbox':alpha.getbbox()}))
