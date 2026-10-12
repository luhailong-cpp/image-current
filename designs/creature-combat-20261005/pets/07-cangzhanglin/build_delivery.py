"""Build the Cangzhanglin combat manifest, technical audit and six-group preview.

Run with the bundled Python and Pillow. This script never writes runtime frames or
generation records. --dry-run performs the same audit but writes no files.
Exit 0: the technical checks pass; exit 1: incomplete/invalid; exit 2: build error.
Visual review and game integration are deliberately never approved by this script.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[3]
PREVIEW = ROOT / 'preview'
ACTIONS = {'hit': (6, 40, '受击'), 'attack': (12, 30, '普攻'), 'cast': (16, 45, '施法')}
REQUIRED_REFS = (
    'designs/pets-xianling-20260924/source/07-cangzhanglin-E.png',
    'designs/pets-xianling-20260924/source/07-cangzhanglin-W.png',
    'designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png',
)
ANCHOR = [512, 942]
PIVOT = [0.5, 0.08]
SHA = re.compile(r'^[a-fA-F0-9]{64}$')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def display_path(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def normalized(value):
    return str(value).replace('\\', '/').lower().rstrip('/')


def as_path(value, record_path=None):
    if not isinstance(value, str) or not value or '\n' in value:
        return None
    path = Path(value.replace('\\', '/'))
    if path.is_absolute():
        return path
    candidates = [ROOT / path]
    if record_path is not None:
        candidates.append(record_path.parent / path)
    candidates.append(PROJECT / path)
    return next((p for p in candidates if p.exists()), candidates[0])


def permitted_reference(path):
    """Never follow a record into the client or another project."""
    value = normalized(path.resolve())
    return value.startswith(normalized(PROJECT) + '/') or '/.codex/generated_images/' in value


def load_records():
    records, errors = [], []
    for path in sorted((ROOT / 'records').rglob('*.json')):
        # Payloads/jobs/receipts are evidence, not final generation records.
        if any(x in path.name.lower() for x in ('.job.', '.payload.', '.receipt.', '.failed')):
            continue
        try:
            value = json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError, OSError) as exc:
            errors.append({'file': display_path(path), 'error': str(exc)})
            continue
        if not isinstance(value, dict):
            continue
        if path.name.endswith('.generation.json') or (
            SHA.fullmatch(str(value.get('sha256', '')))
            and any(k in value for k in ('native', 'configSnapshot', 'actualModel', 'submittedParameters'))
        ):
            records.append((path, value))
    return records, errors


def expected_record_key(path, record):
    final = record.get('file') or record.get('finalFile') or record.get('outputFile')
    if isinstance(final, str):
        match = re.search(r'runtime[/\\](hit|attack|cast)[/\\]([EW])[/\\](\d+)\.png$', final, re.I)
        if match:
            return match[1].lower(), match[2].upper(), int(match[3])
    animation = record.get('animation') or {}
    action = animation.get('action', record.get('action'))
    direction = animation.get('direction', record.get('direction'))
    number = animation.get('frame', record.get('frame'))
    if action in ACTIONS and direction in ('E', 'W') and str(number).isdigit():
        return action, direction, int(number)
    match = re.search(r'(hit|attack|cast)[-_]([EW])[-_](\d+)', path.name, re.I)
    if match:
        return match[1].lower(), match[2].upper(), int(match[3])
    match = re.fullmatch(r'([EW])[-_](hit|attack|cast)', path.parent.name, re.I)
    number = re.match(r'^(\d+)', path.name)
    if match and number:
        return match[2].lower(), match[1].upper(), int(number[1])
    return None


def is_rejected(path, record):
    return record.get('status', '').lower() in ('rejected', 'superseded') or 'rejected' in path.name.lower() or bool(record.get('supersededBy'))


def select_record(records, key, digest):
    matches = [(p, r) for p, r in records if str(r.get('sha256', '')).lower() == digest]
    method = 'final-png-sha256'
    if not matches:
        matches = [(p, r) for p, r in records if expected_record_key(p, r) == key]
        method = 'frame-identity-fallback'
    if not matches:
        return None, None, None
    matches.sort(key=lambda item: (
        not is_rejected(*item), expected_record_key(*item) == key,
        bool(item[1].get('file')), item[0].name.endswith('.generation.json'),
        str(item[1].get('completedAt') or item[1].get('generatedAt') or '')
    ), reverse=True)
    path, record = matches[0]
    return path, record, method


def reference_entries(record):
    values = record.get('references') or record.get('referenceImages') or []
    if isinstance(values, dict):
        values = list(values.values())
    if not values:
        values = (record.get('submittedParameters') or {}).get('referenced_image_paths') or []
    roles = record.get('referenceRoles') or []
    output = []
    for index, value in enumerate(values):
        if isinstance(value, str):
            item = {'path': value, 'role': roles[index] if index < len(roles) else None}
        elif isinstance(value, (list, tuple)) and value:
            item = {'path': value[0], 'role': value[1] if len(value) > 1 else None}
        elif isinstance(value, dict):
            item = {'path': value.get('path') or value.get('file'),
                    'role': value.get('role') or value.get('purpose'), 'sha256': value.get('sha256')}
        else:
            continue
        if item.get('path'):
            output.append(item)
    return output


def source_digests(records):
    values = {}
    for _, record in records:
        for obj in (record.get('native'), record.get('derivedFrom')):
            if isinstance(obj, dict):
                path = obj.get('path') or obj.get('file')
                if path and SHA.fullmatch(str(obj.get('sha256', ''))):
                    values[normalized(as_path(path))] = obj['sha256']
        native = record.get('native') or {}
        for key in ('source', 'sourcePath'):
            if record.get(key) and SHA.fullmatch(str(native.get('sha256', ''))):
                values[normalized(as_path(record[key]))] = native['sha256']
    return values


def check_prompt(value, record_path):
    if isinstance(value, dict):
        value = value.get('path') or value.get('file') or value.get('text')
    if not isinstance(value, str) or not value.strip():
        return {'valid': False, 'kind': 'missing', 'file': None}
    # A long/multiline actual prompt may be embedded in the generation record.
    if '\n' in value or (len(value) > 180 and not value.lower().endswith(('.txt', '.md'))):
        return {'valid': True, 'kind': 'inline-in-record', 'file': display_path(record_path)}
    path = as_path(value, record_path)
    allowed = path is not None and permitted_reference(path)
    exists = bool(allowed and path.is_file() and path.stat().st_size)
    return {'valid': exists, 'kind': 'file', 'file': display_path(path) if path else value,
            'sha256': sha256(path) if exists else None}


def check_evidence(record, record_path):
    files, inline = [], []

    def visit(value, key=''):
        if isinstance(value, dict):
            for name, item in value.items():
                visit(item, name)
        elif isinstance(value, list):
            for item in value:
                visit(item, key)
        elif isinstance(value, str) and value.strip():
            if '\n' not in value and value.lower().endswith(('.txt', '.json', '.md')):
                path = as_path(value, record_path)
                exists = bool(path and permitted_reference(path) and path.is_file() and path.stat().st_size)
                files.append({'file': display_path(path) if path else value, 'exists': exists,
                              'sha256': sha256(path) if exists else None})
            elif key.lower() in ('outputhint', 'output_hint', 'receipt', 'toolresult', 'result', 'content') and len(value) > 30:
                inline.append(key)

    for name in ('evidence', 'receipt', 'toolResult', 'generationReceipt'):
        visit(record.get(name), name)
    return {'valid': bool((files or inline) and all(x['exists'] for x in files)),
            'files': files, 'inlineFields': inline}


def audit_frame(action, direction, number, records, native_digests):
    path = ROOT / 'runtime' / action / direction / f'{number:02}.png'
    frame = {'frame': number, 'action': action, 'direction': direction, 'file': display_path(path),
             'durationMs': ACTIONS[action][1], 'pivot': PIVOT, 'anchorTopLeft': ANCHOR,
             'event': 'damage' if action == 'attack' and number == 7 else 'cast-release' if action == 'cast' and number == 10 else None,
             'exists': path.is_file(), 'sha256': None, 'visualStatus': 'not-verified-by-build-script',
             'clientIntegration': 'not-tested', 'errors': [], 'warnings': []}
    errors, warnings = frame['errors'], frame['warnings']
    if not frame['exists']:
        errors.append('missing-frame')
        return frame
    frame['sha256'] = sha256(path)
    try:
        with Image.open(path) as im:
            im.load()
            frame.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
            if im.size != (1024, 1024):
                errors.append('size-must-be-1024x1024')
            if im.mode != 'RGBA':
                errors.append('mode-must-be-RGBA')
            if im.format != 'PNG':
                errors.append('format-must-be-PNG')
            rgba = im.convert('RGBA')
            frame['pixelSha256'] = hashlib.sha256(rgba.tobytes()).hexdigest()
            alpha = rgba.getchannel('A')
            hist = alpha.histogram()
            bbox = alpha.getbbox()
            frame['alpha'] = {'extrema': list(alpha.getextrema()), 'transparentPixels': hist[0],
                              'opaquePixels': hist[255], 'partialPixels': sum(hist[1:255]),
                              'bbox': list(bbox) if bbox else None}
            if not hist[0] or not hist[255] or bbox is None:
                errors.append('real-transparent-background-and-visible-subject-required')
            if bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == im.width or bbox[3] == im.height):
                warnings.append('nontransparent-pixels-touch-canvas-edge-review-cropping')
    except (OSError, ValueError) as exc:
        errors.append('png-decode-failed: ' + str(exc))
    record_path, record, method = select_record(records, (action, direction, number), frame['sha256'])
    if record is None:
        errors.append('missing-generation-record')
        return frame
    frame['sourceRecord'] = display_path(record_path)
    frame['sourceRecordSha256'] = sha256(record_path)
    frame['recordMatchMethod'] = method
    if method != 'final-png-sha256':
        errors.append('record-sha256-does-not-match-final-png')
    if is_rejected(record_path, record):
        errors.append('selected-record-is-rejected-or-superseded')
    recorded_file = record.get('file')
    if recorded_file and as_path(recorded_file, record_path).resolve() != path.resolve():
        errors.append('record-file-does-not-match-final-path')
    for dim in ('width', 'height'):
        if record.get(dim) is not None and record[dim] != frame.get(dim):
            errors.append('record-' + dim + '-does-not-match-png')
    config = record.get('configSnapshot') or record.get('configurationTarget') or {}
    submitted = record.get('submittedParameters') or {}
    frame['generation'] = {'targetModel': config.get('model'), 'targetQuality': config.get('quality'),
                           'submittedModel': submitted.get('model'), 'submittedQuality': submitted.get('quality'),
                           'actualModel': record.get('actualModel'), 'actualQuality': record.get('actualQuality'),
                           'generatedAt': record.get('generatedAt'), 'tool': record.get('tool'),
                           'route': record.get('route'), 'unverifiedReason': record.get('unverifiedReason')}
    frame['recordedVisualReview'] = record.get('visualReview', record.get('visualStatus'))
    frame['operation'] = record.get('operation')
    frame['derivedFrom'] = record.get('derivedFrom')
    if config.get('model') is None or config.get('quality') is None:
        errors.append('missing-config-target-model-or-quality')
    if not record.get('generatedAt'):
        errors.append('missing-generation-time')
    if record.get('actualModel') is None or record.get('actualQuality') is None:
        warnings.append('actual-model-or-quality-undisclosed-null-preserved')
    frame['prompt'] = check_prompt(record.get('prompt') or record.get('promptPath'), record_path)
    if not frame['prompt']['valid']:
        errors.append('missing-or-empty-prompt-evidence')
    frame['evidence'] = check_evidence(record, record_path)
    if not frame['evidence']['valid']:
        errors.append('missing-or-empty-tool-receipt-evidence')
    frame['references'] = []
    for item in reference_entries(record):
        ref_path = as_path(item['path'], record_path)
        permitted = ref_path is not None and permitted_reference(ref_path)
        exists = bool(permitted and ref_path.is_file())
        entry = {'file': display_path(ref_path) if ref_path else item['path'], 'role': item.get('role'),
                 'exists': exists, 'permittedScope': permitted, 'recordedSha256': item.get('sha256')}
        if not permitted:
            errors.append('reference-outside-permitted-scope: ' + str(item['path']))
        elif exists:
            entry['sha256'] = sha256(ref_path)
            if item.get('sha256') and entry['sha256'] != item['sha256'].lower():
                errors.append('reference-sha256-mismatch: ' + entry['file'])
        else:
            # The retention policy permits deletion of original/intermediate images
            # after delivery. A source digest must still be retained in text.
            digest = item.get('sha256') or native_digests.get(normalized(ref_path))
            historical = '/staging/' in normalized(ref_path) or '/.codex/generated_images/' in normalized(ref_path)
            entry['historicalSourceDigest'] = digest
            entry['retiredHistoricalSource'] = bool(historical and digest)
            if historical and digest:
                warnings.append('historical-source-file-absent-digest-retained: ' + entry['file'])
            else:
                errors.append('missing-reference: ' + entry['file'])
        frame['references'].append(entry)
    reference_paths = {normalized(as_path(x['file'])) for x in frame['references']}
    for required in REQUIRED_REFS:
        if normalized(PROJECT / required) not in reference_paths:
            errors.append('required-original-reference-not-recorded: ' + required)
    return frame


def create_contact_sheet(group):
    count = group['expectedFrames']
    cols = 3 if count == 6 else 4
    rows = (count + cols - 1) // cols
    tile, caption, margin, gap, header = 320, 30, 18, 12, 48
    width = 2 * margin + cols * tile + (cols - 1) * gap
    height = header + margin + rows * (tile + caption) + (rows - 1) * gap + margin
    sheet = Image.new('RGB', (width, height), '#14202c')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=16)
    draw.text((margin, 14), f"CANGZHANGLIN | {group['direction']} / {group['action'].upper()} | {count} x {group['durationMs']} ms", fill='#edf5fa', font=font)
    for index, frame in enumerate(group['frames']):
        left = margin + (index % cols) * (tile + gap)
        top = header + margin + (index // cols) * (tile + caption + gap)
        cell = Image.new('RGBA', (tile, tile), '#c7cdd3')
        cdraw = ImageDraw.Draw(cell)
        for y in range(0, tile, 20):
            for x in range(0, tile, 20):
                if (x // 20 + y // 20) % 2 == 0:
                    cdraw.rectangle((x, y, x + 19, y + 19), fill='#e0e5e9')
        if frame['exists']:
            try:
                with Image.open(ROOT / frame['file']) as im:
                    cell.alpha_composite(im.convert('RGBA').resize((tile, tile), Image.Resampling.LANCZOS))
            except OSError:
                cdraw.text((90, 148), 'INVALID PNG', fill='#971d35', font=font)
        else:
            cdraw.text((94, 148), 'MISSING', fill='#971d35', font=font)
        sheet.paste(cell.convert('RGB'), (left, top))
        # This overlay exists only in the QA sheet, never in runtime images.
        ax, ay = left + ANCHOR[0] * tile / 1024, top + ANCHOR[1] * tile / 1024
        draw.line((ax - 5, ay, ax + 5, ay), fill='#087c85', width=1)
        draw.line((ax, ay - 5, ax, ay + 5), fill='#087c85', width=1)
        label = f"{group['direction']}-{group['action']}  {index + 1:02}/{count:02}"
        if frame['event']:
            label += '  *'
        draw.text((left + 6, top + tile + 6), label, fill='#f4d894' if frame['event'] else '#edf5fa', font=small)
    out = PREVIEW / 'contact' / f"{group['action']}-{group['direction']}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return display_path(out)


def build(dry_run=False):
    records, parse_errors = load_records()
    digests = source_digests(records)
    groups, flat = [], []
    for direction in ('E', 'W'):
        for action, (count, duration, label) in ACTIONS.items():
            frames = [audit_frame(action, direction, i, records, digests) for i in range(1, count + 1)]
            group = {'id': f'{action}-{direction}', 'action': action, 'direction': direction,
                     'label': label, 'expectedFrames': count, 'presentFrames': sum(f['exists'] for f in frames),
                     'durationMs': duration, 'totalDurationMs': count * duration, 'frames': frames,
                     'contactSheet': f'preview/contact/{action}-{direction}.png'}
            groups.append(group)
            flat.extend(frames)
    by_file_sha, by_pixel_sha = defaultdict(list), defaultdict(list)
    for frame in flat:
        if frame.get('sha256'):
            by_file_sha[frame['sha256']].append(frame['file'])
        if frame.get('pixelSha256'):
            by_pixel_sha[frame['pixelSha256']].append(frame['file'])
    duplicate_files = [paths for paths in by_file_sha.values() if len(paths) > 1]
    duplicate_pixels = [paths for paths in by_pixel_sha.values() if len(paths) > 1]
    expected_paths = {f['file'] for f in flat}
    extra_frames = sorted(display_path(p) for p in (ROOT / 'runtime').rglob('*.png') if display_path(p) not in expected_paths)
    errors = [{'file': f['file'], 'issues': f['errors']} for f in flat if f['errors']]
    warnings = [{'file': f['file'], 'issues': f['warnings']} for f in flat if f['warnings']]
    generated_at = datetime.now(timezone.utc).isoformat()
    passed = not (errors or duplicate_files or duplicate_pixels or extra_frames or parse_errors)
    review_path = ROOT / 'qa' / 'final-review.json'
    review = json.loads(review_path.read_text(encoding='utf-8-sig')) if review_path.is_file() else None
    reviewed_shas = {f['file']: f['sha256'] for f in (review or {}).get('frames', [])}
    review_current = bool(review and len(reviewed_shas) == 68 and all(reviewed_shas.get(f['file']) == f.get('sha256') for f in flat))
    if review_current:
        for frame in flat:
            frame['visualStatus'] = 'reviewed-with-notes'
    manifest = {'schemaVersion': 1, 'pet': '苍嶂麟', 'slug': '07-cangzhanglin', 'generatedAt': generated_at,
                'expectedFrames': 68, 'presentFrames': sum(f['exists'] for f in flat), 'canvas': [1024, 1024],
                'pivot': PIVOT, 'anchorTopLeft': ANCHOR, 'directions': {'E': '斜前朝右下', 'W': '真斜后朝左上'},
                'technicalPassed': passed, 'visualStatus': 'reviewed-with-notes' if review_current else 'not-verified-by-build-script',
                'visualReviewRecord': 'qa/final-review.json' if review_current else None,
                'clientIntegration': 'not-tested', 'groups': groups}
    validation = {'schemaVersion': 1, 'generatedAt': generated_at, 'technicalPassed': passed,
                  'expectedFrames': 68, 'presentFrames': manifest['presentFrames'],
                  'missingFrames': [f['file'] for f in flat if not f['exists']], 'extraFrames': extra_frames,
                  'generationRecordsScanned': len(records), 'recordParseErrors': parse_errors,
                  'duplicateFileSha256': duplicate_files, 'duplicatePixelSha256': duplicate_pixels,
                  'errors': errors, 'warnings': warnings,
                  'referenceFilesAllPresent': all(r['exists'] for f in flat for r in f.get('references', [])) and all('references' in f for f in flat),
                  'requiredIdentityAndStyleReferencesPresent': all((PROJECT / p).is_file() for p in REQUIRED_REFS),
                  'runtimeConsumerReferencesPresent': all(f['exists'] for f in flat),
                  'actualModelAndQualityFullyDisclosed': all(f.get('generation', {}).get('actualModel') is not None and f.get('generation', {}).get('actualQuality') is not None for f in flat),
                  'visualReview': {'status': 'not-performed-by-build-script', 'requires': ['all 68 frames', 'six groups at 1x', 'six groups at 0.25x', 'frame stepping']},
                  'gameIntegration': {'status': 'not-tested', 'clientReadOrWritten': False},
                  'scope': 'runtime frames and evidence only; technical pass does not approve anatomy or animation'}
    if not dry_run:
        if review_current:
            validation['visualReview'] = {'status': 'reviewed-with-notes', 'record': 'qa/final-review.json', 'currentFrameShaMatch': True, 'method': review['method']}
        for group in groups:
            create_contact_sheet(group)
        (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (ROOT / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (ROOT / 'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['file']}\n" for f in flat if f['sha256']), encoding='utf-8')
        data = {'pet': manifest['pet'], 'generatedAt': generated_at, 'expectedFrames': 68,
                'presentFrames': manifest['presentFrames'], 'technicalPassed': passed, 'groups': groups}
        template = (PREVIEW / 'template.html').read_text(encoding='utf-8')
        safe_json = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')
        (PREVIEW / 'index.html').write_text(template.replace('__PREVIEW_DATA__', safe_json), encoding='utf-8')
        for group in groups:
            single = dict(data, groups=[group], expectedFrames=group['expectedFrames'], presentFrames=group['presentFrames'])
            single_json = json.dumps(single, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')
            single_template = template.replace('六组已齐全', '本组已齐全').replace('六组共用播放起点，分别按 40 / 30 / 45 ms 每帧循环。', '按本组原时序循环播放。').replace('六组各', '本组')
            single_template = single_template.replace('<div class="grid" id="groups">', '<div class="grid" style="display:block;max-width:600px" id="groups">')
            (PREVIEW / f"{group['id']}.html").write_text(single_template.replace('__PREVIEW_DATA__', single_json), encoding='utf-8')
    summary = {'technicalPassed': passed, 'presentFrames': manifest['presentFrames'], 'expectedFrames': 68,
               'missingFrames': len(validation['missingFrames']), 'frameErrors': len(errors),
               'duplicatePixelGroups': len(duplicate_pixels), 'recordParseErrors': len(parse_errors),
               'wroteFiles': not dry_run}
    print(json.dumps(summary, ensure_ascii=False))
    if errors:
        print(json.dumps({'errors': errors}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='audit without writing generated delivery files')
    args = parser.parse_args()
    try:
        sys.exit(build(args.dry_run))
    except (OSError, ValueError) as exc:
        print(json.dumps({'buildError': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
