from native_work import *
import re, shutil, collections
from datetime import datetime, timezone

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
recorded = now()
history = ZONE/'qa/history'/('local-finalization-'+stamp)
history.mkdir(parents=True, exist_ok=False)
def preserve(path):
    if path.exists():
        relative = path.relative_to(ZONE)
        dest = history/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
def saved(path, value):
    preserve(path)
    write(path, value)

review_path = ZONE/'qa/cross-zone-20261011/review.json'
review = read(review_path)
for item in review['records']:
    for side in ('upper','lower'):
        assert sha(Path(item[side]['file'])) == item[side]['sha256']
    for segment in item['evidence']:
        assert sha(Path(segment['file'])) == segment['sha256']
        segment['status'] = 'passed_visual_review_1to1'
    item['status'] = 'passed_whole_4096_shared_edge_visual_review'
    item['reviewer'] = 'root'
    item['finding'] = 'No visible hard seam, geometry discontinuity or horizontal color band at the shared border in all four 1024x512 strips.'
cross_file = ZONE/'qa/cross-zone-20261011/r02-r03_c13-c14-cross-100pct.png'
review.update(reviewedAtUtc=recorded, cross={'file':cross_file.as_posix(),'sha256':sha(cross_file),'status':'passed_visual_review_1to1','reviewer':'root'}, formalAccepted=False)
saved(review_path, review)

index_path = ZONE/'exports/20261011-local-v1/delivery-index.json'
index = read(index_path)
for tile in index['tiles']:
    assert sha(Path(tile['file'])) == tile['sha256']
assert sha(Path(index['mosaic']['file'])) == index['mosaic']['sha256']
mosaic_crosses = []
for n in (1,2):
    file= index_path.parent/f'cross-{n}-100pct.png'
    mosaic_crosses.append({'file':file.as_posix(),'sha256':sha(file),'status':'passed_visual_review_1to1','reviewer':'root'})
index.update(lastLocalReviewAtUtc=recorded, outerAdjacentTileEdgesNotFullyAcceptedCount=6,
             outerSharedEdgesReviewed=[x['pair'] for x in review['records']],
             outerSharedEdgesReview=review_path.as_posix(), fourTileCrossReviews=mosaic_crosses,
             overallPreviewReview='Two previously recorded internal color bands remain pending; no new failure at the reviewed shared edges or the two 4K intersections.',
             outerEdgeCountDefinition='Six adjacent-tile edges lack whole-edge visual acceptance. Whole-tile formal acceptance remains zero.')
saved(index_path,index)

excluded = {'r01_c13','r01_c14','r02_c13','r02_c14'}
owned = [f'r{r:02d}_c{c:02d}' for r in range(1,8) for c in range(8,15) if f'r{r:02d}_c{c:02d}' not in excluded]
records = [read(f) for f in sorted((ZONE/'native').glob('*.png.generation.json'))]
coordinate_versions = collections.defaultdict(list)
for r in records:
    m = re.fullmatch(r'(r\d{2}_c\d{2}_p\d{2}_\d{2})(?:_v\d+)?',r['id'])
    if m:
        coordinate_versions[m.group(1)].append(r['id'])
