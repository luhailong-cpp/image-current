"""Adopt exact-world native joint repairs into all selected core/halo sources."""
from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import tile_native_workflow as w
T=Path(__file__).resolve().parent
assert T.name=='r12_c10'
stem,repair_rel,tag=sys.argv[1:4];rect=list(map(int,sys.argv[4:8]))
req=w.read(T/'repairs'/(stem+'.request.json'));gb=req['coordinate']['globalBox']
world=[gb[0]+rect[0],gb[1]+rect[1],gb[0]+rect[2],gb[1]+rect[3]]
repair=T/repair_rel;edit=Image.open(repair).convert('RGB');assert edit.size==(1254,1254)
sel=w.read(T/'selected-patches.json');coords={p['id']:p['globalBox'] for p in w.read(T/'coordinate-plan.json')['patches']}
records=[]
for pid,rel in list(sel['patches'].items()):
 pb=coords[pid];b=[max(pb[0],world[0]),max(pb[1],world[1]),min(pb[2],world[2]),min(pb[3],world[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 base=T/rel;im=Image.open(base).convert('RGB');original=np.asarray(im).copy()
 crop=[b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]];at=[b[0]-pb[0],b[1]-pb[1],b[2]-pb[0],b[3]-pb[1]]
 im.paste(edit.crop(crop),tuple(at[:2]))
 out=T/'processed'/(pid+'-'+tag+'.png');out.parent.mkdir(exist_ok=True);assert not out.exists();im.save(out)
 mask=np.ones((1254,1254),bool);mask[at[1]:at[3],at[0]:at[2]]=False;assert np.array_equal(np.asarray(im)[mask],original[mask])
 rec={'file':str(out),'sha256':w.sha(out),'nativeDimensions':[1254,1254],'base':{'path':str(base),'sha256':w.sha(base)},'repair':{'path':str(repair),'sha256':w.sha(repair)},'repairGlobalBox':gb,'adoptedWorldBox':b,'repairCrop':crop,'destination':at,'operation':'unscaled native joint edit replacement in all intersecting source core and halo pixels','resamplingApplied':False,'imageBlur':False,'imagePixelBlend':False,'outsideAdoptedRegionExactMatch':True}
 w.write(out.with_suffix('.png.derivation.json'),rec);sel['patches'][pid]=out.relative_to(T).as_posix();records.append({'patch':pid,'worldBox':b})
sel['updatedAt']=w.now();w.write(T/'selected-patches.json',sel);w.write(T/'repairs'/(tag+'-adoption.json'),{'worldBox':world,'repair':str(repair),'outputs':records})
print(json.dumps({'worldBox':world,'outputs':records}))
