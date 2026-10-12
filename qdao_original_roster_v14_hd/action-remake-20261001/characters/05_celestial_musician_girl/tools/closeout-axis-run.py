"""Close out the 196-frame limb/grip revision only after promotion and browser review.

This module is import-safe. No files are written until every precondition passes.
Run with --check for a read-only readiness check; default execution writes records.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
EV = 'provenance/foot-axis-20261004'
EXPECTED_COUNTS = {'run': 128, 'hit': 12, 'attack': 24, 'cast': 32}
EXPECTED_REPAIRS = 17
BASE_SUCCESSFUL_GENERATIONS = 399
CURRENT_NEW_SLOTS = 194
RETAINED_LEGACY_SLOTS = 2


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def write(path, value):
    (ROOT / path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def slot(row):
    return row['action'], row['direction'], row['frame']


def prompt_entry(row, meta):
    """Preserve each frame's own evidence, including incomplete legacy provenance."""
    generation = meta.get('sourceGeneration') or {}
    submitted = generation.get('submittedParameters') or {}
    prompt = submitted.get('prompt') or generation.get('prompt')
    config = generation.get('configSnapshot') or {}
    return {
        'action': row['action'], 'direction': row['direction'], 'frame': row['frame'],
        'file': row['file'], 'sha256': row['sha256'],
        'nativeSha256': row['nativeSha256'],
        'generationRecord': row['generationRecord'],
        'generationRecordSha256': sha(row['generationRecord']),
        'nativeSourceRecord': meta.get('nativeSourceRecord') or
                              meta.get('source', {}).get('generationRecord'),
        'route': generation.get('route'),
        'targetModel': config.get('model'), 'targetQuality': config.get('quality'),
        'actualModel': generation.get('actualModel'),
        'actualQuality': generation.get('actualQuality'),
        'prompt': prompt,
        'promptAvailability': 'recorded' if prompt else 'historical_not_recorded',
        'promptNote': None if prompt else
            '历史来源未记录可核实提示词；保留来源文字和证据，不按当前批次补造。',
        'references': generation.get('references', []),
        'evidence': generation.get('evidence', {}),
        'source': meta.get('source', {}),
        'sourceGeneration': generation,
        'sourceRetention': meta.get('sourceRetention'),
    }


