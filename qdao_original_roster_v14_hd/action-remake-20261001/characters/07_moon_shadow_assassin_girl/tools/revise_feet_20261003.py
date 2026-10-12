"""Publish only explicitly reviewed foot edits; preserve historical text evidence."""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import argparse, hashlib, json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / 'review/feet-direction-20261003'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def refresh_html():
    from build_preview import main
    assert main() == 0
def scoped(rel):
    p = (ROOT / rel).resolve()
    if not p.is_relative_to(ROOT) or p == ROOT: raise ValueError('Outside character scope')
    return p
TARGETS = [f'attack_E_{i:02}' for i in range(1, 9)] + [f'run_SW_{i:02}' for i in (5, 7, 13)]

def pending():
    m = read(ROOT / 'manifest.json')
    if (REV / 'before-manifest.json').exists(): raise RuntimeError('Revision already opened')
    save(REV / 'before-manifest.json', m)
    save(REV / 'before-visual-review.json', read(ROOT / 'review/final-visual-review.json'))
    save(REV / 'before-preview-derivations.json', read(ROOT / 'preview/derivations.json'))
    for f in m['frames']:
        if f['id'] in TARGETS:
            save(REV / 'superseded-records' / (f['id'] + '.json'), read(ROOT / f['sourceRecord']))
            f['visualApproved'] = False
            f['visualReviewScope'] = 'foot direction correction pending; prior review superseded for this issue'
    m['formalAccepted'] = False
    m['currentReview'] = {'status': 'in_progress', 'reason': 'User requested all-direction foot orientation and grounding recheck', 'targets': TARGETS}
    m['updatedAt'] = now()
    m['note'] = '196 real frame files retained;11 targeted foot-direction corrections and run timing review in progress.'
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/final-visual-review.json', {'reviewedAt': now(), 'offlineAccepted': False, 'status': 'foot direction revision in progress', 'priorReview': 'review/feet-direction-20261003/before-visual-review.json', 'pendingFrames': TARGETS})
    refresh_html()
    print('Marked11 targeted frames pending;196 real frame files retained.')

