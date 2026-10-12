"""Close a manually reviewed delivery and list removable process PNGs.

Does not delete files or infer visual acceptance from frame counts.
"""
from pathlib import Path
import datetime, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'provenance/contact-pairs-20261004'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, x: p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
selection = read(ROOT / 'contact-pairs-selection.json')
review = read(BATCH / 'review-result.json')
assert set(review['reviewedDirections']) == set(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
assert review['staticSequenceReviewed'] and review['browserPreviewChecked']
assert review['unresolvedMaterialItems'] == []
manifest = read(ROOT / 'manifest.json')
profile = read(ROOT / 'run-timing.json')
baseline = {f['slot']: f for f in read(BATCH / 'before-manifest.json')['frames']}
frames = {f['slot']: f for f in manifest['frames']}
for slot, chosen in selection.items():
    f = frames[slot]
    assert sha(ROOT / f['file']) == f['sha256']
    assert f['derivedFrom']['file'] == chosen['source']
    assert sha(ROOT / chosen['source']) == f['derivedFrom']['sha256']
for slot, f in frames.items():
    if not slot.startswith('run/'):
        assert f['sha256'] == baseline[slot]['sha256'], slot

lineage = []
for folder in ['contact4-20261004', 'contact-pairs-20261004']:
    for p in sorted((ROOT / 'generation' / folder).rglob('*.png.generation.json')):
        rec = read(p)
        native = ROOT / rec['file']
        assert native.is_file() and sha(native) == rec['sha256'], str(p)
        refs = []
        for ref in rec.get('references', []):
            path = ref.get('file') or ref.get('path')
            if not path:
                continue
            q = Path(path)
            if not q.is_absolute():
                q = ROOT / q
            item = dict(ref)
            if not item.get('sha256'):
                if q.is_relative_to(ROOT / 'runtime'):
                    input_slot = q.relative_to(ROOT / 'runtime').with_suffix('').as_posix()
                    item['sha256'] = baseline[input_slot]['sha256']
                    item['evidence'] = 'pre-edit manifest snapshot'
                elif q.is_file():
                    item['sha256'] = sha(q)
                    item['evidence'] = 'current input before cleanup'
                else:
                    item['evidence'] = 'historical path; see generation record'
            refs.append(item)
        lineage.append({'generationRecord': p.relative_to(ROOT).as_posix(),
            'generationRecordSha256': sha(p), 'nativeFile': rec['file'],
            'nativeSha256': rec['sha256'], 'references': refs})
write(BATCH / 'edit-lineage.json', {'recordedAt': now, 'items': lineage})

manifest['updatedAt'] = now
manifest['timing']['run'] = {'previewDefaultCycleMs': 1200, 'previewFrameMs': [75] * 16,
    'weightedTiming': False, 'timingFile': 'run-timing.json',
    'directions': profile['directions'], 'clientFinalized': False}
manifest['contactPairsRevision'].update({'status': 'exported_and_offline_reviewed',
    'review': 'provenance/contact-pairs-20261004/review-result.json',
    'uniformFrameMs': 75, 'positionPairMs': 150, 'offlinePreviewReviewed': True,
    'clientValidated': False})
manifest['deliveryStatus'] = 'contact_pairs_revision_exported_and_previewed'
manifest['offlinePlaybackChecked'] = True
manifest['offlineDynamicAcceptance'] = 'offline frame sequences and browser samples; not game movement certification'
manifest['reviewNotes'] = review['notes']
for f in manifest['frames']:
    if f['slot'].startswith('run/'):
        _, d, n = f['slot'].split('/')
        f['phase'] = profile['directions'][d]['phases'][int(n) - 1]
        f['previewDurationMs'] = 75
        f['offlineFootDirectionReviewed'] = True
        f['offlineContactPairReviewed'] = True
    write(ROOT / (f['file'] + '.generation.json'), f)
write(ROOT / 'manifest.json', manifest)
plan = read(BATCH / 'plan.json')
plan.update({'status': 'exported_and_offline_reviewed', 'completedAt': now,
    'review': 'provenance/contact-pairs-20261004/review-result.json'})
write(BATCH / 'plan.json', plan)

items = []
for category in ['generation', 'provenance']:
    for folder in ['contact4-20261004', 'contact-pairs-20261004']:
        directory = ROOT / category / folder
        for p in sorted(p for p in directory.rglob('*') if p.is_file() and p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.gif']):
            assert p.resolve().is_relative_to(directory.resolve())
            items.append({'file': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size})
write(BATCH / 'cleanup-plan.json', {'createdAt': now, 'status': 'ready_after_technical_verification',
    'reason': 'User authorized removal of exported originals, rejects and intermediate images; retain every text record.',
    'manifestSha256': sha(ROOT / 'manifest.json'), 'items': items,
    'count': len(items), 'bytes': sum(i['bytes'] for i in items)})
print(json.dumps({'selected': len(selection), 'lineageRecords': len(lineage), 'cleanupImageCount': len(items)}))
