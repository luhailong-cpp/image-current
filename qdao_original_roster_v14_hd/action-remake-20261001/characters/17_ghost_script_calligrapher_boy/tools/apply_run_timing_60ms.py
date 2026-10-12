"""Apply latest explicit user timing correction, preserving every PNG byte."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(B/'manifest.json');previous=sha(B/'manifest.json')
baseline=B/'provenance/full-body-revision-20261005/manifest-before.json'
assert previous==sha(baseline), 'Timing migration expects unchanged baseline'
pngs={f['file']:sha(B/f['file']) for s in m['sequences'] for f in s['frames']}
for s in m['sequences']:
    if s['action']!='run':continue
    assert s['count']==16 and s['ms']==75 and s['cycleMs']==1200
    s['ms']=60;s['cycleMs']=960
    for f in s['frames']:f['durationMs']=60
m['timingRevision']={'updatedAt':datetime.now(timezone.utc).isoformat(),
    'authority':'User explicitly corrected this chat: 不是已经改成60ms 一帧了吗',
    'action':'run','directions':['N','NE','E','SE','S','SW','W','NW'],
    'previousFrameMs':75,'frameMs':60,'frameCount':16,'cycleMs':960,
    'previousManifestSha256':previous,'imagePixelsChanged':False,'combatTimingChanged':False}
m['status']='needs_review';m['counts']['dynamicPassedSequences']=6
m['acceptance']={'file':None,'sha256':None,'record':{'status':'needs_review','reason':'Full-body image repairs and 60ms run timing require renewed playback'}}
write(B/'manifest.json',m)
req=read(B/'review/contact-pairs-current-20261004.json')
req['frameMs']=60;req['cycleMs']=960;req['pairMs']=120;req['timingAuthority']=m['timingRevision']['authority']
req['status']='images_under_revision_and_60ms_playback_pending';write(B/'review/contact-pairs-current-20261004.json',req)
state=read(B/'review/full-body-revision-state-20261005.json')
state['timingUnchanged']=False;state['runTiming']={'frameMs':60,'cycleMs':960,'frameCount':16,'authority':m['timingRevision']['authority']}
write(B/'review/full-body-revision-state-20261005.json',state)
for name in ['build_run_gif_preview.py','verify_final_package.py','plan_final_cleanup.py','finalize_review.py','export_review_runtime.py']:
    p=B/'tools'/name;s=p.read_text(encoding='utf-8')
    s=s.replace('1200ms','960ms').replace('1200','960').replace('75ms','60ms').replace('75 ms','60 ms')
    if name=='build_run_gif_preview.py':s=s.replace('duration=75','duration=60').replace('[75]*16','[60]*16')
    if name in ['verify_final_package.py','plan_final_cleanup.py','export_review_runtime.py']:s=s.replace('16,75','16,60').replace('16, 75','16, 60')
    p.write_text(s,encoding='utf-8')
for name in ['build_delivery_preview.py','package_delivery.py','execute_final_cleanup.ps1']:
    p=B/'tools'/name;s=p.read_text(encoding='utf-8').replace('run-current-1200ms','run-current-960ms');p.write_text(s,encoding='utf-8')
for name in ['DELIVERY.md','STATUS.md','MERGE_HANDOFF.md','preview/README.md']:
    p=B/name;s=p.read_text(encoding='utf-8').replace('1200ms','960ms').replace('75ms','60ms').replace('75 ms','60 ms')
    p.write_text(s,encoding='utf-8')
assert all(sha(B/p)==h for p,h in pngs.items())
write(B/'review/run-timing-60ms-20261005.json',{'status':'metadata_applied_playback_pending','runTiming':m['timingRevision'],'runtimeFrameSha256':pngs})
print(json.dumps({'status':'metadata_applied_playback_pending','frameMs':60,'cycleMs':960,'pngsUnchanged':len(pngs)}))
