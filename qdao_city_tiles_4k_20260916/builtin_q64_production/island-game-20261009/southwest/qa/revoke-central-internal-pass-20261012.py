from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
issue={'reportedAtUtc':now(),'reviewer':'independent west','globalApproxBox':[15960,43782,16384,44282],'detail':'Right pond leaf and stem region remains soft compared to adopted crisp left pond; full visual pass revoked pending repair.'}
for f in ['current-native-map.json','qa/expansion-central-worker-map.json']:
 d=load(ROOT/f);a=d['candidateArtifacts']['r11_c04'];a.update(internalPassed=False,internalTileSeamsPassed=False,internalStatus='geometry continuous in root review, independent detail exception: soft right pond foliage requires repair',independentReviewException=issue);d['updatedAtUtc']=now();dump(ROOT/f,d)
p=ROOT/'qa'/'central-r11c04-resume-final-root-review.json';r=load(p);r['internalReview']['status']='superseded: independent right pond detail issue';r['independentReviewException']=issue;dump(p,r)
s=load(ROOT/'progress.json');s['currentAdopted4kArtifacts']=load(ROOT/'current-native-map.json')['candidateArtifacts'];s['internalPassed4kCount']=sum(bool(v.get('internalPassed') or v.get('internalTileSeamsPassed')) for v in s['currentAdopted4kArtifacts'].values());s['updatedAtUtc']=now();dump(ROOT/'progress.json',s)
print({'internalPassed':s['internalPassed4kCount'],'exception':issue})
