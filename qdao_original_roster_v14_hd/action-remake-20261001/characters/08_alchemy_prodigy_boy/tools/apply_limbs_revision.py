"""One-shot export of reviewed limb edits; preserve all slots and timing.

All source pixels are staged before any output changes. The original 16/01
contact pair crosses the loop boundary correctly and is intentionally retained.
"""
from pathlib import Path
from PIL import Image
import copy, datetime, hashlib, io, json, sys

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'provenance/limbs-20261004'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, x: p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()
manifest = read(ROOT/'manifest.json')
baseline = read(BATCH/'before-manifest.json')
assert manifest == baseline, 'Runtime manifest changed since the review snapshot'
assert sha(ROOT/'run-timing.json') == sha(BATCH/'before-run-timing.json')
before = {f['slot']: f for f in baseline['frames']}
assert len(before) == 196
selection = {}
for name in ['north', 'south', 'combat', 'feet', 'foot14', 'foot15']:
    chosen = read(BATCH/f'{name}-selection.json')
    assert not set(chosen).intersection(selection), name
    selection.update(chosen)
staged = {}
for slot, frame in before.items():
    data = (ROOT/frame['file']).read_bytes()
    assert digest(data) == frame['sha256'], slot
    staged[slot] = (copy.deepcopy(frame), data)
for slot, chosen in selection.items():
    assert slot in before and chosen['staticReviewed'] is True
    source = (ROOT/chosen['source']).resolve()
    assert source.is_relative_to((ROOT/'generation/limbs-20261004').resolve())
    record_path = Path(str(source)+'.generation.json')
    record = read(record_path)
    assert record['sha256'] == sha(source)
    assert record['actualModel'] is None and record['actualQuality'] is None
    assert (ROOT/record['prompt']).is_file()
    with Image.open(source) as im:
        assert im.mode == 'RGBA' and im.width == im.height and im.width >= 1024
        assert im.getchannel('A').getextrema() == (0,255)
        native = list(im.size)
        output = io.BytesIO()
        im.resize((1024,1024), Image.Resampling.LANCZOS).save(output, format='PNG')
        data = output.getvalue()
    frame = copy.deepcopy(before[slot])
    frame.update({
        'sha256': digest(data),
        'derivedFrom': {'file': chosen['source'], 'sha256': sha(source), 'nativeSize': native,
            'generationRecord': record_path.relative_to(ROOT).as_posix(), 'generationRecordSha256': sha(record_path)},
        'editInput': {'file': before[slot]['file'], 'sha256': before[slot]['sha256'],
            'historicalManifest': 'provenance/limbs-20261004/before-manifest.json',
            'historicalManifestSha256': sha(BATCH/'before-manifest.json')},
        'operation': {'type': 'fixed_whole_canvas_resample_of_registered_runtime_edit',
            'sourceCanvasToPx': [1024,1024], 'offsetPx': [0,0], 'canvas': [1024,1024],
            'rootPx': [512,942], 'perFrameBoundingBoxFit': False, 'footPixelAlignment': False},
        'status': 'limbs_repaired', 'staticPoseReviewed': True, 'visualAccepted': True,
        'visualAcceptanceScope': 'static_pose', 'dynamicAccepted': False, 'clientIntegrated': False,
        'limbsRevision': {'date': '2026-10-05', 'reason': chosen['reason'], 'originalInputSlot': slot}
    })
    staged[slot] = (frame, data)

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
final = staged
published = {slot:{**chosen, 'originalInputSlot':slot, 'finalSlot':slot,
    'finalSha256':final[slot][0]['sha256'],
    'editInputSnapshot':'provenance/limbs-20261004/before-manifest.json'} for slot,chosen in selection.items()}
assert len(final) == 196
assert len({f['sha256'] for f,_ in final.values()}) == 196
assert len({f['derivedFrom']['sha256'] for f,_ in final.values()}) == 196
if '--apply' not in sys.argv:
    print(json.dumps({'ready':True,'edited':len(selection),'frameOrderChanged':False,'finalSlots':sorted(published)}))
    raise SystemExit(0)

write(ROOT/'limbs-selection.json',published)
manifest['frames'] = [final[f['slot']][0] for f in baseline['frames']]
manifest['updatedAt'] = now
manifest['limbsRevision'] = {'selection':'limbs-selection.json','replacedFrames':len(selection),
    'frameOrderChanged':False,'status':'exported_pending_sequence_review',
    'durationChanged':False,'clientValidated':False,
    'phaseNote':'Keep original contact pairs 16/01,02/03,...,14/15; 07/08 is the half-cycle support-foot change.'}
manifest['deliveryStatus'] = 'limbs_revision_exported_pending_preview'
for frame,data in final.values():
    if frame['slot'] not in selection:
        continue
    dest = ROOT/frame['file']
    dest.write_bytes(data)
    write(Path(str(dest)+'.generation.json'),frame)
write(ROOT/'manifest.json',manifest)
print(json.dumps({'exported':len(selection),'frameOrderChanged':False,'total':len(final),'canvas':[1024,1024]}))
