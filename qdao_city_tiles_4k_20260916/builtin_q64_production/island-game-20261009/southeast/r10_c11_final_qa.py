from PIL import Image,ImageChops
from workflow import ROOT,read,write,sha,now
import json,sys
version=sys.argv[1] if len(sys.argv)>1 else 'v02'
f=ROOT/'tiles'/f'r10_c11.candidate-{version}.png';im=Image.open(f).convert('RGB')
base=Image.open(ROOT/'tiles/r10_c11.candidate.png').convert('RGB')
outdir=ROOT/'qa'/f'r10_c11-final-{version}';outdir.mkdir(exist_ok=True)
items=[]
for r in range(4):
    for c in range(3):
        box=[(c+1)*1024-256,r*1024,(c+1)*1024+256,(r+1)*1024]
        items.append({'id':f'h{r+1}{c+1}','kind':'internal_seam','box':box})
for r in range(3):
    for c in range(4):
        box=[c*1024,(r+1)*1024-256,(c+1)*1024,(r+1)*1024+256]
        items.append({'id':f'v{r+1}{c+1}','kind':'internal_seam','box':box})
for r in range(1,4):
    for c in range(1,4):
        items.append({'id':f'j{r}{c}','kind':'junction','box':[c*1024-256,r*1024-256,c*1024+256,r*1024+256]})
changed=[]
for e in items:
    crop=im.crop(e['box']);out=outdir/(e['id']+'.png');crop.save(out)
    equal=ImageChops.difference(crop,base.crop(e['box'])).getbbox() is None
    e.update({'file':out.as_posix(),'sha256':sha(out),'source':f.as_posix(),'sourceSha256':sha(f),'operation':'unscaled original candidate crop','unchangedFromReviewedBase':equal,'status':'inherit_reviewed_geometry' if equal else 'pending_final_visual_review'})
    if not equal:changed.append(e['id'])
write(outdir/'index.json',{'tile':'r10_c11','createdAt':now(),'candidate':f.as_posix(),'candidateSha256':sha(f),'seamCount':24,'junctionCount':9,'items':items,'formalAccepted':False})
print(json.dumps({'changed':changed,'unchangedCount':len(items)-len(changed)}))
