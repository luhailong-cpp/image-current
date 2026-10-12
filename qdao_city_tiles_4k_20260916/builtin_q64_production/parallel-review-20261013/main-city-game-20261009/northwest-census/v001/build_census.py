from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from PIL import Image

ROOT = Path('D:/work/image')
B = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009'
A = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/acceleration-20261010/assignments.json'
OUT = Path(__file__).resolve().parent
ledger = {}
errors = []

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def ref(v, expected=None, image=False):
    p = Path(v).resolve()
    assert p.is_relative_to(B) or p == A or p == ROOT/'AGENTS.md', p
    r = {'file': str(p), 'exists': p.is_file()}
    if not r['exists']:
        if expected: errors.append({'kind':'missing_file', 'file':str(p)})
        return r
    h = sha(p)
    r.update(sha256=h, bytes=p.stat().st_size)
    ledger[str(p)] = h
    if expected:
        r.update(expectedSHA256=expected, hashMatchesRecorded=(h == expected))
        if h != expected: errors.append({'kind':'hash_mismatch','file':str(p),'expected':expected,'actual':h})
    if image:
        with Image.open(p) as im:
            r.update(pixels=list(im.size), mode=im.mode, format=im.format)
    return r

def read(p):
    ref(p)
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def reref(v, image=False):
    if isinstance(v, str): return ref(v, image=image)
    return ref(v['file'], v.get('sha256'), image)

def validate_refs(v):
    if isinstance(v, dict):
        if isinstance(v.get('file'), str) and isinstance(v.get('sha256'), str):
            p = Path(v['file']).resolve()
            if p.is_relative_to(B): ref(p, v['sha256'])
        for value in v.values(): validate_refs(value)
    elif isinstance(v,list):
        for value in v: validate_refs(value)

