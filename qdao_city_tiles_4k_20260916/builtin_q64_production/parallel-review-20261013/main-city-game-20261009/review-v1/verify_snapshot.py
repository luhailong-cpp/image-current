from build_summary import *
from concurrent.futures import ThreadPoolExecutor

def collect_baseline():
    inputs={}
    conflicts=[]
    absent=set()
    def add(p,h,scope):
        if not p or not h: return
        pp=Path(p).resolve()
        if not pp.is_relative_to(ROOT.resolve()) and pp != (ROOT.parent/'acceleration-20261010/assignments.json').resolve(): return
        key=str(pp)
        if key in inputs and inputs[key]['sha256']!=h:
            conflicts.append({'file':key,'old':inputs[key]['sha256'],'new':h,'scope':scope})
        inputs[key]={'file':key,'sha256':h,'scope':scope}
    def addrecord(d,scope):
        if not isinstance(d,dict): return
        add(record_path(d),d.get('sha256'),scope)
    for d in read(NW/'input-hashes.json')['inputs']: addrecord(d,'northwest census actual input')
    for d in read(SW/'input-evidence.json'): addrecord(d,'southwest census metadata input')
    for t in read(SW/'current-tiles.json'):
        for k in ['candidateVerification','contextVerification','assemblyEvidence','selectionManifest']:
            addrecord(t.get(k),'southwest current artifact or selection')
        for n in t.get('nativeSources',[]):
            addrecord(n,'southwest selected native')
            addrecord(n.get('generationRecord'),'southwest selected native receipt')
        for n in t.get('existingReviews',[]): addrecord(n,'southwest reused review')
    for p,d in read(EAST/'input-snapshot.json').items(): add(p,d['sha256'],'east actual input')
    for t in read(EAST/'current-tiles.json'):
        for e in t.get('selectedNativeEntries',[]):
            if not e.get('exists') and e.get('path'): absent.add(str(Path(e['path']).resolve()))
    g=read(GROUP/'manifest.json')
    for d in g['sourceFiles']: addrecord(d,'group01 current full source')
    for d in g['controlSnapshots']:
        if not str(d['file']).endswith('AGENTS.md'): addrecord(d,'group01 captured control')
    return list(inputs.values()),sorted(absent),conflicts

def reconcile_progress():
    p=ROOT/'northwest/progress.json'
    prog=read(p)
    idx=read(OUT/'current-256-coordinate-index.json')['coordinates']
    nw={t['coordinate']:t for t in idx if t['owner']=='northwest'}
    assert len(nw)==60
    pp={t['tile']:t for t in prog['tiles']}
    for k,t in nw.items():
        assert pp[k]['selectedAvailable']==t['selectedCoreCount'],k
        assert pp[k]['formalAccepted'] is False,k
    verified=prog['currentVerifiedDelivery']
    captured=read(NW/'coverage.json')
    assert prog['currentScopeCounts']['internallyPassedTiles']==11
    assert prog['currentScopeCounts']['tilesWithAll16NativePatches']==12
    assert prog['currentScopeCounts']['missingNativePatches']==768
    assert verified['tileCount']==11
    assert sha(verified['file'])==verified['sha256']=='12abf3ec1898a2554971d5f8535e51a955b6e0fe35cc2085d76b284c7300cab2'
    assert verified['sourceAudit']['sha256']==sha(verified['sourceAudit']['file'])
    b=read(OUT/'source-baseline.json')
    matching=[e for e in b['inputs'] if e['file']==str(p)]
    assert len(matching)==1
    old=matching[0]['sha256']; new=sha(p)
    copied=OUT/'northwest-progress-revalidated-snapshot.json'
    save(copied,prog)
    rec={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(p),'priorCapturedSha256':old,'currentSha256':new,'metadataChanged':old!=new,'revalidatedSelectedCountsForAll60OwnedCoordinates':True,'currentAdoptedElevenTileManifestUnchanged':True,'sourceValidationHashVerified':True,'formalAcceptedRemainsZero':True,'revalidatedMeaning':'Current fields needed by this inventory match the captured selected sources and adoption manifest. Old guard remains stale; this new validation permits a second baseline without claiming a byte-level old/new metadata diff.','copiedCurrentProgress':{'file':str(copied),'sha256':sha(copied)}}
    save(OUT/'northwest-progress-revalidation.json',rec)
    matching[0]['sha256']=new
    matching[0]['scope']='northwest progress revalidated at final check'
    b['revalidationRecord']={'file':str(OUT/'northwest-progress-revalidation.json'),'sha256':sha(OUT/'northwest-progress-revalidation.json')}
    b['previousBaseline']={'file':str(OUT/'source-baseline.json'),'sha256':sha(OUT/'source-baseline.json')}
    save(OUT/'source-baseline-v2.json',b)
    print(json.dumps(rec,ensure_ascii=False))