def prepare():
    promotion = read(EV + '/promotion.json')
    browser = read(EV + '/browser-check.json')
    acceptance = read(EV + '/acceptance.json')
    require(promotion.get('status') == 'complete', 'Promotion is not complete.')
    require(browser.get('passed') is True, 'Browser review has not passed.')
    require(acceptance.get('accepted') is True, 'Visual acceptance has not passed.')
    require(acceptance.get('mandatoryCorrectionsRemaining') == [],
            'Visual acceptance still has mandatory corrections.')
    selection_sha = sha('final-selection.json')
    require(browser.get('finalSelectionSha256') ==
            promotion.get('finalSelectionSha256') == selection_sha,
            'Browser/promotion records do not bind the current final selection.')
    require(promotion.get('finalManifestSha256') == sha('final/manifest.json'),
            'Promoted manifest SHA no longer matches.')
    for field, path in [('rootReviewSha256', EV + '/root-review.json'),
                        ('baselineSha256', EV + '/baseline.json')]:
        require(acceptance.get(field) == sha(path), 'Acceptance evidence changed: ' + path)
    audits = acceptance.get('audits', [])
    require({EV + '/' + name for name in [
        'audit-run-arms.json', 'audit-hit.json', 'audit-attack.json', 'audit-cast.json'
    ]}.issubset({item['file'] for item in audits}), 'All-action audits are incomplete.')
    for audit in audits:
        require(sha(audit['file']) == audit['sha256'],
                'Accepted audit SHA changed: ' + audit['file'])

    rows = read('final-selection.json')
    counts = dict(Counter(row['action'] for row in rows))
    require(counts == EXPECTED_COUNTS and len(rows) == 196, 'Expected 196 final frames.')
    by_slot = {slot(row): row for row in rows}
    require(len(by_slot) == 196, 'Duplicate final slots.')
    require(len({row['sha256'] for row in rows}) == 196 and
            len({row['nativeSha256'] for row in rows}) == 196,
            'Final/native source hashes must remain unique.')

    repairs = acceptance.get('repairs', [])
    repaired_slots = {slot(item) for item in repairs}
    require(len(repairs) == len(repaired_slots) == EXPECTED_REPAIRS,
            'All 17 unique repairs must be accepted before closeout.')
    require(promotion.get('repairs') == len(repairs), 'Promotion repair count disagrees.')
    repaired_counts = {action: sum(item['action'] == action for item in repairs)
                       for action in EXPECTED_COUNTS}
    retained_counts = {action: counts[action] - repaired_counts[action]
                       for action in EXPECTED_COUNTS}
    require(all(value >= 0 for value in retained_counts.values()), 'Invalid repair counts.')
    repaired_combat = sum(value for action, value in repaired_counts.items() if action != 'run')
    retained_combat = sum(value for action, value in retained_counts.items() if action != 'run')
    require(promotion.get('repairedRunFrames') == repaired_counts['run'] and
            promotion.get('repairedCombatFrames') == repaired_combat,
            'Promotion action counts disagree with acceptance.')
    require(acceptance.get('retainedRunFrames') == retained_counts['run'] and
            acceptance.get('unchangedCombatFrames') == retained_combat,
            'Acceptance retained counts disagree.')

    baseline = read(EV + '/baseline.json')['files']
    prompts = []
    for row in rows:
        require(sha(row['file']) == row['sha256'], 'Current PNG SHA changed: ' + row['file'])
        meta = read(row['generationRecord'])
        require(meta['sha256'] == row['sha256'] and
                meta['source']['sha256'] == row['nativeSha256'],
                'Sidecar lineage disagrees: ' + row['file'])
        require(row.get('finalVisualPassed') is True and meta.get('finalVisualPassed') is True,
                'Final frame has not passed visual review: ' + row['file'])
        if slot(row) not in repaired_slots:
            require(baseline[row['file']] == row['sha256'],
                    'Unselected final PNG changed: ' + row['file'])
        prompts.append(prompt_entry(row, meta))
    for item in repairs:
        row = by_slot.get(slot(item))
        require(row is not None and row['sha256'] == item['sha256'] and
                row['nativeSha256'] == item['nativeSha256'],
                'Accepted repair is not the promoted final frame: ' + str(slot(item)))
        review = item.get('visualReview') or {}
        require(review.get('passed') is True and review.get('actuallyViewed') is True,
                'Repair lacks actual visual acceptance: ' + str(slot(item)))

    # Generation records describe native AI results. Exported derivatives do not
    # add generations; duplicate records with the same native hash count once.
    native_hashes = set()
    for path in (ROOT / EV).glob('*.generation.json'):
        generation = read(path.relative_to(ROOT))
        native_hash = generation.get('nativeSha256') or generation.get('sha256')
        require(isinstance(native_hash, str) and len(native_hash) == 64,
                'Native generation record lacks a SHA: ' + path.name)
        native_hashes.add(native_hash)
    require({item['nativeSha256'] for item in repairs}.issubset(native_hashes),
            'A selected repair lacks its native generation record.')
    status = read('STATUS.json')
    require(status['newCurrentCandidateSlots'] == CURRENT_NEW_SLOTS and
            status['priorRetainedCandidateSlots'] == RETAINED_LEGACY_SLOTS,
            'Expected 194 current new slots and two retained legacy sources.')
    return {
        'acceptance': acceptance, 'browser': browser, 'promotion': promotion,
        'rows': rows, 'prompts': prompts, 'counts': counts,
        'repairedCounts': repaired_counts, 'retainedCounts': retained_counts,
        'retainedCombat': retained_combat, 'generationCount': len(native_hashes),
        'status': status, 'selectionSha256': selection_sha,
    }


