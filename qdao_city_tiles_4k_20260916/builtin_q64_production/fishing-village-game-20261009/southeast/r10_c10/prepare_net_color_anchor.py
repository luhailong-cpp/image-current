"""Assemble original core/halo pixels as the color anchor around a p24 edit."""
from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths={'p13':'processed/p13-joint-p13-p14-v1.png','p14':'processed/p14-joint-p13-p14-v1.png','p23':'native/p23-v1.png','p24':'native/p24-v1.png','p33':'processed/p33-joint-p33-p34-v1.png','p34':'processed/p34-joint-p33-p34-v1.png'}
coords={p['id']:p['globalBox'] for p in json.loads((T/'coordinate-plan.json').read_text())['patches']}
gb=coords['p24'];im=Image.open(T/paths['p24']).convert('RGB');sources=[]
for pid,rel in paths.items():
 p=T/rel;c=coords[pid];core=[c[0]+115,c[1]+115,c[2]-115,c[3]-115]
 b=[max(gb[0],core[0]),max(gb[1],core[1]),min(gb[2],core[2]),min(gb[3],core[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 crop=[b[0]-c[0],b[1]-c[1],b[2]-c[0],b[3]-c[1]];dest=[b[0]-gb[0],b[1]-gb[1]]
 im.paste(Image.open(p).crop(crop),tuple(dest));sources.append({'path':str(p),'sha256':sha(p),'crop':crop,'destination':dest,'worldBox':b})
out=T/'processed/p24-pre-edit-world-anchor.png';im.save(out)
out.with_suffix('.png.derivation.json').write_text(json.dumps({'file':str(out),'sha256':sha(out),'globalBox':gb,'dimensions':[1254,1254],'sources':sources,'fallbackHaloSource':paths['p24'],'operation':'unscaled native core composite as color-only anchor; not game artwork','resamplingApplied':False},indent=2))

