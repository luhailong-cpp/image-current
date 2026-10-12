"""Promote only reviewed foot-axis repairs; preserve all other final image bytes."""
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
import hashlib, importlib.util, json, sys

ROOT=Path(__file__).resolve().parent.parent
EV='provenance/foot-axis-20261004'
spec=importlib.util.spec_from_file_location('position_promotion',ROOT/'tools/promote-position-run.py')
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(data):return hashlib.sha256(data).hexdigest()
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def check():
    baseline=load(EV+'/baseline.json')['files'];original={p:(ROOT/p).read_bytes() for p in baseline}
    for p,b in original.items():assert sha(b)==baseline[p],f'Baseline changed: {p}'
    a=load(EV+'/acceptance.json');assert a['accepted'] and a['clientValidated'] is False
    assert not a['mandatoryCorrectionsRemaining']
    assert sha((ROOT/(EV+'/baseline.json')).read_bytes())==a['baselineSha256']
    assert sha((ROOT/(EV+'/root-review.json')).read_bytes())==a['rootReviewSha256']
    for audit in a['audits']:assert sha(common.inside(audit['file']).read_bytes())==audit['sha256']
    oldrows=load('final-selection.json');rows=deepcopy(oldrows);by={(r['action'],r['direction'],r['frame']):r for r in rows}
    reg=load('registration.json');writes={};history=[];seen=set()
    for item in a['repairs']:
        action=item['action'];d,f=item['direction'],item['frame'];key=(action,d,f);assert key not in seen;seen.add(key)
        assert action in ['run','hit','attack','cast']
        row=by[key];p=common.inside(item['reviewFile'])
        stageRoot=ROOT/'staging/foot-axis-20261004'
        assert p.is_relative_to((stageRoot/d if action=='run' else stageRoot/action/d).resolve())
        data=p.read_bytes();meta=load(item['reviewFile']+'.generation.json')
        assert meta['file']==item['reviewFile']
        assert sha(data)==item['sha256']==meta['sha256']
        assert row['sha256']==item['previousSha256']
        assert meta['sourceGeneration']['editTargetFormalFile']==row['file']
        assert meta['sourceGeneration']['editTargetFormalSha256']==item['previousSha256']
        assert meta['source']['sha256']==item['nativeSha256']==meta['sourceGeneration']['sha256']
        assert sha(common.inside(meta['source']['file']).read_bytes())==item['nativeSha256']
        common.safe_png_check(data,item['reviewFile'])
        assert meta['transform']['globalScale']==reg['globalScale']==.65
        assert meta['transform']['sourceRoot']==reg['sequences'][action+'/'+d]['sourceRoot']
        assert meta['transform']['targetRoot']==reg['targetRoot']==[512,942]
        assert meta['transform']['perFrameNormalization'] is False
        if action=='run':
            assert meta['supportLeg']==('RIGHT' if f<=8 else 'LEFT')
            assert meta['stancePosition']==row['stancePosition']
        history.append({'row':deepcopy(row),'generationRecord':load(row['generationRecord'])})
        meta.update(file=row['file'],status='offline_artwork_accepted_client_pending',finalVisualPassed=True,clientValidated=False,offlineAcceptance=EV+'/acceptance.json',footAxisReview=item['visualReview'],sourceRetention='Remove intermediate/native image after final references verified; preserve text provenance.')
        row.update(sha256=meta['sha256'],nativeSourceFile=meta['source']['file'],nativeSha256=meta['source']['sha256'],finalVisualPassed=True,clientValidated=False,visualStatus=item['visualReview']['notes'])
        writes[row['file']]=data;writes[row['generationRecord']]=encode(meta)
    assert len({r['sha256'] for r in rows})==len({r['nativeSha256'] for r in rows})==196
    for row in rows:
        if (row['action'],row['direction'],row['frame']) not in seen:assert row==next(r for r in oldrows if r['file']==row['file'])
    manifest=load('final/manifest.json');manifest.update(frames=rows,artworkUpdatedAt=datetime.now(timezone.utc).isoformat(),latestVisualAcceptance=EV+'/acceptance.json',latestFootAxisSelection=EV+'/acceptance.json',status='offline_artwork_complete_client_pending')
    writes['final-selection.json']=encode(rows);writes['final/manifest.json']=encode(manifest)
    return {'acceptance':a,'original':original,'writes':writes,'history':history,'rows':rows}
def main():
    state=check();count=len(state['acceptance']['repairs'])
    runCount=sum(r['action']=='run' for r in state['acceptance']['repairs']);combatCount=count-runCount
    if '--check' in sys.argv:print(json.dumps({'status':'check_passed','repairs':count,'retainedRunFrames':128-runCount,'unchangedCombatFrames':68-combatCount,'uniqueFinalFrames':196}));return
    assert '--promote' in sys.argv
    reportPath=EV+'/promotion.json';historyPath=EV+'/superseded-text-records.json'
    assert not (ROOT/reportPath).exists() and not (ROOT/historyPath).exists()
    for p,b in state['original'].items():assert (ROOT/p).read_bytes()==b,f'Preimage changed: {p}'
    common.atomic_write(historyPath,encode({'savedAt':datetime.now(timezone.utc).isoformat(),'records':state['history'],'imageBackupsCreated':False}))
    report={'status':'in_progress','startedAt':datetime.now(timezone.utc).isoformat(),'repairs':count,'repairedRunFrames':runCount,'repairedCombatFrames':combatCount,'retainedRunFrames':128-runCount,'combatFramesUntouched':68-combatCount,'clientValidated':False}
    common.atomic_write(reportPath,encode(report));written=[]
    try:
        for p,b in state['writes'].items():common.atomic_write(p,b);written.append(p)
        for p,b in state['original'].items():assert (ROOT/p).read_bytes()==state['writes'].get(p,b),f'Unexpected final bytes: {p}'
        report.update(status='complete',completedAt=datetime.now(timezone.utc).isoformat(),finalSelectionSha256=sha(state['writes']['final-selection.json']),finalManifestSha256=sha(state['writes']['final/manifest.json']),registrationUnchanged=True,timingUnchanged=True)
        common.atomic_write(reportPath,encode(report));print(json.dumps(report))
    except Exception as exc:
        failures=[]
        for p in reversed(written):
            try:common.atomic_write(p,state['original'][p])
            except Exception as err:failures.append(str(err))
        report.update(status='failed_rollback_incomplete' if failures else 'failed_rolled_back',error=str(exc),rollbackErrors=failures)
        common.atomic_write(reportPath,encode(report));raise
if __name__=='__main__':main()
