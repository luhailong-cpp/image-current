"""Apply the human user's latest 60ms correction, preserving poses and combat."""
from pathlib import Path
import copy, datetime, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'provenance/limbs-20261004'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(ROOT/'manifest.json')
timing=read(ROOT/'run-timing.json')
old_timing=copy.deepcopy(timing)
old_timing_sha=sha(ROOT/'run-timing.json')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
timing.update({'version':4,'updatedAt':now,'normalCycleMs':960,
    'basis':'Latest human correction: 16 distinct run frames at uniform 60ms; retain existing contact-pair order.',
    'latestHumanTimingCorrection':{'date':'2026-10-05','message':'不是已经改成60ms 一帧了吗','previousFrameMs':75,'frameMs':60}})
for p in timing['directions'].values():
    assert p['frameMs']==[75]*16
    p['frameMs']=[60]*16
    p['positionPairMs']=120
write(ROOT/'run-timing.json',timing)
manifest['timing']['run'].update({'previewDefaultCycleMs':960,'previewFrameMs':[60]*16,
    'directions':copy.deepcopy(timing['directions'])})
for frame in manifest['frames']:
    if frame['slot'].startswith('run/'):
        frame['previewDurationMs']=60
        write(ROOT/(frame['file']+'.generation.json'),frame)
manifest['limbsRevision'].update({'durationChanged':True,'uniformRunFrameMs':60,
    'normalRunCycleMs':960,'timingCorrection':'provenance/limbs-20261004/timing-correction.json'})
manifest['updatedAt']=now
write(ROOT/'manifest.json',manifest)
plan=read(BATCH/'plan.json')
plan['timing'].update({'runFrameMs':60,'runCycleMs':960,'positionPairMs':120,'combatChanged':False})
plan['latestHumanTimingCorrection']='2026-10-05: latest user correction overrides previous 75ms. Frame order and contact pairs remain unchanged.'
write(BATCH/'plan.json',plan)
write(BATCH/'timing-correction.json',{'appliedAt':now,'source':'Latest direct human message in this chat',
    'message':'不是已经改成60ms 一帧了吗','beforeTimingSha256':old_timing_sha,
    'afterTimingSha256':sha(ROOT/'run-timing.json'),'beforeFrameMs':75,'afterFrameMs':60,
    'beforeCycleMs':1200,'afterCycleMs':960,'positionPairMs':120,
    'scope':'Eight run directions only; combat timings and all PNG bytes unchanged',
    'contactPairsUnchanged':timing['contactPairPlan']==old_timing['contactPairPlan']})
print(json.dumps({'runDirections':8,'frameMs':60,'cycleMs':960,'combatChanged':False}))
