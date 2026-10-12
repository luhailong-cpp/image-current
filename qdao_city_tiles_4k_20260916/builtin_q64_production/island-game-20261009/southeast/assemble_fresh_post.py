from workflow import *
import subprocess,sys
from PIL import Image
old=ROOT/'tiles/r09_c13.candidate.png';rec=read(Path(str(old)+'.generation.json'));versions={}
for p in rec['derivedFrom']:
 n=Path(p['file']).stem;pid,v=n.rsplit('_',1);versions[pid[-2:]]=v
versions.update({'22':'v03','32':'v03'})
selection=ROOT/'selection-r09_c13.json';write(selection,{'tile':'r09_c13','patchVersions':versions,'seamShifts':[]})
subprocess.run([sys.executable,str(ROOT/'assemble_tile.py'),str(selection),'v02'],check=True)
subprocess.run([sys.executable,str(ROOT/'qa_from_candidate.py'),str(selection),'v02'],check=True)
new=ROOT/'tiles/r09_c13.candidate-v02.png';a=Image.open(old).convert('RGB');b=Image.open(new).convert('RGB');changed=['h21','h22','h31','h32','v12','v22','v32']
d=read(ROOT/'qa/r09_c13-v02/seams.json');matches=[]
for e in d['entries']:
 equal=a.crop(e['sourceCrop']).tobytes()==b.crop(e['sourceCrop']).tobytes()
 if e['id'] not in changed:assert equal
 matches.append({'id':e['id'],'pixelsIdenticalToPriorCandidate':equal})
write(ROOT/'qa/r09_c13-v02/prior-reviewed-pixel-replay.json',{'source':str(old),'sourceSha256':sha(old),'candidate':str(new),'candidateSha256':sha(new),'changedSeams':changed,'entries':matches})
print(versions)

