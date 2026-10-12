import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
TILE=BASE/'r10_c08'
OUT=HERE/'r10_c08-final'
OUT.mkdir(exist_ok=True)
path=TILE/'processed/colorpass/r10_c08-colorpass-candidate.png'
im=Image.open(path).convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
boxes={'bench-top-left':[31000,39693,31744,39949], 'bench-top-right':[31744,39693,32500,39949],
       'bench-left-adoption':[30989,39821,31245,40960], 'bench-right-adoption':[32243,39821,32499,40960],
       'bench-cross':[31488,39680,32000,40192],
       'canopy-top':[31555,38657,32311,38913], 'canopy-bottom':[31555,38917,32311,39173],
       'canopy-left':[31555,38657,31811,39173], 'canopy-right':[32055,38657,32311,39173]}
records=[]
for name,b in boxes.items():
 crop=[b[0]-28672,b[1]-36864,b[2]-28672,b[3]-36864]
 out=OUT/(name+'.png');im.crop(crop).save(out)
 records.append({'id':name,'globalBox':b,'file':str(out),'sha256':sha(out),'sourceCrop':crop})
(OUT/'manifest.json').write_text(json.dumps({'candidate':str(path),'candidateSha256':sha(path),'operation':'unscaled integer crops from current color candidate','records':records},indent=2)+'\n')
print(str(OUT))