def build_artifacts(m):
    groups = defaultdict(list)
    for f in m['frames']: groups[(f['action'], f['direction'])].append(f)
    artifacts = []
    for (a, d), group in groups.items():
        group.sort(key=lambda f: f['index'])
        sheet = Image.new('RGB', (1200, ((len(group) + 3) // 4) * 326), '#e5e7eb')
        draw = ImageDraw.Draw(sheet); thumbs = []
        for i, f in enumerate(group):
            im = Image.open(ROOT / f['path']).resize((300, 300), Image.Resampling.LANCZOS)
            bg = Image.new('RGBA', (300, 300), '#e5e7eb'); bg.alpha_composite(im)
            thumbs.append(bg.convert('RGB')); sheet.paste(thumbs[-1], (i % 4 * 300, i // 4 * 326))
            draw.text((i % 4 * 300 + 8, i // 4 * 326 + 302), f"{a}/{d}/{i+1:02}  {f['durationMs']}ms", fill='black')
        sources = [{'path': f['path'], 'sha256': f['sha256']} for f in group]
        contact = ROOT / f'preview/{a}-{d}-contact.jpg'; sheet.save(contact, quality=90)
        artifacts.append({'path': contact.relative_to(ROOT).as_posix(), 'sha256': sha(contact), 'sources': sources, 'operation': 'inspection thumbnails only'})
        for label, mult in [('normal', 1), ('slow', 4)]:
            path = ROOT / f'preview/{a}-{d}-{label}.png'; durations = [f['durationMs'] * mult for f in group]
            thumbs[0].save(path, save_all=True, append_images=thumbs[1:], duration=durations, loop=0)
            artifacts.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'sources': sources, 'operation': '300px APNG preview, not game frame', 'durationsMs': durations})
    save(ROOT / 'preview/derivations.json', {'artifacts': artifacts})

def publish():
    selection = read(REV / 'selection.json')
    assert set(selection['selected']) == set(TARGETS) and selection['staticReviewed'] is True
    m = read(ROOT / 'manifest.json'); before = read(REV / 'before-manifest.json')
    assert m['formalAccepted'] is False
    prior = {f['id']: f for f in before['frames']}; replacements = []
    assert all(sha(ROOT / f['path']) == prior[f['id']]['sha256'] for f in m['frames'])
    # Validate every source before replacing any delivered image.
    for key, rel in selection['selected'].items():
        p = scoped(rel); record = read(str(p) + '.generation.json')
        im = Image.open(p); im.load()
        assert im.size == (1254, 1254) and im.mode == 'RGBA' and im.getextrema()[3] == (0, 255)
        assert sha(p) == record['sha256']
        alpha = im.getchannel('A')
        for edge in [(0,0,1254,1),(0,1253,1254,1254),(0,0,1,1254),(1253,0,1254,1254)]:
            assert alpha.crop(edge).getextrema()[1] <= 8, (key, 'opaque border clipped')
    for f in m['frames']:
        if f['id'] not in selection['selected']: continue
        assert sha(ROOT / f['path']) == prior[f['id']]['sha256']
        src = scoped(selection['selected'][f['id']]); native_rec = Path(str(src) + '.generation.json')
        nr = read(native_rec); im = Image.open(src)
        dst = scoped(f['path']); im.resize((1024, 1024), Image.Resampling.LANCZOS).save(dst)
        old = prior[f['id']]
        nr['editSource'] = {'historicalPath': str(dst), 'sha256': old['sha256'], 'historicalSource': True, 'generationRecord': str(REV / 'superseded-records' / (f['id'] + '.json')), 'disposition': 'previous final replaced after verified edit; original provenance retained as text'}
        save(native_rec, nr)
        replacements.append({'id': f['id'], 'path': f['path'], 'previousSHA256': old['sha256'], 'newSHA256': sha(dst), 'source': src.relative_to(ROOT).as_posix(), 'sourceSHA256': sha(src), 'previousSourceRecord': f'review/feet-direction-20261003/superseded-records/{f["id"]}.json'})
        f.update({'sha256': sha(dst), 'visualApproved': False, 'origin': 'builtin_targeted_foot_direction_edit', 'visualReviewScope': 'new foot edit static reviewed; full loop pending'})
        f['nativeProvenance'] = {'historicalPath': src.relative_to(ROOT).as_posix(), 'sha256': sha(src), 'width': 1254, 'height': 1254, 'mode': 'RGBA', 'generationRecord': native_rec.relative_to(ROOT).as_posix(), 'disposition': 'retained_until_cleanup', 'verifiedBeforeCleanup': False}
        save(ROOT / f['sourceRecord'], {'file': str(dst), 'sha256': sha(dst), 'width': 1024, 'height': 1024, 'mode': 'RGBA', 'derivedFrom': {'path': str(src), 'sha256': sha(src), 'generationRecord': str(native_rec), 'dimensions': [1254, 1254]}, 'operation': 'uniform entire1254x1254 canvas resampled to1024x1024 Lanczos; no crop/translation/bboxfit/grounding', 'actualModel': None, 'actualQuality': None, 'visualApproved': False, 'status': 'exported', 'revision': replacements[-1]})
    timing = [43, 71, 71, 43, 43, 43, 43, 43] * 2
    assert sum(timing) == 800
    m['timing'] = {**m['timing'], 'runCycleMs': 800, 'E': timing, 'otherRunDirections': timing, 'previous720': before['timing'], 'scope': 'offline phase-weighted delivery; client unmodified', 'rationale': '02/03 and10/11 each142ms bearing; flight occupies less of cycle; all8 directions inspected before weighting'}
    for f in m['frames']:
        if f['action'] == 'run': f['durationMs'] = timing[f['index']]
    m['currentReview']['status'] = 'replacements_exported_loop_review_pending'
    m['updatedAt'] = now(); save(ROOT / 'manifest.json', m)
    save(REV / 'replacement-ledger.json', {'at': now(), 'replacements': replacements})
    build_artifacts(m)
    (ROOT / 'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in m['frames']), encoding='utf-8')
    refresh_html()
    print('Published11 foot edits and800ms weighted run timing; loop review pending.')

def accept():
    audit = read(REV / 'loop-review.json')
    assert audit['passed'] is True and audit['scope'] == 'offline'
    m = read(ROOT / 'manifest.json')
    assert audit['frameSHA256'] == {f['id']: f['sha256'] for f in m['frames']}
    for f in m['frames']:
        f['visualApproved'] = True
        f['visualReviewScope'] = 'all-direction contact/static recheck, normal run playback samples and selected SW/E-attack quarter-speed/step checks; client not tested; see revision loop-review.json'
        rec = read(ROOT / f['sourceRecord']); rec['visualApproved'] = True; save(ROOT / f['sourceRecord'], rec)
    m['formalAccepted'] = True; m['updatedAt'] = now()
    m['currentReview'] = {'status': 'offline_complete', 'record': 'review/feet-direction-20261003/loop-review.json', 'replacedFrames': TARGETS, 'client': 'not_tested'}
    m['note'] = '196 independent real frames;11 foot edits;800ms phase-weighted run; offline review only.'
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/final-visual-review.json', {'reviewedAt': now(), 'offlineAccepted': True, 'scope': audit['method'], 'acceptedSHA256': audit['frameSHA256'], 'revisionReview': 'review/feet-direction-20261003/loop-review.json', 'clientTested': False})
    save(ROOT / 'preview/progress.json', {'frames': 196, 'offlineAccepted': 196, 'clientIntegrated': 0})
    refresh_html()
    print('Offline revision accepted, pending cleanup verification.')

def cleanup():
    from verify_manifest import verify
    m = read(ROOT / 'manifest.json'); before = verify(m, True)
    assert m['formalAccepted'] and before['passed'], before['errors']
    if not (REV / 'before-cleanup-structure-report.json').exists():
        save(REV / 'before-cleanup-structure-report.json', read(ROOT / 'review/pre-cleanup-structure-report.json'))
    save(ROOT / 'review/pre-cleanup-structure-report.json', before)
    ledger = read(ROOT / 'review/cleanup-ledger.json'); removed = []
    for p in scoped('staging/feet-fix-20261003').rglob('*.png'):
        p = scoped(p); removed.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size, 'reason': 'foot revision native/rejected source; final replacement and previews verified', 'at': now()})
    existing = {(x['path'], x['sha256']) for x in ledger['removed']}
    ledger['removed'].extend(x for x in removed if (x['path'], x['sha256']) not in existing)
    ledger['lastRevisionCleanupAt'] = now()
    ledger['verificationReports'] = ['review/feet-direction-20261003/before-cleanup-structure-report.json', 'review/pre-cleanup-structure-report.json']
    save(ROOT / 'review/cleanup-ledger.json', ledger)
    for x in removed:
        p = scoped(x['path']); assert sha(p) == x['sha256']; p.unlink()
    old = read(REV / 'replacement-ledger.json')['replacements']
    replaced_paths = {str(scoped(x['path'])).replace('\\', '/'): x['previousSHA256'] for x in old}
    replacement_by_path = {str(scoped(x['path'])).replace('\\', '/'): x for x in old}
    historical_refs = {**replaced_paths, **{str(scoped(x['path'])).replace('\\', '/'): x['sha256'] for x in removed}}
    for p in scoped('staging/feet-fix-20261003').rglob('*.png.generation.json'):
        nr = read(p); nr['assetDisposition'] = 'source_removed_after_verified_export'; nr['cleanupLedger'] = 'review/cleanup-ledger.json'
        edit = nr.get('editSource', {})
        editpath = str(edit.get('path', '')).replace('\\', '/')
        if editpath in replacement_by_path and edit.get('sha256') == replacement_by_path[editpath]['previousSHA256']:
            edit['historicalPath'] = edit.pop('path'); edit['historicalSource'] = True
            edit['generationRecord'] = str(ROOT / replacement_by_path[editpath]['previousSourceRecord'])
        for ref in nr.get('references', []):
            refpath = str(ref.get('path', '')).replace('\\', '/')
            if refpath in historical_refs and ref['sha256'] == historical_refs[refpath]:
                ref['historicalPath'] = ref.pop('path'); ref['historicalSource'] = True
                ref['disposition'] = 'source removed or replaced after verified export; generation text and SHA retained'
        save(p, nr)
    for f in m['frames']:
        if f['id'] not in TARGETS: continue
        f['nativeProvenance']['disposition'] = 'removed_after_verified_export'; f['nativeProvenance']['verifiedBeforeCleanup'] = True
        rec = read(ROOT / f['sourceRecord']); rec['derivedFrom']['historicalPath'] = rec['derivedFrom'].pop('path'); rec['derivedFrom']['historicalSource'] = True; save(ROOT / f['sourceRecord'], rec)
    save(ROOT / 'manifest.json', m)
    report = verify(m, True); save(ROOT / 'preview/structure-report.json', report)
    assert report['passed'], report['errors']
    refresh_html()
    print(json.dumps({'cleanedNativeAndRejected': len(removed), 'finalFrames': 196, 'verified': True}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('mode', choices=['pending', 'publish', 'accept', 'cleanup'])
    globals()[parser.parse_args().mode]()
