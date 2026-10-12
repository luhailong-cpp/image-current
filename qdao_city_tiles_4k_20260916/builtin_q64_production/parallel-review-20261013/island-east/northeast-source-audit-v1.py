import json
import hashlib
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path('D:/work/image')
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
ZONE = BASE / 'island-game-20261009/northeast'
OUT = BASE / 'parallel-review-20261013/island-east'
read_set = {}
audit_started = datetime.now(timezone.utc).isoformat()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def rel(p):
    p = Path(p)
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()

def load(p):
    p = Path(p)
    data = p.read_bytes()
    read_set[rel(p)] = hashlib.sha256(data).hexdigest()
    return json.loads(data.decode('utf-8-sig'))

def info(p):
    p = Path(p)
    v = {'path': rel(p), 'exists': p.is_file()}
    if v['exists']:
        v['sha256'] = sha(p)
        with Image.open(p) as im:
            v['size'] = list(im.size)
            v['format'] = im.format
    return v

def same(a,b):
    return list(a or []) == list(b or [])

def origin(tile):
    r,c = map(int,re.fullmatch(r'r(\d+)_c(\d+)',tile).groups())
    return [(c-1)*4096,(r-1)*4096]

p = load(ZONE/'progress.json')
h = load(ZONE/'handoff.json')
resume = load(Path(p['productionResume']))
inventory = load(Path(p['continuationInventory']))
delivery = load(Path(p['deliveryIndex']))
assignments = load(BASE/'acceleration-20261010/assignments.json')
read_set['AGENTS.md'] = sha(ROOT/'AGENTS.md')
read_set['docs/IMAGE_MODEL_REQUIREMENT.md'] = sha(ROOT/'docs/IMAGE_MODEL_REQUIREMENT.md')
exclusions = next(x['coordinates'] for x in assignments['assignments'] if x['id']=='island_northeast_coast')
selections = {}
selection_paths = {}
for path in resume['currentSelections']:
    j = load(Path(path))
    if j['tileId'] not in exclusions:
        selections[j['tileId']] = j
        selection_paths[j['tileId']] = rel(path)

issues = []
def issue(code, tile, finding, evidence, suggestion):
    issues.append({'code':code,'tileId':tile,'finding':finding,'evidence':evidence,'suggestionForOriginalOwner':suggestion})

native = {}
def native_entry(path):
    path=Path(path)
    key=rel(path)
    if key not in native:
        v=info(path)
        gp=Path(str(path)+'.generation.json')
        v['generationRecord']=rel(gp)
        v['generationRecordExists']=gp.is_file()
        v['failures']=[]
        if not v['exists']:
            v['failures'].append('native_file_missing')
        if gp.is_file():
            g=load(gp)
            v['generationRecordSha256']=read_set[rel(gp)]
            v['id']=g.get('id')
            v['recordedSha256']=g.get('sha256')
            v['hashMatchesGenerationRecord']=v.get('sha256')==g.get('sha256')
            v['sizeMatchesGenerationRecord']=same(v.get('size'),[g.get('nativeWidth'),g.get('nativeHeight')])
            v['coreCrop']=g.get('coreCrop')
            v['coreWorldBox']=g.get('coreWorldBox')
            v['nativeWorldBox']=g.get('nativeWorldBox')
            v['recordedStatus']=g.get('status')
            v['actualModel']=g.get('actualModel')
            v['modelStatus']='unconfirmed' if not g.get('actualModel') else 'recorded_actual_model_not_independently_route_verified'
            v['resizedAfterGeneration']=g.get('resizedAfterGeneration')
            v['finalArtUpscaled']=g.get('finalArtUpscaled')
            if not v['hashMatchesGenerationRecord']:v['failures'].append('generation_record_hash_mismatch')
            if not v['sizeMatchesGenerationRecord']:v['failures'].append('generation_record_size_mismatch')
            if v.get('size')!=[1254,1254]:v['failures'].append('native_size_not_1254_square')
            if same(g.get('coreCrop'),[115,115,1139,1139]) is False:v['failures'].append('generation_core_crop_not_1024_contract')
            if g.get('coreWorldBox') and g.get('nativeWorldBox'):
                x,y,x2,y2=g['coreWorldBox']
                if not same(g['nativeWorldBox'],[x-115,y-115,x2+115,y2+115]):v['failures'].append('native_world_box_mismatch')
            ep=g.get('evidence',{})
            if ep.get('receipt'):
                rp=Path(ep['receipt']);v['receiptPath']=rel(rp);v['receiptExists']=rp.is_file()
            if ep.get('originalToolPath'):
                v['originalToolPath']=ep['originalToolPath']
                v['originalToolPathIsOutsideRepository']=not Path(ep['originalToolPath']).is_relative_to(ROOT)
            v['migrationRule']='Rebuild uses the repository native PNG and matching generation record; original external tool path is provenance only. Do not restore deleted external/history files.'
        else:
            v['failures'].append('generation_record_missing')
            v['modelStatus']='unconfirmed'
        v['uses']=[]
        native[key]=v
    return native[key]