def save(name, d):
    p = OUT/name
    with p.open('x',encoding='utf-8') as f: f.write(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def generation(s):
    v = s.get('generationRecord')
    if not v:
        p = Path(s['file']).with_suffix('.png.generation.json')
        if not p.exists(): return None, {}
        v = str(p)
    r = reref(v)
    d = read(r['file'])
    validate_refs(d)
    return r,d

def source(s, tile):
    r = reref(s, image=True)
    r.update(id=s.get('localPatchId',s.get('patch',s.get('id'))), tile=tile)
    gr,g = generation(s)
    derived = g.get('nativeToolOutput') is False or 'deriv' in str(g.get('kind','')).lower()
    r.update(kind='derived_selected_patch' if derived else 'generated_original', generationRecord=gr,
             actualModel=g.get('actualModel'), actualQuality=g.get('actualQuality'))
    r['coordinateEvidence']={k:s[k] for k in ('coreWorldBox','worldBoxWithHalo','coreCropLTRB','coreCrop','tileOriginXY','tileCorePasteXY') if k in s}
    r['recordedReferences']=s.get('recordedReferences',g.get('references',g.get('recordedReferences',[])))
    r['referenceEvidence']={k:s[k] for k in ('request','prompt','receipt','evidence') if k in s}
    if derived:
        r['derivationEvidence']={k:g[k] for k in ('kind','baseNative','repairContexts','sourceMask','operation','copiedPixels','changedPixels','resizedAfterGeneration','verifiedOutsideRepairMaskUnchanged') if k in g}
        r['nativeOriginalClaim']=False
    return r

def assembly_spec(d):
    keys=('method','operation','corePixels','haloPixels','overlapPixels','internalOverlapPixels','grid','origin','coordinates',
          'sourceResampled','sourceUpscaled','finalArtUpscaled','colorMatching','opticalFlow','feathering','blending','blur',
          'hardCutPolicy','minimumErrorPolicy','sourceIndex','sourceIndexMap','nativeContextIntegration','baseManifest','assemblyInput',
          'seamOverrides','pixelProof','pixelProvenanceVerification','binarySourceProvenanceValidatedEveryPixel')
    return {k:d[k] for k in keys if k in d}

created=datetime.now(timezone.utc).isoformat()
assign=read(A)
assignment=next(x for x in assign['assignments'] if x['id']=='city_yamen_north')
nwprogress=read(B/'northwest/progress.json')
acprogress=read(B/'accelerated-yamen-north/progress.json')
nwsummary_path=B/'northwest/verified-eleven-tiles-20261012/2f0946e391eb1655/delivery-summary.json'
nwsummary=read(nwsummary_path)
acsummary_path=B/'accelerated-yamen-north/delivery-20261012-v1/delivery-manifest.json'
acsummary=read(acsummary_path)
joint_path=B/'northwest/joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/joint-assembly.json'
joint=read(joint_path)
jointqa_path=joint_path.parent/'delivery-summary.json'
jointqa=read(jointqa_path)
validate_refs(jointqa)
acboundary_path=B/'accelerated-yamen-north/delivery-20261012-v1/boundary-review.json'
acboundary=read(acboundary_path)
validate_refs(acboundary)
records=[]
for t in nwsummary['tiles']:
    tile=t['tile']; image=Path(t['file']); isjoint='joint-4096' in image.name
    manifest=joint_path if isjoint else image.parent/'assembly.json' if image.name=='candidate.png' else image.with_suffix('.assembly.json')
    assembly=joint if isjoint else read(manifest)
    sources=[s for s in assembly['nativeSources'] if s.get('tile',tile)==tile]
    grids=sources[:16]; extra=sources[16:]
    assert len(grids)==16, tile
    candidate=reref(t,image=True); assert candidate['pixels']==[4096,4096]
    if isjoint:
        qa={'status':'PASS_REUSED_CURRENT_JOINT_EVIDENCE','formalAccepted':False,'evidence':ref(jointqa_path),
            'scope':'joint 2x2 internal seams and shared boundaries',
            'qaCount':jointqa['qaCount'],'directlyViewedCount':jointqa['directlyViewedCount'],
            'identicalHashInheritedCount':jointqa['identicalHashInheritedCount'],
            'blockingCount':jointqa['blockingCount'],'reports':jointqa['reviewReports']}
        external={'status':'partial_passed','scope':'2x2 common boundaries passed; outer boundary pending', 'evidence':ref(jointqa_path)}
    else:
        delivery=B/'northwest'/tile/('delivery-summary-20261012.json' if tile in ('r07_c05','r06_c07') else 'delivery-summary.json')
        qapath=delivery if delivery.exists() and tile in ('r07_c04','r07_c05','r06_c07') else B/'northwest'/tile/'qa/acceptance.json'
        d=read(qapath);validate_refs(d)
        qa={'status':'PASS_REUSED_CURRENT_EVIDENCE','formalAccepted':False,'evidence':ref(qapath),'details':d.get('internalQA',{}),
            'candidateMatchesCurrent':d['candidate']['sha256']==t['sha256']}
        if not qa['candidateMatchesCurrent']:qa['status']='STALE_CANDIDATE_MISMATCH'
        external=d.get('externalQA',{})
        if 'availableActualNorthWestBoundariesPassed' in d:
            qa['qaEvidence']=d['qaEvidence']; external={'status':'partial_passed','northWestPassed':d['availableActualNorthWestBoundariesPassed'],
              'acceptance':d.get('acceptance'),'externalQaEvidence':d.get('externalQaEvidence'), 'pendingSides':['east','south']}
    old=next(x for x in nwprogress['tiles'] if x['tile']==tile)
    stale=[]
    if old.get('latestCandidate') and str(Path(old['latestCandidate']))!=str(image):
        stale.append({'file':old['latestCandidate'],'status':'historical_single_tile_candidate_not_current_adopted_delivery'})
    selected=[source(s,tile) for s in grids]
    row={'coordinate':tile,'owner':'northwest','availableForDelivery':True,'adoptionEvidence':ref(nwsummary_path),
         'candidate':candidate,'worldBox':t['tileWorldBox'],'assemblyManifest':ref(manifest),'assemblySpec':assembly_spec(assembly),
         'selectedPatchCount':16,'selectedSources':selected,'supplementalSources':[source(s,tile) for s in extra],
         'internalQA':qa,'externalQA':external,'formalAccepted':False,'historicalCandidatesNotAdopted':stale}
    records.append(row)

for t in acsummary['tiles']:
    tile=t['tile']; manifest=Path(t['assembly']);assembly=read(manifest)
    review=read(t['review']);validate_refs(review)
    candidate=ref(t['candidate'],t['sha256'],True)
    assert candidate['pixels']==[4096,4096]
    sources=t['selectedNativeOrDerivedPatches'];assert len(sources)==16
    row={'coordinate':tile,'owner':'accelerated-yamen-north','availableForDelivery':True,'adoptionEvidence':ref(acsummary_path),
      'candidate':candidate,'sourceCandidateAlias':ref(t['sourceCandidate'],t['sha256'],True),'worldBox':t['worldBox'],
      'assemblyManifest':ref(manifest),'assemblySpec':assembly_spec(assembly),'selectedPatchCount':16,
      'selectedSources':[source(s,tile) for s in sources],'supplementalSources':[],
      'internalQA':{'status':'PASS_REUSED_CURRENT_EVIDENCE','evidence':ref(t['review']),
        'candidateMatchesCurrent':review['candidate']['sha256']==candidate['sha256'],
        'changedQACount':review['changedQACount'],'actuallyViewedChangedQACount':review['actuallyViewedChangedQACount'],
        'unchangedRetainedQACount':review['unchangedRetainedQACount'],'knownOpenInternalDefects':review['knownOpenInternalDefects']},
      'externalQA':{'status':'partial_local_pass_south_adopted_neighbor_pending','evidence':ref(acboundary_path),
        'sharedAssignedBoundaries':'16 segments locally passed on current four adopted candidates',
        'southBoundaryLimitation':'8 segments use old available native neighbor sources, not current full adopted r05_c04/r05_c05',
        'formalPendingReason':review['formalPendingReason']},'formalAccepted':False,
      'historicalCandidatesNotAdopted':[{'file':assembly.get('baseCandidate',{}).get('file'),'status':'baseline only; prior defects superseded by current reviewed version'}]}
    if tile=='r04_c05':row['assemblySpec']['alphaRecipeClarification']=ref(B/'accelerated-yamen-north/delivery-20261012-v1/d4-final-recipe-clarification.json')
    records.append(row)

pending=next(x for x in nwprogress['tiles'] if x['tile']=='r07_c06')
p=Path(pending['latestCandidate']);m=p.with_suffix('.assembly.json');a=read(m)
selection_path=B/'northwest/r07_c06/selection.json'
selection=read(selection_path) if selection_path.exists() else {}
current=[]
for r in range(1,5):
    for c in range(1,5):
        ident=f's{r:02}_{c:02}';sp=Path(selection.get(ident,f'native/{ident}.png'))
        if not sp.is_absolute():sp=B/'northwest/r07_c06'/sp
        old=next(x for x in a['nativeSources'] if x['id']==ident)
        s=dict(old);s['file']=str(sp);s['sha256']=sha(sp);s['generationRecord']=str(sp.with_suffix('.png.generation.json'))
        current.append(source(s,'r07_c06'))
matches=all(x['sha256']==y['sha256'] for x,y in zip(a['nativeSources'],current))
records.append({'coordinate':'r07_c06','owner':'northwest','availableForDelivery':False,'candidate':ref(p,image=True),
 'worldBox':a['tileWorldBox'],'assemblyManifest':ref(m),'assemblySpec':assembly_spec(a),
 'selectedPatchCount':16,'selectedSources':current,'candidateSourceSelectionMatchesCurrent':matches,
 'internalQA':{'status':'NOT_PASSED','progressEvidence':ref(B/'northwest/progress.json'),'currentCompleteCandidate':False},
 'externalQA':{'status':'pending_repair_and_neighbor_review'},'formalAccepted':False})

records.sort(key=lambda x:x['coordinate'])
available=[x['coordinate'] for x in records if x['availableForDelivery']]
missing=[x['tile'] for x in nwprogress['tiles'] if x['selectedAvailable']==0]
assert len(available)==15 and len(missing)==48
coverage={'schemaVersion':1,'createdAtUTC':created,'scope':'Northwest original 8x8 area including four assigned acceleration coordinates; not full city map',
 'assignmentEvidence':ref(A),'deduplication':'r03_c04/r03_c05/r04_c04/r04_c05 belong only to accelerated-yamen-north',
 'totalUniqueCoordinates':64,'northwestOwnedCoordinates':60,'accelerationOwnedCoordinates':assignment['coordinates'],
 'availableReviewed4KTiles':15,'availableReviewedCoordinates':available,'fullSelectedSourceCoordinates':16,
 'pendingCompleteSourceCoordinate':['r07_c06'],'missingSourceTileCount':48,'missingNativePatches':768,'missingCoordinates':missing,
 'formalAcceptedCount':0,'wholeZoneComplete':False,'wholeMapComplete':False,
 'validationErrors':errors,'newGenerationPerformed':False,'newCropsCreated':False,'actualImageGenerationModel':None}
boundaries={'schemaVersion':1,'createdAtUTC':created,'priorityNewReview':[
 {'north':'r04_c04','south':'r05_c04','worldBoundaryY':16384,'worldXRange':[12288,16384],'segments':4,
  'reason':'Current north delivery was reviewed against old southern native patch cores; now current adopted south 4K is available',
  'northSource':next(x['candidate'] for x in records if x['coordinate']=='r04_c04'),'southSource':next(x['candidate'] for x in records if x['coordinate']=='r05_c04')},
 {'north':'r04_c05','south':'r05_c05','worldBoundaryY':16384,'worldXRange':[16384,20480],'segments':4,
  'reason':'Current north delivery was reviewed against old southern native patch cores; now current adopted south 4K is available',
  'northSource':next(x['candidate'] for x in records if x['coordinate']=='r04_c05'),'southSource':next(x['candidate'] for x in records if x['coordinate']=='r05_c05')}],
 'priorityNewJunctions':[{'worldXY':[16384,16384],'tiles':['r04_c04','r04_c05','r05_c04','r05_c05'],'reason':'Current adopted four-tile intersection not covered by accelerated internal fourway at y=12288'}],
 'reusableAcceleratedInternalEvidence':ref(acboundary_path),'reusableNorthwestInternalAndSharedBoundaryEvidence':ref(nwsummary_path),
 'unavailableAcceleratedOuterNeighborCoordinates':acboundary['missingNeighborTiles'],
 'unavailableAcceleratedOuterSegmentCount':len(acboundary['missingOuterBoundarySegments']),
 'sourceCompleteButUnacceptedNeighbor':'r07_c06',
 'olderFailedAcceleratedReviewStatus':'10/11 failures are historical baseline findings; use 10/12 source-bound current local pass evidence, no invented new repair claim',
 'newVisualAcceptancePerformedByThisCensus':False,'wholeMapComplete':False}
save('current-tiles.json',{'schemaVersion':1,'createdAtUTC':created,'tiles':records,'validationErrors':errors})
save('coverage.json',coverage)
save('cross-area-review-queue.json',boundaries)
changed=[]
for name,digest in ledger.items():
    if sha(name)!=digest:changed.append(name)
save('input-hashes.json',{'createdAtUTC':created,'inputs':[{'file':k,'sha256':v} for k,v in sorted(ledger.items())],
 'inputsUnchangedAtEnd':not changed,'changedInputs':changed,'staleIfAnyInputChanges':True,
 'referenceScopeNote':'Historical recorded shared-image paths/hashes preserved from production evidence; images outside allowed main-city source tree were not opened or revalidated.'})
assert not changed
save('result.json',{'createdAtUTC':created,'currentTiles':str(OUT/'current-tiles.json'),'coverage':coverage,
 'priorityBoundaryPairs':2,'priorityNativeSeamSegments':8,'priorityJunctions':1,'readOnlyProduction':True,'inputCount':len(ledger)})
print(json.dumps({'output':str(OUT),'tiles':len(records),'reviewedDeliverables':len(available),'missingSourceCoordinates':len(missing),
 'inputsHashed':len(ledger),'validationErrors':errors,'selectedDerivedPatches':sum(s['kind']=='derived_selected_patch' for t in records for s in t['selectedSources'])},ensure_ascii=False,indent=2))
