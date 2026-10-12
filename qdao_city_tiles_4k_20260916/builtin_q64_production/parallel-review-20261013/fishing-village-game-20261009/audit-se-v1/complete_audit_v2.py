"""Complete evidence audit from the v1 captured source snapshot; no image processing."""
import json, hashlib, struct
from pathlib import Path
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent
BASE=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009')
ZONE=BASE/'southeast'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    p=Path(p);assert p.resolve().is_relative_to(BASE)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def info(p):
    p=Path(p);d={'file':str(p),'exists':p.is_file()}
    if p.is_file():
        d['sha256']=sha(p)
        d['modifiedAtUtc']=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()
        if p.suffix.lower()=='.png':
            with p.open('rb') as f:h=f.read(24)
            if h[:8]==b'\x89PNG\r\n\x1a\n':d['dimensions']=list(struct.unpack('>II',h[16:24]))
    return d

report=read(OUT/'southeast-evidence-audit-v1.json')
report['supersedes']='southeast-evidence-audit-v1.json; replaces tile-local-only SW lookup with current-tile-ledger lookup.'
bytile={t['tile']:t for t in report['tiles']}
review_assessments=[]
for e in report['tiles']:
    if not e['selectedCount']:continue
    if any(s.get('coreGlobalBox') is None for s in e['selectedSources']):
        r=int(e['tile'][1:3]);c=int(e['tile'][5:7])
        for s in e['selectedSources']:
            sr=int(s['patch'][1]);sc=int(s['patch'][2]);x=(c-1)*4096+(sc-1)*1024;y=(r-1)*4096+(sr-1)*1024
            if s.get('coreGlobalBox') is None:
                s.update(coreGlobalBox=[x,y,x+1024,y+1024],nativeGlobalBox=[x-115,y-115,x+1139,y+1139],geometryBasis='computed from shared contract; no per-tile coordinate-plan located in v1')
    candidate=e.get('candidate',{})
    matches=[]
    for rv in e['reviewDocuments']:
        d=read(rv['file']);expected=None;rp=None
        if isinstance(d.get('candidate'),dict):
            expected=d['candidate'].get('sha256');rp=d['candidate'].get('file') or d['candidate'].get('path')
        else:
            expected=d.get('candidateSha256');rp=d.get('candidate')
        if expected is None and isinstance(d.get('summary'),dict):
            expected=d['summary'].get('candidateSha256');rp=d['summary'].get('candidateFile')
        if expected:
            matches.append({'review':rv['file'],'reviewedCandidate':rp,'reviewedCandidateSha256':expected,'matchesCurrentCandidateHash':expected==candidate.get('sha256')})
    assessment={'tile':e['tile'],'currentSelectionInternalReady':e['internalReady'],'currentCandidateHash':candidate.get('sha256'),'candidateReviewBindings':matches,'allReferencedFileHashBindingsStillMatch':all(b['match'] for r in e['reviewDocuments'] for b in r.get('hashBindings',[])), 'visualInspectionPerformedByThisAudit':False}
    if e['internalReady']:
        assessment['evidenceUse']='reuse existing internal review for the same candidate hash only; does not certify any unreviewed cross-zone edge'
        assessment['hasSameCandidateReviewBinding']=any(m['matchesCurrentCandidateHash'] for m in matches)
    else:assessment['evidenceUse']='retain internal-pending status; historical pass must not override current adopted-selection flags'
    review_assessments.append(assessment)
report['internalEvidenceAssessment']=review_assessments

ledgerPath=BASE/'southwest'/'current-tile-ledger.json';ledger=read(ledgerPath);bySW={t['tile']:t for t in ledger['tiles']}
report['southwestBoundaryLedger']=info(ledgerPath)
boundaries=[]
for r in range(8,15):
    tid=f'r{r:02d}_c08';swid=f'r{r:02d}_c07';e=bytile[tid];sw=bySW[swid];cp=sw.get('current4096');swCandidate=info(cp['path']) if cp else None
    if swCandidate:swCandidate['recordedHashMatches']=swCandidate['sha256']==cp['sha256']
    w={'axis':'vertical','boundaryX':28672,'row':r,'southeastTile':tid,'southwestTile':swid,'southwestCandidate':swCandidate,'southwestLedgerNativeSlots':sw['nativeSlots'],'southwestInternalQa':sw['internalQa'],'southwestRecordedKnownSharedEdgesQa':sw['knownSharedEdgesQa'],'southwestOuterEdgesPending':sw['outerEdgesPending'],'southeastCandidate':e.get('candidate'),'southeastSelectedCount':e['selectedCount'],'segments':[]}
    current={s['patch']:s for s in e['selectedSources']}
    for sr in range(1,5):
        pid=f'p{sr}1';available=bool(swCandidate and swCandidate['exists'] and pid in current)
        w['segments'].append({'segment':sr,'globalY':[(r-1)*4096+(sr-1)*1024,(r-1)*4096+sr*1024],'sourceComplete':available,'southwestCropFrom4096':[3840,(sr-1)*1024,4096,sr*1024],'southeastCropFromSelected1254':[115,115,371,1139],'southeastSource':current.get(pid),'visualAcceptance':'uninspected in this audit'})
    w['fullyAvailable']=all(s['sourceComplete'] for s in w['segments'])
    w['existingCrossZonePass']='No reliable existing current SW c07 / SE c08 visual pass located in audited evidence.'
    boundaries.append(w)
report['westBoundaryAvailability']=boundaries
report['recommendedCurrentCrossZoneChecks']=[{'rows':[10,11],'columns':[7,8],'boundaryX':28672,'sourceComplete':True,'classification':'current exact native-pixel seam inspection possible; no closure inferred from either zone internal QA','note':'r11_c07 internal QA remains pending; use for diagnosis without promoting tile acceptance.'},{'rows':[12,13,14],'columns':[7,8],'sourceComplete':False,'classification':'neighbor_missing','reason':'SW current-tile-ledger records 0 native slots for c07.'}]

changes=[]
for e in report['tiles']:
    m=e['selectedManifest']
    if m['exists']:
        actual=sha(m['file'])
        if actual!=m['sha256']:changes.append({'file':m['file'],'capturedSha256':m['sha256'],'currentSha256':actual,'affectedTile':e['tile']})
report['sourceChangesAtFinalRecheck']=changes
report['snapshotMustBeRecheckedBeforeImageWork']=True
report['auditFinishedAtUtc']=datetime.now(timezone.utc).isoformat()
report['correctionNote']='v1 attempted SW tile-local selected-patches paths; southwest uses a ledger/tiles/native workflow. v2 fixes this and permits r10/r11 cross-zone seam inspection.'
target=OUT/'southeast-evidence-audit-v2.json';assert not target.exists()
target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(target),'westRowsFullyAvailable':[b['row'] for b in boundaries if b['fullyAvailable']],'candidateCurrentHashMatches':[b['southwestCandidate']['recordedHashMatches'] for b in boundaries if b['southwestCandidate']],'finalSelectionChanges':changes,'internalReadyCandidateBindings':[{'tile':a['tile'],'sameCandidateReview':a.get('hasSameCandidateReviewBinding')} for a in review_assessments if a['currentSelectionInternalReady']]},ensure_ascii=False,indent=2))
