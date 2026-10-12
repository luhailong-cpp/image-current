"""Assemble explicit root-approved native candidates; never mutate runtime."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
B=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(B/'review/full-body-root-static-review-20261005.json')
assert r['status']=='passed' and not r['pending'], 'Static review still pending'
history=B/'provenance/full-body-revision-20261005/manifest-before.json'
m=read(B/'manifest.json');baseline=read(history)
rows={f['slot']:f for s in m['sequences'] for f in s['frames']}
baseline_rows={f['slot']:f for s in baseline['sequences'] for f in s['frames']}
already_revised=set(m.get('fullBodyRevision',{}).get('changedSlots',[]))
assert all(f['sha256']==baseline_rows[slot]['sha256'] for slot,f in rows.items() if slot not in already_revised), 'Untargeted images changed since baseline'
assert m['timingRevision']['frameMs']==60 and m['timingRevision']['cycleMs']==960
choices=[]
for slot,c in r['approvedCandidates'].items():
    source=B/'staging'/f"{c['key']}.png"
    rec=source.with_suffix('.png.generation.json')
    record=read(rec)
    assert digest(source)==record['sha256']
    assert rows[slot]['sha256']==digest(B/rows[slot]['file'])
    choices.append({'slot':slot,'key':c['key'],'beforeRuntimeSha256':rows[slot]['sha256'],
        'originalRuntimeSha256':baseline_rows[slot]['sha256'],
        'sourceSha256':digest(source),'sourceGenerationRecordSha256':digest(rec),
        'staticObservation':c['observation']})
out={'status':'selected_for_runtime_playback','selectedAt':datetime.now(timezone.utc).isoformat(),
     'beforeManifestSha256':digest(B/'manifest.json'),'baselineManifestSha256':digest(history),'rootStaticReview':{'file':'review/full-body-root-static-review-20261005.json','sha256':digest(B/'review/full-body-root-static-review-20261005.json')},
     'replacements':choices}
(B/'review/full-body-selected-20261005.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(choices),'slots':[c['slot'] for c in choices]}))
