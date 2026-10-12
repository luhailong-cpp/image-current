from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
jobs=[('remove-bell-v1',(620,0,815,260),False,True),('remove-extra-cap-v1',(480,1080,720,1254),True,False)]
base=Path(read(T/'repairs'/jobs[0][0]/'preparation.json')['base']); image=Image.open(base).convert('RGB');before=np.asarray(image).copy();steps=[]
for name,box,open_bottom,open_top in jobs:
    d=T/'repairs'/name;p=read(d/'preparation.json');r=read(d/'receipt.json');src=Path(r['originalOutput']);native=d/'native.png'
    if not native.exists():shutil.copyfile(src,native)
    assert sha(src)==sha(native)
    new=Image.open(native).convert('RGB');assert new.size==(1254,1254)
    write(d/'generation.json',{**r,'native':str(native),'sha256':sha(native),'measuredSize':[1254,1254],'resized':False})
    yy,xx=np.mgrid[:1254,:1254];x0,y0,x1,y1=box
    alpha=np.minimum(np.clip((xx-x0)/18,0,1),np.clip((x1-1-xx)/18,0,1))
    if not open_top:alpha=np.minimum(alpha,np.clip((yy-y0)/18,0,1))
    if not open_bottom:alpha=np.minimum(alpha,np.clip((y1-1-yy)/18,0,1))
    alpha[(xx<x0)|(xx>=x1)|(yy<y0)|(yy>=y1)]=0
    a=Image.fromarray(np.rint(alpha*255).astype(np.uint8));ap=d/'applied-alpha.png';a.save(ap)
    bx,by,bx1,by1=p['tileBox'];old=image.crop((bx,by,bx1,by1));patch=Image.composite(new,old,a);image.paste(patch,(bx,by))
    patch.save(d/'applied-context-1254.png')
    steps.append({'id':name,'native':str(native),'nativeSha256':sha(native),'alpha':str(ap),'alphaSha256':sha(ap),'nativeCropBox':[0,0,1254,1254],'tilePlacementBox':p['tileBox'],'alphaBounds':box,'sourceResize':False,'method':'integer crop/paste with 18px border alpha; no painted pixels'})
out=T/'candidate'/'r13_c15-4k-ornaments-removed-v1.png';image.save(out)
replay=Image.open(base).convert('RGB')
for s in steps:
    x0,y0,x1,y1=s['tilePlacementBox'];patch=Image.composite(Image.open(s['native']).convert('RGB'),replay.crop((x0,y0,x1,y1)),Image.open(s['alpha']));replay.paste(patch,(x0,y0))
assert replay.tobytes()==image.tobytes()
latest=read(T/'candidate'/'latest-assembly.json');cp=Path(latest['context']['path']);context=Image.open(cp).convert('RGB');context.paste(image,(115,115));co=T/'candidate'/'r13_c15-context-4326-ornaments-removed-v1.png';context.save(co)
change=np.any(before!=np.asarray(image),axis=2);allowed=np.zeros((4096,4096),bool)
for s in steps:
    bx,by,_,_=s['tilePlacementBox'];x0,y0,x1,y1=s['alphaBounds'];allowed[by+y0:by+y1,bx+x0:bx+x1]=True
assert not np.any(change & ~allowed)
m={'tile':T.name,'status':'candidate_pending_visual_review','createdAt':datetime.now(timezone.utc).isoformat(),'base':str(base),'baseSha256':sha(base),'baseContext':str(cp),'baseContextSha256':sha(cp),'steps':steps,'candidate':{'path':str(out),'sha256':sha(out),'size':[4096,4096]},'context':{'path':str(co),'sha256':sha(co),'size':[4326,4326]},'exactReplayVerified':True,'outsideRepairUnchanged':True,'changedPixels':int(change.sum()),'formalAccepted':False,'resized':False}
write(T/'repairs'/'ornaments-composition-v1.json',m)
image.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'review'/'ornaments-v1-preview-only.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'manifest':str(T/'repairs'/'ornaments-composition-v1.json')}))
