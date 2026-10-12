import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('request');p.add_argument('source');p.add_argument('receipt');a=p.parse_args()
q=json.loads(Path(a.request).read_text(encoding='utf-8-sig')); out=R/q['file'];rec=R/q['record'];old=json.loads(rec.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hist=rec.parent/'history';hist.mkdir(exist_ok=True);histfile=hist/(out.stem+'.'+old['sha256'][:12]+'.generation.json');histfile.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
src=Path(a.source);im=Image.open(src);native={'path':str(src),'sha256':sha(src),'width':im.width,'height':im.height,'mode':im.mode,'format':'PNG'}
im=im.convert('RGBA');im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
new={'file':q['file'],'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':old['configSnapshot'],'submittedParameters':dict(q['parameters'],model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality selectors or return fields disclosed','references':q['references'],'prompt':q['promptFile'],'native':native,'width':1024,'height':1024,'format':'PNG','mode':'RGBA','aiEditedFrom':{'priorRecord':histfile.relative_to(R).as_posix(),'priorSha256':old['sha256'],'priorPixelsRetained':False},'operation':{'kind':'uniform full-canvas resize','from':[native['width'],native['height']],'to':[1024,1024],'perFrameAlignment':False},'evidence':a.receipt,'visualStatus':'requires sequence review'}
rec.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'file':q['file'],'sha256':new['sha256']}))
