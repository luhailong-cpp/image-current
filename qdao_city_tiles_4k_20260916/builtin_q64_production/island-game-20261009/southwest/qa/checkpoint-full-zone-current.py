from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
main=load(ROOT/'current-native-map.json');art=main.setdefault('candidateArtifacts',{})
added=[]
for worker in (ROOT/'qa').glob('expansion-*-worker-map.json'):
 for tile,a in load(worker).get('candidateArtifacts',{}).items():
  if tile in art:continue
  rp=a.get('sourceReport') or a.get('report') or a['record'];r=load(rp);assert r['validation']['mismatchedPixels']==0 and r['validation']['pixelCount']==4096**2
  with Image.open(a['path']) as im:assert im.size==(4096,4096)
  assert hashfile(a['path'])==a['sha256'];art[tile]=a;added.append(tile)
main['updatedAtUtc']=now();dump(ROOT/'current-native-map.json',main)
s=load(ROOT/'progress.json');selected=sum(bool(x) for tile,arr in main.items() if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list) for row in arr for x in row)
remaining={tile:[{'subrow':ri+1,'subcolumn':ci+1} for ri,row in enumerate(arr) for ci,stem in enumerate(row) if not stem] for tile,arr in main.items() if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list) and any(not x for row in arr for x in row)}
s.update(updatedAtUtc=now(),currentAdopted4kArtifacts=art,currentAdopted4kFiles={t:a['path'] for t,a in art.items()},selectedCandidateCoreCount=selected,missingCoreCount=784-selected,remainingCoreCoordinates=remaining,savedSourceRecordCount=len(list((ROOT/'native').glob('*.png.generation.json'))),candidate4kCount=len(art),complete4kCount=len(art),fullyCovered4kCount=len(art),remainingTiles=49-len(art),internalPassed4kCount=sum(bool(a.get('internalPassed') or a.get('internalTileSeamsPassed')) for a in art.values()),formalAcceptedCount=0,generationHoldActive=False,networkGenerationBlocked=False,blocking=None,status='generating_full_southwest_zone');dump(ROOT/'progress.json',s)
res=load(ROOT/'production-resume-20261012.json');res.update(updatedAtUtc=now(),candidate4kCount=len(art),remainingTilesWithoutFullCandidate=49-len(art),savedSourceRecordCount=s['savedSourceRecordCount'],generatedNativeCount=s['generatedNativeCount'],selectedCandidateCoreCount=selected,missingCoreCount=784-selected,currentAdopted4kFiles=art);dump(ROOT/'production-resume-20261012.json',res)
assert hashfile(ROOT/'migration-freeze-20261011.json')=='3fa6ba6959db01995e5939314bfade83e68eecf2fcb1647bebad53e2a714f606'
print({'candidates':len(art),'added':added,'selected':selected,'generated':s['generatedNativeCount'],'missing':784-selected,'internalPassed':s['internalPassed4kCount'],'formal':0})
