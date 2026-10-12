from pathlib import Path
from PIL import Image
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
O=B/'r12_c06/pipeline/anchors'
for name,source,box in [
('left-r12c05-v14',B/'r12_c05/repairs-resume-20261012/integrated-local-v14/r12_c05.candidate.context.png',[4096,0,4326,4326]),
('top-r11c06-v5',B/'integrated-20261011/v5/r11_c06.candidate.context.png',[0,4096,4326,4326])]:
    dest=O/(name+'.png');im=Image.open(source).convert('RGB').crop(box)
    if dest.exists():assert Image.open(dest).tobytes()==im.tobytes()
    else:im.save(dest)
    ev=Path(str(dest)+'.derivation.json');assert not ev.exists()
    atomic_json(ev,{'source':str(source),'sourceSha256':sha(source),'sourceCropBox':box,'output':str(dest),'sha256':sha(dest),'operation':'exact native crop; no resampling','sourceResampling':False,'forTile':'r12_c06'})
print('exact anchors preserved')

