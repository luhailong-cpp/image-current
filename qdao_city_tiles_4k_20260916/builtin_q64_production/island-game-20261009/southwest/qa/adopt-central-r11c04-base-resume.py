import sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
prefix='c04-hardseam-central-r11c04-resume-v01';report=ROOT/'qa'/(prefix+'-report.json');r=load(report)
artifact={'path':r['outputs'][0]['path'],'sha256':r['outputs'][0]['sha256'],'dimensions':[4096,4096],'sourceIdMask':r['outputs'][1]['path'],'record':str(report),'sourceReport':str(report),'nativeSourceCount':len(r['inputs']),'nativePixelsVerified':r['validation']['mismatchedPixels']==0,'internalPassed':False,'internalStatus':'full16 assembled; native24 seam segments inspected, golden beam step and pond detail softness need localized repair','allOuterTileEdgesPassed':False,'formalAccepted':False}
for filename in ['current-native-map.json','qa/expansion-central-worker-map.json']:
 d=load(ROOT/filename);d.setdefault('candidateArtifacts',{})['r11_c04']=artifact;d['updatedAtUtc']=now();dump(ROOT/filename,d)
s=load(ROOT/'progress.json');s.setdefault('currentAdopted4kArtifacts',{})['r11_c04']=artifact
s.setdefault('currentAdopted4kFiles',{})['r11_c04']=artifact['path']
s.update(updatedAtUtc=now(),currentCandidate=artifact['path'],currentPreview=r['outputs'][3]['path'],candidate4kCount=9,complete4kCount=9,fullyCovered4kCount=9,remainingTiles=40,missingCoreCount=784-s['selectedCandidateCoreCount'],savedSourceRecordCount=len(list((ROOT/'native').glob('*.png.generation.json'))))
s['remainingCoreCoordinates']={tile:[{'subrow':ri+1,'subcolumn':ci+1} for ri,row in enumerate(arr) for ci,stem in enumerate(row) if not stem] for tile,arr in load(ROOT/'current-native-map.json').items() if re.fullmatch(r'r\d{2}_c\d{2}',tile) and isinstance(arr,list) and any(not x for row in arr for x in row)}
dump(ROOT/'progress.json',s)
resume=load(ROOT/'production-resume-20261012.json');resume.update(updatedAtUtc=now(),candidate4kCount=9,remainingTilesWithoutFullCandidate=40,savedSourceRecordCount=s['savedSourceRecordCount'],generatedNativeCount=s['generatedNativeCount'],selectedCandidateCoreCount=s['selectedCandidateCoreCount'],missingCoreCount=s['missingCoreCount'],currentAdopted4kFiles=s['currentAdopted4kArtifacts'],currentCoordinate='r11_c04 all16 core positions; eave and pond local repairs next');dump(ROOT/'production-resume-20261012.json',resume)
print({'completeCandidateCount':9,'formalAccepted':0,'path':artifact['path'],'exactSameCoordinatePixels':r['validation']['pixelCount']})

