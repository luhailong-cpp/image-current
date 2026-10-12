"""Compose the three independent source audits without modifying their inputs."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import re

OUT = Path(__file__).resolve().parent
REPO = OUT.parent.parent.parent.parent
BASE = REPO/'qdao_city_tiles_4k_20260916/builtin_q64_production'
DEST = OUT/'island-east-verification-v1.json'
QUEUE = OUT/'remaining-owner-queues-v1.json'
assert not DEST.exists() and not QUEUE.exists()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def ref(p):
    return {'repositoryRelativePath':p.relative_to(REPO).as_posix(),'sha256':sha(p)}

names={'northeast':'northeast-sources-v1.json','southeast':'southeast-sources-v2.json','accelerated-northeast-coast':'coast-sources-v2.json'}
reports={z:read(OUT/n) for z,n in names.items()}
ne,se,co=[reports[z] for z in names]
ns,ss,cs=ne['summary'],se['summary'],co['summary']

per_zone=[
 {'zone':'northeast','ownedTileCount':ns['ownedTileCount'],'completeCandidateFileHashSizeConfirmedCount':ns['currentCompleteCandidateFileHashSizeConfirmedCount'],'completeCandidateSourceAndPositionConfirmedCount':ns['completeCandidateOriginAndContributionConfirmedCount'],'selectedUniqueNativeSourceCount':ns['selectedReferencedUniqueNativeSourceCount'],'nativeContributionPositionsConfirmedCount':ns['confirmedNativeContributionCount'],'nativeContributionPositionsUncertainCount':ns['uncertainNativeContributionCount'],'missingReferencedSourceFileCount':ns['missingNativeSourceFileCount'],'incompleteOwnedTileCount':ns['incompleteOwnedTileCount'],'missingSelectedCoreCount':ns['missingSelectionCoreCount'],'missingGeneratedCoreCountFromCurrentInventory':ns['missingGeneratedCoreCountFromCurrentInventory'],'generatedButUnselectedCurrentCandidateCount':ns['currentGeneratedButUnselectedCandidateCount'],'actualImageModelUnconfirmedNativeCount':ns['selectedReferencedUnknownModelNativeSourceCount']},
 {'zone':'southeast','ownedTileCount':49,'completeCandidateFileHashSizeConfirmedCount':ss['candidateFileAndHashConfirmedCount'],'completeCandidateSourceAndPositionConfirmedCount':ss['currentCompleteCandidateCount'],'selectedUniqueNativeSourceCount':ss['currentReferencedUniqueNativeSourceCount'],'nativeContributionPositionsConfirmedCount':ss['contributionMappingsConfirmedCount'],'nativeContributionPositionsUncertainCount':ss['contributionMappingUncertainCount'],'missingReferencedSourceFileCount':ss['referencedNativeFileMissingCount'],'incompleteOwnedTileCount':ss['missingFullNativeTileCountFromCurrentLists'],'missingSelectedCoreCount':ss['currentSelectedMissingCoreCount'],'missingGeneratedCoreCountFromCurrentInventory':ss['noSavedNativeInCurrentInventoryCoreCount'],'generatedButUnselectedCurrentCandidateCount':ss['existingSavedButUnselectedCoreCount'],'actualImageModelUnconfirmedNativeCount':ss['actualModelUnconfirmedUniqueNativeCount']},
 {'zone':'accelerated-northeast-coast','ownedTileCount':4,'completeCandidateFileHashSizeConfirmedCount':cs['currentCompleteCandidateTilesConfirmed'],'completeCandidateSourceAndPositionConfirmedCount':cs['currentCompleteCandidateTilesConfirmed'],'selectedUniqueNativeSourceCount':cs['uniqueSelectedNativeSourceImagesConfirmed'],'nativeContributionPositionsConfirmedCount':cs['nativeContributionPositionsConfirmed'],'nativeContributionPositionsUncertainCount':cs['sourceIdentityOrPositionUncertainCount'],'missingReferencedSourceFileCount':cs['missingSelectedNativeFiles'],'incompleteOwnedTileCount':0,'missingSelectedCoreCount':0,'missingGeneratedCoreCountFromCurrentInventory':0,'generatedButUnselectedCurrentCandidateCount':0,'actualImageModelUnconfirmedNativeCount':cs['actualImageModelUnknownNativeCount']}
]
summary={k:sum(z[k] for z in per_zone) for k in per_zone[0] if k!='zone'}
summary['totalOwnedCorePositions']=summary['ownedTileCount']*16
summary['selectedCorePositions']=summary['totalOwnedCorePositions']-summary['missingSelectedCoreCount']
summary['formalAcceptedCount']=0
summary['sourceIdentityPositionUncertainCount']=summary['nativeContributionPositionsUncertainCount']
summary['historicalAnchorReviewAssociationsUncertainCount']=ns['uncertainHistoricalAnchorReviewAssociations']
summary['secondaryPointerConflictingRecordCount']=ss['secondaryPointerDifferenceRecordCount']
summary['secondaryPointerConflictingFieldCount']=ss['secondaryPointerDifferenceFieldCount']
selected_source_paths={x['source'] for x in ne['nativeContributions']} | {x['path'] for x in se['migration']['checkedNativeSources']} | {x['repositoryRelativePath'] for t in co['tiles'] for x in t['sources']}
assert len(selected_source_paths)==summary['selectedUniqueNativeSourceCount']
summary['selectedNativeSourcesGloballyDeduplicated']=True
summary['currentReferencedNativeSourcesIncludingUnselectedConfirmedCount']=summary['selectedUniqueNativeSourceCount']+summary['generatedButUnselectedCurrentCandidateCount']
summary['unknownModelDoesNotImplyMissingSource']=True
summary['mapComplete']=False

# Core coordinates in both source naming conventions are expanded to one explicit
# tile/subrow/subcolumn id and a repository-independent world pixel rectangle.
def normalize(tile, core):
    nums=re.search(r'_p(\d+)_(\d+)',core)
    if nums:
        sr,sc=map(int,nums.groups())
    else:
        sr,sc=int(core[0]),int(core[1])
    tr,tc=map(int,re.fullmatch(r'r(\d+)_c(\d+)',tile).groups())
    x=(tc-1)*4096+(sc-1)*1024
    y=(tr-1)*4096+(sr-1)*1024
    return {'coreId':f'{tile}_p{sr:02d}_{sc:02d}','coreWorldBox':[x,y,x+1024,y+1024]}

owner_queues={}
for zone,items in [('northeast',ne['suggestedAdjacentOwnerQueue']),('southeast',se['remainingQueue']['connectedPriorityBatch'])]:
    q=[]
    for priority,item in enumerate(items,1):
        tile=item.get('tileId',item.get('tile'))
        cores=item.get('missingSelectedCoreIds',item.get('missingCoreCoordinates'))
        entry={'priority':priority,'tileId':tile,'originalOwner':zone,'coordinatesReservedByThisAudit':False,'missingSelectedCoreCount':len(cores),'missingSelectedCores':[normalize(tile,c) for c in cores],'evidence':item}
        q.append(entry)
    assert 4<=len(q)<=8
    coords={tuple(map(int,re.fullmatch(r'r(\d+)_c(\d+)',x['tileId']).groups())) for x in q}
    reached={next(iter(coords))}
    while True:
        more={b for b in coords for a in reached if abs(a[0]-b[0])+abs(a[1]-b[1])==1}
        if more<=reached:break
        reached|=more
    assert reached==coords, f'Owner queue is not adjacent: {zone}'
    owner_queues[zone]={'tileCount':len(q),'missingSelectedCoreCount':sum(x['missingSelectedCoreCount'] for x in q),'fourNeighborConnected':True,'items':q}

queue_doc={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Two dated 4–8 adjacent tile suggestion queues for original owners; no coordinate reservation or image requests. Resolve full-candidate reference issues before continuing.','sourceReports':{z:ref(OUT/n) for z,n in names.items()},'ownerQueues':owner_queues,'accelerationAssignmentHasNoMissingCores':True,'latestProductionMustBeRecheckedBeforeExecution':True,'missingCurrentListCoverageDoesNotProveNoHistoricalFileExists':True,'generatedButUnselectedCurrentSourceCount':summary['generatedButUnselectedCurrentCandidateCount'],'newGenerationPerformed':False,'ownerRecordsModified':False}
queue_doc['existingSavedButUnselectedNortheastSources']=ne['currentGeneratedButUnselectedCandidates']
queue_doc['existingSavedButUnselectedSoutheastSources']=se['remainingQueue']['existingSavedButUnselectedSources']
queue_doc['fullCandidatesPendingReviewAreNotMissingCoreTiles']=['r03_c10','r12_c13']
QUEUE.write_text(json.dumps(queue_doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Reuse the companion stitching task's existing hash evidence; no image opened.
peer_root=BASE/'parallel-review-20261013/island-game-20261009/root-audit-v01'
peer_inv=read(peer_root/'inventory.json')
peer_cross=read(peer_root/'legacy-cross-zone-reuse.json')
expected={s['id']:s['sha256'] for t in co['tiles'] for s in t['sources']}
peer_sources=[s for t in peer_inv['tiles'] if t['zone']=='accelerated-northeast-coast' for s in t['sources']]
peer_matches=sum(expected.get(s['id'])==s['sha256'] for s in peer_sources)
assert peer_matches==64
se_conflicts=se['conflictsAndUncertainties']
reference_issues={'northeast':ne['referenceIssues'],'southeast':se_conflicts,'accelerated-northeast-coast':co['issues']}
reference_resolution=[
 {'priority':1,'zone':'northeast','action':'Use the 12 current complete candidate paths/hashes in the northeast report. Resolve its referenceIssues and unsupported historical anchor/review links in a new owner version. Do not pick sources by newest filename alone.','evidenceReport':ref(OUT/names['northeast'])},
 {'priority':1,'zone':'southeast','action':'Use currentAdoptedCandidates plus pendingCandidates (15 complete candidates). Eight secondary records have twelve differing path/hash fields; owner must mark the current authority or synchronize in a new version. Preserve v01/v02 alternatives and existing files.','secondaryRecordsWithDifferences':ss['secondaryPointerDifferenceRecordCount'],'differingFields':ss['secondaryPointerDifferenceFieldCount'],'evidenceReport':ref(OUT/names['southeast'])},
 {'priority':2,'zone':'accelerated-northeast-coast','action':'Four candidates and 64 selected native cores agree with the fixed compact ZIP. Keep the ZIP unchanged and also preserve the 64 native images outside it during migration. West r01_c12/r02_c12 belongs to northeast owner.'}
]

report={'schemaVersion':1,'auditId':'island-east-verification-v1','createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':{'map':'island-game-20261009','zones':list(names),'excludedOtherMapAreas':True,'onlyCurrentReferencedSourcesInspected':True,'sourceAndMissingCoordinateAuditOnly':True,'visualReviewRepeated':False,'imagesGenerated':False,'imagesEditedOrAssembled':False,'gitOperationsPerformed':False,'otherDirectoriesWritten':False,'originalOwnersRetainSourceAndProgressWriteAuthority':True,'reportDirectory':OUT.relative_to(REPO).as_posix()},'summary':summary,'perZone':per_zone,'sourceReports':{z:ref(OUT/n) for z,n in names.items()},'firstResolveCompleteCandidateReferences':reference_resolution,'referenceIssuesAndUncertainties':reference_issues,'remainingOwnerQueues':ref(QUEUE),'reusedCompanionEvidence':{'northeastAndCoastInventory':ref(peer_root/'inventory.json'),'coastNativeSourceHashesMatched':peer_matches,'crossZoneReuseReport':ref(peer_root/'legacy-cross-zone-reuse.json'),'samePixelPassedSegmentsReused':sum(x['canReusePassedEvidence'] for x in peer_cross),'segmentsTotal':len(peer_cross),'noVisualReviewPerformedByThisAudit':True,'reuseValidOnlyForCapturedMatchingHashes':True},'migration':{'pathRule':'Resolve repository-relative paths against the new clone root; original absolute D:/work/image prefixes are not a portable authority.','generationCachePathRule':'Use retained native copies and generation records. External original output cache paths are provenance, not restoration targets.','coastDeliveryNativeImagesNotIncluded':64,'doNotRestoreDeletedDirectories':True,'fixedSnapshotOrUploadBatchModified':False,'uploadStatusConfirmedByThisAudit':False},'currentModelPolicy':co['currentModelPolicy'],'snapshotLimits':{'northeastAuditStartedAtUtc':ne.get('auditStartedAtUtc'),'northeastAuditCompletedAtUtc':ne['createdAtUtc'],'northeastChangedInputRecordCount':ns['inputRecordChangedDuringAuditCount'],'southeastSnapshot':{k:v for k,v in se['inputSnapshot'].items() if k!='inputs'},'coastLastFreshnessCheckAtUtc':co['freshnessAfterProductionResumed']['checkedAtUtc'],'coastChangedInputCount':len(co['freshnessAfterProductionResumed']['changedFiles']),'newOrChangedProductionSourcesNotAutomaticallyPassed':True,'missingGeneratedCoreCountsUseCurrentInventoryOnly':True,'unreferencedHistoricalVersionsNotSearched':True},'formalAcceptedCount':0,'mapComplete':False,'taskCompleteDoesNotMeanMapComplete':True}
ne_stability=read(OUT/'northeast-source-stability-v1.json')
assert ne_stability['auditReportSha256']==sha(OUT/names['northeast'])
report['snapshotLimits']['northeastFinalStabilityReport']=ref(OUT/'northeast-source-stability-v1.json')
report['snapshotLimits']['northeastEndHashCheckFinishedAtUtc']=ne_stability['endCheckFinishedAtUtc']
report['snapshotLimits']['northeastChangedNativeOrCandidateFiles']=ne_stability['changedNativeAndCandidateFiles']
report['snapshotLimits']['northeastChangedInputRecords']=ne_stability['changedInputRecords']
DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(DEST),'queue':str(QUEUE),'summary':summary,'perZone':per_zone,'ownerQueueTileCounts':{k:v['tileCount'] for k,v in owner_queues.items()}},ensure_ascii=False,indent=2))
