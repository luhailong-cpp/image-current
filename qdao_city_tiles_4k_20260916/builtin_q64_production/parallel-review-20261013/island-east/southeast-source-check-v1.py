import json, pathlib, hashlib, struct, re, datetime, collections

ROOT = pathlib.Path(r'D:\work\image')
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
ZONE = BASE / 'island-game-20261009/southeast'
OUT = BASE / 'parallel-review-20261013/island-east'
json_cache, file_cache, input_reads = {}, {}, {}
def path(value, relative=ZONE):
    p = pathlib.Path(value)
    return p if p.is_absolute() else relative / p
def rel(p):
    try: return pathlib.Path(p).relative_to(ROOT).as_posix()
    except ValueError: return str(p).replace('\\', '/')
def read(p):
    p = path(p)
    key = str(p).lower()
    if key not in json_cache:
        raw = p.read_bytes()
        input_reads[key] = {'path':rel(p),'sha256AtRead':hashlib.sha256(raw).hexdigest(),'readAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        json_cache[key] = json.loads(raw.decode('utf-8-sig'))
    return json_cache[key]
def file_info(p):
    p = path(p)
    key = str(p).lower()
    if key not in file_cache:
        info = {'path':rel(p), 'exists':p.is_file()}
        if p.is_file():
            h = hashlib.sha256()
            with p.open('rb') as f:
                header = f.read(24)
                h.update(header)
                for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
            info.update(sha256=h.hexdigest(), bytes=p.stat().st_size)
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                info['dimensions'] = list(struct.unpack('>II', header[16:24]))
        file_cache[key] = info
    return dict(file_cache[key])
def checked(p, expected=None):
    info=file_info(p)
    if expected: info.update(expectedSha256=expected, hashMatches=info.get('sha256')==expected)
    return info
def tile_origin(tile):
    r,c=map(int,re.match(r'r(\d+)_c(\d+)',tile).groups())
    return [(c-1)*4096,(r-1)*4096]

progress=read('progress.json')
counts=read('current-zone-counts-20261013.json')
state=read('production-state.json')
assignment=read(BASE/'acceleration-20261010/assignments.json')
adopted=progress['currentAdoptedCandidates']
complete=adopted+progress['pendingCandidates']
all_sources={}
candidate_results=[]
contribution_count=0
mapping_confirmed=0
mapping_uncertain=[]
global_position_conflicts=[]
generation_global_unknown=[]

def source_check(source, tile, group):
    global contribution_count,mapping_confirmed
    contribution_count+=1
    native=path(source['file'])
    result={'tile':tile,'group':group,'native':checked(native,source.get('sha256'))}
    origin=source.get('originInTile')
    if origin is None and 'tileToNativeOffset' in source: origin=[-v for v in source['tileToNativeOffset']]
    crop=source.get('sourceCrop')
    dest=source.get('destinationBox')
    if dest is None and 'destination' in source:
        ds=source['destination']
        if len(ds)==4: dest=ds
        elif crop: dest=[ds[0],ds[1],ds[0]+crop[2]-crop[0],ds[1]+crop[3]-crop[1]]
    if crop and dest and origin is None: origin=[dest[0]-crop[0],dest[1]-crop[1]]
    dims=result['native'].get('dimensions')
    issues=[]
    if crop:
        if not dims or not(0<=crop[0]<crop[2]<=dims[0] and 0<=crop[1]<crop[3]<=dims[1]): issues.append('native_crop_out_of_bounds')
        if dest and [crop[2]-crop[0],crop[3]-crop[1]] != [dest[2]-dest[0],dest[3]-dest[1]]: issues.append('crop_destination_size_mismatch')
    if dest and not(0<=dest[0]<dest[2]<=4096 and 0<=dest[1]<dest[3]<=4096): issues.append('destination_outside_tile')
    if origin is None: issues.append('mapping_origin_missing')
    if origin and dims:
        overlap=[max(0,origin[0]),max(0,origin[1]),min(4096,origin[0]+dims[0]),min(4096,origin[1]+dims[1])]
        if overlap[0]>=overlap[2] or overlap[1]>=overlap[3]: issues.append('native_has_no_tile_overlap')
        result['nativeOverlapBoundsInTile']=overlap
    result.update(sourceCrop=crop,destinationBox=dest,originInTile=origin,mappingIssues=issues)
    if origin is not None and not issues: mapping_confirmed+=1
    else: mapping_uncertain.append({'tile':tile,'file':rel(native),'issues':issues})
    record=path(source.get('record') or source.get('generationRecord') or str(native)+'.generation.json')
    result['generationRecord']=checked(record,source.get('generationRecordSha256'))
    unique_key=str(native).lower()
    if unique_key not in all_sources:
        ni=checked(native,source.get('sha256'))
        ni.update(generationRecord=result['generationRecord'],usedBy=[])
        if record.is_file():
            rd=read(record)
            ni['recordedNativeSha256Matches']=rd.get('sha256')==ni.get('sha256')
            ni['recordedDimensions']=[rd.get('width'),rd.get('height')]
            ni['recordedDimensionsMatch']=ni.get('dimensions')==ni['recordedDimensions']
            ni['actualModel']=rd.get('actualModel')
            ni['modelEvidenceStatus']='unconfirmed' if not rd.get('actualModel') else 'recorded_actual_model_requires_evidence'
            ni['resizedAfterGeneration']=rd.get('resizedAfterGeneration')
            op=rd.get('sourceOutputPath')
            if op: ni['sourceOutput']=checked(op,rd.get('sourceOutputSha256') or rd.get('sha256'))
            ni['coordinateRecord']=rd.get('coordinate')
            ni['tileRelativeOriginRecord']=rd.get('tileRelativeOrigin')
        all_sources[unique_key]=ni
    all_sources[unique_key]['usedBy'].append({'tile':tile,'group':group})
    ni=all_sources[unique_key]
    coord=ni.get('coordinateRecord') or {}
    rd=read(record) if record.is_file() else {}
    native_box=coord.get('nativeGlobalBox') or rd.get('nativeGlobalBox')
    rec_origin=None
    if native_box: rec_origin=native_box[:2]
    elif rd.get('targetTileBox'):
        source_tile=re.match(r'(r\d+_c\d+)',native.name).group(1)
        anchor=tile_origin(source_tile); rec_origin=[anchor[i]+rd['targetTileBox'][i] for i in range(2)]
    elif coord.get('nativeBoxRelativeToTile'):
        source_tile=coord.get('tile') or re.match(r'(r\d+_c\d+)',native.name).group(1)
        anchor=tile_origin(source_tile); rec_origin=[anchor[i]+coord['nativeBoxRelativeToTile'][i] for i in range(2)]
    elif ni.get('tileRelativeOriginRecord') is not None:
        rd=read(record)
        rt=rd.get('tile')
        if rt:
            anchor=tile_origin(rt); rec_origin=[anchor[i]+ni['tileRelativeOriginRecord'][i] for i in range(2)]
    if origin:
        anchor=tile_origin(tile); actual_origin=[anchor[i]+origin[i] for i in range(2)]
        result['mappedNativeGlobalOrigin']=actual_origin
        if rec_origin:
            result['recordedNativeGlobalOrigin']=rec_origin
            result['globalOriginMatchesRecord']=actual_origin==rec_origin
            if actual_origin!=rec_origin: global_position_conflicts.append({'tile':tile,'file':rel(native),'mappedGlobalOrigin':actual_origin,'recordedGlobalOrigin':rec_origin})
        else: generation_global_unknown.append({'tile':tile,'file':rel(native)})
    return result

for item in complete:
    tile=item['tile']; candidate=path(item['candidate'])
    ci=checked(candidate,item['sha256'])
    if tile=='r08_c11': manifest=ZONE/'qa/r08_c11-v01-sol/source-audit.json'
    else:
        manifest=path(str(candidate)+'.generation.json')
        if not manifest.exists(): manifest=path(str(candidate)+'.sources.json')
    data=read(manifest)
    groups=[]
    if tile=='r10_c11':
        manifest=ZONE/'qa/r10_c11-independent-v04/source-audit.json'; data=read(manifest)
    for key in ['sources','contributions','derivedFrom','entries','repairOverlays','overlays']:
        if isinstance(data.get(key),list) and data[key] and isinstance(data[key][0],dict) and 'file' in data[key][0]: groups.append((key,data[key]))
    contributions=[source_check(s,tile,key) for key,sources in groups for s in sources]
    evidence={'manifest':file_info(manifest)}
    for key in ['sourceID','sourceId','sourceIdMap']:
        if data.get(key):
            expected=data.get(key+'Sha256')
            evidence['sourceIdMap']=checked(data[key],expected)
    proof=item.get('sourceProof')
    if proof: evidence['existingSourceProof']=file_info(path(proof))
    review=item.get('review')
    if review: evidence['reusedReview']=file_info(path(review))
    for key in ['allContributionsPixelExact','visiblePixelIdentityVerified','exactPixelReplayVerified','pixelReplayExact','sourceReplayMismatch','mismatchedPixelCount','replayMismatchedPixels','fullCoverage']:
        if key in data: evidence[key]=data[key]
    candidate_results.append({'tile':tile,'candidate':ci,'dimensionsAre4096Square':ci.get('dimensions')==[4096,4096],'statusFromCurrentProgress':{k:item.get(k) for k in ['fullyCovered','internalPassed','externalPassed','formalAccepted','status','pending'] if k in item},'sources':contributions,'existingEvidence':evidence})

# Current partial tiles: use their present selected versions only; do not inspect rejected versions.
partial=[]
for tile in ['r13_c11','r13_c13','r14_c12']:
    d=read('progress-'+tile+'.json')
    versions=d.get('selectedVersions') or d.get('workingVersions') or {}
    selected=[]
    for coord,version in sorted(versions.items()):
        native=ZONE/f'native/{tile}_p{coord}_{version}.png'
        x=(int(coord[1])-1)*1024; y=(int(coord[0])-1)*1024
        record=read(str(native)+'.generation.json') if path(str(native)+'.generation.json').exists() else {}
        selected.append(source_check({'file':str(native),'sha256':record.get('sha256'),'sourceCrop':[115,115,1139,1139],'destinationBox':[x,y,x+1024,y+1024]},tile,'current_partial_selected'))
    missing=[f'{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in versions]
    partial.append({'tile':tile,'progress':file_info('progress-'+tile+'.json'),'selectedCoreCount':len(versions),'missingCoreCoordinates':missing,'sources':selected,'thisReviewDispatchesGeneration':False})

# Compare current unversioned index pointers without following the old candidate pictures.
pointer_differences=[]
root_by_tile={v['tile']:v for v in complete}
for p in sorted(ZONE.glob('selected-native*.json'))+sorted(ZONE.glob('selection-*.json'))+sorted(ZONE.glob('progress-r*.json')):
    if '-v0' in p.name or '-repaired-' in p.name or '-sol-' in p.name: continue
    d=read(p); tile=d.get('tile') or d.get('currentTile')
    if tile not in root_by_tile: continue
    current=root_by_tile[tile]
    for key in ['candidate','latestCandidate','lastCandidate','candidate4k']:
        if d.get(key) and path(d[key]).resolve()!=path(current['candidate']).resolve():
            pointer_differences.append({'tile':tile,'record':rel(p),'field':key,'recorded':rel(path(d[key])),'currentProgress':rel(path(current['candidate'])),'type':'older_or_alternative_pointer_do_not_auto_promote'})
    for key in ['candidateSha256','candidate4kSha256']:
        if d.get(key) and d[key]!=current['sha256']:
            pointer_differences.append({'tile':tile,'record':rel(p),'field':key,'recorded':d[key],'currentProgress':current['sha256'],'type':'older_or_alternative_hash'})

missing_tiles=counts['missingNativeTiles']
current_inventory=read('saved-native-inventory-20261013.json')
raw_coverage=current_inventory['rawCoordinatesWithAnySavedVersion']
unselected_saved=[]
partial_map={p['tile']:p for p in partial}
all_missing_queue=[]
for tile in missing_tiles:
    entry={'tile':tile,'owner':'original_southeast_owner','reservationChanged':False}
    if tile in partial_map:
        entry.update(missingCoreCoordinates=partial_map[tile]['missingCoreCoordinates'],missingCoreCount=len(partial_map[tile]['missingCoreCoordinates']),basis='current_selected_versions_and_current_progress_verified')
    else:
        entry.update(missingCoreCoordinates=[f'{r}{c}' for r in range(1,5) for c in range(1,5)],missingCoreCount=16,basis='current_zone_missing_native_tile_list_only_not_a_historical_file_absence_claim')
    entry['classification']='selection_uncovered_core_count_not_synonymous_with_missing_files'
    entry['existingSavedButUnselectedCoreCoordinates']=[c for c in entry['missingCoreCoordinates'] if c in raw_coverage.get(tile,[])]
    entry['noSavedNativeInCurrentInventoryCoreCoordinates']=[c for c in entry['missingCoreCoordinates'] if c not in raw_coverage.get(tile,[])]
    entry['noSavedNativeInCurrentInventoryCoreCount']=len(entry['noSavedNativeInCurrentInventoryCoreCoordinates'])
    for coord in entry['existingSavedButUnselectedCoreCoordinates']:
        prefix=f'{tile}_p{coord}_'
        matched=[n for n in current_inventory['entries'] if pathlib.Path(n['file']).name.startswith(prefix)]
        for n in matched:
            # This is the only saved unselected coordinate cited by the current inventory.
            review_path=ZONE/f'qa/{tile}-resume-sol-20261012/{pathlib.Path(n["file"]).stem}-visual-review.json'
            review=read(review_path) if review_path.is_file() else {}
            unselected_saved.append({'tile':tile,'coordinate':coord,'native':checked(n['file'],n.get('sha256')),'generationRecord':file_info(str(n['file'])+'.generation.json'),'reviewRecord':file_info(review_path),'reviewPass':review.get('localVisualSeamsPassed'),'reviewFinding':review.get('note'),'disposition':'preserved_unselected_repair_or_owner_decision_required_not_missing_artwork_file'})
    all_missing_queue.append(entry)

priority_tiles=['r14_c12','r13_c11','r13_c13','r14_c11','r14_c13','r13_c14','r12_c14','r11_c14']
queue_by_tile={e['tile']:e for e in all_missing_queue}
native_list=list(all_sources.values())
missing_native=[n for n in native_list if not n['exists']]
hash_bad=[n for n in native_list if n.get('hashMatches') is False or n.get('recordedNativeSha256Matches') is False]
record_missing=[n for n in native_list if not n['generationRecord']['exists']]
external_missing=[n for n in native_list if n.get('sourceOutput') and not n['sourceOutput']['exists']]
external_bad=[n for n in native_list if n.get('sourceOutput',{}).get('hashMatches') is False]
dimension_bad=[n for n in native_list if n.get('recordedDimensionsMatch') is False]

report={
 'schemaVersion':1,'task':'island east current native source and missing-coordinate verification','zone':'southeast',
 'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'instructions':{'rootAGENTS':file_info(ROOT/'AGENTS.md'),'modelPreferenceClarification':file_info(ROOT/'docs/IMAGE_MODEL_REQUIREMENT.md'),'readCompletely':True,'latestModelPolicy':'Free/existing GPT Image 2.5 preferred; existing builtin 2.0 fallback permitted by user 2026-10-13. No metadata alone does not stop original owner production. This independent audit still performs no generation.','originalZoneReadOnly':True,'noGitOperations':True,'noNewImagesOrAIRepairs':True,'noVisualReviewOrAssembly':True,'noOtherChatsOrWindows':True,'actualModelUnconfirmedNotMissingArtwork':True},
 'scope':{'baseDirectory':rel(BASE),'zoneDirectory':rel(ZONE),'currentAuthority':rel(ZONE/'progress.json'),'currentCountsRecord':file_info('current-zone-counts-20261013.json'),'deliveryRecord':'No southeast delivery JSON exists; no delivery acceptance asserted.','historyPolicy':'Only current candidate source manifests and current partial selected versions read. Old candidate pointers compared as strings only; their images not read. Native generation records checked one level; their edit-target histories not followed.'},
 'summary':{
  'currentCompleteCandidateCount':len(complete),'currentAdoptedCandidateCount':len(adopted),'pendingCompleteCandidateCount':len(progress['pendingCandidates']),
  'candidateFileAndHashConfirmedCount':sum(c['candidate'].get('hashMatches') is True and c['dimensionsAre4096Square'] for c in candidate_results),
  'candidateUncertainCount':sum(c['candidate'].get('hashMatches') is not True or not c['dimensionsAre4096Square'] for c in candidate_results),
  'currentReferencedUniqueNativeSourceCount':len(native_list),'completeCandidateSourceContributionCount':sum(len(c['sources']) for c in candidate_results),
  'partialSelectedSourceContributionCount':sum(len(p['sources']) for p in partial),'totalSourceContributionCount':contribution_count,
  'contributionMappingsConfirmedCount':mapping_confirmed,'contributionMappingUncertainCount':len(mapping_uncertain),
  'referencedNativeFileMissingCount':len(missing_native),'nativeHashConflictCount':len(hash_bad),'nativeGenerationRecordMissingCount':len(record_missing),'nativeDimensionConflictCount':len(dimension_bad),
  'globalOriginConflictCount':len(global_position_conflicts),'generationGlobalOriginNotExplicitCount':len(generation_global_unknown),
  'actualModelUnconfirmedUniqueNativeCount':sum(n.get('modelEvidenceStatus')=='unconfirmed' for n in native_list),
  'externalOriginalOutputMissingCount':len(external_missing),'externalOriginalOutputHashConflictCount':len(external_bad),
  'missingFullNativeTileCountFromCurrentLists':len(missing_tiles),'currentSelectedMissingCoreCount':sum(e['missingCoreCount'] for e in all_missing_queue),
  'explicitPartialMissingCoreCount':sum(len(p['missingCoreCoordinates']) for p in partial),'otherUncoveredTileCoreCountFromCurrentLists':16*(len(missing_tiles)-len(partial)),
  'existingSavedButUnselectedCoreCount':sum(len(e['existingSavedButUnselectedCoreCoordinates']) for e in all_missing_queue),'noSavedNativeInCurrentInventoryCoreCount':sum(e['noSavedNativeInCurrentInventoryCoreCount'] for e in all_missing_queue),
  'secondaryPointerDifferenceFieldCount':len(pointer_differences),'secondaryPointerDifferenceRecordCount':len(set(p['record'] for p in pointer_differences)),
  'formalAcceptedCount':0,'mapCompleted':False},
 'boundaryAssignment':{'record':file_info(BASE/'acceleration-20261010/assignments.json'),'islandCoastAssignment':next(a for a in assignment['assignments'] if a['id']=='island_northeast_coast'),'southeastOverlap':False,'explanation':'The accelerated island coordinates are r01-r02/c13-c14; southeast ownership is r08-r14/c08-c14.'},
 'migration':{'rule':'Use repository-relative paths under a new clone root. Keep saved native PNG and generation record together. Original C:/Users cache path is provenance only when matching local native hash exists. Do not restore deleted directories.','checkedNativeSources':native_list,'missingExternalOriginalOutputs':[{'native':n['path'],'output':n['sourceOutput']} for n in external_missing],'badExternalOriginalOutputs':[{'native':n['path'],'output':n['sourceOutput']} for n in external_bad]},
 'completeCandidates':candidate_results,'currentPartialTiles':partial,
 'conflictsAndUncertainties':{'secondaryPointerDifferences':pointer_differences,'globalPositionConflicts':global_position_conflicts,'mappingUncertain':mapping_uncertain,'generationGlobalOriginNotExplicit':generation_global_unknown,'nativeHashConflicts':hash_bad,'nativeDimensionConflicts':dimension_bad,
 'sharedCountAndStateNotes':[
  {'record':'progress.json','fields':['latestCandidates','coveredTiles','internalPassedTiles'],'recordedEntryCount':len(progress['latestCandidates']),'currentCompleteCandidateCount':len(complete),'recommendation':'Original owner should explicitly designate currentAdoptedCandidates plus pendingCandidates as current index or synchronize legacy subset fields in a separate owner-controlled change.'},
  {'record':'production-state.json','field':'tiles','recordedEntryCount':len(state.get('tiles',[])),'currentCompleteCandidateCount':len(complete),'recommendation':'Do not use this old ten-tile list as the sole migration or completion manifest.'},
  {'record':'progress.json','field':'remainingAssigned4kCount','recorded':progress.get('remainingAssigned4kCount'),'currentMissingNative4kCount':counts['counts']['missingNative4kCount'],'recommendation':'Owner should reconcile 37 versus 34 using current distinct-tile list; this report does not modify either.'},
  {'tile':'r12_c12','field':'alternative_selected_native_v02','recommendation':'Current adopted root and tile progress point to v01. A versioned v02 selection exists but is not current adopted authority; do not select it by filename order or promote without original owner review.'}
 ]},
 'reusedSeamEvidence':{'statement':'Existing reviewed JSON reused; no visual reassessment or seam image creation performed. Missing outside neighbors are separate from native source absence.','r08_c11':file_info('qa/r08_c11-v01-sol/root-independent-source-replay-20261013.json'),'r12_c13':file_info('qa/r12_c13-resume-sol-20261012/candidate-v02-seam-review.json'),'r14_c12':file_info('qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json')},
 'remainingQueue':{'policy':'Recommendation to existing owner only; no coordinate reservation, prompt dispatch or generation performed. Original owners have resumed production under latest user policy: existing builtin 2.0 fallback is allowed. Recheck current progress and versions before executing this dated queue.','classificationAuthority':file_info('saved-native-inventory-20261013.json'),'existingSavedButUnselectedSources':unselected_saved,'fullCandidatePendingReviewExcludedFromMissingArtQueue':[i['tile'] for i in progress['pendingCandidates']],'firstFixCurrentReferenceIssues':True,'connectedPriorityBatch':[queue_by_tile[t] for t in priority_tiles],'allCurrentlyMissingNativeTiles':all_missing_queue},
 'limitations':['Source dimensions, hashes, recorded crop/offset geometry and existing proof hashes checked mechanically. Existing exact-pixel replay statements are reused, not independently recomputed.','Current unreferenced historical images are not scanned. Counts of unselected cores outside the three partial tiles are current-list coverage counts, not proof that every possible saved historical file is absent.','No acceptance of artwork, model route or completed map is asserted.']}
end_checks=[]
for key,entry in input_reads.items():
    p=pathlib.Path(key)
    sha=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    end_checks.append(dict(entry,sha256AtEnd=sha,unchangedDuringAudit=sha==entry['sha256AtRead']))
report['inputSnapshot']={'startedAtUtc':min(e['readAtUtc'] for e in end_checks),'finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readInputCount':len(end_checks),'changedInputCount':sum(not e['unchangedDuringAudit'] for e in end_checks),'inputs':end_checks,'liveOwnerProductionNote':'Read-only point-in-time report; original owner retains all writes and may produce newer versions after these reads. No new owner version is replaced or adopted by this report.'}
OUT.mkdir(parents=True,exist_ok=True)
version=1
while (OUT/f'southeast-sources-v{version}.json').exists(): version+=1
destination=OUT/f'southeast-sources-v{version}.json'
with destination.open('x',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(destination),'summary':report['summary'],'globalConflicts':global_position_conflicts[:10],'mappingUncertain':mapping_uncertain[:10],'dimensionConflicts':[(n['path'],n.get('dimensions'),n.get('recordedDimensions')) for n in dimension_bad]},ensure_ascii=False))
