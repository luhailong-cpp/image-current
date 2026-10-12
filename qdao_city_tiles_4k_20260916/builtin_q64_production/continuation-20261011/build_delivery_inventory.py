"""Read-only current-manifest inventory; writes only the coordinator's report."""
import json, re, struct, hashlib
from pathlib import Path
from datetime import datetime, timezone
from inventory_probe import BASE, MAPS, read

OUT=BASE/'continuation-20261011'/'delivery-inventory.json'
rows=[]
def pstr(p): return Path(p).as_posix()
def resolve(p,z):
    p=Path(p)
    return p if p.is_absolute() else z/p
def ev(p):
    p=Path(p)
    return {'path':pstr(p),'exists':p.is_file(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None}
def image(p,z):
    p=resolve(p,z)
    r={'path':pstr(p),'exists':p.is_file()}
    if r['exists']:
        try:
            with p.open('rb') as f: b=f.read(24)
            if b[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('not PNG')
            r['pixels']=list(struct.unpack('>II',b[16:24]))
            r['bytes']=p.stat().st_size
            r['is4096CandidateSize']=r['pixels']==[4096,4096]
        except Exception as e: r['error']=str(e)
    return r
def new(m,zname,target):
    z=BASE/m/zname; d=read(z/'progress.json')
    r={'map':m,'zone':zname,'ownedTargetTiles':target,'snapshotProgress':ev(z/'progress.json'),
       'workerUpdatedAt':d.get('updatedAt',d.get('updatedAtUtc')),'workerStatus':d.get('status'),
       'workerReportedCounters':{k:v for k,v in d.items() if isinstance(v,(int,bool)) and (('Count' in k and not any(s in k.lower() for s in ['native','repair','patch','core','generated','image','failed','provenance','error'])) or k=='tilesComplete')},
       'candidates':[],'reviewEvidence':[],'previews':[],'notes':[],
       'groupSeamPassedCandidateCount':'unknown','formalAcceptedCountReported':d.get('formalAcceptedCount','unknown'),
       'wholeZoneComplete':False}
    rows.append(r); return z,d,r
def add(r,z,t,p,source,active=True,internal='unknown',group='unknown',art='unknown'):
    r['candidates'].append({'tile':t,'artifact':image(p,z),'pointerSource':pstr(source),
        'activeVersionConfirmed':active,'internalPassReported':internal,'groupSeamPassReported':group,'artAcceptanceReported':art})
def preview(r,z,p):
    if p: r['previews'].append(image(p,z))
def tileid(x):
    return re.findall(r'r\d{2}_c\d{2}',str(x))[-1]

m=MAPS[0]
z,d,r=new(m,'accelerated-yamen-north',4)
src=Path(d['deliveryManifest']); a=read(src)
for t in a['tiles']: add(r,z,t['tile'],t['candidate'],src,internal='unknown',group=False)
r['reviewEvidence'].append(ev(src)); r['groupSeamPassedCandidateCount']=0
r['notes'].append('Four assigned candidates exist; delivery explicitly records open roof/structural boundary findings. Saved repair outputs do not imply they have been integrated or accepted.')
for k in ['preview','regionPreview','combined']:
    v=a.get(k)
    if isinstance(v,dict): preview(r,z,v.get('path',v.get('file')))
z,d,r=new(m,'northwest',60)
for t in d['tiles']:
    if t.get('jointCandidate'): add(r,z,tileid(t['jointCandidate']['file']),t['jointCandidate']['file'],z/'progress.json',internal=True,group=True)
a=d['currentJointDelivery']; r['reviewEvidence'].append(ev(a['file'])); preview(r,z,a['jointImage']['file']); r['groupSeamPassedCandidateCount']=4
z,d,r=new(m,'northeast',64)
for t in d['tiles']:
    if t.get('candidate'): add(r,z,tileid(t['candidate']),t['candidate'],z/'progress.json',internal=t.get('internalPassed','unknown'))
r['groupSeamPassedCandidateCount']=d.get('connectedGroupReviewed4kCount','unknown')
r['notes'].append('Four-tile connected-group review is reported by owner; fifth tile interior passed is separate from all exterior joins.')
z,d,r=new(m,'southwest',64)
src=Path(d['currentCandidateCatalog']); a=read(src)
for t,v in a['tiles'].items(): add(r,z,t,v['candidate']['file'],src,internal=v.get('internalPassed','unknown'),group=False)
r['reviewEvidence']=[ev(src),ev(a['qaReview'])]; preview(r,z,a['preview']['file']);r['groupSeamPassedCandidateCount']=0
r['notes']+=a['remainingIssues']
z,d,r=new(m,'southeast',64)
for t in d['tiles']:
    v=t.get('candidate')
    if v: add(r,z,tileid(v['path']),v['path'],z/'progress.json',internal='unknown')
preview(r,z,d['preview']);r['reviewEvidence'].append(ev(d['latestReviewSnapshot']))
r['notes'].append('Current four candidates are recorded while native repairs continue; aggregate internal count uses a restricted historical/current definition, so it is not propagated per tile.')

m=MAPS[1]
z,d,r=new(m,'accelerated-jewelry-approach',6)
src=Path(d['deliveryManifest']);a=read(src)
for t in a['sources']: add(r,z,t['tile'],t['file'],src,internal=True,group=True)
preview(r,z,a['preview']['file']);preview(r,z,a['regionCandidate']['file']);r['groupSeamPassedCandidateCount']=4
r['reviewEvidence']=[ev(src)]+[ev(v['file']) for v in a['qaEvidence']]
r['extensionProgress']=[]
for t in ['r05_c10','r05_c11']:
    s=z/t/'progress.json';v=read(s)
    r['extensionProgress'].append({'tile':t,'record':ev(s),'selectedCorePositionsReported':v.get('selectedNativeCoreCount'),'requiredCorePositions':16,'candidate4kPresentInCurrentRecord':False,'status':v['status']})
r['notes'].append('Original four are preserved. Two south-extension tiles are partial and are not counted as completed 4K candidates.')
z,d,r=new(m,'northwest',49)
for t,v in d['currentCandidates'].items():
    add(r,z,t,v['candidate'],z/'progress.json',internal='unknown');r['reviewEvidence'].append(ev(resolve(v['qa'],z)))
z,d,r=new(m,'northeast',43)
for t,v in d['activeCandidates'].items(): add(r,z,t,v['path'],z/'progress.json',internal=v.get('internalPassed','unknown'))
r['reviewEvidence'].append(ev(d['activeCandidateRecord']['path']))
r['notes'].append('Owner progress target 45 predates two extra coordinates transferred to jewelry window; effective target is 49 minus current six-coordinate assignment = 43.')
z,d,r=new(m,'southwest',49)
src=Path(d['artDeliveryIndex']);a=read(src)
for t in a['artAccepted']:
    add(r,z,t['tile'],t['file']['path'],src,internal=True,group='unknown',art=t['status']);r['reviewEvidence'].append(ev(t['artAudit']['path']))
preview(r,z,a['preview']['path']);r['notes'].append('Active art-delivery-index has six art_accepted files; older progress coverage/internal counters contradict this newer artifact list. Art acceptance does not claim whole-zone completion or every outside neighbor joined.')
r['artAcceptedCandidateCountReported']=len(a['artAccepted'])
z,d,r=new(m,'southeast',49)
for t in ['r10_c08','r10_c09','r11_c08']:
    p=z/'ready-for-edge-QA'/f'{t}.png';add(r,z,t,p,z/'progress.json',internal='unknown')
for t in ['r11_c09','r11_c10','r12_c09','r13_c09','r14_c09']:
    src=z/t/'progress.json'; a=read(src); add(r,z,t,a['candidate'],src,internal=a.get('internalReady4kCount')==1)
src=z/'r10_c10/qa/internal-review/review-round2-final.json';a=read(src);add(r,z,'r10_c10',a['candidate'],src,internal=True);r['reviewEvidence'].append(ev(src))
r['notes'].append('Zone progress is older than r14_c09 per-tile export. Nine explicitly addressed 4K files are inventoried. r12_c08/r12_c10/new south expansions remain partial or lack a current full-tile pointer in scoped records; no history-wide PNG census used.')

m=MAPS[2]
z,d,r=new(m,'accelerated-northeast-coast',4)
for t in d['candidateTiles']:
    add(r,z,tileid(t),z/'candidates'/(t+'.png'),z/'progress.json',internal='unknown')
for p in ['qa/audit-final-r02-c13/final-review.json','qa/audit-c14/review.json']:r['reviewEvidence'].append(ev(z/p))
r['notes'].append('Two addressed full-size candidates; north-row tiles remain incomplete. South edge review alone does not establish every outside edge passed.')
z,d,r=new(m,'northeast',45)
src=z/'handoff.json';a=read(src)
for p in a['pixelCoveredCandidates']:add(r,z,tileid(p),p,src,internal=tileid(p) in ['r03_c12','r03_c13','r03_c14','r04_c12'])
extra=z/'tiles/r04_c14.png';der=Path(str(extra)+'.derivation.json')
if extra.exists() and der.exists():add(r,z,'r04_c14',extra,der,active='unknown',internal='unknown')
r['notes'].append('handoff names five active full candidates. r04_c14 has since exported to the unversioned tiles directory with derivation; current-selection/QA not refreshed in handoff, so this sixth active version is unknown.')
z,d,r=new(m,'northwest',49)
src=z/'selected-native.json';a=read(src)
add(r,z,'r03_c03',a['currentCandidate']['path'],src,internal=a['currentCandidate']['internalVisualPassed'])
r['reviewEvidence'].append(ev(z/a['currentCandidate']['review']['path']))
# Inspect only baseline exports in the immediate current tiles directory; do not choose newest versions.
for t in ['r03_c02','r03_c04','r04_c03','r04_c04','r05_c03','r05_c04']:
    p=z/'tiles'/f'{t}_candidate-v1_4096.png';assembly=p.with_suffix('.assembly.json')
    if p.is_file() and assembly.is_file():add(r,z,t,p,assembly,active='unknown')
r['notes'].append('progress and selected-native are stale for neighbors. Seven unique coordinates have baseline/explicit 4096 exports, but six current adopted revisions and their current QA are unknown. Version number is deliberately not treated as adoption.')
z,d,r=new(m,'southeast',49)
for t,p in d['latestCandidates'].items(): add(r,z,t,p,z/'progress.json',internal=t in d['internalPassedTiles'])
r['notes'].append('Two roof ownership closures remain open. Single reported external-pass count is not a whole-region acceptance.')
z,d,r=new(m,'southwest',49)
src=Path(d['currentCandidate']);a=read(src)
for t in a['tiles']:add(r,z,t['tile'],t['path'],src,internal=t['internalPassed'],group=t['connectedGroupEdgesPassed'])
preview(r,z,a['preview']['path']);preview(r,z,a['combined']['path']);r['reviewEvidence']=[ev(src),ev(a['groupReview']['path'])];r['groupSeamPassedCandidateCount']=4
r['notes']+=a['limitations']

for r in rows:
    valid=[c for c in r['candidates'] if c['artifact'].get('is4096CandidateSize')]
    r['verifiedStoredCandidateCoordinates']=len({c['tile'] for c in valid})
    r['verifiedActiveCandidateCoordinates']=len({c['tile'] for c in valid if c['activeVersionConfirmed'] is True})
    r['activeRevisionUnknownCoordinates']=[c['tile'] for c in valid if c['activeVersionConfirmed']!='unknown' and c['activeVersionConfirmed'] is not True] + [c['tile'] for c in valid if c['activeVersionConfirmed']=='unknown']
    r['unverifiedArtifactReferences']=[c for c in r['candidates'] if not c['artifact'].get('is4096CandidateSize')]
    r['remainingWithoutConfirmedActiveCandidateRange']={'min':r['ownedTargetTiles']-r['verifiedStoredCandidateCoordinates'],'max':r['ownedTargetTiles']-r['verifiedActiveCandidateCoordinates'],'scope':'scoped listed artifacts at snapshot; excludes unlisted/ongoing worker outputs'}
summary=[]
for m,total in zip(MAPS,[256,196,196]):
    rr=[r for r in rows if r['map']==m]
    stored=sum(r['verifiedStoredCandidateCoordinates'] for r in rr);active=sum(r['verifiedActiveCandidateCoordinates'] for r in rr)
    summary.append({'map':m,'targetTiles':total,'effectiveOwnershipSum':sum(r['ownedTargetTiles'] for r in rr),'verifiedStored4096CandidateCoordinates':stored,'verifiedActive4096CandidateCoordinates':active,'activeRevisionUnknown':stored-active,'remainingWithoutConfirmedActiveCandidateRange':{'min':total-stored,'max':total-active},'wholeMapComplete':False,'formalAcceptedCountReported':sum(r['formalAcceptedCountReported'] for r in rr if isinstance(r['formalAcceptedCountReported'],int))})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'owner':'root coordinator','scope':'15 zone progress files and explicitly linked/current delivery artifacts only','method':{'workerFilesModified':False,'imageFilesModified':False,'gitOperationsPerformed':False,'historicalImageTreeCensus':False,'verification':'Referenced file existence and PNG IHDR dimensions. Small JSON evidence is hashed; huge PNGs are not hashed or decoded. No new independent visual seam review in this inventory. Worker review claims are attributed and never inferred from image counts.','unknownPolicy':'Missing/contradictory current-adoption or QA state remains unknown; never choose a revision by largest filename version.'},'mapSummary':summary,'totals':{'targetTiles':648,'verifiedStored4096CandidateCoordinates':sum(x['verifiedStored4096CandidateCoordinates'] for x in summary),'verifiedActive4096CandidateCoordinates':sum(x['verifiedActive4096CandidateCoordinates'] for x in summary),'formalAcceptedCountReported':0,'wholeMapsCompleted':0},'zones':rows,'limitations':['A 4096 PNG plus delivery pointer proves a candidate export, not aesthetic/seam acceptance or single-generation native 4K.','No runtime/capacity tests are part of this inventory. Art completion is not held on runtime testing.','Workers may advance after this snapshot. Counts describe these current records, not every historical file on disk.','All art, originals, previews and worker manifests were retained unchanged.']}
report['totals']['remainingWithoutConfirmedActiveCandidateRange']={'min':648-report['totals']['verifiedStored4096CandidateCoordinates'],'max':648-report['totals']['verifiedActive4096CandidateCoordinates']}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':pstr(OUT),'totals':report['totals'],'maps':summary,'referenceErrors':[{'map':r['map'],'zone':r['zone'],'references':r['unverifiedArtifactReferences']} for r in rows if r['unverifiedArtifactReferences']]},ensure_ascii=False,indent=2))
