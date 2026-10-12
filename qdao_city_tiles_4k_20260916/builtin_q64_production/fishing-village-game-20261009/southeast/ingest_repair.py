"""Save one builtin seam edit with unscaled-world coverage provenance."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
z=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
tile,stem,source=sys.argv[1:4]
t=z/tile
req=read(t/'repairs'/f'{stem}.request.json')
out=t/'repairs'/f'{stem}.png'
shutil.copy2(source,out)
im=Image.open(out)
refs=[{'path':p,'sha256':sha(p),'role':req['referenceRoles'].get(str(i+1))} for i,p in enumerate(req['referenced_image_paths'])]
rec={'file':str(out),'sha256':sha(out),'ingestedAt':datetime.now(timezone.utc).isoformat(),'nativeDimensions':list(im.size),'format':im.format,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':read(z.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin no selector or response metadata','prompt':str(t/'repairs'/f'{stem}.prompt.txt'),'references':refs,'evidence':{'request':str(t/'repairs'/f'{stem}.request.json'),'receipt':str(t/'repairs'/f'{stem}.receipt.json'),'sourcePath':source},'coordinate':req['coordinate'],'status':'candidate_pending_adoption_and_QA','upsamplingApplied':False}
write(out.with_suffix('.png.generation.json'),rec)
print(json.dumps({'file':str(out),'nativeDimensions':list(im.size),'sha256':rec['sha256']}))

