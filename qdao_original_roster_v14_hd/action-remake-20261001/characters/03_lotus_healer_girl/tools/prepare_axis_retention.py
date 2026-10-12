"""Prepare retention after the video-axis revision is actually exported and reviewed."""
import json
from datetime import datetime,timezone
import cleanup_generation as cleanup
B=cleanup.BASE
decision=cleanup.read(B/'review/axis-revision-decisions-20261004.json')
assert decision['status']=='verified_ready_for_retention'
overview=cleanup.read(B/'review/all-actions-selection.json')
assert overview['selectedExported']==196
selected={cleanup.absolute(B/f['source']).as_posix() for g in overview['groups'] for f in g['frames']}
inventory={p.as_posix() for p in cleanup.walk_files(B/'generation') if p.suffix.lower()=='.png'}
keep=sorted(inventory & selected); retire=sorted(inventory-selected)
assert len(keep)==195
plan,snapshots=cleanup.build_plan('all-sources',keep,retire)
assert {x['path'] for x in plan['delete']}==set(retire)
assert {x['path'] for x in plan['keep']}==set(keep)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
freeze=cleanup.review_output('review/axis-export-freeze-'+stamp+'.json')
cleanup.seal(plan,snapshots,freeze)
plan['freezeFile']=freeze.as_posix(); plan['freezeSha256']=cleanup.sha(freeze)
plan['retentionDecision']='Video-axis revision completed: preserve all selected native design masters and 196 full-canvas exports; retire superseded source images and rejected attempts, retaining text provenance.'
output=cleanup.review_output('review/cleanup-plan-axis-'+stamp+'.json')
cleanup.write_new(output,plan)
print(json.dumps({'plan':output.as_posix(),'freeze':freeze.as_posix(),'dryRun':True,'deleted':0,**plan['counts']}))
