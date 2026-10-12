from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from assemble_r03_c03 import append_hard
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=R/'work-r04_c04/tiles/r04_c04.candidate-repair-v5.png'
a=R/'native/r04_c04_s04_s03_v01.png';b=R/'native/r04_c04_s04_s04_v01.png'
aa,bb=[np.array(Image.open(z).convert('RGB')) for z in [a,b]]
pixels,ids,path=append_hard(aa,np.ones(aa.shape[:2],np.uint8),bb,np.full(bb.shape[:2],2,np.uint8),'foot-context')
crop=pixels[:,79:1333].copy();cis=ids[:,79:1333].copy()
# Before bottom halo, use exact current repaired tile pixels.
base=np.array(Image.open(p));crop[:1139]=base[2957:4096,2012:3266]
o=R/'work-r04_c04/guides/r04_c04_tall_wood_foot_bridge_v01.guide.png';Image.fromarray(crop).save(o)
rec={'file':str(o),'sha256':sha(o),'globalNativeBox':[14300,15245,15554,16499],'insideTileSource':str(p),'insideTileSha256':sha(p),'sourceCrop':[2012,2957,3266,4096],'bottomHaloSources':[{'file':str(z),'sha256':sha(z)} for z in [a,b]],'bottomContextHardcutPath':path,'resample':False,'operation':'exact existing final pixels plus native bottom halo; guide only'}
Path(str(o)+'.derivation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(str(o))

