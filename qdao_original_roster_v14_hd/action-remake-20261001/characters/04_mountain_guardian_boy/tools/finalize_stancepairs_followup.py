"""Finalize the continuous two-frame-position follow-up after root's SHA-bound visual approval.

Default / --check performs a read-only preflight. --apply updates metadata and
deletes only this round's PNG/GIF intermediates beneath provenance/. It never
creates approval, edits formal pixels, changes timing, or overwrites old evidence.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# --check must not create import caches in this shared workspace.
sys.dont_write_bytecode = True
from PIL import Image
from build_preview import verified_deleted_native
from finalize_delivery import (
    ROOT, SPECS, entries_by_file, local, measure, read, rel, require, save, sha,
)
from timing_profile import RUN_NORMAL_DURATIONS

APPROVAL = 'provenance/audit/stancepairs_final_visual_approval_20261004.json'
SNAPSHOT = 'provenance/audit/export_stancepairs_precleanup_snapshot_20261004.json'
LEDGER = 'provenance/audit/stancepairs_image_retention_20261004.json'
TOOL = 'tools/finalize_stancepairs_followup.py'


def now():
    return datetime.now(timezone.utc).isoformat()


def provenance_images():
    """Resolve every deletion target before planning any mutation."""
    result = {}
    boundary = (ROOT / 'provenance').resolve()
    for original in (ROOT / 'provenance').rglob('*'):
        if original.suffix.lower() not in ('.png', '.gif'):
            continue
        resolved = original.resolve()
        require(not original.is_symlink() and resolved == original.absolute(),
                f'Redirected cleanup path: {original}')
        require(resolved.is_relative_to(boundary) and resolved.is_file(),
                f'Cleanup outside provenance image scope: {original}')
        name = rel(resolved)
        result[name] = {'path': name, 'sha256': sha(resolved),
                        'bytes': resolved.stat().st_size}
    return result


def assert_unchanged(plan):
    for name, digest in plan['guards'].items():
        require(sha(local(name)) == digest, f'Input changed after preflight: {name}')
    require(provenance_images() == plan['candidates'],
            'Provenance image inventory changed after preflight')
    actual = {rel(p) for p in (ROOT / 'frames').rglob('*')
              if p.is_file() and p.suffix.lower() == '.png'}
    require(actual == {f['path'] for f in plan['frames']},
            'Formal PNG inventory changed after preflight')
    for name in plan['outputs']:
        p = local(name)
        original = ROOT / name
        require(not original.is_symlink() and p == original.absolute(),
                f'Redirected output path: {name}')
        require(not p.with_name(p.name + '.tmp').exists(), f'Temporary output exists: {name}')
    require(not local(SNAPSHOT).exists() and not local(LEDGER).exists(),
            'Follow-up snapshot/ledger already exists; inspect rather than rerun cleanup')


def preflight():
    """All 196 exports, approval entries and old/live native proofs before writes."""
    require(ROOT == Path(__file__).resolve().parents[1]
            and ROOT.name == '04_mountain_guardian_boy', 'Wrong character root')
    require(RUN_NORMAL_DURATIONS == [75] * 16, 'Run must remain uniform 1200ms')
    expected = {f'frames/{a}/{d}/frame_{n:02d}.png'
                for a, (count, directions, _) in SPECS.items()
                for d in directions for n in range(1, count + 1)}
    actual = {rel(p) for p in (ROOT / 'frames').rglob('*')
              if p.is_file() and p.suffix.lower() == '.png'}
    require(len(expected) == 196 and actual == expected, 'Expected exactly 196 formal PNGs')
    guards = {}

    def guarded_read(name):
        p = local(name)
        before = sha(p)
        data = read(p)
        require(sha(p) == before, f'JSON changed while reading: {name}')
        if name in guards:
            require(guards[name] == before, f'Evidence changed during preflight: {name}')
        guards[name] = before
        return data

    approval = guarded_read(APPROVAL)
    require(approval.get('character') == ROOT.name, 'Approval character mismatch')
    for key in ('reviewer', 'reviewedAt', 'scope'):
        require(isinstance(approval.get(key), str) and approval[key].strip(),
                f'Approval missing {key}')
    require(datetime.fromisoformat(approval['reviewedAt'].replace('Z', '+00:00')).utcoffset()
            is not None, 'Approval reviewedAt requires timezone')
    require(approval.get('automaticallyApproved') is not True, 'Automatic approval forbidden')
    approvals = entries_by_file(approval.get('entries'), expected, 'root approval')
    manifest = guarded_read('manifest.delivery.json')
    review = guarded_read('review.json')
    timing = guarded_read('runtime_timing.json')
    require(all(x.get('character') == ROOT.name for x in (manifest, review, timing)),
            'Existing delivery metadata character mismatch')
    prior_rows = entries_by_file(
        [{**row, 'file': row.get('path')} for row in manifest.get('files', [])],
        expected, 'prior delivery')
    run = timing.get('run', {})
    require(run.get('frameMs') == 75 and run.get('offlineDefaultLoopMs') == 1200
            and run.get('offlineFrameDurationsMs') == [75] * 16,
            'runtime_timing.json must already use uniform 1200ms')
    guards[TOOL] = sha(local(TOOL))
    for name in ('tools/build_preview.py', 'tools/finalize_delivery.py', 'tools/timing_profile.py'):
        guards[name] = sha(local(name))
    if local('frames.sha256').exists():
        guards['frames.sha256'] = sha(local('frames.sha256'))

    frames = []
    for action, (count, directions, duration) in SPECS.items():
        for direction in directions:
            for index in range(1, count + 1):
                name = f'frames/{action}/{direction}/frame_{index:02d}.png'
                path = local(name, 'frames')
                record = rel(path.with_suffix('.generation.json'))
                data = guarded_read(record)
                export, pixels = measure(path)
                try:
                    require((export['width'], export['height'], export['mode'], export['format'])
                            == (1024, 1024, 'RGBA', 'PNG'), f'Formal format: {name}')
                    require(data.get('file') == name and data.get('sha256') == export['sha256'],
                            f'Formal sidecar SHA mismatch: {name}')
                    require(prior_rows[name].get('record') == record,
                            f'Prior delivery sidecar path mismatch: {name}')
                    if prior_rows[name]['sha256'] == export['sha256']:
                        require(prior_rows[name].get('recordSha256') == guards[record],
                                f'Unchanged PNG has untracked sidecar edits: {name}')
                    require(data.get('actualModel') is None and data.get('actualQuality') is None,
                            f'Unconfirmed actual model/quality changed: {name}')
                    require(data.get('frameDurationMs') == duration,
                            f'Unexpected duration; this tool does not retime: {name}')
                    if action == 'run':
                        require(duration == 75, 'Run spec changed')
                        run_record = data.get('runTiming', {})
                        require(isinstance(run_record, dict), f'Invalid runTiming: {name}')
                        for key, value in (('offlinePreviewDefaultLoopMs', 1200),
                                           ('offlinePreviewFrameMs', 75),
                                           ('offlinePreviewFrameDurationsMs', [75] * 16)):
                            require(key not in run_record or run_record[key] == value,
                                    f'Conflicting run timing declaration: {name}')
                    approved = approvals[name]
                    require(approved.get('sha256') == export['sha256']
                            and approved.get('status') == 'visual_passed',
                            f'Root has not approved current PNG SHA: {name}')
                    if 'independentPoseObserved' in approved:
                        require(isinstance(approved['independentPoseObserved'], bool),
                                f'Invalid pose observation: {name}')
                    native = data.get('nativeSource')
                    require(isinstance(native, dict), f'Native record missing: {name}')
                    require(isinstance(data.get('derivedFrom', []), list),
                            f'derivedFrom must be a list: {name}')
                    native_path = local(native.get('path'), 'provenance')
                    require(native['path'] == rel(native_path), f'Noncanonical native path: {name}')
                    live = native_path.is_file()
                    if live:
                        require(native.get('fileRetained') is not False,
                                f'Native claims deletion but exists: {name}')
                        measured, native_pixels = measure(native_path)
                        try:
                            require(measured['width'] >= 1024 and measured['height'] >= 1024
                                    and measured['mode'] == 'RGBA' and measured['format'] == 'PNG',
                                    f'Native size/format: {name}')
                            require(all(native.get(k) == measured[k]
                                        for k in ('sha256', 'width', 'height', 'mode', 'format')),
                                    f'Live native source binding mismatch: {name}')
                            resized = native_pixels.resize((1024, 1024), Image.Resampling.LANCZOS)
                            try:
                                require(resized.tobytes() == pixels.tobytes(),
                                        f'Whole-canvas LANCZOS reproduction failed: {name}')
                            finally:
                                resized.close()
                        finally:
                            native_pixels.close()
                        native_measurement = {'path': native['path'], **measured}
                        evidence = None
                        guards[native['path']] = measured['sha256']
                    else:
                        require(not native_path.exists() and native.get('fileRetained') is False,
                                f'Native missing without declared deletion: {name}')
                        binding = native['precleanupSnapshot']
                        snapshot_path = local(binding['path'], 'provenance/audit')
                        ledger_path = local(native['retentionRecord'], 'provenance/audit')
                        snapshot = guarded_read(rel(snapshot_path))
                        guarded_read(rel(ledger_path))
                        require(guards[rel(snapshot_path)] == binding['sha256'],
                                f'Old snapshot changed: {name}')
                        valid, basis = verified_deleted_native(
                            {'path': name, 'sha256': export['sha256']}, native)
                        require(valid, f'Deleted native verification failed: {name}: {basis}')
                        row = next(x for x in snapshot['entries'] if x['file'] == name)
                        require(row['export']['rgbaPixelSha256'] == export['rgbaPixelSha256'],
                                f'Old export pixel measurement mismatch: {name}')
                        native_measurement = copy.deepcopy(row['native'])
                        evidence = copy.deepcopy(binding)
                    guards[name] = export['sha256']
                    frames.append({'action': action, 'direction': direction, 'frame': index,
                                   'path': name, 'sha256': export['sha256'], 'record': record,
                                   'recordSha256BeforeFinalization': guards[record], 'data': data,
                                   'approval': approved, 'export': export, 'native': native_measurement,
                                   'liveNative': live, 'priorNativeEvidence': evidence,
                                   'pngChangedSinceDelivery': prior_rows[name]['sha256'] != export['sha256']})
                finally:
                    pixels.close()
    for key in ('sha256', 'rgbaPixelSha256'):
        require(len({f['export'][key] for f in frames}) == 196, f'Duplicate formal {key}')
    require(len({f['native']['sha256'] for f in frames}) == 196, 'Duplicate native SHA')
    candidates = provenance_images()
    require({f['native']['path'] for f in frames if f['liveNative']} <= set(candidates),
            'Cleanup plan omits a measured live native')
    for name, row in candidates.items():
        require(name not in guards or guards[name] == row['sha256'],
                f'Native changed before cleanup inventory: {name}')
        guards[name] = row['sha256']
    outputs = [f['record'] for f in frames] + ['review.json', 'manifest.delivery.json',
               'frames.sha256', SNAPSHOT, LEDGER]
    plan = {'frames': frames, 'approval': approval, 'approvalSha256': guards[APPROVAL],
            'manifest': manifest, 'review': review, 'candidates': candidates,
            'guards': guards, 'outputs': outputs}
    assert_unchanged(plan)
    return plan


def apply(plan):
    assert_unchanged(plan)  # Final full gate before the first write.
    frames = plan['frames']
    approval = plan['approval']
    timestamp = now()
    snapshot = {'schema': 'qdao-export-precleanup-snapshot-v1', 'character': ROOT.name,
                'measuredAt': timestamp, 'audit': {'method': 'full_read_only_preflight',
                'validator': {'path': TOOL, 'sha256': plan['guards'][TOOL]}},
                'visualApproval': {'path': APPROVAL, 'sha256': plan['approvalSha256']},
                'entries': []}
    for f in frames:
        snapshot['entries'].append({
            'file': f['path'], 'sha256': f['sha256'], 'record': f['record'],
            'recordSha256BeforeFinalization': f['recordSha256BeforeFinalization'],
            'export': f['export'], 'native': f['native'], 'wholeCanvasResizePixelMatch': True,
            'nativeVerificationBasis': ('live_native_whole_canvas_LANCZOS'
                                        if f['liveNative'] else 'verified_deleted_native'),
            'priorNativeEvidence': f['priorNativeEvidence']})
    save(local(SNAPSHOT), snapshot)
    snapshot_binding = {'path': SNAPSHOT, 'sha256': sha(local(SNAPSHOT))}
    for f in frames:
        data = f['data']
        previous = data.get('review', {})
        data['review'] = {'status': 'visual_passed', 'automaticallyApproved': False,
                          'reviewedAt': approval['reviewedAt'], 'scope': approval['scope'],
                          'reviewer': approval['reviewer'], 'priorReview': previous,
                          'sourceBoundSha256': f['sha256'], 'clientDynamicStatus': 'not_integrated',
                          'approvalRecord': APPROVAL, 'approvalSha256': plan['approvalSha256']}
        for key in ('independentPoseObserved', 'observation'):
            if key in f['approval']:
                data['review'][key] = f['approval'][key]
        if f['action'] == 'run':
            # Newly registered frames may lack the delivery-level timing annotation.
            data.setdefault('runTiming', {}).update(
                offlinePreviewDefaultLoopMs=1200, offlinePreviewFrameMs=75,
                offlinePreviewFrameDurationsMs=[75] * 16, clientApprovedLoopMs=None,
                status='user_selected_offline_1200_client_unconfirmed')
        if f['liveNative']:
            data['nativeSource']['precleanupSnapshot'] = snapshot_binding
            for source in [data['nativeSource'], *data.get('derivedFrom', [])]:
                if isinstance(source, dict) and source.get('path') == f['native']['path'] \
                        and source.get('sha256') == f['native']['sha256']:
                    source['fileRetained'] = True
        save(local(f['record']), data)
    review = copy.deepcopy(plan['review'])
    review.update(reviewedAt=approval['reviewedAt'], finalizedAt=timestamp,
                  generated=196, exported=196, staticVisualPassed=196,
                  offlineSequenceReview=approval.get('offlineSequenceReview', 'not_declared'),
                  clientIntegration='not_integrated', clientDynamicAcceptance='not_run',
                  methods=approval.get('methods', []), observations=approval.get('observations', {}),
                  frameBindings=[{key: f[key] for key in
                                  ('action', 'direction', 'frame', 'path', 'sha256', 'record')}
                                 for f in frames],
                  audit=SNAPSHOT, auditSha256=snapshot_binding['sha256'],
                  rootVisualApproval={'path': APPROVAL, 'sha256': plan['approvalSha256']})
    save(local('review.json'), review)
    ledger = {'schema': 'qdao-image-retention-v2', 'character': ROOT.name, 'startedAt': now(),
              'policy': '仅清理本轮provenance下PNG/GIF中间图；保留正式图、旧快照和全部文字。',
              'precleanupSnapshot': snapshot_binding,
              'visualApproval': {'path': APPROVAL, 'sha256': plan['approvalSha256']},
              'files': [{**row, 'status': 'pending'} for row in plan['candidates'].values()],
              'outsideCharacterDirectoryTouched': False}
    save(local(LEDGER), ledger)
    for item in ledger['files']:
        try:
            original = ROOT / item['path']
            path = local(item['path'], 'provenance')
            require(not original.is_symlink() and path == original.absolute()
                    and path.suffix.lower() in ('.png', '.gif'),
                    f'Cleanup path changed: {item["path"]}')
            require(sha(path) == item['sha256'], f'Cleanup content changed: {item["path"]}')
            path.unlink()
            item.update(status='deleted', deletedAt=now())
        except (OSError, ValueError) as error:
            item.update(status='failed', attemptedAt=now(), error=str(error))
        save(local(LEDGER), ledger)
    ledger.update(completedAt=now(),
                  deletedCount=sum(x['status'] == 'deleted' for x in ledger['files']),
                  failedCount=sum(x['status'] == 'failed' for x in ledger['files']))
    save(local(LEDGER), ledger)
    removed = {x['path']: x for x in ledger['files'] if x['status'] == 'deleted'}
    for f in frames:
        if not f['liveNative']:
            continue  # Old deletion proof and source retention metadata remain untouched.
        data = f['data']
        for source in [data['nativeSource'], *data.get('derivedFrom', [])]:
            if not isinstance(source, dict):
                continue
            item = removed.get(source.get('path'))
            if item and source.get('sha256') == item['sha256']:
                source.update(fileRetained=False, deletedAt=item['deletedAt'], retentionRecord=LEDGER,
                              retentionNote='本轮实际删除成功后登记；证据见SHA绑定的新清理前快照。')
        save(local(f['record']), data)
    manifest = copy.deepcopy(plan['manifest'])
    old_cleanup = manifest.get('cleanup')
    if old_cleanup:
        manifest.setdefault('cleanupHistory', []).append(old_cleanup)
    manifest.update(createdAt=timestamp, targetFrames=196, exportedFrames=196,
                    files=[{'path': f['path'], 'sha256': f['sha256'], 'record': f['record'],
                            'recordSha256': sha(local(f['record']))} for f in frames],
                    review='review.json', timing='runtime_timing.json',
                    cleanup={'record': LEDGER, 'deleted': ledger['deletedCount'],
                             'failed': ledger['failedCount']})
    save(local('manifest.delivery.json'), manifest)
    hashes = local('frames.sha256')
    temporary = hashes.with_name(hashes.name + '.tmp')
    require(not temporary.exists(), 'frames.sha256 temporary path exists')
    temporary.write_text(''.join(f['sha256'] + '  ' + f['path'] + '\n' for f in frames), encoding='utf-8')
    temporary.replace(hashes)
    return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='只读全量核验（默认）')
    mode.add_argument('--apply', action='store_true', help='核验通过后写入审核/交付并清理本轮中间图')
    args = parser.parse_args()
    plan = preflight()
    result = {'mode': 'apply' if args.apply else 'check', 'formalFrames': 196,
              'rootApprovedCurrentShaFrames': 196,
              'liveNativeFrames': sum(f['liveNative'] for f in plan['frames']),
              'verifiedDeletedNativeFrames': sum(not f['liveNative'] for f in plan['frames']),
              'pngChangedSinceDelivery': [f['path'] for f in plan['frames'] if f['pngChangedSinceDelivery']],
              'cleanupCandidateCount': len(plan['candidates']), 'runFrameMs': 75,
              'runCycleMs': 1200, 'automaticVisualApproval': False}
    if args.apply:
        ledger = apply(plan)
        result.update(deleted=ledger['deletedCount'], cleanupFailed=ledger['failedCount'])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.apply and ledger['failedCount']:
        raise SystemExit('Partial cleanup: inspect the new ledger; do not rerun blindly.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        raise SystemExit(str(error)) from error
