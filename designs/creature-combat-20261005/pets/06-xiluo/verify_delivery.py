"""Build the delivery manifest and audit real generated frames; never creates poses.
Usage: python verify_delivery.py [--allow-partial] [--contact-sheets]
Outputs: manifest.json, qa/technical-validation.json, optional six contact sheets.
No mutation of PNGs or source generation records. Exit 1 when incomplete/invalid
unless --allow-partial permits missing frames (other errors still fail).
"""
import argparse, hashlib, json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SPECS = {'hit': (6, 40, 2), 'attack': (12, 30, 7), 'cast': (16, 45, 10)}
IDENTITIES = [
    ROOT.parents[2] / 'pets-xianling-20260924/source/06-xiluo-E.png',
    ROOT.parents[2] / 'pets-xianling-20260924/source/06-xiluo-W.png',
    ROOT.parents[2] / 'attribute-panels/v2-painted/01-character-ui-no-affinity.png',
]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def norm(path):
    return str(Path(path).resolve()).replace('\\', '/').casefold()

def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def refs_of(rec):
    result = []
    for item in rec.get('references', []):
        p = item if isinstance(item, str) else item.get('path', item.get('file'))
        if p:
            result.append(p)
    return result

def receipt_refs(rec):
    for candidate in [rec.get('arguments', {}).get('referenced_image_paths'),
                      rec.get('references'), rec.get('submittedParameters', {}).get('referenced_image_paths')]:
        if candidate:
            return [x if isinstance(x, str) else x.get('path', x.get('file')) for x in candidate]
    return []

