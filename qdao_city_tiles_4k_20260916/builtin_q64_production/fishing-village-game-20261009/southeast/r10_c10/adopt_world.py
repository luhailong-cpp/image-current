"""Propagate a bounded unscaled native edit to every intersecting local patch."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
T=Path(__file__).resolve().parent
pid,repair_rel,tag=sys.argv[1:4];box=list(map(int,sys.argv[4:8]))
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
coords={p['id']:p['globalBox'] for p in read(T/'coordinate-plan.json')['patches']}
gb=coords[pid];world=[gb[0]+box[0],gb[1]+box[1],gb[0]+box[2],gb[1]+box[3]]
repair=T/repair_rel;edit=Image.open(repair).convert('RGB');assert edit.size==(1254,1254)
sel=read(T/'selected-patches.json');records=[]
for key,rel in list(sel['patches'].items()):
 pb=coords[key];b=[max(pb[0],world[0]),max(pb[1],world[1]),min(pb[2],world[2]),min(pb[3],world[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 base=T/rel;im=Image.open(base).convert('RGB');original=np.asarray(im).copy()
 crop=[b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]];dest=[b[0]-pb[0],b[1]-pb[1],b[2]-pb[0],b[3]-pb[1]]
 im.paste(edit.crop(crop),tuple(dest[:2]));out=T/'processed'/f'{key}-{tag}.png';assert not out.exists();im.save(out)
 mask=np.ones((1254,1254),bool);mask[dest[1]:dest[3],dest[0]:dest[2]]=False;assert np.array_equal(np.asarray(im)[mask],original[mask])
 rec={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'base':{'path':str(base),'sha256':sha(base)},'repair':{'path':str(repair),'sha256':sha(repair)},'repairGlobalBox':gb,'adoptedWorldBox':b,'repairCrop':crop,'destination':dest,'operation':'unscaled bounded native edit propagated to intersecting core and halo pixels','resamplingApplied':False,'outsideAdoptedRegionExactMatch':True}
 out.with_suffix('.png.derivation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8');sel['patches'][key]=out.relative_to(T).as_posix();records.append({'patch':key,'worldBox':b})
(T/'selected-patches.json').write_text(json.dumps(sel,indent=2),encoding='utf-8')
print(json.dumps({'worldBox':world,'outputs':records}))