contributions=[]
tile_rows=[]
candidate_by_tile={x['tileId']:x for x in resume['completeCandidates']}
derivations={}
for tile,cand in candidate_by_tile.items():
    if tile in exclusions:continue
    dp=Path(str(cand['file'])+'.derivation.json')
    derivations[tile]=load(dp) if dp.is_file() else None

for tile,s in sorted(selections.items()):
    ox,oy=origin(tile)
    selected_ids=[]
    for ri,row in enumerate(s['cores']):
        for ci,nid in enumerate(row):
            if not nid:continue
            selected_ids.append(nid)
            n=native_entry(ZONE/'native'/f'{nid}.png')
            expected=[ox+ci*1024,oy+ri*1024,ox+(ci+1)*1024,oy+(ri+1)*1024]
            n['uses'].append({'tileId':tile,'role':'selected_core','selection':selection_paths[tile]})
            coordok=same(n.get('coreWorldBox'),expected)
            contributions.append({'tileId':tile,'role':'selected_core','sourceId':nid,'source':n['path'],'sourceCrop':[115,115,1139,1139],'tileLocalBox':[ci*1024,ri*1024,(ci+1)*1024,(ri+1)*1024],'worldContributionBox':expected,'generationWorldCoordinateMatches':coordok,'confirmed':coordok and not n['failures']})
    row={'tileId':tile,'selection':selection_paths[tile],'selectedCoreCount':len(selected_ids),'selectedCoreIds':selected_ids,'selectedOverlayAliases':s.get('overlays',[]),'missingSelectionCoreIds':[f'{tile}_p{ri+1:02d}_{ci+1:02d}' for ri,row in enumerate(s['cores']) for ci,v in enumerate(row) if not v]}
    d=derivations.get(tile)
    if tile in candidate_by_tile:
        c=candidate_by_tile[tile]
        row['candidate']=info(c['file'])
        row['candidate']['resumeSha256']=c.get('sha256')
        row['candidate']['hashMatchesResume']=row['candidate'].get('sha256')==c.get('sha256')
        row['candidate']['derivation']=rel(str(c['file'])+'.derivation.json')
        row['candidate']['derivationExists']=d is not None
        row['candidate']['internalReviewFromCurrentRecord']=c.get('internalReview')
        row['candidate']['formalAccepted']=False
        row['candidate']['failures']=[]
        if not row['candidate']['exists']:row['candidate']['failures'].append('candidate_missing')
        if not row['candidate']['hashMatchesResume']:row['candidate']['failures'].append('candidate_resume_hash_mismatch')
        if d:
            row['candidate']['derivationSha256']=d.get('sha256')
            row['candidate']['hashMatchesDerivation']=row['candidate'].get('sha256')==d.get('sha256')
            row['candidate']['sizeMatches4096']=row['candidate'].get('size')==[4096,4096]
            row['candidate']['worldBox']=d.get('worldBox')
            row['candidate']['worldBoxMatchesTile']=same(d.get('worldBox'),[ox,oy,ox+4096,oy+4096])
            row['candidate']['sourceIdsMatchSelection']=[x['id'] for x in d.get('sources',[])]==selected_ids
            if not row['candidate']['hashMatchesDerivation']:row['candidate']['failures'].append('candidate_derivation_hash_mismatch')
            if not row['candidate']['sizeMatches4096']:row['candidate']['failures'].append('candidate_size_not_4096')
            if not row['candidate']['worldBoxMatchesTile']:row['candidate']['failures'].append('candidate_world_box_mismatch')
            if not row['candidate']['sourceIdsMatchSelection']:row['candidate']['failures'].append('derivation_sources_selection_mismatch')
            srcfails=[]
            for src in d.get('sources',[]):
                n=native_entry(src['file'])
                rect=src.get('coreCrop')
                paste=src.get('tileLocalPaste')
                m=re.search(r'_p(\d+)_(\d+)',src['id'])
                er,ec=map(int,m.groups())
                exp=[(ec-1)*1024,(er-1)*1024]
                checks={'hash':n.get('sha256')==src.get('sha256'),'crop':same(rect,[115,115,1139,1139]),'paste':same(paste[:2] if paste else [],exp)}
                if 'nativeSize' in src:checks['size']=same(src['nativeSize'],n.get('size'))
                if not all(checks.values()):srcfails.append({'source':n['path'],'checks':checks})
            row['candidate']['derivationCoreSourceFailures']=srcfails
            overlays=[]
            aliases=[]
            for o in d.get('requiredOverlays',[]):
                n=native_entry(o['source'])
                nid=Path(o['source']).stem
                alias=o.get('id') or (f"{o['sharedRepairId']}-{tile}" if o.get('sharedRepairId') else nid)
                aliases.append(alias)
                n['uses'].append({'tileId':tile,'role':'selected_overlay','selectionAlias':alias,'derivation':row['candidate']['derivation']})
                crop=o.get('coreCrop',[])
                paste=o.get('tileLocalPaste',[])
                world=[ox+paste[0],oy+paste[1],ox+paste[0]+crop[2]-crop[0],oy+paste[1]+crop[3]-crop[1]] if len(crop)==4 and len(paste)>=2 else None
                nw=n.get('nativeWorldBox')
                sourceworld=[nw[0]+crop[0],nw[1]+crop[1],nw[0]+crop[2],nw[1]+crop[3]] if nw and len(crop)==4 else None
                checks={'sourceHash':n.get('sha256')==o.get('sha256'),'sourceCropInBounds':bool(len(crop)==4 and n.get('size') and 0<=crop[0]<crop[2]<=n['size'][0] and 0<=crop[1]<crop[3]<=n['size'][1]),'noScale':bool(len(crop)==4 and (len(paste)==2 or same([paste[2]-paste[0],paste[3]-paste[1]],[crop[2]-crop[0],crop[3]-crop[1]]))),'worldContributionMatchesSourcePosition':same(world,sourceworld)}
                if o.get('worldPaste'):checks['worldPaste']=same(o['worldPaste'],world[:2] if world else [])
                contribution={'tileId':tile,'role':'selected_overlay','sourceId':nid,'selectionAlias':alias,'source':n['path'],'sourceCrop':crop,'tileLocalPaste':paste,'worldContributionBox':world,'sourceWorldContributionBox':sourceworld,'checks':checks,'confirmed':all(checks.values()) and not n['failures']}
                contributions.append(contribution);overlays.append(contribution)
            row['candidate']['overlayAliasesMatchSelection']=aliases==s.get('overlays',[])
            row['candidate']['overlayCount']=len(overlays)
            row['candidate']['overlayContributionFailures']=[x for x in overlays if not x['confirmed']]
            row['candidate']['originAndContributionConfirmed']=not row['candidate']['failures'] and not srcfails and all(x['confirmed'] for x in contributions if x['tileId']==tile) and row['candidate']['overlayAliasesMatchSelection']
        else:row['candidate']['failures'].append('derivation_missing')
    tile_rows.append(row)

