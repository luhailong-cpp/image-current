from pathlib import Path
from PIL import Image
import json,sys,hashlib
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
S=Path(sys.argv[1]);out=B/'r12_c06/pipeline/guides/p01_01.row1-layout-fix-v02.native-anchor-guide.png'
assert not out.exists()
P=B/'r12_c06/native';im=Image.open(S).convert('RGB');refs=[]
for f,sbox,t in [('p01_01.png',[0,0,230,1254],[0,0]),('p01_02.png',[0,0,230,720],[1024,0]),('p01_03.png',[0,720,230,990],[1024,720])]:
    p=P/f;im.paste(Image.open(p).convert('RGB').crop(sbox),tuple(t));refs.append({'source':str(p),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceCropBox':sbox,'targetXY':t})
im.save(out);atomic_json(Path(str(out)+'.derivation.json'),{'source':str(S),'sourceSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'nativeAnchorCrops':refs,'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'guideOnly':True,'gameArt':False,'operation':'Exact native pixel copy guidance; no resampling, drawing, recoloring or final compositing.'});print(out)

