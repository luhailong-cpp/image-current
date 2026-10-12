from PIL import Image
from pathlib import Path
import json,hashlib
D=Path(__file__).parent;ROOT=D.parents[1]
p=ROOT/'r04_c05/continuation-20261011/south-v3/integrated-candidate-native.png';im=Image.open(p);assert hashlib.sha256(p.read_bytes()).hexdigest()=='0e9a0c64dd52be40467e10750e4de055051de8fdf67dd26deba57e4506a6f35f'
boxes={'timber-residual':[0,850,500,1200],'pavement-line':[1820,1870,2320,2190],'plinth-tone':[1790,2640,2290,3290],'south-green':[2940,3850,4096,4096]}
out=[]
for name,box in boxes.items():
 f=D/('diagnostic-c05-'+name+'.png');im.crop(box).save(f);out.append({'label':name,'file':str(f),'tileBox':box,'sourceCandidate':str(p),'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativePixelScale':1,'resampled':False})
(D/'c05-diagnostic-crops.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

