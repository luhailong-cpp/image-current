import json
from pathlib import Path
import pipeline as p
items=[];contract=p.contract()
neighbors={'r03_c04':{'north':'r02_c04','west':'r03_c03'},'r03_c05':{'north':'r02_c05','east':'r03_c06'},'r04_c04':{'west':'r04_c03','south':'r05_c04'},'r04_c05':{'east':'r04_c06','south':'r05_c05'}}
for tile,edges in neighbors.items():
 for side,other in edges.items():
  directory=p.tile_dir(other,contract);patches=[f's04_{i:02d}' if side=='north' else f's01_{i:02d}' if side=='south' else f's{i:02d}_04' if side=='west' else f's{i:02d}_01' for i in range(1,5)]
  sources=[]
  for patch in patches:
   f=p.selected(directory,patch)
   sources.append({'patch':patch,'file':str(f),'exists':f.exists(),'sha256':p.sha(f) if f.exists() else None})
  items.append({'tile':tile,'edge':side,'neighbor':other,'available':sum(v['exists'] for v in sources),'sources':sources})
p.put_json(p.ROOT/'outer-neighbor-inventory.json',{'edges':items})
print(json.dumps([{'tile':i['tile'],'edge':i['edge'],'neighbor':i['neighbor'],'available':i['available']} for i in items]))
