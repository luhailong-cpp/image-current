"""Export reviewed native edits at fixed canvas scale and close their provenance.

Usage: python tools/apply_contact_pairs.py [--apply]
Only selected, statically reviewed frames are replaced. Existing unrelated frames
are checked against the manifest before any writes. No pose or pixel alignment.
"""
from pathlib import Path
from PIL import Image
import hashlib, json, datetime, sys, io

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, x: p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
selection = json.loads((ROOT/'contact-pairs-selection.json').read_text(encoding='utf-8'))
frames = {f['slot']:f for f in manifest['frames']}
assert len(frames) == 196 and selection
assert all(sha(ROOT/f['file']) == f['sha256'] for f in frames.values())
staged = []
for slot, chosen in selection.items():
    assert slot in frames and slot.startswith('run/')
    assert chosen['staticReviewed'] is True
    src = (ROOT/chosen['source']).resolve()
    assert src.is_relative_to(ROOT/'generation') and src.suffix == '.png'
    rec_path = Path(str(src)+'.generation.json')
    rec = json.loads(rec_path.read_text(encoding='utf-8'))
    assert sha(src) == rec['sha256']
    with Image.open(src) as im:
        assert im.mode == 'RGBA' and im.width == im.height and im.width >= 1024
        assert im.getchannel('A').getextrema() == (0,255)
        native = list(im.size)
        out = im.resize((1024,1024), Image.Resampling.LANCZOS)
        blob = io.BytesIO(); out.save(blob, format='PNG'); data = blob.getvalue()
    baseline_path = ROOT/chosen['editInputSnapshot']
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    old = next(f for f in baseline['frames'] if f['slot'] == slot)
    f = dict(frames[slot])
    f.update({
        'sha256':hashlib.sha256(data).hexdigest(),
        'derivedFrom':{'file':chosen['source'],'sha256':sha(src),'nativeSize':native,
            'generationRecord':rec_path.relative_to(ROOT).as_posix(),
            'generationRecordSha256':sha(rec_path)},
        'editInput':{'file':old['file'],'sha256':old['sha256'],
            'historicalManifest':chosen['editInputSnapshot'],
            'historicalManifestSha256':sha(baseline_path)},
        'operation':{'type':'fixed_whole_canvas_resample_of_registered_runtime_edit',
            'sourceCanvasToPx':[1024,1024],'offsetPx':[0,0],'canvas':[1024,1024],
            'rootPx':[512,942],'perFrameBoundingBoxFit':False,'footPixelAlignment':False},
        'status':'contact_pairs_pose_repaired','staticPoseReviewed':True,
        'visualAccepted':True,'visualAcceptanceScope':'static_pose',
        'dynamicAccepted':False,'clientIntegrated':False,
        'contactPairsRevision':{'date':'2026-10-04','reason':chosen['reason']}
    })
    staged.append((f,data))
assert len({f['derivedFrom']['sha256'] for f,_ in staged}) == len(staged)
if '--apply' not in sys.argv:
    print(json.dumps({'ready':True,'selected':len(staged),'runtimeWritten':False}))
    raise SystemExit(0)
for f,data in staged:
    path = ROOT/f['file']; path.write_bytes(data)
    write(Path(str(path)+'.generation.json'), f)
    frames[f['slot']] = f
manifest['frames'] = [frames[f['slot']] for f in manifest['frames']]
manifest['updatedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest['contactPairsRevision'] = {'selection':'contact-pairs-selection.json',
    'replacedFrames':len(staged),'status':'exported_pending_sequence_review',
    'plan':'provenance/contact-pairs-20261004/plan.json'}
write(ROOT/'manifest.json',manifest)
print(json.dumps({'exported':len(staged),'total':len(frames),'canvas':[1024,1024]}))