delivery_checks=[]
for t in delivery['tiles']:
    current=next(x for x in tile_rows if x['tileId']==t['tileId'])['candidate']
    delivery_checks.append({'tileId':t['tileId'],'file':rel(t['file']),'deliverySha256':t['sha256'],'currentSha256':current['sha256'],'hashMatchesCurrent':t['sha256']==current['sha256'],'worldBoxMatchesCurrent':same(t.get('worldBox'),current.get('worldBox'))})
    if t['sha256']!=current['sha256']:
        issue('delivery_hash_stale',t['tileId'],'Current delivery-index points at a file whose current bytes differ from its recorded hash.',delivery_checks[-1],'Owner should issue a new delivery index; preserve the fixed historical export and do not overwrite it.')

if p.get('completeNativeCoverageTiles')!=p.get('fullyCovered4kCount') or p.get('selectedCoreCoordinates')!=p.get('selectedCoreCoordinateCount'):
    issue('mixed_legacy_and_current_counters',None,'progress and handoff retain migration/freeze fields alongside newer production fields.',{'progress':rel(ZONE/'progress.json'),'handoff':rel(ZONE/'handoff.json'),'legacy':{'complete4kCount':p.get('complete4kCount'),'completeNativeCoverageTiles':p.get('completeNativeCoverageTiles'),'selectedCoreCoordinates':p.get('selectedCoreCoordinates'),'missingFullCoverageTiles':p.get('missingFullCoverageTiles')},'current':resume['coverage']},'Keep frozen baseline evidence intact; clarify legacy labels in a later owner-authored progress/handoff revision. Use currentSelections and completeCandidates for current local work.')

