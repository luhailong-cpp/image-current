"""Close reviewed final assets and prepare an exact, bounded image cleanup."""
from pathlib import Path
import datetime, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT/'provenance/limbs-20261004'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p,x: p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
review = read(BATCH/'review-result.json')
assert review['staticSequenceReviewed'] and review['browserPreviewChecked']
assert review['reviewedFrames'] == 196 and review['unresolvedMaterialItems'] == []
selection = read(ROOT/'limbs-selection.json')
manifest = read(ROOT/'manifest.json')
before = {f['slot']:f for f in read(BATCH/'before-manifest.json')['frames']}
timing = read(ROOT/'run-timing.json')
old_timing = read(BATCH/'before-run-timing.json')
assert timing['normalCycleMs'] == 960
assert timing['contactPairPlan'] == old_timing['contactPairPlan']
for direction,profile in timing['directions'].items():
    assert profile['frameMs'] == [60]*16 and profile['positionPairMs'] == 120
    assert profile['phases'] == old_timing['directions'][direction]['phases']
    assert profile['supportFootByFrame'] == old_timing['directions'][direction]['supportFootByFrame']
for action in ['hit','attack','cast']:
    assert manifest['timing'][action] == read(BATCH/'before-manifest.json')['timing'][action]
for f in manifest['frames']:
    assert sha(ROOT/f['file']) == f['sha256']
    oldslot = f['slot']
    if f['slot'] not in selection:
        assert f['sha256'] == before[oldslot]['sha256']
    else:
        assert f['derivedFrom']['file'] == selection[f['slot']]['source']
        assert selection[f['slot']]['originalInputSlot'] == oldslot
    assert sha(ROOT/f['derivedFrom']['generationRecord']) == f['derivedFrom']['generationRecordSha256']
lineage = []
for p in sorted((ROOT/'generation/limbs-20261004').rglob('*.png.generation.json')):
    rec = read(p)
    assert sha(ROOT/rec['file']) == rec['sha256']
    refs = []
    for ref in rec.get('references',[]):
        ref = dict(ref)
        name = ref.get('file') or ref.get('path')
        if name and not ref.get('sha256'):
            q = Path(name)
            if not q.is_absolute(): q = ROOT/q
            q = q.resolve()
            if q.is_relative_to((ROOT/'runtime').resolve()):
                slot = q.relative_to(ROOT/'runtime').with_suffix('').as_posix()
                ref['sha256'] = before[slot]['sha256']
                ref['evidence'] = 'before-manifest snapshot; input slot unchanged'
            elif q.is_file():
                ref['sha256'] = sha(q)
                ref['evidence'] = 'input still present before cleanup'
        refs.append(ref)
    lineage.append({'generationRecord':p.relative_to(ROOT).as_posix(),
        'generationRecordSha256':sha(p),'nativeFile':rec['file'],
        'nativeSha256':rec['sha256'],'references':refs})
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
write(BATCH/'edit-lineage.json',{'recordedAt':now,'items':lineage})
manifest['limbsRevision'].update({'status':'exported_and_offline_reviewed',
    'review':'provenance/limbs-20261004/review-result.json','offlinePreviewReviewed':True,'completedAt':now})
manifest['deliveryStatus'] = 'limbs_revision_exported_and_previewed'
manifest['updatedAt'] = now
manifest['reviewNotes'] = review['notes']
for f in manifest['frames']:
    f['offlineLimbsReviewed'] = True
    if f['slot'] in selection: f['limbsRevision']['offlineSequenceReviewed'] = True
    write(ROOT/(f['file']+'.generation.json'),f)
write(ROOT/'manifest.json',manifest)
plan = read(BATCH/'plan.json')
plan.update({'status':'exported_and_offline_reviewed','completedAt':now,'replacedFrames':len(selection)})
write(BATCH/'plan.json',plan)
items = []
for folder in [ROOT/'generation/limbs-20261004',BATCH]:
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.suffix.lower() in ['.png','.jpg','.jpeg','.gif','.webp']:
            assert p.resolve().is_relative_to(folder.resolve())
            items.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
write(BATCH/'cleanup-plan.json',{'createdAt':now,'status':'ready_after_technical_verification',
    'manifestSha256':sha(ROOT/'manifest.json'),'items':items,'count':len(items),'bytes':sum(x['bytes'] for x in items),
    'policy':'Remove exported originals, rejected candidates and inspection images; preserve all text records and current runtime/preview.'})
print(json.dumps({'selected':len(selection),'lineageRecords':len(lineage),'cleanupImages':len(items)}))
