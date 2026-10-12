from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parent
SOURCE=Path('C:/Users/luyua/.codex/generated_images/01a12076-19f9-7f00-8135-01e1b5fb7007/exec-16027d54-b06d-4e48-9070-9be22a4088fe.png')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,d): (ROOT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
native=ROOT/'native.png'
if not native.exists(): shutil.copyfile(SOURCE,native)
im=Image.open(native); assert im.size==(1254,1254)
if 'A' in im.getbands(): assert im.getchannel('A').getextrema()==(255,255)
write('generation.json',{'status':'succeeded_pending_visual_seam_review','tool':'image_gen.imagegen','generatedAtUtc':datetime.now(timezone.utc).isoformat(),'originalOutput':str(SOURCE),'native':str(native),'sha256':sha(native),'measuredSize':list(im.size),'actualModel':None,'actualQuality':None,'resized':False,'request':str(ROOT/'request.json'),'requestSha256':sha(ROOT/'request.json')})
old=np.asarray(Image.open(ROOT/'four-core-corner-edit-target-1254.png').convert('RGB'))
new=np.asarray(im.convert('RGB'))
# Report nearest dark grout centres where fixed upper-left meets writable quadrants.
def center(a,axis,p,lo,hi):
    v=a[lo:hi,p].mean(1) if axis=='x' else a[p,lo:hi].mean(1)
    return lo+int(v.argmin())
points=[]
for a,label in [(old,'original'),(new,'generated')]:
    points.append({'image':label,'at_x624_y':center(a,'x',624,380,460),'at_y624_x':center(a,'y',624,480,570)})
write('boundary-registration-measurement.json',points)
print(json.dumps({'native':str(native),'sha256':sha(native),'boundary':points}))

# One rigid integer source translation. The two independent grout entry points
# determine this registration; no scaling, deformation, drawn pixels or old-core edits.
best=None
for dx in range(-30,1):
    for dy in range(-20,11):
        vx=center(new,'x',624-dx,380-dy,460-dy)+dy
        hy=center(new,'y',624-dy,480-dx,570-dx)+dx
        error=abs(vx-410)+abs(hy-512)
        score=(error,abs(dx)+abs(dy))
        if best is None or score<best[0]: best=(score,dx,dy,vx,hy)
_,dx,dy,vx,hy=best
canvas=Image.fromarray(old.copy()); canvas.paste(im.convert('RGB'),(dx,dy)); registered=np.asarray(canvas)
yy,xx=np.mgrid[:1254,:1254]
edge=np.minimum.reduce([xx,yy,1253-xx,1253-yy]).astype(np.float32)
alpha=np.clip((edge-32)/100,0,1)
alpha[:625,:625]=0
alpha[:,1254+dx:]=0
if dy<0: alpha[1254+dy:,:]=0
alpha8=np.round(alpha*255).astype(np.uint8)
Image.fromarray(alpha8).save(ROOT/'trial-alpha.png')
trial=Image.composite(Image.fromarray(registered),Image.fromarray(old),Image.fromarray(alpha8))
assert trial.crop((0,0,625,625)).tobytes()==Image.fromarray(old).crop((0,0,625,625)).tobytes()
trial.save(ROOT/'trial-corner-composite.png')
write('trial-composition.json',{'status':'unpromoted_pending_visual_QA','nativeSha256':sha(native),'targetSha256':sha(ROOT/'four-core-corner-edit-target-1254.png'),'rigidIntegerTranslation':[dx,dy],'translationBasis':'Fit both independent grout entries from immutable upper-left; one rigid transform across reused native pixels','boundaryGroutCentresAfter':[vx,hy],'boundaryGroutCentresBefore':[410,512],'alpha':str(ROOT/'trial-alpha.png'),'alphaSha256':sha(ROOT/'trial-alpha.png'),'candidate':str(ROOT/'trial-corner-composite.png'),'candidateSha256':sha(ROOT/'trial-corner-composite.png'),'immutableUpperLeftPixelsExact':True,'resized':False,'publishedToTiles':False})
print(json.dumps({'trial':str(ROOT/'trial-corner-composite.png'),'translation':[dx,dy],'boundaryGroutCentresAfter':[vx,hy]}))
