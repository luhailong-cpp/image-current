from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast');D=Path(__file__).resolve().parent
box=(32150,44941,33404,46195)
base=Image.new('RGB',(1254,1254));sources=[]
for tile in ['r11_c08','r11_c09','r12_c08','r12_c09']:
 T=Z/tile
 plan=json.loads((T/'coordinate-plan.json').read_text()); coords={p['id']:p['globalBox'] for p in plan['patches']}
 sel=json.loads((T/'selected-patches.json').read_text())['patches']
 if tile=='r12_c08':sel['p14']='native/p14-v2.png'
 for pid,rel in sel.items():
  g=coords[pid];c=(g[0]+115,g[1]+115,g[0]+1139,g[1]+1139)
  b=(max(c[0],box[0]),max(c[1],box[1]),min(c[2],box[2]),min(c[3],box[3]))
  if b[0]>=b[2] or b[1]>=b[3]:continue
  p=T/rel;crop=tuple(b[i]-g[i%2] for i in range(4))
  base.paste(Image.open(p).crop(crop),(b[0]-box[0],b[1]-box[1]))
  sources.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crop':crop,'worldBox':b,'selected':not(tile=='r12_c08' and pid=='p14')})
out=D/'r12c08-rail-v2-actual-core-preview';out.mkdir(exist_ok=True)
base.save(out/'input-actual-cores.png')
rect=(315,65,1000,720)
p=base.copy();p.paste(Image.open(D/'r12c08-rail-joint-v2.png').crop(rect),rect[:2]);p.save(out/'candidate.png')
boxes={'left':(219,1,411,784),'right':(904,1,1096,784),'top':(251,1,1064,161),'bottom':(251,624,1064,784),'north-core':(0,0,1254,320),'north-cross':(362,0,874,371)}
records=[]
for name,b in boxes.items():
 path=out/(name+'.png');p.crop(b).save(path);records.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'localBox':b})
manifest={'worldBox':box,'nativeAdoptionRect':rect,'worldAdoptionRect':[32465,45006,33150,45661],'candidateSource':str(D/'r12c08-rail-joint-v2.png'),'sources':sources,'evidence':records,'selected':False,'formalAccepted':False,'resamplingApplied':False}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'sources':len(sources),'evidence':len(records)}))

