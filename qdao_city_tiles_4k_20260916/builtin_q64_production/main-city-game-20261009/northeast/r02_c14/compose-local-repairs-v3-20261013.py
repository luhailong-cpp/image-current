from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=read(Q/'composition-v2.json');base=Path(prior['candidate']);original=Image.open(base).convert('RGB');out=original.copy();assert sha(base)==prior['candidateSha256']
f=T/'native/repairs/roof-left-local-v2-20261013.png';rec=read(Path(str(f)+'.generation.json'));assert sha(f)==rec['sha256']
crop=[0,260,1139,930];origin=[0,2445];a,b,c,d=crop;x,y=origin
out.paste(Image.open(f).convert('RGB').crop(crop),(x+a,y+b))
dest=T/'candidates/r02_c14.local-repairs-v3-20261013.png';assert not dest.exists();out.save(dest)
box=[x+a,y+b,x+c,y+d];check=out.copy();check.paste(original.crop(box),box[:2]);assert ImageChops.difference(check,original).getbbox() is None
window=Q/'roof-left-composed-v3.png';out.crop([0,2445,1254,3699]).save(window)
binding={'baseCandidate':str(base),'baseSha256':sha(base),'candidate':str(dest),'candidateSha256':sha(dest),'priorComposition':str(Q/'composition-v2.json'),'layers':[{'id':'roof-left','file':str(f),'sha256':sha(f),'origin':origin,'crop':crop}],'outsideRepairRectangleByteIdentical':True,'operation':'Integer native crop/paste; no resizing or blending.','status':'local_visual_review_pending','internalPassed4kCount':0,'formalAcceptedCount':0}
(Q/'composition-v3.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
print(json.dumps(binding))

