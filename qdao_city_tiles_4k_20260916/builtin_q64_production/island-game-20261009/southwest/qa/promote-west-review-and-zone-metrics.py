from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
main=load(ROOT/'current-native-map.json');w=load(ROOT/'qa'/'expansion-west-worker-map.json')['candidateArtifacts']['r10_c02'];review=ROOT/'qa'/'c04-hardseam-west-r10c02-v01-review.json';v=load(review)
assert v['candidateSha256']==hashfile(w['path']) and v['visualReview']['internalTileSeamsPassed'] is True
w.update(internalPassed=True,internalStatus='pass native24 seams and9junctions viewed by west; root layout preview seen',review=str(review),allOuterTileEdgesPassed=False,formalAccepted=False)
main['candidateArtifacts']['r10_c02']=w;main['updatedAtUtc']=now();dump(ROOT/'current-native-map.json',main)
print({'promoted':'r10_c02','review':str(review)})
