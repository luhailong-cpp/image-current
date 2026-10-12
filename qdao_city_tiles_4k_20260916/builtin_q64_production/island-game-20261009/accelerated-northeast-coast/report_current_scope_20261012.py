from pathlib import Path
import coast_work as c
B=Path(__file__).resolve().parent
p=c.read(B/'progress.json')
s=c.read(B/'current-selection-20261012.json')
assert len(s['candidates'])==4 and sum(len(v) for v in s['native'].values())==64
updates={'deduplicatedTargetWholeTileCount':4,'tilesWithAll16NativeCoresCount':4,
 'complete4096CandidateCount':4,'internallyReviewedWholeTileCount':3,
 'wholeTilesMissingNativeCoresCount':0,'completeWholeTilesPendingRepairOrReviewCount':1,
 'remainingCoreCount':0,'remainingCoordinates':[],'coveredCoreCount':64,
 'pendingNecessaryRepairsCount':0,'pendingFinalReviewTiles':['r01_c14'],
 'externalNeighborAcceptanceIsNotMissingLocalArtwork':True,
 'currentTile':'r01_c14','currentPatch':None,'inFlightRequestCount':0,
 'status':'regional_candidates_ready_final_qa_pending','updatedAtUtc':c.now(),
 'nextStep':'Finish r01_c14 current selected-source final QA; run four-candidate integrity audit and build verified local delivery.',
 'latestUserContinuationAuthorization':'继续做完，然后并告诉我都还剩多少'}
p.update(updates);c.write(B/'progress.json',p)
print({k:p[k] for k in ['deduplicatedTargetWholeTileCount','complete4096CandidateCount','internallyReviewedWholeTileCount','wholeTilesMissingNativeCoresCount','completeWholeTilesPendingRepairOrReviewCount','remainingCoreCount']})