listed_delivery={x['tileId'] for x in delivery['tiles']}
unlisted=sorted(set(candidate_by_tile)-listed_delivery)
issue('delivery_is_historical_subset',None,'The current progress.deliveryIndex is a 2026-10-11 six-candidate export; six current full candidates are absent. It is not a current 12-candidate delivery manifest.',{'deliveryIndex':rel(p['deliveryIndex']),'exportedAtUtc':delivery.get('exportedAtUtc'),'listedTileIds':sorted(listed_delivery),'currentUnlistedTileIds':unlisted},'Use production-resume completeCandidates and their versioned paths for local continuation; have the original owner create a new versioned delivery manifest after the fixed upload cutoff. Do not replace the fixed export.')

# Review records are reused as evidence; images/crops are never visually opened or remade.
review_paths=set()
for tile,d in derivations.items():
    if not d:continue
    for key in ['qa','reviewRecord','acceptanceRecord','reviewPath']:
        if isinstance(d.get(key),str) and d[key].endswith('.json'):review_paths.add(d[key])
for tile,s in selections.items():
    for key in ['reviewRecord','reviewPath','review']:
        if isinstance(s.get(key),str) and s[key].endswith('.json'):review_paths.add(s[key])
review_paths.update(h.get('externalSeamReviews',[]))
reviews=[]
for path in sorted(review_paths):
    rp=Path(path)
    if not rp.is_absolute():rp=ZONE/rp
    item={'path':rel(rp),'exists':rp.is_file(),'visualReviewReusedOnly':True}
    if rp.is_file():
        j=load(rp)
        item['recordSha256']=read_set[rel(rp)]
        item['tileId']=j.get('tileId')
        item['status']=j.get('status',j.get('internalReview'))
        item['formalAccepted']=j.get('formalAccepted',False)
        cp=j.get('candidatePath',j.get('candidate'))
        ch=j.get('candidateSha256',j.get('sha256'))
        if cp and isinstance(cp,str) and ch:
            current=next((t.get('candidate') for t in tile_rows if t.get('candidate',{}).get('path')==rel(cp)),None)
            item['candidatePath']=rel(cp);item['recordedCandidateSha256']=ch
            if current:item['hashMatchesCurrentCandidate']=ch==current['sha256']
        if 'records' in j:
            item['reviewedPairs']=[{'pair':r.get('pair'),'status':r.get('status'),'lowerRecordedSha256':r.get('lower',{}).get('sha256'),'lowerPath':rel(r['lower']['file']) if r.get('lower',{}).get('file') else None} for r in j['records']]
    reviews.append(item)

