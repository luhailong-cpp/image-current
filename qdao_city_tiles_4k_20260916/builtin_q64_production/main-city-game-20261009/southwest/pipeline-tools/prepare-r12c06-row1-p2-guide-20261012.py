from pathlib import Path
from PIL import Image
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
T=B/'r12_c06';dest=T/'pipeline/guides/p01_02.row1-layout-fix-v01.native-anchor-guide.png';assert not dest.exists()
src=T/'native/p01_02.png';im=Image.open(src).convert('RGB')
left=T/'refinement/versions/row1-layout-fix-v02/p01_01.png';right=T/'native/p01_03.png'
im.paste(Image.open(left).convert('RGB').crop([1024,0,1254,1254]),[0,0])
im.paste(Image.open(right).convert('RGB').crop([0,0,230,1254]),[1024,0])
im.save(dest)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
atomic_json(Path(str(dest)+'.derivation.json'),{'source':str(src),'sourceSha256':sha(src),'nativeAnchorCrops':[{'source':str(left),'sha256':sha(left),'crop':[1024,0,1254,1254],'targetXY':[0,0]},{'source':str(right),'sha256':sha(right),'crop':[0,0,230,1254],'targetXY':[1024,0]}],'output':str(dest),'sha256':sha(dest),'guideOnly':True,'gameArt':False,'sourceResampling':False,'operation':'Exact native pixel paste for imagegen geometry correction only'})
print(dest)

