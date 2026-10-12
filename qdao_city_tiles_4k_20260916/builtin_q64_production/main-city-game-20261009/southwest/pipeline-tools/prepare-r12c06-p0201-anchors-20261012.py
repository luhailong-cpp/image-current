from pathlib import Path
from PIL import Image
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
S=Path(sys.argv[1]);T=B/'r12_c06';anchor=T/'pipeline/guides/p02_01.resume-20261012-v01.continuity-seed.png';out=T/'pipeline/guides/p02_01.resume-20261012-v03.native-anchor-guide.png';assert not out.exists()
im=Image.open(S).convert('RGB');im.paste(Image.open(anchor).convert('RGB').crop([0,0,230,1254]),[0,0]);im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
atomic_json(Path(str(out)+'.derivation.json'),{'source':str(S),'sourceSha256':sha(S),'anchor':str(anchor),'anchorSha256':sha(anchor),'anchorCrop':[0,0,230,1254],'output':str(out),'sha256':sha(out),'guideOnly':True,'gameArt':False,'sourceResampling':False,'operation':'Native exact left anchor paste for imagegen only'})
print(out)

