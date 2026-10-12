from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-resume-sol-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
vs=read(R/'progress-r12_c13.json')['selectedVersions'];vs.update({'31':'v02','41':'v01'})
out=R/'tiles/r12_c13.candidate-sol-20261012-v01.png';assert not out.exists();im=Image.new('RGB',(4096,4096));sources=[]
for rc,v in sorted(vs.items()):
 p=R/'native'/f'r12_c13_p{rc}_{v}.png';a=Image.open(p).convert('RGB');assert a.size==(1254,1254);x=(int(rc[1])-1)*1024;y=(int(rc[0])-1)*1024;im.paste(a.crop((115,115,1139,1139)),(x,y));sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'destination':[x,y],'role':'native core; overlay replaces failed portions in p31/p41'})
p=R/'native/r12_c13_deck_corner_whole_v03.png';im.paste(Image.open(p).convert('RGB').crop((115,115,1139,1139)),(0,2567));sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'destination':[0,2567],'role':'registered whole physical board/deck corner correction; overrides base'})
im.save(out);write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'width':4096,'height':4096,'operation':'exact source-native 1024 core crop/paste with registered native object core overlay; no resampling or paint','sources':sources,'selectedPatchVersions':vs,'formalAccepted':False,'status':'provisional_full_coverage_pending_seam_review','createdAtUtc':datetime.now(timezone.utc).isoformat()})
w=R/'tiles/r12_c12.candidate-sol-20261012-v01.png';wi=Image.open(w).convert('RGB');qa=Q/'candidate-v01-west-full-seam.png';seam=Image.new('RGB',(512,4096));seam.paste(wi.crop((3840,0,4096,4096)),(0,0));seam.paste(im.crop((0,0,256,4096)),(256,0));seam.save(qa);write(Path(str(qa)+'.trace.json'),{'operation':'exact native-derived full candidate west core hard seam','resampled':False,'sources':[{'file':w.as_posix(),'sha256':sha(w),'crop':[3840,0,4096,4096],'destination':[0,0]},{'file':out.as_posix(),'sha256':sha(out),'crop':[0,0,256,4096],'destination':[256,0]}],'file':qa.as_posix(),'sha256':sha(qa)})
for row in [3,4]:
 q=Q/f'candidate-v01-west-row{row}.png';seam.crop((0,(row-1)*1024,512,row*1024)).save(q)
print(json.dumps({'candidate':out.as_posix(),'sha256':sha(out),'west':[str(Q/'candidate-v01-west-row3.png'),str(Q/'candidate-v01-west-row4.png')],'formalAccepted':False}))

