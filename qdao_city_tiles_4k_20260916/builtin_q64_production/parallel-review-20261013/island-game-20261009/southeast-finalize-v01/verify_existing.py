from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import gc
from PIL import Image, ImageChops

ROOT = Path('D:/work/image')
REVIEW = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009'
AUDIT = REVIEW / 'southeast-audit-v01'
OUT = Path(__file__).resolve().parent
Image.MAX_IMAGE_PIXELS = None

def now():
    return datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write_new(name, data):
    with (OUT / name).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def image_sha(im):
    # No conversion, resize, compositing, color adjustment or save is performed.
    return hashlib.sha256(im.tobytes()).hexdigest()

def ref_check(ref):
    p = Path(ref['file'])
    result = {'file': str(p), 'expectedSha256': ref.get('sha256')}
    try:
        before = p.stat()
        result['actualSha256'] = sha(p)
        after = p.stat()
        result.update(bytes=after.st_size, mtimeNs=after.st_mtime_ns,
                      changedDuringRead=(before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns),
                      hashMatches=result['actualSha256'] == result['expectedSha256'])
    except (OSError, ValueError) as e:
        result.update(error=str(e), hashMatches=False, changedDuringRead=False)
    return result

started = now()
snapshot = read(AUDIT / 'snapshot-inputs.json')
with ThreadPoolExecutor(max_workers=3) as pool:
    checks = list(pool.map(ref_check, snapshot['inputs']))
changed = [x for x in checks if not x['hashMatches'] or x['changedDuringRead']]
write_new('source-recheck.json', {
    'schemaVersion': 1, 'zone': 'southeast', 'startedAtUtc': started,
    'finishedAtUtc': now(), 'snapshotCreatedAtUtc': snapshot['createdAtUtc'],
    'snapshotFile': str(AUDIT / 'snapshot-inputs.json'),
    'snapshotSha256AtRead': sha(AUDIT / 'snapshot-inputs.json'),
    'inputCount': len(checks), 'hashMatchedCount': sum(x['hashMatches'] for x in checks),
    'changedOrUnreadableCount': len(changed), 'snapshotStale': bool(changed),
    'nativeReconstructionAuditRerun': False,
    'scope': 'SHA-256 reread of previously inventoried inputs only; no re-run of 444 native reconstruction audit',
    'changes': changed, 'inputs': checks,
})
print(f'snapshot inputs {len(checks)}; changed/unreadable {len(changed)}', flush=True)

