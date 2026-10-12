from pathlib import Path
import sys,json
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import tile_native_workflow as w
T=Path(__file__).resolve().parent;Q=T/'qa/adoption';Q.mkdir(parents=True,exist_ok=True)
def crop_world(box):
 im=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));sources=[]
 for tile in ['r12_c09','r12_c10']:
  S=w.ZONE/tile;plan=w.read(S/'coordinate-plan.json');coords={p['id']:p for p in plan['patches']}
  for pid,rel in w.read(S/'selected-patches.json')['patches'].items():
   g=coords[pid]['globalBox'];core=[g[0]+115,g[1]+115,g[0]+1139,g[1]+1139];b=[max(core[0],box[0]),max(core[1],box[1]),min(core[2],box[2]),min(core[3],box[3])]
   if b[0]>=b[2] or b[1]>=b[3]:continue
   src=S/rel;im.paste(Image.open(src).crop((b[0]-g[0],b[1]-g[1],b[2]-g[0],b[3]-g[1])),(b[0]-box[0],b[1]-box[1]));sources.append({'path':str(src),'sha256':w.sha(src)})
 return im,sources
boxes={'joint-top':[36851,45587,38131,45843],'joint-left':[36851,45587,37107,46997],'joint-right-upper':[37875,45587,38131,46195],'joint-bottom-left':[36851,46741,37888,46997],'west-row2':[36608,46080,37120,47104]}
records=[]
for name,b in boxes.items():
 im,src=crop_world(b);p=Q/(name+'.png');im.save(p);d={'file':str(p),'sha256':w.sha(p),'globalBox':b,'sources':src,'resamplingApplied':False,'visualStatus':'pending'};w.write(p.with_suffix('.png.derivation.json'),d);records.append(d)
w.write(Q/'stairs-manifest.json',records);print(json.dumps({'count':len(records),'path':str(Q)}))
