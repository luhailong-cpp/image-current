"""Read-only source/evidence audit. No image decoding or processing, no production writes."""
import hashlib, json, struct, re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009')
ZONE = BASE/'southeast'
OUT = Path(__file__).resolve().parent
ASSIGNMENTS = BASE.parent/'acceleration-20261010'/'assignments.json'
START = datetime.now(timezone.utc).isoformat()
CACHE = {}

def within(p):
    p = Path(p).resolve()
    return p.is_relative_to(BASE) or p == ASSIGNMENTS.resolve()

def read(p):
    p=Path(p)
    assert within(p), str(p)
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    p=Path(p)
    assert within(p), str(p)
    st=p.stat(); key=(str(p.resolve()), st.st_size, st.st_mtime_ns)
    if key not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        CACHE[key]=h.hexdigest()
    return CACHE[key]

def info(p):
    p=Path(p)
    rec={'file':str(p),'exists':p.is_file()}
    if not p.is_file():return rec
    assert within(p), str(p)
    st=p.stat(); rec.update(sha256=sha(p), bytes=st.st_size, modifiedAtUtc=datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat())
    if p.suffix.lower()=='.png':
        with p.open('rb') as f:head=f.read(24)
        if head[:8]==b'\x89PNG\r\n\x1a\n':rec['dimensions']=list(struct.unpack('>II',head[16:24]))
    return rec

def localpath(value,td):
    if isinstance(value,dict): value=value.get('file') or value.get('path')
    if not isinstance(value,str):return None
    p=Path(value)
    if not p.is_absolute():p=td/p
    return p.resolve()

def brief(value,level=0):
    if isinstance(value,dict):
        return {k:brief(v,level+1) for k,v in value.items() if k not in {'evidence','seamReports','intersectionReports','independentReplay','sourcePixelSignature','sources','segments','crossings','images','reviews','seams','patches','derivedFrom','nativeOutputs'}}
    if isinstance(value,list):
        if len(value)>8:return {'count':len(value),'first':brief(value[0],level+1),'last':brief(value[-1],level+1)}
        return [brief(v,level+1) for v in value]
    return value

def bindings(data):
    found=[]
    def walk(d):
        if isinstance(d,dict):
            path=d.get('file') or d.get('path') or d.get('output')
            expected=d.get('sha256') or d.get('outputSha256')
            if isinstance(path,str) and isinstance(expected,str):
                p=Path(path)
                if p.is_absolute() and within(p):
                    actual=sha(p) if p.is_file() else None
                    found.append({'file':str(p),'expectedSha256':expected,'actualSha256':actual,'match':actual==expected})
            for v in d.values():walk(v)
        elif isinstance(d,list):
            for v in d:walk(v)
    walk(data)
    # The review's own evidence pixels being unchanged alone is not a claim that
    # every source selection is unchanged. Candidate bindings are checked separately.
    return found

