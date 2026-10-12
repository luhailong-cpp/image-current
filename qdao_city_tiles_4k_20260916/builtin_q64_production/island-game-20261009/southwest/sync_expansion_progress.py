"""Synchronize disjoint expansion selections; never reduce completed artifacts."""
import re
from production import *

def sync():
 idx=load(ROOT/'current-native-map.json'); workers=[]
 for p in sorted((ROOT/'qa').glob('expansion-*-worker-map.json')):
  data=load(p)
  for tile,arr in data.items():
   if not re.fullmatch(r'r\d{2}_c\d{2}',tile) or not isinstance(arr,list):continue
   assert len(arr)==4 and all(len(row)==4 for row in arr)
   target=idx.setdefault(tile,[[None]*4 for _ in range(4)])
   for r,row in enumerate(arr):
    for c,stem in enumerate(row):
     if stem:assert (ROOT/'native'/f'{stem}.png.generation.json').exists();target[r][c]=stem
   workers.append({'path':str(p),'tile':tile,'selectedCount':sum(x is not None for row in arr for x in row)})
 idx['updatedAtUtc']=now();dump(ROOT/'current-native-map.json',idx)
 generated=[];covered=set()
 for p in (ROOT/'native').glob('*.png.generation.json'):
  rec=load(p)
  if rec.get('tool')=='image_gen.imagegen' or rec.get('route')=='builtin':generated.append(str(p))
  co=rec.get('coordinates',{})
  if co.get('tile') and co.get('subrow') and co.get('subcolumn'):covered.add((co['tile'],co['subrow'],co['subcolumn']))
 selected=sum(sum(x is not None for row in arr for x in row) for tile,arr in idx.items() if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list))
 s=load(ROOT/'progress.json');s.update(updatedAtUtc=now(),generatedNativeCount=len(generated),corePositionsGenerated=len(covered),selectedCandidateCoreCount=selected,corePositionsCovered=selected,expansionWorkers=workers);dump(ROOT/'progress.json',s)
 dump(ROOT/'qa/expansion-current-sync.json',{'createdAtUtc':now(),'generatedNativeCount':len(generated),'selectedCoreCount':selected,'workers':workers,'currentExportedCandidates':s.get('candidate4kCount'),'formalAccepted':False})
 print({'generated':len(generated),'selectedCoreCount':selected,'workers':workers})

if __name__=='__main__':sync()
