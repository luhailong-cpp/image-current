"""Finalize the reviewed hand/foot revision; never generate or publish pixels.

Run phases after publication, then accept after this revision's visual, browser
and timing reviews. Cleanup delegates to the existing scoped, ledgered routine.
Importing this module does not run a mode or change the previous tool's globals.
"""
import argparse
from contextlib import contextmanager

import finish_grounding_delivery as previous
from revise_feet_20261003 import ROOT, read, save, sha, now, scoped
from build_preview import main as build_html

NAME = 'limb-axis-20261005'
REV = ROOT / 'review' / NAME
REVISIONS = [
    'direction-alignment-20261004',
    'direction-combat-20261004',
    'run-grounding-20261004',
    'axis-continuity-20261004',
    NAME,
]
BEFORE_SHA256 = '91bbe99694aed3dacec6292411a7f49d4852154da4b6b6aec75a912fcade87fc'
REVIEW_PATH = f'review/{NAME}/final-review.json'
SELECTION_PATH = f'review/{NAME}/selection.json'
FRAME_COUNT = 196
RUN_DIRECTIONS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
EXPECTED_IDS = {
    f'{action}_{direction}_{number:02}'
    for action, directions, count in (
        ('run', RUN_DIRECTIONS, 16),
        ('hit', ('E', 'W'), 6),
        ('attack', ('E', 'W'), 12),
        ('cast', ('E', 'W'), 16),
    )
    for direction in directions for number in range(1, count + 1)
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frame_map(manifest):
    frames = manifest['frames']
    by_id = {f['id']: f for f in frames}
    require(len(frames) == FRAME_COUNT and set(by_id) == EXPECTED_IDS,
            'Expected exactly the 196 unique delivery frame IDs.')
    return by_id


def current_state():
    """Validate every frame and immutable phase field before any writes."""
    baseline_path = REV / 'before-manifest.json'
    require(sha(baseline_path) == BEFORE_SHA256, 'Frozen before-manifest changed.')
    baseline = read(baseline_path)
    manifest = read(ROOT / 'manifest.json')
    before, frames = frame_map(baseline), frame_map(manifest)
    expected_timing = {**baseline['timing'], 'runCycleMs': 960, 'runFrameMs': 60,
                       'E': [60] * 16, 'otherRunDirections': [60] * 16,
                       'rationale': manifest['timing']['rationale']}
    require(manifest['timing'] == expected_timing,
            'Only the authorized run timing may change:16 x60ms=960ms.')
    require(len({f['sha256'] for f in frames.values()}) == FRAME_COUNT,
            'Duplicate final frame digests.')
    for key, frame in frames.items():
        old = before[key]
        for field in ('action', 'direction', 'index', 'path', 'sourceRecord',
                      'phase', 'support', 'events'):
            require((field in frame, frame.get(field)) == (field in old, old.get(field)),
                    f'{key}: {field} differs from frozen baseline.')
        require(frame['durationMs'] == (60 if frame['action'] == 'run' else old['durationMs']),
                f'{key}: only run duration may change to60ms.')
        require(sha(scoped(frame['path'])) == frame['sha256'],
                f'{key}: current PNG digest differs from manifest.')
    return manifest, frames, before


def run_phase_document(frames, require_current=False):
    doc = read(ROOT / 'review/run-phase-review.json')
    require(set(doc['directions']) == set(RUN_DIRECTIONS),
            'Run phase review must cover all eight directions.')
    for direction, rows in doc['directions'].items():
        require(len(rows) == 16 and {r['frame'] for r in rows} == set(range(1, 17)),
                f'{direction}: phase review must contain 16 unique frames.')
        for row in rows:
            key = f"run_{direction}_{row['frame']:02}"
            frame = frames[key]
            for field in ('phase', 'support'):
                require(row[field] == frame[field], f'{key}: stale {field} review.')
            if require_current:
                require(row['sha256'] == frame['sha256'], f'{key}: stale phase SHA.')
            row['sha256'] = frame['sha256']
    if require_current:
        require(doc.get('limbRevision') == SELECTION_PATH,
                'Run phases mode for this revision before acceptance.')
        require(doc.get('limbRevisionBeforeManifestSHA256') == BEFORE_SHA256,
                'Run phase review refers to a different baseline.')
    return doc


def phases():
    _, frames, _ = current_state()
    doc = run_phase_document(frames)
    doc.update({
        'updatedAt': now(),
        'limbRevision': SELECTION_PATH,
        'limbRevisionBeforeManifestSHA256': BEFORE_SHA256,
        'limbRevisionNote': (
            'Hand/foot revision: all196 phase/support/events match the frozen baseline. '
            'Latest direct user correction sets128 run durations to60ms;68 combat durations unchanged. '
            'Current run digests refreshed. '
            'This metadata check is not visual or playback acceptance.'),
    })
    save(ROOT / 'review/run-phase-review.json', doc)
    print('All196 support/phase/event records unchanged; run60ms;128 run digests refreshed.')


def reviewed_state():
    manifest, frames, before = current_state()
    run_phase_document(frames, require_current=True)
    selection = read(REV / 'selection.json')
    selected = selection['selected']
    require(selection.get('staticReviewed') is True, 'Selection is not statically reviewed.')
    require(set(selected) <= set(frames), 'Selection contains unknown frame IDs.')
    changed = {key for key in frames if frames[key]['sha256'] != before[key]['sha256']}
    require(changed == set(selected), 'Changed frames differ from this revision selection.')
    stage = scoped(f'staging/{NAME}')
    for key, path in selected.items():
        require(scoped(path).is_relative_to(stage), f'{key}: selected source outside revision.')
    replacements = read(REV / 'replacement-ledger.json')['replacements']
    ledger = {row['id']: row for row in replacements}
    require(len(replacements) == len(selected) and set(ledger) == set(selected),
            'Replacement ledger does not match selection exactly.')
    for key, row in ledger.items():
        require(row['path'] == frames[key]['path']
                and row['previousSHA256'] == before[key]['sha256']
                and row['newSHA256'] == frames[key]['sha256']
                and scoped(row['source']) == scoped(selected[key]),
                f'{key}: replacement ledger differs from baseline/current selection.')
    review = read(REV / 'final-review.json')
    require(review.get('passed') is True and review.get('scope') == 'offline',
            'This revision requires a passed offline final-review.')
    hashes = {key: frame['sha256'] for key, frame in frames.items()}
    require(review.get('frameSHA256') == hashes,
            'Final review must match all 196 current frame digests exactly.')
    require(isinstance(review.get('method'), str) and review['method'].strip(),
            'Final review must describe the actual hand/foot inspection scope.')
    if 'replacedFrames' in review:
        require(sorted(review['replacedFrames']) == sorted(selected),
                'Final review replacement list differs from current selection.')
    for filename in ('browser-check.json', 'timing-verification.json'):
        require(read(REV / filename).get('passed') is True,
                f'This revision requires passed {filename}.')
    return manifest, frames, review, sorted(selected)


@contextmanager
def previous_revision():
    # Keep the original routine and all its boundary/ledger assertions intact.
    require(__debug__, 'Do not use optimized Python: inherited safety assertions are required.')
    old_revisions, old_rev = previous.REVISIONS, previous.REV
    previous.REVISIONS, previous.REV = list(REVISIONS), REV
    try:
        yield
    finally:
        previous.REVISIONS, previous.REV = old_revisions, old_rev


def accept():
    manifest, frames, review, selected = reviewed_state()
    records = []
    for key, frame in frames.items():
        path = scoped(frame['sourceRecord'])
        record = read(path)
        require(record['sha256'] == frame['sha256'], f'{key}: source record digest mismatch.')
        records.append((path, record))
    revisions = {name: sorted(read(ROOT / 'review' / name / 'selection.json')['selected'])
                 for name in REVISIONS}
    # Validate all five prompt collections before changing acceptance flags.
    with previous_revision():
        previous.prompt_indexes()
    scope = f'Hand/foot revision; offline only. See {REVIEW_PATH}. {review["method"]}'
    for frame in frames.values():
        frame['visualApproved'] = True
        frame['visualReviewScope'] = scope
    for path, record in records:
        record['visualApproved'] = True
        save(path, record)
    manifest.update({
        'formalAccepted': True, 'updatedAt': now(),
        'currentReview': {
            'status': 'offline_complete', 'record': REVIEW_PATH,
            'replacedFrames': selected, 'revisions': revisions,
            'handFootReviewScope': review.get('detailedScope', review['method']),
            'client': 'not_tested',
        },
        'note': (
            f'196 independent frames; {len(selected)} hand/foot revision replacements. '
            'Phase, support-leg identity and events unchanged from frozen baseline; '
            'latest direct user correction: run16 x60ms=960ms; combat durations unchanged. '
            'Actual review scope is recorded in the current '
            'limb-axis final-review; offline acceptance only.'),
    })
    save(ROOT / 'manifest.json', manifest)
    save(ROOT / 'review/final-visual-review.json', {
        'reviewedAt': now(), 'offlineAccepted': True, 'scope': review['method'],
        'acceptedSHA256': review['frameSHA256'], 'revisionReview': REVIEW_PATH,
        'replacedFrames': selected, 'clientTested': False,
    })
    save(ROOT / 'preview/progress.json', {
        'frames': FRAME_COUNT, 'offlineAccepted': FRAME_COUNT, 'clientIntegrated': 0,
    })
    require(build_html() == 0, 'Failed to rebuild current preview HTML.')
    print(f'Accepted 196 current offline frames; {len(selected)} replacements in {NAME}.')


def cleanup():
    manifest, _, review, _ = reviewed_state()
    require(manifest.get('formalAccepted') is True
            and all(f.get('visualApproved') is True for f in manifest['frames']),
            'Current delivery has not been accepted.')
    current_review = manifest.get('currentReview', {})
    require(current_review.get('record') == REVIEW_PATH
            and current_review.get('status') == 'offline_complete',
            'Manifest acceptance belongs to a different revision.')
    final = read(ROOT / 'review/final-visual-review.json')
    require(final.get('offlineAccepted') is True
            and final.get('revisionReview') == REVIEW_PATH
            and final.get('acceptedSHA256') == review['frameSHA256'],
            'Current final-visual acceptance is missing or stale.')
    with previous_revision():
        previous.cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['phases', 'accept', 'cleanup'])
    globals()[parser.parse_args().mode]()
