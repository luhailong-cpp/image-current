from pathlib import Path
import json,sys,hashlib
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
pid,repair_rel,tag=sys.argv[1:4]
rect=list(map(int,sys.argv[4:8]));assert len(rect)==4
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(T/'selected-patches.json');base=T/s['patches'][pid];repair=T/repair_rel
im=Image.open(base).convert('RGB');edit=Image.open(repair).convert('RGB');assert im.size==edit.size==(1254,1254)
out=T/'processed'/f'{pid}-{tag}.png';assert not out.exists()
a=np.asarray(im).copy();im.paste(edit.crop(rect),(rect[0],rect[1]));im.save(out)
b=np.asarray(im);mask=np.ones((1254,1254),dtype=bool);mask[rect[1]:rect[3],rect[0]:rect[2]]=False
assert np.array_equal(a[mask],b[mask])
coord=next(p for p in read(T/'coordinate-plan.json')['patches'] if p['id']==pid)['globalBox']
d={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'operation':'unscaled bounded native AI edit replacement; all pixels outside adopted rectangle verified unchanged','base':{'path':str(base),'sha256':sha(base)},'repair':{'path':str(repair),'sha256':sha(repair)},'adoptedNativeBox':rect,'adoptedWorldBox':[coord[0]+rect[0],coord[1]+rect[1],coord[0]+rect[2],coord[1]+rect[3]],'resamplingApplied':False,'outsideAdoptionExactPixelMatch':True}
out.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
s['patches'][pid]=out.relative_to(T).as_posix();(T/'selected-patches.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
print(json.dumps(d))

