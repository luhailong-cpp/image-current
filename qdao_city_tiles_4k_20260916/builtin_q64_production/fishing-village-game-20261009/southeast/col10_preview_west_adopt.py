from PIL import Image
from pathlib import Path
import tile_native_workflow as w
import json
T=w.ZONE/'r12_c10';S=T/'processed/weststairs-v2-preview';S.mkdir(parents=True,exist_ok=True)
repair=T/'repairs/west-stairs-joint-v2.png';gb=[36237,45965,37491,47219];world=[36864,46080,37376,47219];sel=w.read(T/'selected-patches.json');coords={p['id']:p['globalBox'] for p in w.read(T/'coordinate-plan.json')['patches']};records=[]
for pid,rel in sel['patches'].items():
 p=coords[pid];b=[max(p[0],world[0]),max(p[1],world[1]),min(p[2],world[2]),min(p[3],world[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 base=T/rel;im=Image.open(base).convert('RGB');crop=[b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]];at=[b[0]-p[0],b[1]-p[1],b[2]-p[0],b[3]-p[1]];im.paste(Image.open(repair).crop(crop),at[:2]);out=S/(pid+'-weststairs-v2-candidate.png');im.save(out)
 d={'patch':pid,'file':str(out),'sha256':w.sha(out),'base':str(base),'baseSha256':w.sha(base),'repair':str(repair),'repairSha256':w.sha(repair),'repairCrop':crop,'destination':at,'worldBox':b,'resamplingApplied':False,'imageBlur':False,'imagePixelBlend':False,'status':'provisional unselected'};w.write(out.with_suffix('.png.derivation.json'),d);records.append(d)
w.write(S/'manifest.json',{'worldBox':world,'outputs':records,'status':'provisional unselected'})
Q=T/'qa/weststairs-v2-preview';Q.mkdir(parents=True,exist_ok=True)
overrides={('r12_c09',pid):w.ZONE/'r12_c09'/rel for pid,rel in w.read(w.ZONE/'r12_c09/processed/joint-stairs/provisional-selection.json')['replacements'].items()};overrides.update({('r12_c10',r['patch']):Path(r['file']) for r in records})
def crop_world(box):
 im=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));sources=[]
 for tile in ['r12_c09','r12_c10']:
  D=w.ZONE/tile;coord={p['id']:p['globalBox'] for p in w.read(D/'coordinate-plan.json')['patches']}
  for pid,rel in w.read(D/'selected-patches.json')['patches'].items():
   g=coord[pid];c=[g[0]+115,g[1]+115,g[2]-115,g[3]-115];b=[max(c[0],box[0]),max(c[1],box[1]),min(c[2],box[2]),min(c[3],box[3])]
   if b[0]>=b[2] or b[1]>=b[3]:continue
   src=overrides.get((tile,pid),D/rel);im.paste(Image.open(src).crop((b[0]-g[0],b[1]-g[1],b[2]-g[0],b[3]-g[1])),(b[0]-box[0],b[1]-box[1]));sources.append({'path':str(src),'sha256':w.sha(src)})
 return im,sources
boxes={'left':[36189,45952,36445,47347],'right':[37248,45952,37504,47104],'top':[36189,45952,37504,46208],'bottom-left':[36189,46976,36864,47232],'core-shared-edge':[36608,46080,37120,47104]}
qa=[]
for key,b in boxes.items():
 im,ss=crop_world(b);f=Q/(key+'.png');im.save(f);d={'file':str(f),'globalBox':b,'sha256':w.sha(f),'sources':ss,'resamplingApplied':False};w.write(f.with_suffix('.png.derivation.json'),d);qa.append(d)
w.write(Q/'manifest.json',qa);print(json.dumps({'provisional':records,'QA':str(Q)}))
