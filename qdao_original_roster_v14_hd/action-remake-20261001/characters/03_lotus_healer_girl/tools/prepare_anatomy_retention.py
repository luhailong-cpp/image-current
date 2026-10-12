"""Seal completed anatomy revision, preserving every current native design master."""
import json
from datetime import datetime,timezone
import cleanup_generation as cleanup
B=cleanup.BASE
decision=cleanup.read(B/'review/anatomy-revision-decisions-20261005.json')
assert decision['status']=='verified_ready_for_retention'
overview=cleanup.read(B/'review/all-actions-selection.json')
assert overview['selectedExported']==196
selected={cleanup.absolute(B/f['source']).as_posix() for g in overview['groups'] for f in g['frames']}
inventory={p.as_posix() for p in cleanup.walk_files(B/'generation') if p.suffix.lower()=='.png'}
keep=sorted(inventory & selected); retire=sorted(inventory-selected)
assert len(keep)==195
reviewed_retire={(B/p).resolve().as_posix() for p in decision['retiredSources']}
assert set(retire)==reviewed_retire, ('Unreviewed image in retention set',set(retire)^reviewed_retire)
plan,snapshots=cleanup.build_plan('all-sources',keep,retire)
assert {x['path'] for x in plan['delete']}==set(retire)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
freeze=cleanup.review_output('review/anatomy-export-freeze-'+stamp+'.json')
cleanup.seal(plan,snapshots,freeze)
plan['freezeFile']=freeze.as_posix(); plan['freezeSha256']=cleanup.sha(freeze)
plan['retentionDecision']='Anatomy revision exported and verified; keep 195 current native design masters and 196 exports; remove only reviewed superseded/rejected images, preserving all text provenance.'
output=cleanup.review_output('review/cleanup-plan-anatomy-'+stamp+'.json')
cleanup.write_new(output,plan)
print(json.dumps({'plan':output.as_posix(),'freeze':freeze.as_posix(),'dryRun':True,**plan['counts']}))