def inspect_frame(action, direction, number, native_index):
    count, ms, event_at = SPECS[action]
    rel = f'runtime/{action}/{direction}/{number:02}.png'
    rec_rel = f'records/{action}/{direction}/{number:02}.json'
    entry = {'file': rel, 'action': action, 'direction': direction, 'frame': number,
             'durationMs': ms, 'pivot': [0.5, 0.08], 'anchorTopLeft': [512, 942],
             'event': {'hit': 'damage', 'attack': 'attack_hit', 'cast': 'cast_release'}[action] if number == event_at else None,
             'generationRecord': rec_rel, 'status': 'missing'}
    errors, warnings = [], []
    p = ROOT / rel
    if not p.is_file():
        return entry, errors, warnings
    entry['status'] = 'present'
    entry['sha256'] = digest(p)
    try:
        with Image.open(p) as im:
            im.load()
            entry.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
            if im.size != (1024, 1024) or im.mode != 'RGBA' or im.format != 'PNG':
                errors.append('Expected 1024x1024 RGBA PNG')
            alpha = im.convert('RGBA').getchannel('A')
            b0 = alpha.getbbox()
            b16 = alpha.point(lambda x: 255 if x > 16 else 0).getbbox()
            b128 = alpha.point(lambda x: 255 if x > 128 else 0).getbbox()
            entry['alpha'] = {'extrema': list(alpha.getextrema()), 'bboxAbove0': b0,
                              'bboxAbove16': b16, 'bboxAbove128': b128,
                              'fullyTransparentPixels': alpha.histogram()[0]}
            entry['pixelSha256'] = hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
            if alpha.getextrema() != (0, 255):
                errors.append('Expected both transparent and opaque alpha regions')
            if b16 and (b16[0] == 0 or b16[1] == 0 or b16[2] == im.width or b16[3] == im.height):
                warnings.append('Alpha >16 touches canvas boundary; visually inspect clipping')
    except Exception as exc:
        errors.append(f'PNG unreadable: {exc}')
    if not (ROOT / rec_rel).is_file():
        errors.append('Generation record missing')
        return entry, errors, warnings
    try:
        rec = read_json(ROOT / rec_rel)
        entry['generationRecordSha256'] = digest(ROOT / rec_rel)
        for key in ['generatedAt', 'tool', 'route', 'configSnapshot', 'actualModel', 'actualQuality',
                    'unverifiedReason', 'native', 'operation', 'visualReview']:
            if key not in rec:
                errors.append(f'Record field missing: {key}')
        if rec.get('sha256') != entry['sha256']:
            errors.append('PNG SHA mismatch with generation record')
        if norm(resolve(rec.get('file', ''))) != norm(p):
            errors.append('Record file path mismatch')
        for key, value in [('action', action), ('direction', direction), ('frame', number),
                           ('durationMs', ms), ('width', 1024), ('height', 1024)]:
            if rec.get(key) != value:
                errors.append(f'Record {key} mismatch')
        for key in ['model', 'quality']:
            if key not in rec.get('submittedParameters', {}):
                errors.append(f'submittedParameters.{key} missing')
        if (rec.get('actualModel') is None or rec.get('actualQuality') is None) and not rec.get('unverifiedReason'):
            errors.append('Unknown model/quality missing explanation')
        if not rec.get('configSnapshot', {}).get('sources'):
            errors.append('Config snapshot lacks source evidence')
        expected_offset = [0, 28 if direction == 'E' else -13]
        op = rec.get('operation', {})
        if op.get('offset') != expected_offset or abs(op.get('scale', 0) - 1024 / 1254) > 1e-9 or op.get('perFrameAlignment') is not False:
            errors.append('Export does not use fixed directional whole-canvas transform')
        prompt = rec.get('prompt')
        receipt = rec.get('evidence', {}).get('receipt')
        entry['prompt'] = prompt
        entry['receipt'] = receipt
        for label, value in [('prompt', prompt), ('receipt', receipt)]:
            if not value or not resolve(value).is_file():
                errors.append(f'Missing {label} evidence')
            else:
                entry[label + 'Sha256'] = digest(resolve(value))
        if receipt and resolve(receipt).is_file():
            r = read_json(resolve(receipt))
            rr = {norm(resolve(x)) for x in receipt_refs(r) if x}
            declared = {norm(resolve(x)) for x in refs_of(rec)}
            if not declared.issubset(rr):
                errors.append('Record references do not match receipt submitted references')
        actual_refs = {norm(resolve(x)) for x in refs_of(rec)}
        for mandatory in IDENTITIES:
            if norm(mandatory) not in actual_refs:
                errors.append(f'Mandatory identity/style reference absent: {mandatory.name}')
        reference_checks = []
        for reference in refs_of(rec):
            path = resolve(reference)
            historical = native_index.get(norm(path))
            state = 'available' if path.is_file() else 'historical_source_recorded' if historical else 'missing_untracked'
            item = {'path': reference, 'status': state}
            if path.is_file():
                item['sha256'] = digest(path)
            elif historical:
                item['sourceEvidence'] = historical
                item['dependencyRole'] = 'historical_generation_input_not_runtime_dependency'
            else:
                errors.append(f'Untracked missing reference: {reference}')
            reference_checks.append(item)
        entry['references'] = reference_checks
        native = rec.get('native', {})
        native_path = resolve(native.get('path', ''))
        if not native.get('sha256') or not native.get('width') or not native.get('height'):
            errors.append('Native dimensions/SHA missing')
        if native_path.is_file() and digest(native_path) != native.get('sha256'):
            errors.append('Native SHA mismatch')
        entry['native'] = dict(native, currentlyAvailable=native_path.is_file(),
                               auditStatus='available_sha_verified' if native_path.is_file() else 'historical_sha_recorded_pixels_removed',
                               requiredForRuntime=False)
        entry['actualModel'] = rec.get('actualModel')
        entry['actualQuality'] = rec.get('actualQuality')
        entry['configTarget'] = rec.get('configSnapshot')
        entry['visualReview'] = rec.get('visualReview')
        entry['dynamicReview'] = rec.get('dynamicReview', 'not_verified')
    except Exception as exc:
        errors.append(f'Record audit exception: {exc}')
    return entry, errors, warnings