group_results = []
for group_name in ['g01-r09-r10-c12-c13', 'g02-r11-r12-c11-c12']:
    manifest_path = AUDIT / group_name / 'manifest.json'
    m = read(manifest_path)
    assembly_ref = ref_check(m['nativeAssembly'])
    source_refs = [ref_check(x) for x in m['inputs']]
    quadrants = []
    crop_checks = []
    contact_checks = []
    with Image.open(m['nativeAssembly']['file']) as opened:
        assembly = opened.copy()
    for inp, ref in zip(m['inputs'], source_refs):
        x, y = inp['groupOrigin']
        with Image.open(inp['file']) as src:
            src.load()
            box = [x, y, x + src.width, y + src.height]
            cut = assembly.crop(box)
            input_pixel_sha = image_sha(src)
            quadrant_pixel_sha = image_sha(cut)
            match = src.mode == cut.mode and src.size == cut.size and input_pixel_sha == quadrant_pixel_sha
            quadrants.append({
                'tileId': inp['tileId'], 'inputFile': inp['file'], 'groupBox': box,
                'inputMode': src.mode, 'assemblyCropMode': cut.mode,
                'inputSize': list(src.size), 'assemblyCropSize': list(cut.size),
                'inputFileHashMatchesManifest': ref['hashMatches'],
                'inputPixelSha256': input_pixel_sha, 'assemblyCropPixelSha256': quadrant_pixel_sha,
                'pixelExact': match, 'comparedPixels': src.width * src.height,
            })
            cut.close()
    by_id = {x['id']: x for x in m['crops']}
    for c in m['crops']:
        if 'groupSourceBox' not in c:
            continue
        expected = assembly.crop(c['groupSourceBox'])
        with Image.open(c['file']) as actual:
            actual.load()
            ep, ap = image_sha(expected), image_sha(actual)
            crop_checks.append({
                'id': c['id'], 'file': c['file'], 'groupSourceBox': c['groupSourceBox'],
                'fileSha256MatchesManifest': sha(c['file']) == c['sha256'],
                'expectedPixelSha256': ep, 'actualPixelSha256': ap,
                'pixelExact': expected.mode == actual.mode and expected.size == actual.size and ep == ap,
                'dimensions': list(actual.size), 'resampled': False,
            })
        expected.close()
    # Validate only corrected contact panels. The v01 panels stay preserved and excluded.
    for c in m['crops']:
        if not c['id'].endswith('-v02') or 'displayOrder' not in c:
            continue
        with Image.open(c['file']) as panel:
            cells = []
            for k, child_id in enumerate(c['displayOrder']):
                child = by_id[child_id]
                with Image.open(child['file']) as crop:
                    crop.load()
                    x, y = (k % 2) * crop.width, (k // 2) * crop.height
                    cell = panel.crop([x, y, x + crop.width, y + crop.height])
                    cp, pp = image_sha(crop), image_sha(cell)
                    cells.append({'childId': child_id, 'cropPixelSha256': cp,
                                  'panelCellPixelSha256': pp,
                                  'pixelExact': crop.mode == cell.mode and crop.size == cell.size and cp == pp})
                    cell.close()
            contact_checks.append({'id': c['id'], 'file': c['file'],
                                   'fileSha256MatchesManifest': sha(c['file']) == c['sha256'],
                                   'cells': cells, 'pixelExact': all(x['pixelExact'] for x in cells)})
    group = {
        'groupId': m['groupId'], 'manifest': str(manifest_path),
        'manifestSha256AtRead': sha(manifest_path), 'assembly': assembly_ref,
        'assemblyDimensions': list(assembly.size), 'assemblyMode': assembly.mode,
        'sources': source_refs, 'quadrants': quadrants, 'crops': crop_checks,
        'correctedContactPanels': contact_checks,
        'excludedContactPanels': [c['file'] for c in m['crops'] if c.get('excludedReason')],
        'sourceStale': any(not x['hashMatches'] or x['changedDuringRead'] for x in source_refs),
        'allQuadrantsPixelExact': all(x['pixelExact'] for x in quadrants),
        'allNativeCropsPixelExact': all(x['pixelExact'] and x['fileSha256MatchesManifest'] for x in crop_checks),
        'allCorrectedContactsPixelExact': all(x['pixelExact'] and x['fileSha256MatchesManifest'] for x in contact_checks),
        'formalAccepted': False,
    }
    group_results.append(group)
    assembly.close()
    gc.collect()
    print(f'{group_name}: {len(quadrants)} quadrants / {len(crop_checks)} native crops exact={group["allQuadrantsPixelExact"] and group["allNativeCropsPixelExact"]}', flush=True)

break_manifest = read(AUDIT / 'breakpoints/manifest.json')
breakpoints = []
for b in break_manifest['breakpoints']:
    ref = ref_check(b)
    src_refs = [ref_check(s) for s in b['sources']]
    with Image.open(b['file']) as panel:
        panel.load()
        pieces = []
        for s in b['sources']:
            with Image.open(s['file']) as source:
                expected = source.crop(s['sourceCrop'])
                x, y = s.get('destination', [0, 0])
                actual = panel.crop([x, y, x + expected.width, y + expected.height])
                ep, ap = image_sha(expected), image_sha(actual)
                pieces.append({'sourceFile': s['file'], 'sourceCrop': s['sourceCrop'],
                               'destination': [x, y], 'expectedPixelSha256': ep,
                               'actualPixelSha256': ap,
                               'pixelExact': expected.mode == actual.mode and expected.size == actual.size and ep == ap})
                expected.close()
                actual.close()
    breakpoints.append({'id': b['id'], 'file': b['file'], 'fileCheck': ref,
                        'sourceChecks': src_refs, 'pieces': pieces,
                        'sourceStale': any(not x['hashMatches'] or x['changedDuringRead'] for x in src_refs),
                        'pixelExact': all(x['pixelExact'] for x in pieces), 'formalAccepted': False})

checks_pass = all(g['assembly']['hashMatches'] and not g['assembly']['changedDuringRead'] and
                  not g['sourceStale'] and g['allQuadrantsPixelExact'] and
                  g['allNativeCropsPixelExact'] and g['allCorrectedContactsPixelExact']
                  for g in group_results)
checks_pass = checks_pass and all(b['fileCheck']['hashMatches'] and not b['fileCheck']['changedDuringRead'] and
                                  not b['sourceStale'] and b['pixelExact'] for b in breakpoints)
result = {
    'schemaVersion': 1, 'zone': 'southeast', 'startedAtUtc': started, 'finishedAtUtc': now(),
    'sourceSnapshotStale': bool(changed), 'sourceRecheck': str(OUT / 'source-recheck.json'),
    'operation': 'Read-only SHA-256 comparison of encoded files and raw image pixels; no output images created',
    'noImageConversionOrResampling': True,
    'quadrantsChecked': sum(len(g['quadrants']) for g in group_results),
    'fullTilePixelsCompared': sum(x['comparedPixels'] for g in group_results for x in g['quadrants']),
    'nativeCropsChecked': sum(len(g['crops']) for g in group_results),
    'correctedContactPanelsChecked': sum(len(g['correctedContactPanels']) for g in group_results),
    'breakpointImagesChecked': len(breakpoints), 'allMechanicalChecksPassed': checks_pass,
    'groups': group_results, 'breakpoints': breakpoints,
    'formalAccepted': False, 'newGenerationPerformed': False, 'productionModified': False,
}
write_new('pixel-verification.json', result)
print(json.dumps({k: result[k] for k in ['sourceSnapshotStale', 'quadrantsChecked', 'fullTilePixelsCompared', 'nativeCropsChecked', 'correctedContactPanelsChecked', 'breakpointImagesChecked', 'allMechanicalChecksPassed']}, ensure_ascii=False), flush=True)