# Record the potentially stale association of reviews and historical base anchors without
# treating a whole-file revision as evidence of a changed edge. No historical PNG is scanned.
current_hashes={t['candidate']['path']:t['candidate']['sha256'] for t in tile_rows if 'candidate' in t}
stale_links=[]
def links(obj,loc):
    if isinstance(obj,dict):
        f=obj.get('file',obj.get('source',obj.get('neighbor')))
        hv=obj.get('sha256',obj.get('neighborSha256'))
        if isinstance(f,str) and hv:
            key=rel(f)
            if key in current_hashes and hv!=current_hashes[key]:
                stale_links.append({'record':loc,'path':key,'recordedSha256':hv,'currentSha256':current_hashes[key],'interpretation':'Historical input/review snapshot associated with a mutable current path; full-file mismatch does not prove the relevant border changed.'})
        for k,v in obj.items():
            if k not in ['priorSelectionHistory','priorRevision']:links(v,loc+'/'+k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):links(v,f'{loc}/{i}')
for tile,d in derivations.items():
    if d:links(d,rel(str(candidate_by_tile[tile]['file'])+'.derivation.json'))
for r in reviews:
    if r['exists']:links(load(ROOT/r['path']),r['path'])
if stale_links:issue('historical_anchor_or_review_hash_differs',None,'Current derivations/reviews still carry historical snapshot hashes against some mutable candidate paths. Reusing them requires preserved edge/anchor evidence, not a whole-file hash substitution.',stale_links,'Preserve old recorded hashes. For the current candidate, associate an existing unchanged-edge proof or a newer seam-review record with exact candidate hashes. Do not automatically re-mark the old review as current or perform a new visual review in this task.')

peerbase = BASE/'parallel-review-20261013/island-game-20261009/root-audit-v01'
peer_evidence = {}
for peername in ['inventory.json','input-snapshot.json','legacy-cross-zone-reuse.json']:
    peerpath=peerbase/peername
    if peerpath.is_file():
        peer_evidence[peername]=load(peerpath)
peer_reuse=peer_evidence.get('legacy-cross-zone-reuse.json',[])
peer_summary={'paths':[rel(peerbase/n) for n in peer_evidence],'generatedAtUtc':peer_evidence.get('inventory.json',{}).get('generatedAtUtc'),'scope':'Reuse metadata and source hash/positions only; no images opened or new visual claims.','crossZoneReusedPassedSegmentCount':sum(x.get('canReusePassedEvidence') is True and x.get('oldEvidenceHashValid') is True and x.get('currentPixelsIdentical') is True for x in peer_reuse),'segments':[{'pair':x.get('pair'),'segment':x.get('segment'),'canReusePassedEvidence':x.get('canReusePassedEvidence'),'currentPixelsIdentical':x.get('currentPixelsIdentical'),'oldEvidenceHashValid':x.get('oldEvidenceHashValid'),'worldBox':x.get('newEvidence',{}).get('worldBox')} for x in peer_reuse]}
peer_ne_native={}
for tile in peer_evidence.get('inventory.json',{}).get('tiles',[]):
    if tile.get('zone')=='northeast':
        for src in tile.get('sources',[]):
            peer_ne_native[rel(src['file'])]=src