def contact_sheet(action, direction, count):
    cols = 4
    size, header = 320, 28
    rows = (count + cols - 1) // cols
    canvas = Image.new('RGB', (cols * size, rows * (size + header)), '#1d2b32')
    draw = ImageDraw.Draw(canvas)
    for index in range(count):
        x = index % cols * size
        y = index // cols * (size + header)
        draw.text((x + 10, y + 8), f'{action} {direction} {index + 1:02}', fill='#ecddbb')
        p = ROOT / f'runtime/{action}/{direction}/{index + 1:02}.png'
        if p.exists():
            with Image.open(p) as im:
                image = im.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
                canvas.paste(image, (x, y + header), image)
        else:
            draw.text((x + 80, y + 150), 'MISSING', fill='#ff7777')
    target = ROOT / 'qa' / f'{action}-{direction}-contact.jpg'
    canvas.save(target, quality=93)
    return target.relative_to(ROOT).as_posix()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--contact-sheets', action='store_true')
    args = parser.parse_args()
    (ROOT / 'qa').mkdir(exist_ok=True)
    native_index = {}
    ledger_path = ROOT / 'generation-audit.json'
    if ledger_path.is_file():
        for item in read_json(ledger_path).get('entries', []):
            if item.get('nativePath') and item.get('sha256'):
                native_index[norm(item['nativePath'])] = {
                    'ledger': 'generation-audit.json', 'receipt': item.get('receipt'),
                    'sha256': item['sha256']}
    for rp in (ROOT / 'records').rglob('*.json'):
        try:
            rec = read_json(rp)
            native = rec.get('native', {})
            path = native.get('path') or rec.get('nativePath')
            sha = native.get('sha256')
            if path and sha:
                native_index[norm(path)] = {'record': rp.relative_to(ROOT).as_posix(), 'sha256': sha}
        except (ValueError, OSError):
            pass
    frames, groups, errors, warnings, missing = [], [], [], [], []
    hashes, pixel_hashes = defaultdict(list), defaultdict(list)
    for action, (count, ms, event) in SPECS.items():
        for direction in ['E', 'W']:
            group = []
            for number in range(1, count + 1):
                entry, es, ws = inspect_frame(action, direction, number, native_index)
                frames.append(entry)
                group.append(entry['file'])
                if entry['status'] == 'missing':
                    missing.append(entry['file'])
                for detail in es:
                    errors.append({'file': entry['file'], 'error': detail})
                for detail in ws:
                    warnings.append({'file': entry['file'], 'warning': detail})
                if entry.get('sha256'):
                    hashes[entry['sha256']].append(entry['file'])
                if entry.get('pixelSha256'):
                    pixel_hashes[entry['pixelSha256']].append(entry['file'])
            groups.append({'action': action, 'direction': direction, 'count': count,
                           'durationMs': ms, 'totalDurationMs': count * ms, 'eventFrame': event,
                           'files': group, 'dynamicReview': 'not_verified', 'clientIntegration': 'not_tested'})
    duplicates = [files for files in hashes.values() if len(files) > 1]
    pixel_duplicates = [files for files in pixel_hashes.values() if len(files) > 1]
    for files in pixel_duplicates:
        errors.append({'files': files, 'error': 'Identical RGBA frame pixels'})
    expected_paths = {item['file'] for item in frames}
    extra = [p.relative_to(ROOT).as_posix() for p in (ROOT / 'runtime').rglob('*.png')
             if p.relative_to(ROOT).as_posix() not in expected_paths]
    if extra:
        warnings.append({'warning': 'Unexpected runtime PNGs', 'files': extra})
    now = datetime.now(timezone.utc).isoformat()
    status = 'failed' if errors else 'pending_missing_frames' if missing else 'passed'
    report = {'checkedAt': now, 'technicalStatus': status, 'expectedFrames': 68,
              'presentFrames': 68-len(missing), 'missing': missing, 'errors': errors,
              'warnings': warnings, 'duplicateFileSha256': duplicates,
              'duplicatePixelSha256': pixel_duplicates, 'extraRuntimeFiles': extra,
              'scope': 'Technical audit only; single-frame review is quoted from records. Playback and game integration are separate.',
              'visualPlayback': 'not_asserted_by_this_script', 'clientIntegration': 'not_tested'}
    manifest = {'schemaVersion': 1, 'asset': '06-xiluo', 'name': '汐螺', 'generatedAt': now,
                'technicalStatus': status, 'expectedFrames': 68, 'presentFrames': 68-len(missing),
                'missing': missing, 'canvas': [1024,1024], 'pivot': [0.5,0.08],
                'anchorTopLeft': [512,942], 'directions': {'E': '斜前朝右下', 'W': '真斜后朝左上'},
                'groups': groups, 'frames': frames, 'validation': 'qa/technical-validation.json',
                'preview': 'preview.html', 'visualReview': 'qa/visual-review.json',
                'mediaPreview': 'preview/media-manifest.json', 'clientIntegration': 'not_tested'}
    if args.contact_sheets:
        report['contactSheets'] = [contact_sheet(a,d,n) for a,(n,_,_) in SPECS.items() for d in ['E','W']]
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'qa/technical-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['technicalStatus','expectedFrames','presentFrames','missing','errors','warnings']},ensure_ascii=False,indent=2))
    return 1 if errors or (missing and not args.allow_partial) else 0

if __name__ == '__main__':
    raise SystemExit(main())