contract=read(BASE/'production-contract.json')
assignment=read(ASSIGNMENTS)
delivery=read(ZONE/'delivery-index-20261012.json')
delivery_entries={e['tile']:e for e in delivery['entries']}
entries=[]
snapshot_files=[]
for r in range(8,15):
    for c in range(8,15):
        tid=f'r{r:02d}_c{c:02d}';td=ZONE/tid;sf=td/'selected-patches.json'
        e={'tile':tid,'tileCoreGlobalBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096], 'selectedManifest':info(sf)}
        selection=read(sf) if sf.is_file() else {}
        patches=selection.get('patches',{})
        e.update(selectedCount=len(patches),missingPatches=[f'p{i}{j}' for i in range(1,5) for j in range(1,5) if f'p{i}{j}' not in patches],internalReady=selection.get('internalReady',False),formalAccepted=selection.get('formalAccepted',False),status=selection.get('status','not_generated'))
        if sf.is_file():snapshot_files.append((sf,e['selectedManifest']['sha256']))
        pp=td/'coordinate-plan.json'; plan=read(pp) if pp.is_file() else {}
        pentries={p['id']:p for p in plan.get('patches',[])}
        e['coordinatePlan']=info(pp)
        e['referenceDeclarations']=plan.get('references',[])
        e['referenceFilesNotRead']='Outside allowed audit source scope; recorded hashes/roles are declarations, not current independent image comparison.'
        e['selectedSources']=[]
        for pid,rel in sorted(patches.items()):
            p=td/rel;source=info(p);pgeo=pentries.get(pid,{})
            source.update(patch=pid,classification='selected_native_original' if p.parent.name=='native' else 'selected_existing_derivative',coreCropNative=pgeo.get('coreCropNative',[115,115,1139,1139]),coreGlobalBox=pgeo.get('coreBox'),nativeGlobalBox=pgeo.get('globalBox'))
            side=[Path(str(p)+ext) for ext in ('.generation.json','.derivation.json')]
            source['provenanceRecords']=[info(s) for s in side if s.is_file()]
            e['selectedSources'].append(source)
        cp=localpath(selection.get('candidate') or delivery_entries.get(tid,{}).get('candidate'),td)
        if cp:
            e['candidate']=info(cp)
            expected=selection.get('candidateSha256') or delivery_entries.get(tid,{}).get('candidateSha256')
            e['candidate']['recordedSha256']=expected
            e['candidate']['recordedHashMatches']=(expected==e['candidate'].get('sha256')) if expected else None
            e['candidate']['assemblyPixelReplayInThisAudit']=False
            e['candidate']['assemblyPixelReplayNote']='This audit reads PNG headers/hashes only; does not decode images or reassemble candidates.'
        e['declaredMaterialPending']=selection.get('materialPending',False)
        e['reviewDocuments']=[]
        for k,v in selection.items():
            if re.search(r'Review|^qa$|qaManifest',k,re.I):
                rp=localpath(v,td)
                if rp and within(rp) and rp.suffix.lower()=='.json' and rp.is_file():
                    rv=read(rp); rr=info(rp); rr.update(field=k,conclusion=brief(rv),hashBindings=bindings(rv))
                    e['reviewDocuments'].append(rr)
        de=delivery_entries.get(tid,{})
        e['deliveryIndexComparison']={'recordedSelectedCount':de.get('selectedPositions'), 'countMatchesCurrent':de.get('selectedPositions')==len(patches), 'recordedInternalReady':de.get('internalReady'), 'internalFlagMatchesCurrent':de.get('internalReady')==e['internalReady']}
        entries.append(e)

bytile={e['tile']:e for e in entries}
boundaries=[]
for r in range(8,15):
    se=bytile[f'r{r:02d}_c08'];swid=f'r{r:02d}_c07';sf=BASE/'southwest'/swid/'selected-patches.json'
    sd=read(sf) if sf.is_file() else {};sp=sd.get('patches',{})
    west={'axis':'vertical','boundaryX':28672,'row':r,'southeastTile':se['tile'],'southwestTile':swid,'southwestSelection':info(sf),'southeastSelectedCount':se['selectedCount'],'southwestSelectedCount':len(sp),'segments':[]}
    for sr in range(1,5):
        left=f'p{sr}4';right=f'p{sr}1'; srs={x['patch']:x for x in se['selectedSources']}
        sources=[]
        if left in sp:sources.append(info(sf.parent/sp[left]))
        if right in srs:sources.append(srs[right])
        west['segments'].append({'segment':sr,'globalY':[(r-1)*4096+(sr-1)*1024,(r-1)*4096+sr*1024],'southwestPatch':left,'southeastPatch':right,'sourceComplete':left in sp and right in srs,'sources':sources,'visualAcceptance':'not independently inspected in this audit'})
    west['fullyAvailable']=all(s['sourceComplete'] for s in west['segments'])
    boundaries.append(west)

external_reports=[]
for rel in ('seam-qa/r13_c08-selected-color-v2/root-available-external-review.json','seam-qa/r13_c08-selected-color-v2/west-segment-1.qa.json','seam-qa/independent-20261010/external-open-issues.json','seam-qa/G3-shared-stairs-resume-20261012/root-v3-independent-geometry-review.json','seam-qa/repair-resume-20261012/root-v8-independent-geometry-review.json'):
    p=ZONE/rel
    if p.is_file():
        d=read(p);rec=info(p);rec.update(conclusion=brief(d),hashBindings=bindings(d));external_reports.append(rec)

changes=[]
for sf,expected in snapshot_files:
    actual=sha(sf)
    if actual!=expected:changes.append({'file':str(sf),'startSha256':expected,'endSha256':actual})
selected=sum(e['selectedCount'] for e in entries)
report={'schemaVersion':1,'auditStartedAtUtc':START,'auditFinishedAtUtc':datetime.now(timezone.utc).isoformat(),'auditScope':'southeast selected sources, geometry declarations and existing QA evidence only; no image decoding, visual inspection, generation, production modification, Git or upload','readRoot':str(BASE),'writeRoot':str(OUT),'newGenerationAllowedForThisTask':False,'actualModelForExistingSources':'not independently verified; never relabeled as GPT Image 2.5','inventoryIsAtomicSnapshot':False,'sourceChangesDuringAudit':changes,'staleIfAnyInputHashChanges':True,'summary':{'targetTiles':49,'fullySelected16PatchTiles':sum(e['selectedCount']==16 for e in entries),'internallyReadyByCurrentSelection':sum(bool(e['internalReady']) for e in entries),'formalAcceptedByCurrentSelection':sum(bool(e['formalAccepted']) for e in entries),'selectedPatchPositions':selected,'missingSelectedPatchPositions':784-selected,'partialTiles':[{'tile':e['tile'],'selectedCount':e['selectedCount'],'missing':e['missingPatches']} for e in entries if 0<e['selectedCount']<16],'noSelectionTiles':[e['tile'] for e in entries if not e['selectedCount']],'internallyPendingFullTiles':[e['tile'] for e in entries if e['selectedCount']==16 and not e['internalReady']],'candidatePngDimensions':[e['candidate'].get('dimensions') for e in entries if 'candidate' in e],'selectedPngDimensions':sorted({tuple(s.get('dimensions',[])) for e in entries for s in e['selectedSources']})},'geometry':{'formalTile':[4096,4096],'grid':[14,14],'subgrid':[4,4],'nativeInputExpected':[1254,1254],'core':[1024,1024],'halo':115,'neighborOverlap':230,'coreCrop':[115,115,1139,1139],'assembly':'paste 16 exact core crops at 1024-grid positions, no resampling/blending/warping; existing adopted derivatives retain their existing processing provenance'},'deliveryIndex':info(ZONE/'delivery-index-20261012.json'),'progress':info(ZONE/'progress.json'),'contract':info(BASE/'production-contract.json'),'assignment':info(ASSIGNMENTS),'assignmentDeduplication':'No acceleration assignment overlaps southeast (all village acceleration coordinates r03..r05 c10..c11); southeast 49 target coordinates are unique.','tiles':entries,'westBoundaryAvailability':boundaries,'externalEvidence':external_reports,'reusableEvidenceLimits':['An internal pass is not a cross-tile/cross-zone pass.','r13_c08 existing available external review explicitly excludes west and south.','Old missing-neighbor reports must be regenerated from current sources if neighboring tiles now exist.','Hash-only audit does not certify visual quality or exact pixel core assembly.'],'recommendedCurrentCrossZoneChecks':[{'rows':[10,11,12,13],'columns':[7,8],'boundaryX':28672,'reason':'Use current selected sources from both zones; prior southeast western report was neighbor-missing. Preserve current hashes before cropping.','candidateSources':[bytile[f'r{r:02d}_c08'].get('candidate') for r in range(10,14)]}]}
target=OUT/'southeast-evidence-audit-v1.json'
assert not target.exists(),'Versioned report already exists; do not overwrite'
target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(target),'summary':report['summary'],'changesDuringAudit':changes,'westRowsFullyAvailable':[b['row'] for b in boundaries if b['fullyAvailable']]},ensure_ascii=False,indent=2))
