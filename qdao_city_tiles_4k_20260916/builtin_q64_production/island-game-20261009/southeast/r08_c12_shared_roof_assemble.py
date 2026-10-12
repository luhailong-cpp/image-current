from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,os
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2),encoding='utf-8')
a=R/'tiles/r08_c12.candidate-v3.png';b=R/'tiles/r09_c12.candidate-v02.png';p=R/'native/r08_c12_repair_roof_shared_v01.png'
A=Image.open(a).convert('RGB');B=Image.open(b).convert('RGB');P=Image.open(p).convert('RGB')
A.paste(P.crop((115,115,1139,696)),(1536,3515));B.paste(P.crop((115,696,1139,1139)),(1536,0))
out=R/'tiles/r08_c12.candidate-v4.png';proposal=R/'qa/r08_c12-r09c12-roof-counterpart-proposal.png';A.save(out);B.save(proposal)
r=read(str(a)+'.generation.json');r.update(file=str(out),sha256=sha(out),base=str(a),baseSha256=sha(a),baseRecord=str(a)+'.generation.json',status='candidate_requires_shared_neighbor_counterpart')
piece={'file':str(p),'sha256':sha(p),'sourceCrop':[115,115,1139,696],'destination':[1536,3515],'destinationBox':[1536,3515,2560,4096],'record':str(p)+'.generation.json'}
r['repairOverlays'].append(piece);write(str(out)+'.generation.json',r)
write(str(proposal)+'.generation.json',{'file':str(proposal),'sha256':sha(proposal),'base':str(b),'baseSha256':sha(b),'operation':'exactnativecropandhardpaste; noresize','contribution':{'file':str(p),'sha256':sha(p),'sourceCrop':[115,696,1139,1139],'destinationBox':[1536,0,2560,443]},'status':'proposal_only_root_must_review_and_apply'})
C=Image.new('RGB',(4096,8192));C.paste(A,(0,0));C.paste(B,(0,4096))
for name,box in {'left':[1408,3515,1664,4539],'right':[2432,3515,2688,4539],'top':[1536,3387,2560,3643],'bottom':[1536,4411,2560,4667],'shared':[1536,3840,2560,4352]}.items():C.crop(box).save(R/'qa'/f'r08_c12.shared-roof-{name}.png')
A.resize((1024,1024),Image.Resampling.LANCZOS).save(R/'qa/r08_c12.preview-v4.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'counterpart':str(proposal),'counterpartSha':sha(proposal)}))

