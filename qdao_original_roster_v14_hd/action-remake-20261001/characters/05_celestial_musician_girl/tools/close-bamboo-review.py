"""Close the SHA-bound current-reference review after all visual reports exist."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent
REVIEW=ROOT/'provenance/bamboo-reference-20261003'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report_specs=[('combat-review.json','targetFrames','references'),('run-EW-review.json','rows','referenceRows'),('run-NS-review.json','rows','referenceRows'),('SE-NW-review.json','frames','referenceFrames'),('run-NE-SW-review.json','rows','referenceRows')]
current=load(ROOT/'final-selection.json')
key=lambda r:(r.get('action','run'),r['direction'],r['frame'])
current_map={key(r):r for r in current}
accept=load(REVIEW/'SE-repair-acceptance.json');assert accept['accepted'] is True
superseded=load(REVIEW/'SE-superseded-records.json')
old_map={key(r['selection']):r['selection'] for r in superseded['records']}
new_map={('run','SE',r['frame']):r for r in accept['frames']}
coverage={};references=[];reports=[]
for filename,target_key,reference_key in report_specs:
    report=load(REVIEW/filename)
    reports.append({'file':f'provenance/bamboo-reference-20261003/{filename}','sha256':sha(REVIEW/filename),'targetFrames':len(report[target_key])})
    for row in report[target_key]:
        k=key(row);assert k not in coverage
        final=current_map[k];assert sha(ROOT/final['file'])==final['sha256']
        if k in new_map:
            assert row['sha256']==old_map[k]['sha256']
            assert new_map[k]['sha256']==final['sha256'] and new_map[k]['nativeSha256']==final['nativeSha256']
            verdict='locally_repaired_and_reaccepted'
        else:
            assert row['sha256']==final['sha256'],k
            assert row.get('mandatoryCorrection',False) is False and row.get('requiredRepair',False) is False
            assert row.get('decision')!='must_correct'
            verdict='retained_after_current_reference_comparison'
        coverage[k]={'action':k[0],'direction':k[1],'frame':k[2],'file':final['file'],'sha256':final['sha256'],'decision':verdict,'reviewReport':filename}
    for row in report[reference_key]:
        file=row.get('sourcePath',row.get('path',row.get('file')));p=Path(file)
        assert p.is_file() and sha(p)==row['sha256'],file
        references.append({'action':row.get('action','run'),'direction':row['direction'],'frame':row['frame'],'file':str(p),'sha256':row['sha256']})
assert set(coverage)==set(current_map) and len(coverage)==196 and len(references)==196
timing=load(ROOT/'animation-timing.json');assert timing['run']['frameMs']==75 and timing['run']['cycleMs']==1200
now=datetime.now(timezone.utc).isoformat()
result={'completedAt':now,'status':'offline_bamboo_comparison_and_five_local_repairs_complete','reference':'09_bamboo_archer_girl current manifest referenced images, explicitly user-approved','targetFrames':196,'retainedUnchanged':191,'locallyRepaired':5,'mandatoryRepairsRemaining':0,'reports':reports,'frames':list(coverage.values()),'referenceFrames':references,'referencePixelsStillMatchAllReviewSnapshots':True,'currentRunTiming':timing['run'],'singleCycleVerification':'provenance/run/timing-1200-checks.json','browserVerification':'provenance/run/timing-1200-browser.json','latestSEBrowserVerification':'provenance/bamboo-reference-20261003/SE-repaired-browser.json','clientIntegrated':False,'clientRuntimeValidated':False,'historicalAcceptanceNote':'Earlier offline acceptance/static reports refer to their recorded PNG hashes. Five SE slots are superseded by the new repair acceptance; earlier timing comparisons are historical and current timing is 1200ms.'}
assert (REVIEW/'SE-repaired-browser.json').is_file()
save(REVIEW/'closeout.json',result)
status=load(ROOT/'STATUS.json');status.update(updatedAt=now,status='offline_artwork_complete_client_pending',finalVisualPassed=196,latestReferenceReview='provenance/bamboo-reference-20261003/closeout.json',latestLocalRepairCount=5,nativeSourcesRetained=False)
status['remaining']['run']=0;status['sequences']['run/SE']['visualPassed']=True;status.pop('pendingLocalRepairs',None)
status['newSuccessfulGeneratedImages']=294;status['supersededNewImages']=101
save(ROOT/'STATUS.json',status)
manifest=load(ROOT/'final/manifest.json');manifest['latestReferenceReview']='provenance/bamboo-reference-20261003/closeout.json';save(ROOT/'final/manifest.json',manifest)
for name in ['README.md','MERGE_HANDOFF.md']:
    p=ROOT/name;text=p.read_text(encoding='utf-8-sig')
    note='\n2026-10-03 竹弓当前版对照收尾：196帧均已按同向实图复核，191帧保留，东南跑步01/02/03/12/13局部重修近右靴鞋尖方向，持琴手臂和原动作相位保留。跑步统一16×75ms＝1200ms；正常播放、单圈停止与首尾衔接已检查。详见[本轮验收](provenance/bamboo-reference-20261003/closeout.json)与[五帧修复验收](provenance/bamboo-reference-20261003/SE-repair-acceptance.json)。旧离线验收和选表保留其历史SHA，本轮五帧以新记录为准。客户端仍未接入实测。\n'
    assert '竹弓当前版对照收尾' not in text
    p.write_text(text.rstrip()+'\n'+note,encoding='utf-8')
print(json.dumps({'reviewed':196,'retained':191,'repaired':5,'remaining':0,'runCycleMs':1200},ensure_ascii=False))
