from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent;R=T/'repairs';D=T/'review'/'repaired-v1';D.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=read(T/'candidate'/'latest-assembly.json'); original=Path(base['candidate']['path'])
steps=sorted([read(p) for p in R.glob('*.composition.json')],key=lambda x:x['createdAt'])
a=Image.open(original).convert('RGB');last=sha(original)
for s in steps:
    assert s['sourceSha256']==last
    native=Path(s['native']);mask=Path(s['alpha']);assert sha(native)==s['nativeSha256'] and sha(mask)==s['alphaSha256']
    rect=s['placement']; im=Image.open(native).convert('RGB');m=Image.open(mask)
    assert im.size==(1254,1254)
    a.paste(Image.composite(im,a.crop(rect),m),(rect[0],rect[1]))
    saved=Image.open(s['output']).convert('RGB')
    assert np.array_equal(np.asarray(a),np.asarray(saved))
    assert sha(s['output'])==s['outputSha256'];last=s['outputSha256']
lastpath=Path(steps[-1]['output'])
context=Image.open(base['context']['path']).convert('RGB');context.paste(a,(115,115))
cp=T/'candidate'/'r14_c13-context-4326-repaired-v1.png';context.save(cp)
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r14_c13','baseAssemblyPointerSnapshot':base,'steps':steps,'exactPixelReplayVerified':True,'resampled':False,'candidate':{'path':str(lastpath),'sha256':sha(lastpath),'size':[4096,4096]},'context':{'path':str(cp),'sha256':sha(cp),'size':[4326,4326]},'internalArtQA':'pending_visual','externalNeighborSeamQA':'pending_repair_and_review','formalAccepted':False}
mf=T/'candidate'/'r14_c13-repaired-v1-manifest.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for pos in [1024,2048,3072]:
    a.crop((pos-256,0,pos+256,4096)).save(D/f'vertical-x{pos}-100pct.png')
    a.crop((0,pos-256,4096,pos+256)).save(D/f'horizontal-y{pos}-100pct.png')
    for y in [1024,2048,3072]:a.crop((pos-450,y-450,pos+450,y+450)).save(D/f'junction-x{pos}-y{y}-100pct.png')
for label,box in {'north':[0,0,4096,256],'south':[0,3840,4096,4096],'west':[0,0,256,4096],'east':[3840,0,4096,4096]}.items():a.crop(box).save(D/f'edge-{label}-100pct.png')
a.resize((1024,1024),Image.Resampling.LANCZOS).save(D/'overview-preview-only.png')
print(json.dumps({'verifiedRepairCount':len(steps),'manifest':str(mf),'review':str(D),'candidate':str(lastpath),'context':str(cp)}))

