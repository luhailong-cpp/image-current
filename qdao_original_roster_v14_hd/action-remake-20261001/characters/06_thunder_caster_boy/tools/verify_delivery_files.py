"""Final read-only verification of current preview sources, durations and handoff references."""
from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
status=json.loads((R/'STATUS.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((R/'preview/manifest.json').read_text(encoding='utf-8-sig'))
errors=[];checked=[]
timing=json.loads((R/'animation-timing.json').read_text(encoding='utf-8-sig'))['run']
if timing['frameMs']!=60 or timing['cycleMs']!=960 or timing['durationsMs']!=[60]*16:errors.append('run timing config')
for seq in manifest['sequences']:
    if seq['action']=='run' and (seq['duration_ms']!=60 or seq['cycle_ms']!=960):errors.append(seq['id']+' not 60ms')
    if seq['missing']:errors.append(seq['id']+' missing')
    for f in seq['frames']:
        if sha(R/f['path'])!=f['sha256']:errors.append(f['path']+' SHA')
    for label,factor in [('normal',1),('slow',4)]:
        p=R/f"preview/{seq['action']}_{seq['direction']}_{label}.webp"
        with Image.open(p) as im:
            durations=[]
            for i in range(im.n_frames):im.seek(i);im.load();durations.append(im.info.get('duration'))
            if len(durations)!=seq['expected_count'] or durations!=[seq['duration_ms']*factor]*seq['expected_count']:errors.append(p.name+' timing')
        checked.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'frameCount':len(durations),'durationMs':durations,'cycleMs':sum(durations)})
for cycle in [960,3840]:
    p=R/f'preview/run-eight-directions-{cycle}.webp';g=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
    if sha(p)!=g['sha256'] or any(sha(R/f['file'])!=f['sha256'] for f in g['derivedFrom']):errors.append(p.name+' source')
    with Image.open(p) as im:
        ds=[]
        for n in range(im.n_frames):im.seek(n);im.load();ds.append(im.info['duration'])
    if ds!=[cycle//16]*16:errors.append(p.name+' timing')
for match in re.finditer(r'\]\(([^)]+)\)',(R/'MERGE_HANDOFF.md').read_text(encoding='utf-8')):
    rel=match.group(1)
    if not rel.startswith(('http:','https:')) and not (R/rel).exists():errors.append('handoff link '+rel)
if not status['complete']:errors.append('local status incomplete')
if len(status['files'])!=196 or any(sha(R/f['path'])!=f['sha256'] for f in status['files']):errors.append('status source mismatch')
if len(status['events']['run']['currentFramePositionObservations'])!=128:errors.append('position observations incomplete')
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':not errors,'errors':errors,'runtimeFrames':196,'sequencePreviews':checked,'runFrameMs':60,'runCycleMs':960,'clientIntegrated':False}
(R/'review/delivery_verification_20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':not errors,'errors':errors,'sequencePreviews':len(checked),'runtimeFrames':196}))
raise SystemExit(bool(errors))
