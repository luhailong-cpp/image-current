"""One-time contact-pose revision, tied to frozen pre-revision hashes."""
import argparse
from pathlib import Path
from PIL import Image
from revise_feet_20261003 import ROOT, read, save, sha, now, scoped
from rebuild_previews import build_artifacts
from build_preview import main as build_html

REV = ROOT / 'review/bamboo-reference-20261003'
TARGETS = {'run_N_01', 'run_NW_09'}


def publish():
    m = read(ROOT / 'manifest.json')
    before = {f['id']: f for f in read(REV / 'before-manifest.json')['frames']}
    selection = read(REV / 'selection.json')
    assert set(selection['selected']) == TARGETS and selection['staticReviewed'] is True
    assert not m['formalAccepted'] and m['timing']['runCycleMs'] == 1200
    assert all(sha(ROOT / f['path']) == before[f['id']]['sha256'] for f in m['frames'])
    for key, rel in selection['selected'].items():
        src = scoped(rel)
        record = read(str(src) + '.generation.json')
        with Image.open(src) as im:
            assert im.size == (1254, 1254) and im.mode == 'RGBA' and im.getextrema()[3] == (0, 255)
            alpha = im.getchannel('A')
            assert all(alpha.crop(edge).getextrema()[1] <= 8 for edge in
                       ((0,0,1254,1),(0,1253,1254,1254),(0,0,1,1254),(1253,0,1254,1254)))
        assert sha(src) == record['sha256']
    replacements = []
    for f in m['frames']:
        if f['id'] not in TARGETS:
            continue
        src = scoped(selection['selected'][f['id']])
        dst = scoped(f['path'])
        native_record = Path(str(src) + '.generation.json')
        nr = read(native_record)
        with Image.open(src) as im:
            im.resize((1024, 1024), Image.Resampling.LANCZOS).save(dst)
        old = before[f['id']]
        archived = REV / 'superseded-records' / (f['id'] + '.json')
        nr['replacesFinal'] = {'historicalPath': str(dst), 'sha256': old['sha256'], 'historicalSource': True,
                              'generationRecord': str(archived), 'disposition': 'previous final replaced after verified edit; text provenance retained'}
        edit_ref = nr['references'][0]
        if Path(edit_ref['path']).resolve() == dst:
            nr['editSource'] = dict(nr['replacesFinal'])
        else:
            # A retry may edit an earlier native candidate, not the old final PNG.
            nr['editSource'] = {'path': edit_ref['path'], 'sha256': edit_ref['sha256'],
                                'generationRecord': edit_ref['path'] + '.generation.json'}
        for ref in nr.get('references', []):
            if '09_bamboo_archer_girl' in ref.get('path', ''):
                ref['role'] = 'user-approved same-direction motion reference only; own07 identity and daggers retained'
        save(native_record, nr)
        replacements.append({'id': f['id'], 'path': f['path'], 'previousSHA256': old['sha256'],
                             'newSHA256': sha(dst), 'source': src.relative_to(ROOT).as_posix(), 'sourceSHA256': sha(src),
                             'previousSourceRecord': archived.relative_to(ROOT).as_posix()})
        f.update({'sha256': sha(dst), 'visualApproved': False, 'origin': 'builtin_targeted_contact_pose_edit',
                  'visualReviewScope': 'new contact-pose edit static reviewed; sequence pending'})
        f['nativeProvenance'] = {'historicalPath': src.relative_to(ROOT).as_posix(), 'sha256': sha(src), 'width': 1254, 'height': 1254,
                                 'mode': 'RGBA', 'generationRecord': native_record.relative_to(ROOT).as_posix(),
                                 'disposition': 'retained_until_cleanup', 'verifiedBeforeCleanup': False}
        save(ROOT / f['sourceRecord'], {'file': str(dst), 'sha256': sha(dst), 'width': 1024, 'height': 1024, 'mode': 'RGBA',
             'derivedFrom': {'path': str(src), 'sha256': sha(src), 'generationRecord': str(native_record), 'dimensions': [1254,1254]},
             'operation': 'uniform entire1254x1254 canvas resampled to1024x1024 Lanczos; no crop/translation/bboxfit/grounding',
             'actualModel': None, 'actualQuality': None, 'visualApproved': False, 'status': 'exported', 'revision': replacements[-1]})
    m['currentReview']['status'] = 'two_contact_edits_exported_loop_review_pending'
    m['updatedAt'] = now()
    save(ROOT / 'manifest.json', m)
    save(REV / 'replacement-ledger.json', {'at': now(), 'replacements': replacements})
    (ROOT / 'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in m['frames']), encoding='utf-8')
    build_artifacts(m)
    assert build_html() == 0
    print('Published2 contact edits;1200ms/75ms retained; final sequence review pending.')


def accept():
    m = read(ROOT / 'manifest.json')
    review = read(REV / 'final-review.json')
    assert review['passed'] is True and review['scope'] == 'offline'
    assert review['frameSHA256'] == {f['id']: f['sha256'] for f in m['frames']}
    for f in m['frames']:
        f['visualApproved'] = True
        f['visualReviewScope'] = 'same-direction bamboo contact-sheet comparison and targeted native/final-frame samples; APNG delay and player-function virtual-clock tests; client untested; see bamboo-reference final-review.json'
        rec = read(ROOT / f['sourceRecord'])
        rec['visualApproved'] = True
        save(ROOT / f['sourceRecord'], rec)
    m['formalAccepted'] = True
    m['updatedAt'] = now()
    m['currentReview'] = {'status': 'offline_complete', 'record': 'review/bamboo-reference-20261003/final-review.json',
                          'replacedFrames': sorted(TARGETS), 'referenceCharacter': '09_bamboo_archer_girl', 'client': 'not_tested'}
    m['note'] = '196 independent real frames; latest2 contact edits after bamboo comparison;1200ms uniform run,75ms per frame; offline review only.'
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/final-visual-review.json', {'reviewedAt': now(), 'offlineAccepted': True, 'scope': review['method'],
         'acceptedSHA256': review['frameSHA256'], 'revisionReview': 'review/bamboo-reference-20261003/final-review.json', 'clientTested': False})
    save(ROOT / 'preview/progress.json', {'frames': 196, 'offlineAccepted': 196, 'clientIntegrated': 0})
    assert build_html() == 0
    print('Current2-frame contact revision and1200ms offline playback accepted.')