def reconcile_sw_progress():
    p=ROOT/'southwest/progress.json'; prog=read(p)
    idx=[t for t in read(OUT/'current-256-coordinate-index.json')['coordinates'] if t['owner']=='southwest']
    assert prog['selectedNativePatchCount']==sum(t['selectedCoreCount'] for t in idx)==258
    assert prog['complete4kCandidateCount']==sum(t['fullCurrent4KCandidate'] for t in idx)==15
    assert prog['formalAcceptedCount']==0
    base=read(OUT/'source-baseline-v2.json')
    old={e['file']:e for e in base['inputs']}
    for k in ['currentVerifiedInventory','current4kCandidateCatalog','countsSnapshot']:
        v=str(Path(prog[k]).resolve()); assert sha(v)==old[v]['sha256'],k
    partials={t['coordinate']:t['selectedCoreCount'] for t in idx if 0<t['selectedCoreCount']<16}
    assert partials=={k:v['verifiedNativeSlotCount'] for k,v in prog['currentPartials'].items()}
    oldsha=old[str(p)]['sha256']; newsha=sha(p)
    copied=OUT/'southwest-progress-revalidated-snapshot.json'; save(copied,prog)
    rec={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(p),'priorCapturedSha256':oldsha,'currentSha256':newsha,'metadataChanged':oldsha!=newsha,'currentInventoryCatalogCountsManifestHashesUnchanged':True,'allThreePartialCountsMatch':True,'fullCandidateCount':15,'selectedCoreCount':258,'formalAcceptedCount':0,'copiedCurrentProgress':{'file':str(copied),'sha256':sha(copied)},'scope':'Revalidate current coverage/adoption fields without overwriting earlier stale guard or claiming byte-level old/new metadata diff.'}
    rp=OUT/'southwest-progress-revalidation.json'; save(rp,rec)
    old[str(p)]['sha256']=newsha; old[str(p)]['scope']='southwest progress revalidated at final check'
    base['southwestRevalidationRecord']=f_record(rp) if 'f_record' in globals() else {'file':str(rp),'sha256':sha(rp)}
    base['previousBaselineV2']={'file':str(OUT/'source-baseline-v2.json'),'sha256':sha(OUT/'source-baseline-v2.json')}
    save(OUT/'source-baseline-v3.json',base)
    print(json.dumps(rec))

def verify(version=None):
    baseline=OUT/(f'source-baseline-{version}.json' if version else 'source-baseline.json')
    if not baseline.exists():
        inputs,absent,conflicts=collect_baseline()
        save(baseline,{'capturedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'absentSelectedFiles':absent,'baselineConflicts':conflicts,'policyFile':'D:/work/image/AGENTS.md','policySha256':sha('D:/work/image/AGENTS.md'),'validityRule':'If any captured selected source, current selection/adoption metadata, or reused review changes, its dependent conclusions expire; a new version must be reviewed. Snapshot does not follow later production automatically.'})
    b=read(baseline)
    def one(e):
        p=Path(e['file']); actual=sha(p) if p.exists() else None
        return {'file':str(p),'expected':e['sha256'],'actual':actual,'scope':e['scope']} if actual!=e['sha256'] else None
    with ThreadPoolExecutor(max_workers=4) as pool: changed=[x for x in pool.map(one,b['inputs']) if x]
    appeared=[p for p in b['absentSelectedFiles'] if Path(p).exists()]
    gm=read(GROUP/'manifest.json')
    group_changed=[e for e in changed if e['file'] in {x['file'] for x in gm['sourceFiles']}]
    final={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':str(baseline),'inputCount':len(b['inputs']),'absentSelectedFileCount':len(b['absentSelectedFiles']),'changedInputs':changed,'appearedSelectedFiles':appeared,'baselineConflicts':b['baselineConflicts'],'stale':bool(changed or appeared or b['baselineConflicts']),'group01SourcePixelsStale':bool(group_changed),'newPolicySha256':sha('D:/work/image/AGENTS.md'),'ruleReread':True,'scope':'Captured existing-source batch only; later production belongs to a new snapshot'}
    # This guard produces a timestamped new result; it never relabels earlier evidence.
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    save(OUT/f'source-guard-{stamp}.json',final)
    print(json.dumps(final,ensure_ascii=False))

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='reconcile': reconcile_progress()
    elif len(sys.argv)>1 and sys.argv[1]=='reconcile-sw': reconcile_sw_progress()
    else: verify(sys.argv[1] if len(sys.argv)>1 else None)
