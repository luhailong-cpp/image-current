"""Prepare a text-only final retention plan; deletion is a separate reviewed apply."""
from pathlib import Path
import json
from datetime import datetime, timezone
import cleanup_generation as cleanup

B = cleanup.BASE
overview = json.loads((B/'review/all-actions-selection.json').read_text(encoding='utf-8-sig'))
assert overview['selectedExported'] == 196
selected = {cleanup.absolute(B/f['source']).as_posix() for g in overview['groups'] for f in g['frames']}
inventory = {p.as_posix() for p in cleanup.walk_files(B/'generation') if p.suffix.lower()=='.png'}
keep = sorted(inventory & selected)
retire = sorted(inventory - selected)
assert len(keep)==195 and len(retire)==285, (len(keep), len(retire))
plan, snapshots = cleanup.build_plan('all-sources', keep, retire)
assert {x['path'] for x in plan['delete']} == set(retire)
assert {x['path'] for x in plan['keep']} == set(keep)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
freeze = cleanup.review_output('review/final-export-freeze-'+stamp+'.json')
cleanup.seal(plan, snapshots, freeze)
plan['freezeFile'] = freeze.as_posix()
plan['freezeSha256'] = cleanup.sha(freeze)
plan['retentionDecision'] = 'All 196 final slots are populated and browser-verified. Keep selected native design masters and exports. Retire all unselected attempts and ancestors; retain their text provenance and SHA without image backups.'
output = cleanup.review_output('review/cleanup-plan-final-'+stamp+'.json')
cleanup.write_new(output, plan)
print(json.dumps({'plan':output.as_posix(),'freeze':freeze.as_posix(),'dryRun':True,'deleted':0,**plan['counts']}))