selections = {f.stem.replace('selection-',''):read(f) for f in sorted(ZONE.glob('selection-r??_c??.json'))}
complete = [t['tileId'] for t in index['tiles']]
passed = [t['tileId'] for t in index['tiles'] if t['internalReview'].startswith('passed')]
selected = [v for s in selections.values() for row in s['cores'] for v in row if v]
assert len(selected) == len(set(selected))
assert len(owned)==45 and len(records)==177 and len(coordinate_versions)==116 and len(selected)==115
assert len(complete)==6 and len(passed)==4
inventory=[]
for tid in owned:
    all_coords=[f'{tid}_p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)]
    s=selections.get(tid,{'cores':[[None]*4 for _ in range(4)],'overlays':[]})
    chosen=[v for row in s['cores'] for v in row if v]
    base_chosen={re.sub(r'_v\d+$','',v) for v in chosen}
    inventory.append({'tileId':tid,'fullNativeCandidate':tid in complete,'internalPassed':tid in passed,
                      'formalAccepted':False,'generatedCoreCoordinates':[c for c in all_coords if c in coordinate_versions],
                      'selectedCoreIds':chosen,'repairOverlayPlacementCount':len(s.get('overlays',[])),
                      'missingGeneratedCoordinates':[c for c in all_coords if c not in coordinate_versions],
                      'unselectedCoordinates':[c for c in all_coords if c not in base_chosen],
                      'pendingIssues':s.get('pendingIssues',[])})
inventory_doc={'updatedAtUtc':recorded,'ownedTileCount':45,'targetCoreCoordinates':720,
               'generatedNativeFiles':177,'nativeCoreVersions':sum(len(v) for v in coordinate_versions.values()),
               'nativeRepairVersions':sum('_cross_' in r['id'] for r in records),
               'uniqueGeneratedCoreCoordinates':116,'selectedCoreCoordinates':115,
               'selectedCoreCountIsNotAcceptance':True,'missingGeneratedCoreCoordinates':604,
               'missingSelectedCoreCoordinates':605,'fullCoverageTiles':6,'internallyPassedTiles':4,
               'tilesWithoutFullCoverage':39,'formalAcceptedTiles':0,'excludedElsewhere':sorted(excluded),
               'tileInventory':inventory}
inventory_path=ZONE/'qa/continuation-inventory-20261011.json'
saved(inventory_path,inventory_doc)
summary={x['tileId']:{'coreCoverage':len(x['selectedCoreIds']),'generatedCoreCoordinates':len(x['generatedCoreCoordinates']),
                     'repairOverlays':x['repairOverlayPlacementCount'],'internalPassed':x['internalPassed'],
                     'missingCores':len(x['unselectedCoordinates'])} for x in inventory if x['selectedCoreIds']}

error={'stage':'subagent runtime after latest restoration relay','error':'Fatal error: application network permission was revoked',
       'resolved':False,'recordedAtUtc':recorded,'evidenceType':'collaboration.list_agents runtime status observed by root; not an image-generation receipt',
       'currentlyObservedErroredAgents':['/root/east_resume','/root/southeast_resume'],
       'additionalEarlierReportedErroredAgent':'/root/south_resume',
       'retriesAfterRenewedDenial':0,'localWorkContinued':True}
error_path=ZONE/'qa/network-runtime-block-20261011.json'
saved(error_path,error)
steps=[
    {'priority':1,'task':'Restore permitted builtin image generation before issuing new image calls; no network retry during the current denied state.'},
    {'priority':2,'task':'Repair the gold gourd color band around local y2048 in r03_c12/r03_c13 and the slender bottle band around local y3072 in r03_c12; regenerate only targeted native areas and inspect all repair perimeters.'},
    {'priority':3,'task':'Finish r03_c11 p02_01,p03_01,p04_01 and repair the recorded stair/paving junction defects.'},
    {'priority':4,'task':'Continue r05_c12_p02_04 from its saved anchored guide; finish remaining r05_c12 cores.'},
    {'priority':5,'task':'Continue r05_c13_p01_01 from its saved anchored guide; repair p02_03/p02_04 roof-edge step, then finish remaining cores.'},
    {'priority':6,'task':'Continue remaining owned tiles listed in the inventory, then recheck full outside edges. Do not generate the four externally assigned tiles.'}
]
shared=[{'pair':pair,'reviewedPixels':4096,'geometry':'pass','scope':'shared edge only'} for pair in index['sharedEdgeGeometryReviewedPairs']]
shared += [{'pair':x['pair'],'reviewedPixels':4096,'geometry':'pass','scope':'shared external border only','reviewFile':review_path.as_posix()} for x in review['records']]
p=read(ZONE/'progress.json')
p.update(status='blocked_by_application_network_permission_local_outputs_saved',updatedAtUtc=recorded,
         generatedNativeCount=177,selectedCoreCoordinateCount=115,generatedCoreCoordinateCount=116,
         fullyCovered4kCount=6,internalPassed4kCount=4,complete4kCount=4,formalAcceptedCount=0,
         ownedTarget4kCount=45,ownedRemainingTarget4kCount=45,ownedRemainingTarget4kCountDefinition='Legacy field: total owned target, not number still lacking coverage.',
         missingFullCoverage4kCount=39,target4kCount=49,activeTiles=['r03_c11','r03_c12','r03_c13','r05_c12','r05_c13'],
         currentTile='r05_c12',currentPatch='r05_c12_p02_04',tileSummary=summary,
         inFlightStatus='none; image generation blocked; local review and export completed',
         nextStep=steps[0]['task'],nextSteps=steps,knownSharedEdgesReviewed=shared,
         continuationInventory=inventory_path.as_posix(),deliveryIndex=index_path.as_posix(),
         actualModel=None,actualQuality=None,submittedModel=None,submittedQuality=None)
usable=[r for r in records if r.get('status','').startswith(('usable_native','usable_seed'))]
p.update(usableNativeCount=len(usable),usableCorePatchCount=sum('_cross_' not in r['id'] for r in usable),
         usableRepairOverlayCount=sum('_cross_' in r['id'] for r in usable),
         usableCountDefinition='Historical per-native status; not whole-tile acceptance.')
p.setdefault('errors',[]).append(error)
saved(ZONE/'progress.json',p)
h=read(ZONE/'handoff.json')
h.pop('unfinishedSparseCandidate',None)
h.update(status=p['status'],updatedAtUtc=recorded,generatedNativeCount=177,fullyCovered4kCount=6,internalPassed4kCount=4,
         selectedCoreCoordinateCount=115,generatedCoreCoordinateCount=116,formalAcceptedCount=0,
         finishedInternalCandidates=['tiles/'+t+'.png' for t in passed],pixelCoveredCandidates=['tiles/'+t+'.png' for t in complete],
         activeTiles=p['activeTiles'],currentTile=p['currentTile'],currentPatch=p['currentPatch'],inFlightStatus=p['inFlightStatus'],
         nextAction=steps[0]['task'],nextSteps=steps,ownedTarget4kCount=45,missingFullCoverage4kCount=39,
         deliveryIndex=index_path.as_posix(),continuationInventory=inventory_path.as_posix(),
         externalSeamReviews=[review_path.as_posix()],actualModel=None,actualQuality=None,submittedModel=None,submittedQuality=None,
         sparseCandidates=[(ZONE/'qa'/f'{t}-sparse-wip-20261011.png').as_posix() for t in ('r03_c11','r05_c12','r05_c13')],
         legacyGateFilesAreNotCurrentRequirements=True)
saved(ZONE/'handoff.json',h)
cp=ZONE/'qa/r03_c11-progress.json'
c=read(cp)
c.update(status='partial_native_candidate_with_geometry_repairs_pending_network_blocked',updatedAtUtc=recorded,
         generated=[r['id'] for r in records if r['id'].startswith('r03_c11_p')],
         generatedCoordinateCount=13,selectedCoreIds=selections['r03_c11']['cores'],currentId='r03_c11_p02_01',
         pendingIssues=selections['r03_c11']['pendingIssues'])
if 'r03_c11_p01_01' not in c['accepted']:c['accepted'].append('r03_c11_p01_01')
c['acceptedDefinition']='Local core checks only; no whole-tile or formal acceptance.'
saved(cp,c)

recovered=ZONE/'native/r03_c11_p01_01.png'
recovered_info={'id':'r03_c11_p01_01','file':recovered.as_posix(),'sha256':sha(recovered),
                'kind':'recovery_of_previously_generated_output','newGenerationInThisLocalRound':False,
                'generationRecord':(ZONE/'native/r03_c11_p01_01.png.generation.json').as_posix()}
prior=read(ZONE/'qa/southeast-network-resume-20261011.json')
prior['currentReviewStatus']='candidate_with_unresolved_geometry'
continuation={'resumedAt':"2026-10-11 11:49:59 UTC",'resumedAtDefinition':'Start of final local-only reconciliation recorded by root; not an image-generation restart time.',
              'updatedAtUtc':recorded,'status':p['status'],'currentCoordinate':'r05_c12_p02_04',
              'firstRealNewImageOutputAfterLatestDenial':None,'firstRealNewImageOutputSha256':None,
              'priorConfirmedBuiltinOutput':prior,'recoveredPreviouslyGeneratedOutput':recovered_info,
              'mergedRepairsAlreadyVerified':[{'id':'r04_c12_cross_01_02_jar_paint_repair_v4','sha256':'f43a3346ee20cb34be4d1a549d9bbd18395ab5b5af3d8e876f589ffeaa4177fc','placementTiles':['r03_c12','r04_c12'],'status':'passed and already merged before this final local reconciliation'}],
              'coverage':{k:v for k,v in inventory_doc.items() if k!='tileInventory'},
              'candidateExport':index['mosaic'],'deliveryIndex':index_path.as_posix(),
              'internalSeams':{'passedTiles':passed,'colorRepairPendingTiles':['r03_c12','r03_c13']},
              'outerSeams':{'reviewedGroupAdjacentPairs':index['sharedEdgeGeometryReviewedPairs'],'reviewedCrossZonePairs':[r['pair'] for r in review['records']],'pendingAdjacentEdges':6,'mapBoundaryEdges':2,'formalWholeTileAcceptance':False},
              'inventory':inventory_path.as_posix(),'nextSteps':steps,'errors':[error],
              'actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,
              'allHistoricalVersionsRetained':True}
saved(ZONE/'continuation-round-20261011.json',continuation)
saved(ZONE/'local-continuation-20261011.json',continuation)
print(json.dumps({'saved':True,'nativeFiles':177,'uniqueCoreCoordinates':116,'selectedCoordinates':115,'covered4k':6,'internalPassed':4,'formalAccepted':0,'pendingOutsideEdges':6,'history':history.as_posix(),'index':index_path.as_posix()}))

