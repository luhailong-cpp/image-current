from pathlib import Path
from PIL import Image
import json,hashlib,os,sys
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,x:Path(p).write_text(json.dumps(x,indent=2),encoding='utf-8')
base,neighbor,pid,revision=sys.argv[1:];a=R/base;b=R/neighbor;p=R/'native'/f'{pid}.png'
q=read(R/'prompts'/f'{pid}.request.json');x,y=q['nativeTileBox'][:2];sx0=int(os.environ.get('ISLAND_R08_SOURCE_LEFT','115'));assert sx0 in (0,115);x0=x+sx0;x1=x+1139;y0=y+115;y1=y+1139;cut=4096-y
A=Image.open(a).convert('RGB');B=Image.open(b).convert('RGB');P=Image.open(p).convert('RGB')
A.paste(P.crop((sx0,115,1139,cut)),(x0,y0));B.paste(P.crop((sx0,cut,1139,1139)),(x0,0))
out=R/'tiles'/f'r08_c12.candidate-{revision}.png';proposal=R/'qa'/f'r08_c12-r09c12-counterpart-{revision}.png';A.save(out);B.save(proposal)
r=read(str(a)+'.generation.json');r.update(file=str(out),sha256=sha(out),base=str(a),baseSha256=sha(a),baseRecord=str(a)+'.generation.json',status='candidate_requires_shared_neighbor_counterpart')
piece={'file':str(p),'sha256':sha(p),'sourceCrop':[sx0,115,1139,cut],'destination':[x0,y0],'destinationBox':[x0,y0,x1,4096],'record':str(p)+'.generation.json'}
r['repairOverlays'].append(piece);write(str(out)+'.generation.json',r)
prior=read(str(b)+'.generation.json')
extras=prior.get('contributions',[]) if 'contribution' not in prior else [prior['contribution']]
write(str(proposal)+'.generation.json',{'file':str(proposal),'sha256':sha(proposal),'base':str(b),'baseSha256':sha(b),'operation':'exactnativecropandhardpaste; noresize','contributions':extras+[{'file':str(p),'sha256':sha(p),'sourceCrop':[sx0,cut,1139,1139],'destinationBox':[x0,0,x1,y1-4096]}],'status':'proposal_only_root_must_review_and_apply'})
C=Image.new('RGB',(4096,8192));C.paste(A,(0,0));C.paste(B,(0,4096))
for name,box in {'left':[x0-128,y0,x0+128,y1],'right':[x1-128,y0,x1+128,y1],'top':[x0,y0-128,x1,y0+128],'bottom':[x0,y1-128,x1,y1+128],'shared':[x0,3840,x1,4352]}.items():C.crop(box).save(R/'qa'/f'r08_c12.{revision}-shared-{name}.png')
A.resize((1024,1024),Image.Resampling.LANCZOS).save(R/'qa'/f'r08_c12.preview-{revision}.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'counterpart':str(proposal),'counterpartSha':sha(proposal)}))

