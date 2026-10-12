import sys,json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
B=Path(__file__).resolve().parents[1]; Z=B.parent
sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as a
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def boundaries():
    dest=B/'qa'/'external-native-pairs';dest.mkdir(exist_ok=True)
    records=[]
    for side,neighbor in [('west','r05_c05'),('south','r06_c06')]:
        for i in range(1,5):
            own=f's{i:02d}_01' if side=='west' else f's04_{i:02d}'
            oth=f's{i:02d}_04' if side=='west' else f's01_{i:02d}'
            x=p.selected_path(B,own); y=p.selected_path(Z/neighbor,oth)
            if not y.exists():
                records.append({'side':side,'segment':i,'status':'neighbor_missing','own':str(x),'neighbor':str(y)});continue
            p.validate_native(x,B,own);p.validate_native(y,Z/neighbor,oth)
            xx=np.asarray(Image.open(x).convert('RGB'));yy=np.asarray(Image.open(y).convert('RGB'))
            left,right=(yy,xx) if side=='west' else (xx.transpose(1,0,2),yy.transpose(1,0,2))
            joined,_=a.append_with_minimum_seam(left,right)
            crop=Image.fromarray(joined).crop((979,115,1299,1139)).transpose(Image.Transpose.ROTATE_90)
            f=dest/f'{side}-segment{i:02d}.png';crop.save(f)
            records.append({'side':side,'segment':i,'status':'pending','file':str(f),'sha256':sha(f),'own':{'file':str(x),'sha256':sha(x)},'neighbor':{'file':str(y),'sha256':sha(y)},'operation':'binary minimum-error pair seam, crop original pixels 320x1024 rotated90; no resizing/blend','scope':'native source pair diagnostic; final candidate cross-tile assembly not accepted'})
    (dest/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    print(json.dumps(records,indent=2))
if __name__=='__main__':boundaries()