def cleanup():
    from verify_manifest import verify
    m = read(ROOT / 'manifest.json')
    assert m['formalAccepted'] and all(f['nativeProvenance']['disposition'] == 'retained_until_cleanup' for f in m['frames'] if f['id'] in TARGETS)
    before = verify(m, True)
    assert before['passed'], before['errors']
    archive = REV / 'before-cleanup-structure-report.json'
    assert not archive.exists(), 'Cleanup already opened; inspect state before retrying'
    save(archive, read(ROOT / 'review/pre-cleanup-structure-report.json'))
    save(ROOT / 'review/pre-cleanup-structure-report.json', before)
    ledger = read(ROOT / 'review/cleanup-ledger.json')
    removed = []
    for p in scoped('staging/bamboo-reference-20261003').rglob('*.png'):
        p = scoped(p)
        removed.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size,
                        'reason': 'bamboo-reference native/rejected contact edit; final and preview references verified', 'at': now()})
    ledger['removed'].extend(removed)
    ledger['lastRevisionCleanupAt'] = now()
    ledger['verificationReports'] = list(dict.fromkeys(ledger.get('verificationReports', []) + [archive.relative_to(ROOT).as_posix(), 'review/pre-cleanup-structure-report.json']))
    save(ROOT / 'review/cleanup-ledger.json', ledger)
    for x in removed:
        p = scoped(x['path'])
        assert sha(p) == x['sha256']
        p.unlink()
    old = read(REV / 'replacement-ledger.json')['replacements']
    replaced = {str(scoped(x['path'])).replace('\\','/'): x for x in old}
    historical = {str(scoped(x['path'])).replace('\\','/'): x['sha256'] for x in removed}
    historical.update({p: x['previousSHA256'] for p, x in replaced.items()})
    for p in scoped('staging/bamboo-reference-20261003').rglob('*.png.generation.json'):
        nr = read(p)
        nr['assetDisposition'] = 'source_removed_after_verified_export'
        nr['cleanupLedger'] = 'review/cleanup-ledger.json'
        if not nr.get('editSource') and nr.get('references'):
            first = nr['references'][0]
            nr['editSource'] = {'path': first['path'], 'sha256': first['sha256'],
                                'generationRecord': first['path'] + '.generation.json'}
        edit = nr.get('editSource', {})
        key = str(edit.get('path','')).replace('\\','/')
        if key in historical and edit.get('sha256') == historical[key]:
            edit['historicalPath'] = edit.pop('path')
            edit['historicalSource'] = True
            if key in replaced:
                edit['generationRecord'] = str(ROOT / replaced[key]['previousSourceRecord'])
        for ref in nr.get('references', []):
            key = str(ref.get('path','')).replace('\\','/')
            if key in historical and ref.get('sha256') == historical[key]:
                ref['historicalPath'] = ref.pop('path')
                ref['historicalSource'] = True
                ref['disposition'] = 'source replaced or removed after verified export; SHA and text retained'
        save(p, nr)
    for f in m['frames']:
        if f['id'] not in TARGETS:
            continue
        f['nativeProvenance']['disposition'] = 'removed_after_verified_export'
        f['nativeProvenance']['verifiedBeforeCleanup'] = True
        rec = read(ROOT / f['sourceRecord'])
        rec['derivedFrom']['historicalPath'] = rec['derivedFrom'].pop('path')
        rec['derivedFrom']['historicalSource'] = True
        save(ROOT / f['sourceRecord'], rec)
    save(ROOT / 'manifest.json', m)
    report = verify(m, True)
    save(ROOT / 'preview/structure-report.json', report)
    assert report['passed'], report['errors']
    assert build_html() == 0
    save(REV / 'cleanup-result.json', {'at': now(), 'removedImages': len(removed), 'totalLedgerEntries': len(ledger['removed']), 'structurePassed': True})
    print(f'Cleaned{len(removed)} native/rejected images;196 final frames verified.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['publish','accept','cleanup'])
    globals()[parser.parse_args().mode]()