peer_summary['matchingCurrentNortheastCoreSources']=sum(k in peer_ne_native and v.get('sha256')==peer_ne_native[k].get('sha256') for k,v in native.items())
peer_summary['changedCurrentNortheastSourcesSincePeerSnapshot']=[k for k,v in native.items() if k in peer_ne_native and v.get('sha256')!=peer_ne_native[k].get('sha256')]
for link in stale_links:
    link['currentAssociationStatus']='historical_anchor_or_review_requires_owner_association'
    if '/qa/cross-zone-20261011/review.json/' in link['record'] and peer_summary['crossZoneReusedPassedSegmentCount']==8:
        link['currentAssociationStatus']='supported_by_peer_exact_pixel_evidence_reuse'
        link['reusedEvidence']=rel(peerbase/'legacy-cross-zone-reuse.json')

selected_native_count=len(native)
selected_native_unknown_count=sum(x['modelStatus']=='unconfirmed' for x in native.values())
unselected_candidates=[]
unselected_coords=sorted({co for tile in inventory['tileInventory'] for co in set(tile['unselectedCoordinates'])-set(tile['missingGeneratedCoordinates'])})
for co in unselected_coords:
    eligible=[x for x in resume['newOutputs'] if re.sub(r'_v\d+$','',x.get('id',''))==co and x.get('status')=='candidate_unreviewed']
    if not eligible:
        unselected_candidates.append({'coordinate':co,'currentCandidate':None,'status':'no_unreviewed_current_resume_candidate_found','selectionCoverage':False})
        continue
    latest=max(eligible,key=lambda x:x.get('generatedAt',''))
    n=native_entry(latest['file'])
    n['uses'].append({'role':'current_generated_but_unselected_candidate','coordinate':co,'resume':rel(p['productionResume'])})
    unselected_candidates.append({'coordinate':co,'currentCandidateId':latest['id'],'currentCandidatePath':n['path'],'sha256':n.get('sha256'),'size':n.get('size'),'hashMatchesResume':n.get('sha256')==latest.get('sha256'),'fileAndGenerationRecordConfirmed':not n['failures'],'status':latest.get('status'),'selectionCoverage':False,'suggestionForOriginalOwner':'Review the current candidate first; do not choose an older rejected base version or generate another duplicate by filename guessing.'})

inv_by_tile={x['tileId']:x for x in inventory['tileInventory']}
for row in tile_rows:
    iv=inv_by_tile[row['tileId']]
    row['inventorySelectedIdsMatch']=iv['selectedCoreIds']==row['selectedCoreIds']
    row['missingGeneratedCoreIdsFromCurrentInventory']=iv['missingGeneratedCoordinates']
    row['unselectedExistingCandidateCoordinatesFromInventory']=sorted(set(iv['unselectedCoordinates'])-set(iv['missingGeneratedCoordinates']))

queue_tiles=['r04_c10','r05_c10','r05_c11','r06_c11','r06_c12','r06_c13','r06_c14','r07_c14']
queue=[]
for i,tile in enumerate(queue_tiles,1):
    iv=inv_by_tile[tile]
    refs=[]
    ox,oy=origin(tile)
    for other,c in candidate_by_tile.items():
        nx,ny=origin(other)
        if abs(nx-ox)+abs(ny-oy)==4096:
            refs.append({'tileId':other,'candidatePath':rel(c['file']),'sha256':c['sha256'],'edgeStatus':'Existing candidate boundary only; visual continuity remains the seam-review task/original owner responsibility.'})
    queue.append({'priority':i,'tileId':tile,'originalOwner':'northeast','reservationCreated':False,'action':'Original-owner continuation suggestion only. First resolve full-candidate references above. Existing/free 2.5 is preferred; if unavailable the user allows existing built-in 2.0. This audit task does not generate or reserve coordinates.','missingSelectedCoreCount':len(iv['unselectedCoordinates']),'missingSelectedCoreIds':iv['unselectedCoordinates'],'missingGeneratedCoreCountFromCurrentInventory':len(iv['missingGeneratedCoordinates']),'missingGeneratedCoreIdsFromCurrentInventory':iv['missingGeneratedCoordinates'],'existingButUnselectedCoordinatesFromCurrentInventory':sorted(set(iv['unselectedCoordinates'])-set(iv['missingGeneratedCoordinates'])),'availableFullNeighborReferences':refs})

