"""Finalize current production status after verified local delivery; no artwork/Git/upload changes."""
from pathlib import Path
import json
import coast_work as c
B=Path(__file__).resolve().parent
ORDER=['r02_c13','r02_c14','r01_c13','r01_c14']
manifest_path=B/'delivery-20261012/manifest.json'
m=c.read(manifest_path)
assert m['productionComplete'] and m['regionalQaComplete']
assert m['candidateTileCount']==4 and m['coveredCoreCount']==64 and m['remainingCoreCount']==0
assert m['formalAccepted'] is False and m['formalAcceptedCount']==0
archive=B/'delivery-20261012'/m['archive']['file']
archive_sha=c.sha(archive)
assert archive.with_suffix('.zip.sha256').read_text(encoding='utf-8').split()[0]==archive_sha
for tile in m['tiles']:
    assert c.sha(B/tile['file'])==tile['sha256']
    for source in tile['sources']:
        assert c.sha(B/source['file'])==source['sha256']
for path in [B/'progress.json',B/'production-resume-20261012.json']:
    p=c.read(path)
    assert p['coveredCoreCount']==64 and p['remainingCoreCount']==0 and p['complete4096CandidateCount']==4
completion_path=B/'production-completion-20261012.json'
assert not completion_path.exists()
stamp=c.now()
common={
 'status':'completed_region_candidates_pending_formal_external_acceptance',
 'productionComplete':True,'regionalQaComplete':True,'complete4096CandidateCount':4,
 'coveredCoreCount':64,'remainingCoreCount':0,'remainingCoordinates':[],'nextMissingCore':None,
 'currentTile':None,'currentPatch':None,'inFlightRequestCount':0,
 'internalFullyReviewedTiles':ORDER,'internalFullyReviewedTileCount':4,'internalReviewPending':[],
 'deduplicatedTargetWholeTileCount':4,'tilesWithAll16NativeCoresCount':4,
 'internallyReviewedWholeTileCount':4,'wholeTilesMissingNativeCoresCount':0,
 'completeWholeTilesPendingRepairOrReviewCount':0,'pendingNecessaryRepairsCount':0,'pendingFinalReviewTiles':[],
 'externalNeighborAcceptanceIsNotMissingLocalArtwork':True,
 'formalAccepted':False,'formalAcceptedCount':0,
 'completedAtUtc':stamp,'updatedAtUtc':stamp,
 'nextStep':'Local four-tile production and regional QA complete. Upload owner may capture these new outputs; west c12 external acceptance remains pending.',
 'deliveryManifest':manifest_path.as_posix(),'deliveryManifestSha256':c.sha(manifest_path),
 'deliveryArchive':archive.as_posix(),'deliveryArchiveSha256':archive_sha,
 'completionRecord':completion_path.as_posix(),
 'pendingExternalEdges':m['pendingExternalEdges'],
 'newOutputUploadStatus':'not_confirmed_by_upload_owner','gitOperationsPerformed':False,
 'builtinOnly':True,'paidApiAllowed':False,'actualImageModel':'unknown','actualImageQuality':'unknown',
 'resizedFinalPixels':False,'nativeInputDimensions':[1254,1254],'candidateDimensions':[4096,4096],
 'native4kGeneration':False}
for name in ['progress.json','production-resume-20261012.json']:
    p=c.read(B/name); p.update(common); c.write(B/name,p)
p=c.read(B/'current-selection-20261012.json');p.update(common);c.write(B/'current-selection-20261012.json',p)
completion={**common,'assignment':ORDER,'regionWorldBox':m['regionWorldBox'],
 'generatedNativeCount':len(list((B/'native').glob('*.png'))),
 'currentCandidates':[{'tileId':t['tileId'],'file':(B/t['file']).as_posix(),'sha256':t['sha256'],
 'dimensions':t['dimensions'],'selectedCores':t['selectedCores'],'qaReport':(B/t['qaReport']).as_posix(),
 'qaReportSha256':t['qaReportOriginalSha256'],'resizedFinalPixels':False} for t in m['tiles']],
 'resolutionStatement':m['resolutionClaim'],
 'historicalFreezeManifest':{'file':(B/'migration-freeze-20261011.json').as_posix(),
 'sha256':c.sha(B/'migration-freeze-20261011.json'),'modifiedByFinalization':False},
 'preservedOriginalsDraftsAndPreviews':True,'uploadPerformedByThisWorker':False}
c.write(completion_path,completion)
print(json.dumps({'completionRecord':completion_path.as_posix(),'productionComplete':True,
 'formalAccepted':False,'candidateCount':4,'coveredCoreCount':64,'generatedNativeCount':completion['generatedNativeCount'],
 'deliveryArchive':archive.as_posix(),'deliveryArchiveSha256':archive_sha},ensure_ascii=False))