def main():
    state = prepare()
    repaired = state['repairedCounts']
    retained = state['retainedCounts']
    count = state['generationCount']
    summary = {
        'replacements': sum(repaired.values()), 'repairedByAction': repaired,
        'retainedByAction': retained, 'retainedCombat': state['retainedCombat'],
        'generationsThisRevision': count,
        'successfulGenerationsTotal': BASE_SUCCESSFUL_GENERATIONS + count,
        'allFinalFrames': len(state['rows']),
    }
    if '--check' in sys.argv:
        print(json.dumps(dict(status='ready_without_writes', **summary)))
        return
    now = datetime.now(timezone.utc).isoformat()
    repairs = state['acceptance']['repairs']
    repaired_frames = {}
    for item in repairs:
        repaired_frames.setdefault(item['action'], {}).setdefault(item['direction'], []).append(item['frame'])
    for directions in repaired_frames.values():
        for frames in directions.values():
            frames.sort()
    write(EV + '/selected-prompt-set.json', {
        'createdAt': now, 'scope': 'all 196 current final frames',
        'provenancePolicy': 'Per-frame original evidence; legacy omissions remain explicit.',
        'currentNewSlots': CURRENT_NEW_SLOTS, 'retainedLegacySlots': RETAINED_LEGACY_SLOTS,
        'finalSelectionSha256': state['selectionSha256'], 'frames': state['prompts'],
    })
    status = state['status']
    status.update(
        updatedAt=now, status='offline_artwork_complete_client_pending',
        newSuccessfulGeneratedImages=BASE_SUCCESSFUL_GENERATIONS + count,
        supersededNewImages=BASE_SUCCESSFUL_GENERATIONS + count - CURRENT_NEW_SLOTS,
        latestReferenceReview=EV + '/closeout.json', latestLocalRepairCount=len(repairs))
    status['footAxisReview'] = {
        'status': 'offline_artwork_and_browser_review_passed',
        'scope': 'all 196 frames: legs, foot axes, shoulders, elbows, wrists and qin grip',
        'acceptance': EV + '/acceptance.json', 'browserReview': EV + '/browser-check.json',
        'referenceReview': EV + '/reference-review.json',
        'reviewedFinalFrames': len(state['rows']), 'repairedFramesByAction': repaired_frames,
        'repairedCount': len(repairs), 'repairedByAction': repaired,
        'retainedByAction': retained, 'retainedRunFrames': retained['run'],
        'retainedCombatFrames': state['retainedCombat'],
        'mandatoryCorrectionsRemaining': [], 'clientValidated': False,
    }
    closeout = {
        'completedAt': now, 'status': 'offline_artwork_and_browser_complete_client_pending',
        'allFinalFrames': len(state['rows']), 'reviewedFinalFrames': len(state['rows']),
        'runFrames': state['counts']['run'], 'combatFrames': 196 - state['counts']['run'],
        'independentlyDrawnReplacementSources': len(repairs),
        'repairedByAction': repaired, 'retainedByAction': retained,
        'reusedCorrectRunSources': retained['run'],
        'reusedCorrectCombatSources': state['retainedCombat'],
        'successfulGenerationsBaseline': BASE_SUCCESSFUL_GENERATIONS,
        'successfulGenerationsThisRevision': count,
        'successfulGenerationsTotal': BASE_SUCCESSFUL_GENERATIONS + count,
        'currentNewSlots': CURRENT_NEW_SLOTS, 'retainedLegacySlots': RETAINED_LEGACY_SLOTS,
        'acceptance': EV + '/acceptance.json', 'promotion': EV + '/promotion.json',
        'browser': EV + '/browser-check.json', 'promptSet': EV + '/selected-prompt-set.json',
        'acceptanceSha256': sha(EV + '/acceptance.json'),
        'browserCheckSha256': sha(EV + '/browser-check.json'),
        'finalSelectionSha256': state['selectionSha256'],
        'animationTiming': 'animation-timing.json',
        'animationTimingSha256': sha('animation-timing.json'),
        'timing': {'run': {'frameMs': 75, 'cycleMs': 1200},
                   'hit': {'frameMs': 40, 'cycleMs': 240},
                   'attack': {'frameMs': 30, 'cycleMs': 360},
                   'cast': {'frameMs': 45, 'cycleMs': 720}},
        'mandatoryCorrectionsRemaining': [], 'clientValidated': False,
        'contactFramesByDirection': state['acceptance']['contactFramesByDirection'],
        'cleanupRecord': EV + '/cleanup.json',
        'cleanupStatus': 'See the separate cleanup record; closeout does not perform cleanup.',
    }
    write('STATUS.json', status)
    write(EV + '/closeout.json', closeout)
    print(json.dumps(dict(updated=True, **summary)))


if __name__ == '__main__':
    main()