owned=set(inv_by_tile)-set(exclusions)
allmissing=[]
for tile in sorted(owned):
    iv=inv_by_tile[tile]
    if iv['unselectedCoordinates']:
        allmissing.append({'tileId':tile,'missingSelectedCoreCount':len(iv['unselectedCoordinates']),'missingSelectedCoreIds':iv['unselectedCoordinates'],'missingGeneratedCoreIdsFromCurrentInventory':iv['missingGeneratedCoordinates']})

changed=[]
for path,oldhash in read_set.items():
    q=ROOT/path
    if not q.is_file() or sha(q)!=oldhash:changed.append(path)
summary={'ownedTileCount':len(owned),'excludedAcceleratedTileCount':len(exclusions),'currentSelectionManifestCount':len(selections),'currentReferencedUniqueNativeSourceCount':len(native),'selectedCoreCoordinateCount':sum(t['selectedCoreCount'] for t in tile_rows),'selectedOverlayContributionCount':sum(x['role']=='selected_overlay' for x in contributions),'uniqueOverlaySourceCount':len({x['source'] for x in contributions if x['role']=='selected_overlay'}),'currentCompleteCandidateCount':len(candidate_by_tile),'currentCompleteCandidateFileHashSizeConfirmedCount':sum('candidate' in t and not t['candidate']['failures'] for t in tile_rows),'completeCandidateOriginAndContributionConfirmedCount':sum(t.get('candidate',{}).get('originAndContributionConfirmed',False) for t in tile_rows),'nativeSourceFileHashSizeConfirmedCount':sum(not x['failures'] for x in native.values()),'missingNativeSourceFileCount':sum(not x['exists'] for x in native.values()),'missingGenerationRecordCount':sum(not x['generationRecordExists'] for x in native.values()),'nativeHashOrDimensionFailureCount':sum(bool(x['failures']) for x in native.values()),'confirmedNativeContributionCount':sum(x['confirmed'] for x in contributions),'uncertainNativeContributionCount':sum(not x['confirmed'] for x in contributions),'actualModelUnconfirmedNativeSourceCount':sum(x['modelStatus']=='unconfirmed' for x in native.values()),'actualModelUnconfirmedCompleteCandidateCount':sum(d is not None and not d.get('actualModel') for d in derivations.values()),'missingSelectionCoreCount':sum(x['missingSelectedCoreCount'] for x in allmissing),'missingGeneratedCoreCountFromCurrentInventory':sum(len(x['missingGeneratedCoreIdsFromCurrentInventory']) for x in allmissing),'incompleteOwnedTileCount':len(allmissing),'internalPassedCandidateCountFromCurrentRecord':inventory['internalPassed4kCount'],'formalAcceptedCountFromCurrentRecord':inventory['formalAcceptedCount'],'referenceIssueGroupCount':len(issues),'historicalAnchorReviewHashAssociationCount':len(stale_links),'inputRecordChangedDuringAuditCount':len(changed),'suggestedAdjacentQueueTileCount':len(queue)}
report={'schemaVersion':1,'reportVersion':'northeast-sources-v1','createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Read-only source/path/hash/native-contribution and missing-coordinate audit for current northeast references only. No historical version sweep, no image viewing, visual reassessment, generation, repair, stitching, shared progress changes, Git or other chat/window actions.','rootAGENTSRead':True,'constraints':{'sharedDirectoriesReadOnly':True,'writeDirectory':rel(OUT),'sourceModelIsNotRelabeled':True,'unknownActualModelIsNotMissingArtwork':True,'mapCompleteClaim':False,'queueDoesNotReserveCoordinates':True},'summary':summary,'currentAuthoritativeRecords':{'progress':rel(ZONE/'progress.json'),'handoff':rel(ZONE/'handoff.json'),'productionResume':rel(p['productionResume']),'continuationInventory':rel(p['continuationInventory']),'deliveryIndex':rel(p['deliveryIndex']),'sourceRecordUpdatedAtUtc':inventory['updatedAtUtc'],'selectionReferenceBasis':'production-resume.currentSelections; current complete candidate paths use production-resume.completeCandidates and progress.pixelCoveredCandidates, not an unversioned filename guess.','excludedCoordinates':exclusions},'completeCandidateAndSelectionAudit':tile_rows,'directNativeSourceAudit':list(native.values()),'nativeContributions':contributions,'currentDeliveryReferenceChecks':delivery_checks,'reusedReviewEvidence':reviews,'referenceIssues':issues,'remainingCoreInventory':allmissing,'suggestedAdjacentOwnerQueue':queue,'inputRecordSha256':read_set,'changedInputsDuringAudit':changed,'limitations':['PNG decoding is limited to size/format metadata; this task makes no visual acceptance claim and does not rebuild or stitch pixels.','Generated-but-unselected candidate absence is taken from current production inventory, not a search through all historical versions.','Actual image-generation model remains unconfirmed wherever records lack actualModel; target/config values do not prove GPT Image 2.5.','Historical snapshot input and review associations retain their original hashes; a later full-file change may leave an edge unchanged, so those associations need explicit evidence before reuse.']}
report['auditStartedAtUtc']=audit_started
report['currentModelPolicy']='User clarification 2026-10-13: prefer free/existing 2.5; existing built-in 2.0 is allowed if unavailable. This audit generates no new images. Unknown model metadata does not stop owner production and is not missing artwork.'
report['peerEvidenceReuse']=peer_summary
report['summary']['selectedReferencedUniqueNativeSourceCount']=selected_native_count
report['summary']['selectedReferencedUnknownModelNativeSourceCount']=selected_native_unknown_count
report['summary']['currentGeneratedButUnselectedCandidateCount']=len(unselected_candidates)
report['summary']['currentGeneratedButUnselectedCandidateConfirmedCount']=sum(x.get('fileAndGenerationRecordConfirmed',False) and x.get('hashMatchesResume',False) for x in unselected_candidates)
report['summary']['peerCrossZonePassedSegmentsReused']=peer_summary['crossZoneReusedPassedSegmentCount']
report['summary']['uncertainHistoricalAnchorReviewAssociations']=sum(x.get('currentAssociationStatus')!='supported_by_peer_exact_pixel_evidence_reuse' for x in stale_links)
report['currentGeneratedButUnselectedCandidates']=unselected_candidates
report['migrationPathMapping']={'currentRepositoryRoot':'D:/work/image','reportPaths':'Repository-relative except original external tool provenance.','ownerRecordsUseAbsolutePaths':True,'currentPathsMissingCount':summary['missingNativeSourceFileCount'],'laterMachineRecommendation':'Resolve all owner-record D:/work/image and D:\\work\\image prefixes against the new repository root in memory, verify matching native and candidate hashes, and use these repository-relative report paths. Do not restore deleted history or original tool-image directories. This audit does not rewrite owner records.'}
target=OUT/'northeast-sources-v1.json'
if '--write' in sys.argv:
    with target.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({'summary':summary,'nativeFailures':[v for v in native.values() if v['failures']],'candidateFailures':[v for v in tile_rows if v.get('candidate',{}).get('failures') or v.get('candidate',{}).get('derivationCoreSourceFailures') or v.get('candidate',{}).get('overlayContributionFailures')],'unconfirmedContributions':[v for v in contributions if not v['confirmed']],'issues':issues,'reportPath':rel(target) if '--write' in sys.argv else None},ensure_ascii=False,indent=2))
