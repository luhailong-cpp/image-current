"""Build this character's read-only offline timing review; never alter source PNGs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import struct

CHAR = Path(__file__).resolve().parents[1]
ROOT = CHAR.parents[3]
PREVIEW = CHAR / 'preview'
OLD = ROOT / 'qdao_original_roster_v13/candidate/01_ice_sword_girl'
PRIOR = ROOT / 'qdao_original_roster_v14_hd/run-correction-20260930/characters/01_ice_sword_girl'
SELECTION = CHAR / 'review/run-E-selection.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path, base=PREVIEW):
    return os.path.relpath(path, base).replace('\\', '/')


def png_size(path):
    data = path.read_bytes()[:24]
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Not a PNG: {path}')
    return list(struct.unpack('>II', data[16:24]))


def write(name, data):
    (PREVIEW / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def selection_snapshot():
    if not SELECTION.exists():
        return {'schemaVersion': 1, 'characterId': CHAR.name, 'direction': 'E',
                'canvasSize': [1024, 1024], 'root': None,
                'timing': {'status': 'trial', 'uniformCycleMs': 1200},
                'frames': [None] * 16, 'snapshotStatus': 'selection_file_not_yet_created'}
    selection = read(SELECTION)
    frames = selection.get('frames', [])
    if len(frames) != 16:
        raise ValueError('Selection must retain exactly 16 slots, including nulls.')
    durations = selection.get('timing', {}).get('frameDurationsMs')
    if durations is not None and (len(durations) != 16 or any(not isinstance(n, (int, float)) or n <= 0 for n in durations)):
        raise ValueError('frameDurationsMs must be 16 strictly positive durations.')
    errors = []
    for index, frame in enumerate(frames, 1):
        if frame is None:
            continue
        if frame.get('frame') != index:
            raise ValueError(f'Selection slot {index} is not labeled frame {index}.')
        if not frame.get('path'):
            raise ValueError(f'Non-null slot {index} lacks path.')
        path = (CHAR / frame['path']).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError(f'Selection must reference a workspace file: {path}')
        if not path.exists():
            frame['previewFileError'] = 'File missing; displayed blank'
            errors.append(f'E{index:02}: missing file')
            continue
        current_sha = sha(path)
        frame['verifiedFileSha256'] = current_sha
        frame['verifiedFileSize'] = png_size(path)
        if frame.get('sha256') and current_sha != frame['sha256']:
            frame['previewFileError'] = 'SHA mismatch; displayed blank'
            errors.append(f'E{index:02}: SHA mismatch')
    selection['snapshotSource'] = '../review/run-E-selection.json'
    selection['snapshotSourceSha256'] = sha(SELECTION)
    selection['snapshotStatus'] = 'embedded_at_build_time'
    selection['fileValidationErrors'] = errors
    return selection


def main():
    PREVIEW.mkdir(exist_ok=True)
    manifest_path = OLD / 'manifest.json'
    source_path = OLD / 'processing/frame-sources.json'
    manifest, sources = read(manifest_path), read(source_path)
    manifest_shas = {f['path']: f['sha256'] for f in manifest['files']}
    frames = []
    for index in range(1, 17):
        key = f'walk/E/{index:02}.png'
        path, source = OLD / key, sources[key]
        digest = sha(path)
        receipt_ref = source.get('generation', {}).get('receipt', {})
        receipt_path = OLD / receipt_ref['path'] if receipt_ref.get('path') else None
        frames.append({
            'frame': index, 'path': relative(path), 'sha256': digest,
            'nativeSize': png_size(path), 'status': 'historical_512_baseline_only',
            'manifestSha256': manifest_shas.get(key),
            'sourceRecordOutputSha256': source.get('output_sha256'),
            'hashesMatch': digest == manifest_shas.get(key) == source.get('output_sha256'),
            'sourceRecordKey': key, 'historicalSource': source.get('source'),
            'historicalPrompt': source.get('prompt'),
            'historicalGeneration': source.get('generation'),
            'historicalReceiptSha256': sha(receipt_path) if receipt_path and receipt_path.exists() else None,
            'historicalReceiptRecordedSha256': receipt_ref.get('sha256'),
            'historicalReceipt': read(receipt_path) if receipt_path and receipt_path.exists() else None,
            'historicalTranslationPx': source.get('translation_px'),
            'historicalAnchorAfterPx': source.get('anchor_after_px'),
            'actualModel': None, 'actualQuality': None,
            'modelQualityEvidence': 'Historical records retained verbatim. No actual model/quality inferred from requested model or processor status.',
            'plannedPhase': None,
            'actualContact': None,
            'notes': '旧512输出；历史最低alpha贴地。未在此预览制作中逐帧标定解剖脚接触。旧passed不授予本次HD或接地通过。'
        })
    baseline = {
        'schemaVersion': 1, 'characterId': CHAR.name, 'direction': 'E',
        'canvasSize': [512, 512],
        'root': {'point': manifest['alignment']['root_px'], 'status': 'historical_minimum_alpha_anchor_only',
                 'definition': '历史输出锚点；按lowest_alpha_gt_8对齐，不能作为可信虚拟根点或鞋底接触证明。'},
        'historicalAlignment': manifest['alignment'],
        'historicalStatus': manifest.get('status'),
        'currentUse': 'timing_baseline_only_not_native_HD_not_grounding_repair',
        'cycleComparisonsMs': [],
        'clientRuntimeVerified': False,
        'sourceManifest': {'path': relative(manifest_path), 'sha256': sha(manifest_path)},
        'sourceRecords': {'path': relative(source_path), 'sha256': sha(source_path)},
        'frames': frames
    }
    selection = selection_snapshot()
    prior_review = read(PRIOR / 'review.json')
    prior_drafts = []
    for path in sorted((PRIOR / 'generation/E').glob('*.png')):
        related = [path.with_name(path.stem + suffix) for suffix in ('.provenance.json', '.receipt.json', '.png.generation.json')]
        prior_drafts.append({'path': relative(path), 'sha256': sha(path), 'nativeSize': png_size(path),
                             'records': [{'path': relative(r), 'sha256': sha(r)} for r in related if r.exists()],
                             'latestPriorFinding': next((f for f in prior_review['findings'] if f['file'] == relative(path, PRIOR)), None),
                             'selectedAutomatically': False})
    audit = {
        'schemaVersion': 1, 'builtAtUtc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Read-only source evidence and offline preview. No source pixels, transforms, shared files or client settings changed.',
        'baseline': {'frames': 16, 'sizes': sorted(set(tuple(f['nativeSize']) for f in frames)),
                     'shaMatchesOldManifestAndSources': all(f['hashesMatch'] for f in frames)},
        'priorReview': {'path': relative(PRIOR / 'review.json'), 'sha256': sha(PRIOR / 'review.json'),
                        'status': prior_review['status'], 'approvedFrames': prior_review['approvedFrames']},
        'priorNativeDrafts': prior_drafts,
        'selectionFilePresent': SELECTION.exists(),
        'selectionSha256': sha(SELECTION) if SELECTION.exists() else None,
        'nativeSelectedSlotCount': sum(f is not None for f in selection['frames']),
        'sourceTransformInPreview': 'Whole original canvas contained in square canvas; no bbox fit, translation, interpolation, duplication or mirroring.',
        'contactEvidence': 'plannedPhase is author intent; actualContact is separately authored visual evidence. Null remains unknown.',
        'browserRuntimeVerification': 'Not determined by builder; see preview/verification.json and QA_NOTES.md for the separately dated browser run.',
        'clientRuntimeVerified': False
    }
    write('baseline-E.json', baseline)
    write('source-audit.json', audit)
    data = json.dumps({'baseline': baseline, 'selection': selection, 'audit': audit}, ensure_ascii=False).replace('</', '<\\/')
    (PREVIEW / 'preview-data.js').write_text('window.PREVIEW_DATA = ' + data + ';\n', encoding='utf-8')
    print(json.dumps({'preview': str(PREVIEW / 'index.html'), 'baselineFrames': 16,
                      'baselineHashesMatch': audit['baseline']['shaMatchesOldManifestAndSources'],
                      'nativeSelectedSlots': audit['nativeSelectedSlotCount'],
                      'selectionErrors': selection.get('fileValidationErrors', [])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
