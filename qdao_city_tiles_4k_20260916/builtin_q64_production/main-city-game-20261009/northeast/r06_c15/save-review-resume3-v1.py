from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageChops
T=Path(__file__).resolve().parent;R=T/'qa/local-repair-resume3-20261013'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((T/'qa/local-repair-resume2-20261013/composition-v1.json').read_text())
candidate=Path(old['candidate']);base=Path(old['base']);assert sha(candidate)==old['candidateSha256']
a=Image.open(base).convert('RGB');b=Image.open(candidate).convert('RGB')
edge_boxes=[[0,0,4096,115],[0,3981,4096,4096],[0,0,115,4096],[3981,0,4096,4096]]
assert all(ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None for box in edge_boxes)
pending={'panel':'Primary duplicated panel fixed, but vertical rail step remains near crop bottom at tile x445..490,y3565..3600.', 'roof':'Primary roof splice improved; new phase/color discontinuity at repair lower boundary y3240.', 'wallrail':'Rail termination improved; wall tone jump and narrow post notch at repair lower boundary y2200.', 'upperroof':'Primary y1024 splice improved; shifted circular eave terminals and material mismatch at repair lower boundary y1170.'}
reviews=[]
for name in ['panel','ledge','roof','trunk','wallrail','fascia','upperroof']:
 f=T/'qa/local-repair-resume2-20261013'/f'{name}-composited-v1.png'
 reviews.append({'id':name,'file':str(f),'sha256':sha(f),'viewedNative1254':True,'status':'P2-pending' if name in pending else 'passed-local-geometry','finding':pending.get(name,'Main local geometry now continuous; minor texture tone variation only.')})
out=R/'visual-review-resume3-v1.json';assert not out.exists()
report={'tile':T.name,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':str(candidate),'candidateSha256':sha(candidate),'baseSha256':sha(base),'reviews':reviews,'pendingP2Count':len(pending),'pendingIssues':pending,'internalPassed4kCount':0,'formalAcceptedCount':0,'unchanged115pxOuterEdges':True,'reuse':'Baseline 24 seam/9 intersection review retained for unchanged areas; 7 edited1254 windows visually checked.','rejectedComposition':{'file':str(T/'candidates/r06_c15.local-repairs-resume3-v2.png'),'reason':'Binary minimum-difference composition introduced holes/edge phase breaks; retained for traceability and not selected.'},'nextStep':'Continue independent r07_c16 native cores against internally passed r07_c15 west candidate. These 4 P2 defects stay unpassed for bounded later AI repair.'}
out.write_text(json.dumps(report,indent=2)+'\n')
p=T/'tile-progress.json';progress=json.loads(p.read_text(encoding='utf-8-sig'));progress.update(candidate=str(candidate),candidateSha256=sha(candidate),pendingP2Count=4,internalPassed4kCount=0,internalPassed=False,status='complete-native-candidate-4-local-P2-pending',localVisualReview=str(out),nextStep=report['nextStep'],owner='/root/east_resume3',updatedAt=report['createdAt']);p.write_text(json.dumps(progress,indent=2)+'\n')
print(json.dumps({'candidate':str(candidate),'pendingP2Count':4,'internalPassed4kCount':0}))
