from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
m=load(ROOT/'current-native-map.json');s=load(ROOT/'progress.json');targets={f'r{r:02}_c{c:02}' for r in range(8,15) for c in range(1,8)}
assert len(targets)==49
selected={t:sum(bool(x) for row in m[t] for x in row) if isinstance(m.get(t),list) else 0 for t in targets}
full=[t for t,n in selected.items() if n==16];art=m['candidateArtifacts'];passed=[t for t,a in art.items() if t in targets and (a.get('internalPassed') or a.get('internalTileSeamsPassed'))];pending=[t for t in full if t not in passed];missing=[t for t,n in selected.items() if n<16]
metrics={'checkedAtUtc':now(),'deduplicatedTargetTileCount':49,'tilesWithAll16NativeCores':len(full),'verified4kCandidateTileCount':len(art),'internallyPassedTileCount':len(passed),'tilesStillMissingNativeCores':len(missing),'completeNativeTilesPendingRepairOrInternalReview':len(pending),'selectedNativeCoreCount':sum(selected.values()),'missingNativeCoreCount':784-sum(selected.values()),'fullNativeTiles':sorted(full),'internallyPassedTiles':sorted(passed),'completeNativeTilesPendingRepairOrInternalReviewList':sorted(pending),'tilesStillMissingNativeCoresList':sorted(missing),'outerEdgesPendingIsNotMissingNativeCoverage':True,'formalAcceptedCount':0,'generationContinuing':True,'currentCentralPosition':'r12_c03_s04_02 guide ready, no un-ingested successful root output; last s04_01 original preserved'}
assert metrics['tilesWithAll16NativeCores']+metrics['tilesStillMissingNativeCores']==49
s['currentZoneMetrics']=metrics;s['updatedAtUtc']=now();dump(ROOT/'progress.json',s);dump(ROOT/'qa'/'current-deduplicated-zone-metrics-20261012.json',metrics)
res=load(ROOT/'production-resume-20261012.json');res['currentZoneMetrics']=metrics;res['updatedAtUtc']=now();dump(ROOT/'production-resume-20261012.json',res)
print({k:v for k,v in metrics.items() if not isinstance(v,list)})
