from pathlib import Path
import json, hashlib, shutil, sys
from datetime import datetime, timezone
from PIL import Image
T=Path(__file__).resolve().parent
Q=T/'qa'/'native-repairs'; Q.mkdir(parents=True,exist_ok=True)
BASE=T/'qa'/'core-baseline'/'c283fdfb38adab68f261'/'r05_c14-core-baseline.candidate.png'
CAND=T/'candidates'/'r05_c14.candidate.png'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now(): return datetime.now(timezone.utc).isoformat()
cmd=sys.argv[1]; name=sys.argv[2]
if cmd=='crop':
    x,y=map(int,sys.argv[3:5]); source=CAND if CAND.exists() else BASE
    im=Image.open(source).convert('RGB')
    target=Q/(name+'-input.png'); im.crop((x,y,x+1254,y+1254)).save(target)
    save(Q/(name+'-input.json'),{'createdAt':now(),'file':str(target),'sha256':sha(target),'source':str(source),'sourceSha256':sha(source),'origin':[x,y],'size':[1254,1254],'operation':'integer crop no resizing','actualModel':None,'actualQuality':None})
    print(target)
elif cmd=='apply':
    src=Path(sys.argv[3]); bounds=list(map(int,sys.argv[4:8]))
    meta=json.loads((Q/(name+'-input.json')).read_text())
    source=Path(meta['source']); assert sha(source)==meta['sourceSha256']
    native=T/'native'/(name+'.png'); assert not native.exists()
    shutil.copy2(src,native); new=Image.open(native).convert('RGB'); assert new.size==(1254,1254)
    im=Image.open(source).convert('RGB'); ox,oy=meta['origin']; x1,y1,x2,y2=bounds
    assert 0<=x1<x2<=1254 and 0<=y1<y2<=1254
    mask=Image.new('L',(1254,1254),0); pix=mask.load()
    for y in range(y1,y2):
        for x in range(x1,x2):
            # Texture-only 16px edge taper; full native pixels in repair center.
            dx=min(x-x1+1,x2-x); dy=min(y-y1+1,y2-y)
            if oy+y2==4096: dy=y-y1+1
            if ox+x2==4096: dx=x-x1+1
            pix[x,y]=round(255*min(1,dx/16,dy/16))
    maskpath=Q/(name+'-mask.png'); mask.save(maskpath)
    im.paste(new,(ox,oy),mask); CAND.parent.mkdir(exist_ok=True); im.save(CAND)
    payload=json.loads((T/'prompts'/(name+'.request.json')).read_text())
    receipt=T/'receipts'/(name+'.receipt.json')
    record={'file':str(native),'sha256':sha(native),'generatedAt':now(),'nativeSize':[1254,1254],'sourceOutputPath':str(src),'tool':'image_gen','route':'builtin','submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host returned no model or quality fields','resized':False,'prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(T/'prompts'/(name+'.request.json')),'evidence':str(receipt),'references':[{'file':p,'sha256':sha(p),'role':payload['referenceRoles'][i]} for i,p in enumerate(payload['referenced_image_paths'])],'operation':'native localized cross-seam repair'}
    save(Path(str(native)+'.generation.json'),record)
    integration={'createdAt':now(),'input':meta,'native':str(native),'nativeSha256':sha(native),'mask':str(maskpath),'maskSha256':sha(maskpath),'localMaskBounds':bounds,'output':str(CAND),'outputSha256':sha(CAND),'resized':False,'blurred':False,'warped':False,'method':'integer native overlay; 16px alpha taper only at perimeter; no resampling or blur'}
    save(Q/(name+'-integration.json'),integration)
    im.crop((ox,oy,ox+1254,oy+1254)).save(Q/(name+'-after.png'))
    print(json.dumps(integration))
else: raise ValueError(cmd)

