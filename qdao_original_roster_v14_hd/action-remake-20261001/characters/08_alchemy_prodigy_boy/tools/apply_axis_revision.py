"""Export individually reviewed shoe-axis edits without pose alignment.

Sources are work-in-progress until all three review selections are present.
Use --apply once; cleanup later removes native sources, not their text records.
"""
from pathlib import Path
from PIL import Image
import datetime, hashlib, io, json, sys

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'provenance/axis-20261004'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, x: p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = read(ROOT / 'manifest.json')
baseline = read(BATCH / 'before-manifest.json')
frames = {f['slot']: f for f in manifest['frames']}
old_frames = {f['slot']: f for f in baseline['frames']}
selection = {}
for name in ['north', 'south', 'west']:
    chosen = read(BATCH / f'{name}-selection.json')
    assert not set(chosen).intersection(selection), name
    selection.update(chosen)
assert selection and len(frames) == 196
assert sha(ROOT/'run-timing.json') == sha(BATCH/'before-run-timing.json')
for slot, f in frames.items():
    assert sha(ROOT/f['file']) == f['sha256'] == old_frames[slot]['sha256'], slot
staged = []
for slot, chosen in sorted(selection.items()):
    assert slot.startswith('run/') and chosen['staticReviewed'] is True
    chosen['editInputSnapshot'] = 'provenance/axis-20261004/before-manifest.json'
    source = (ROOT/chosen['source']).resolve()
    assert source.is_relative_to(ROOT/'generation/axis-20261004')
    rec_path = Path(str(source)+'.generation.json')
    rec = read(rec_path)
    assert rec['sha256'] == sha(source)
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert rec['submittedParameters']['model'] is None
    assert rec['submittedParameters']['quality'] is None
    assert (ROOT/rec['prompt']).is_file()
    with Image.open(source) as im:
        assert im.mode == 'RGBA' and im.width == im.height and im.width >= 1024
        assert im.getchannel('A').getextrema() == (0,255)
        native = list(im.size)
        out = im.resize((1024,1024), Image.Resampling.LANCZOS)
        buffer = io.BytesIO(); out.save(buffer,format='PNG'); data = buffer.getvalue()
    f = dict(frames[slot])
    f.update({
        'sha256': hashlib.sha256(data).hexdigest(),
        'derivedFrom': {'file': chosen['source'], 'sha256': sha(source), 'nativeSize': native,
            'generationRecord': rec_path.relative_to(ROOT).as_posix(), 'generationRecordSha256': sha(rec_path)},
        'editInput': {'file': old_frames[slot]['file'], 'sha256': old_frames[slot]['sha256'],
            'historicalManifest': chosen['editInputSnapshot'], 'historicalManifestSha256': sha(BATCH/'before-manifest.json')},
        'operation': {'type': 'fixed_whole_canvas_resample_of_registered_runtime_edit',
            'sourceCanvasToPx': [1024,1024], 'offsetPx': [0,0], 'canvas': [1024,1024],
            'rootPx': [512,942], 'perFrameBoundingBoxFit': False, 'footPixelAlignment': False},
        'status': 'shoe_axis_repaired', 'staticPoseReviewed': True,
        'visualAccepted': True, 'visualAcceptanceScope': 'static_pose',
        'dynamicAccepted': False, 'clientIntegrated': False,
        'axisRevision': {'date': '2026-10-04', 'reason': chosen['reason']}
    })
    staged.append((f,data))
assert len({f['sha256'] for f,_ in staged}) == len(staged)
if '--apply' not in sys.argv:
    print(json.dumps({'ready':True,'selected':len(staged),'slots':sorted(selection)}))
    raise SystemExit(0)
write(ROOT/'axis-selection.json', selection)
for f,data in staged:
    dest = ROOT/f['file']; dest.write_bytes(data)
    write(Path(str(dest)+'.generation.json'),f)
    frames[f['slot']] = f
manifest['frames'] = [frames[f['slot']] for f in manifest['frames']]
manifest['updatedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest['axisRevision'] = {'selection':'axis-selection.json','replacedFrames':len(staged),
    'status':'exported_pending_sequence_review','referenceVideo':'provenance/axis-20261004/video-source.json',
    'timingChanged':False,'clientValidated':False}
manifest['deliveryStatus'] = 'axis_revision_exported_pending_preview'
write(ROOT/'manifest.json',manifest)
print(json.dumps({'exported':len(staged),'total':len(frames),'canvas':[1024,1024]}))
