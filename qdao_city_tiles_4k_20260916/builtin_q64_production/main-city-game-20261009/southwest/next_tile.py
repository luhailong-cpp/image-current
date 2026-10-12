"""Native-art preparation for r11_c05. Never generates art or changes zone progress."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parent
TILE = 'r11_c05'
T = ROOT / TILE
PREVIOUS = ROOT / 'r10_c05'
ORIGIN = (16384, 40960)
N, C, H = 1254, 1024, 115
OVERLAP = 2 * H
CONTRACT_PATH = ROOT.parent / 'production-contract.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path).resolve()
    if not path.is_relative_to(T.resolve()):
        raise ValueError('Writes are restricted to r11_c05')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pid(r, c):
    if r not in range(1, 5) or c not in range(1, 5):
        raise ValueError('Patch row and column must each be 1..4')
    return f'p{r:02d}_{c:02d}'


def info(r, c):
    name = pid(r, c)
    x, y = ORIGIN[0] + (c - 1) * C, ORIGIN[1] + (r - 1) * C
    return {'id': name, 'row': r, 'column': c,
            'coreWorldBox': [x, y, x + C, y + C],
            'contextWorldBox': [x - H, y - H, x + C + H, y + C + H],
            'nativeCoreBox': [H, H, H + C, H + C]}


def check_file(item):
    path = Path(item['file'])
    if not path.is_file() or sha(path) != item['sha256']:
        raise ValueError(f'Missing or changed recorded input: {path}')
    return path


def contract():
    data = read(CONTRACT_PATH)
    plan = data['nativePatchPlan']
    assert data['artCanvasPixels'] == [65536, 65536]
    assert data['formalTilePixels'] == [4096, 4096]
    assert (plan['expectedNativePixels'], plan['corePixels'], plan['haloPixels']) == (N, C, H)
    assert data['builtinOnly'] and not data['paidApiAllowed']
    check_file({'file': data['layoutReference'], 'sha256': data['layoutSha256']})
    check_file({'file': data['detailStyleReference'], 'sha256': data['detailSha256']})
    return data


def checkpoint(status, **extra):
    write(T / 'checkpoint.json', {'tile': TILE, 'updatedAtUtc': now(), 'status': status,
          'generatedNativeCount': len(list((T / 'native').glob('*.generation.json'))),
          'formalAcceptedCount': 0, 'clientMappingValidated': False,
          'capacity5000Validated': False, **extra})


def init():
    data = contract()
    if list((T / 'native').glob('*.png')):
        raise ValueError('Refusing init after native outputs exist')
    for folder in ('guides', 'native', 'prompts', 'receipts', 'qa', 'output'):
        (T / folder).mkdir(parents=True, exist_ok=True)
    with Image.open(data['layoutReference']) as src:
        overview = src.convert('RGB')
    entries = []
    for r in range(1, 5):
        for c in range(1, 5):
            rec = info(r, c)
            world = rec['contextWorldBox']
            box = [world[0] * overview.width / 65536, world[1] * overview.height / 65536,
                   world[2] * overview.width / 65536, world[3] * overview.height / 65536]
            guide = T / 'guides' / f'{pid(r, c)}.layout-only.png'
            overview.transform((N, N), Image.Transform.EXTENT, box, Image.Resampling.NEAREST).save(guide)
            rec.update({'guide': str(guide), 'guideSha256': sha(guide), 'layoutSourceBox': box,
                        'guideOnly': True, 'gameArt': False,
                        'derivedFrom': [{'file': data['layoutReference'], 'sha256': data['layoutSha256']}],
                        'operation': 'nearest-neighbor layout sampling only; not native game art'})
            write(str(guide) + '.derivation.json', rec)
            entries.append(rec)
    write(T / 'coordinates.json', {'tile': TILE,
          'tileCoreWorldBox': [16384, 40960, 20480, 45056],
          'tileContextWorldBox': [16269, 40845, 20595, 45171],
          'nativePixels': N, 'corePixels': C, 'haloPixels': H,
          'adjacentOverlapPixels': OVERLAP, 'halfOpenCoordinates': True, 'patches': entries})
    write(T / 'batch-evidence.json', {**read(ROOT / 'batch-evidence.json'),
          'copiedAtUtc': now(), 'inheritedFrom': str(ROOT / 'batch-evidence.json'),
          'inheritedEvidenceSha256': sha(ROOT / 'batch-evidence.json'),
          'contractSha256': sha(CONTRACT_PATH),
          'note': 'Same builtin batch configuration target; actual model and quality remain undisclosed.'})
    checkpoint('layout_guides_only', nextStep='Prepare p01_01 using selected refined r10_c05 p04_01.')
    print(json.dumps({'tile': TILE, 'guideCount': len(entries), 'generatedNativeCount': 0}))


def native_source(record_path, expected_coordinates):
    record_path = Path(record_path).resolve()
    rec = read(record_path)
    path = check_file(rec)
    if rec['coordinates'] != expected_coordinates:
        raise ValueError(f'Neighbor coordinates do not match: {record_path}')
    with Image.open(path) as im:
        im.load()
        if im.size != (N, N) or im.format != 'PNG':
            raise ValueError(f'Neighbor is not a native {N}-square PNG: {path}')
        image = im.convert('RGB')
    if rec.get('resizedAfterGeneration') is not False or rec.get('nativePixelsPreserved') is not True:
        raise ValueError(f'Neighbor native provenance is missing: {record_path}')
    return image, {'file': str(path), 'sha256': sha(path),
                   'generationRecord': str(record_path), 'generationRecordSha256': sha(record_path),
                   'coordinates': rec['coordinates']}


def previous_info(c):
    coords = read(PREVIOUS / 'coordinates.json')
    rec = next(p for p in coords['patches'] if p['id'] == pid(4, c))
    return {k: rec[k] for k in ('id', 'row', 'column', 'coreWorldBox', 'contextWorldBox', 'nativeCoreBox')}


def selected_upper(c):
    selection_path = PREVIOUS / 'refinement' / 'selection.json'
    selection = read(selection_path)
    name = pid(4, c)
    record_path = (PREVIOUS / selection[name]).resolve()
    expected = (PREVIOUS / 'refinement' / 'native' / f'{name}.png.generation.json').resolve()
    if record_path != expected:
        raise ValueError(f'{name} must select the refined stone source; original stone is forbidden')
    image, ref = native_source(record_path, previous_info(c))
    ref.update({'selectionFile': str(selection_path), 'selectedRecord': selection[name],
                'sourceTile': 'r10_c05', 'sourcePatch': name})
    return image, ref


def prepare(r, c):
    name, rec, data = pid(r, c), info(r, c), contract()
    if (T / 'native' / f'{name}.png').exists():
        raise ValueError('Refusing to rewrite request after native output exists')
    guide = T / 'guides' / f'{name}.layout-only.png'
    guide_rec = read(str(guide) + '.derivation.json')
    check_file({'file': str(guide), 'sha256': guide_rec['guideSha256']})
    with Image.open(guide) as im:
        seed = im.convert('RGB')
    neighbors = []
    left = None
    if c > 1:
        left, ref = native_source(T / 'native' / f'{pid(r, c - 1)}.png.generation.json', info(r, c - 1))
        seed.paste(left.crop((C, 0, N, N)), (0, 0))
        ref.update({'role': 'left native neighbor; copy rightmost 230 pixels without resampling',
                    'sourceCrop': [C, 0, N, N], 'targetBox': [0, 0, OVERLAP, N],
                    'effectiveTargetBox': [0, OVERLAP, OVERLAP, N]})
        neighbors.append(ref)
    if r == 1:
        upper, ref = selected_upper(c)
    else:
        upper, ref = native_source(T / 'native' / f'{pid(r - 1, c)}.png.generation.json', info(r - 1, c))
    ref.update({'role': 'upper native neighbor; copy bottommost 230 pixels without resampling',
                'sourceCrop': [0, C, N, N], 'targetBox': [0, 0, N, OVERLAP],
                'effectiveTargetBox': [0, 0, N, OVERLAP]})
    neighbors.append(ref)
    corner = {'box': [0, 0, OVERLAP, OVERLAP], 'pasteOrder': ['left when present', 'upper'],
              'priority': 'upper', 'reason': 'Preserve continuous upper row, including r10/r11 external edge.',
              'bothSourcesPresent': left is not None, 'blendingOrResampling': False}
    if left is not None:
        diff = ImageChops.difference(left.crop((C, 0, N, OVERLAP)), upper.crop((0, C, OVERLAP, N)))
        corner.update({'inputCornerMaxAbsDifference': max(v[1] for v in diff.getextrema()),
                       'inputCornerMeanAbsDifference': sum(ImageStat.Stat(diff).mean) / 3,
                       'visualReviewRequired': True})
    seed.paste(upper.crop((0, C, N, N)), (0, 0))
    seed_path = T / 'guides' / f'{name}.continuity-seed.png'
    seed.save(seed_path)
    refs = [{'file': str(seed_path), 'sha256': sha(seed_path),
             'role': 'edit target: coarse layout plus exact native neighbor strips; new native interior required'}]
    for key, role in [('layoutReference', 'approved v9 whole-city geometry only; never render the whole city'),
                      ('detailStyleReference', 'approved clean natural grey stone and daylight material target'),
                      ('primaryStyleReference', 'approved refined rounded Daoist chibi hand-painted style; do not copy UI')]:
        refs.append({'file': data[key], 'sha256': sha(data[key]), 'role': role})
    prompt = f'''Use case: precise-object-edit. Asset: one native game-map detail patch for 五行奇谈, immediately south of the arena fragment. Output one opaque square PNG; requested native canvas 1254x1254.
EDIT IMAGE 1 ONLY at the EXACT framing of patch {name} in tile {TILE}. Its world-art context box is {rec['contextWorldBox']} and central 1024x1024 core is [115,115,1139,1139]. The guide is a tiny close spatial fragment. Do not zoom out, recenter, widen the crop, or make a complete building, arena, city or scene.
Image 2 is the approved city layout, for geometry only. Image 3 is the approved clean natural grey stone and soft daylight reference. Image 4 is the primary refined Daoist chibi painting style: polished rounded forms, clear contours, soft volume; copy no UI, text, people, moon or new scene.
Repaint every coarse interior area of image 1 into genuine crisp native detail, preserving every silhouette, paving direction, tread/riser edge, shadow boundary, curb and clipped object exactly where the guide places it. Keep the established oblique overhead map camera and scale. This crop continues the pale stone arena steps/approach; render only the surfaces actually visible. If the guide shows only stone, retain that close stone crop, with no new props or architecture.
Stone must be CLEAN NATURAL GREY or pale blue-grey limestone: broad calm painted faces, softly rounded bevels, restrained shallow seams, sparse faint hand-painted strokes and gentle smooth tonal variation. No dense cellular stone pattern, marble veins, branching vein networks, flaky fragments, stippling, pebble noise, dirty scratches, or red paving. Do not simulate smooth stone by blur; retain crisp geometry and refined material volume. Preserve any warm wood or red railing already present; never invent a complete emblem or character from partial marks.
CONTINUITY: image 1 contains native neighbor artwork already generated at this exact scale. Its topmost 230 pixels are fixed native context copied from the upper neighbor. Preserve that complete strip, including line intersections, lighting and clean stone finish, and extend each line naturally into the new area. Do not redraw the strip in a different arrangement or add a divider at its edge.
'''
    if c > 1:
        prompt += 'The leftmost 230 pixels below the top strip are fixed native context from the left neighbor. At the top-left 230x230 corner, the upper source takes priority; it was copied last. Preserve that exact corner rather than blending conflicting layouts. Continue left-neighbor lines into the interior with no visible boundary.\n'
    prompt += 'No extra buildings, towers, pots, people, labels, borders, grids, watermarks, text or clutter. Keep any existing festival decoration sparse. Output only this single cropped fragment as newly painted native art; the coarse guide must never be delivered as enlarged final art.\n'
    prompt_path = T / 'prompts' / f'{name}.prompt.txt'
    prompt_path.write_text(prompt, encoding='utf-8')
    request_path = T / 'prompts' / f'{name}.request.json'
    write(request_path, {'prompt': prompt, 'referenced_image_paths': [q['file'] for q in refs],
          'transparent_background': False, 'references': refs, 'neighborSources': neighbors,
          'cornerTreatment': corner, 'coordinates': rec, 'requestedNativePixels': [N, N],
          'submittedParameters': {'model': None, 'quality': None}, 'preparedAtUtc': now()})
    write(str(seed_path) + '.derivation.json', {'file': str(seed_path), 'sha256': sha(seed_path),
          'operation': 'exact native strips pasted onto layout-only guide; not final art',
          'guide': str(guide), 'guideSha256': sha(guide), 'neighbors': neighbors,
          'cornerTreatment': corner, 'nativeStripResampling': False, 'gameArt': False})
    checkpoint('prepared_for_builtin_generation', activePatch=name, request=str(request_path),
               nextStep='Inspect seed and call builtin image_gen with saved prompt and all four reference paths.')
    print(json.dumps({'request': str(request_path), 'seed': str(seed_path), 'neighborCount': len(neighbors)}))


def validate_request(r, c):
    name = pid(r, c)
    req_path = T / 'prompts' / f'{name}.request.json'
    req = read(req_path)
    if req['coordinates'] != info(r, c):
        raise ValueError('Request coordinates changed')
    prompt_path = T / 'prompts' / f'{name}.prompt.txt'
    if prompt_path.read_text(encoding='utf-8') != req['prompt']:
        raise ValueError('Prompt text differs from request')
    for ref in req['references'] + req['neighborSources']:
        check_file(ref)
    for ref in req['neighborSources']:
        check_file({'file': ref['generationRecord'], 'sha256': ref['generationRecordSha256']})
        if ref.get('sourceTile') == 'r10_c05':
            if read(ref['selectionFile']).get(ref['sourcePatch']) != ref['selectedRecord']:
                raise ValueError('Upper tile selection changed; prepare the input again')
    with Image.open(req['references'][0]['file']) as seed:
        seed = seed.convert('RGB')
    for ref in req['neighborSources']:
        target = ref['effectiveTargetBox']
        src_box = list(ref['sourceCrop'])
        if target[1]:
            src_box[1] += target[1]
        with Image.open(ref['file']) as im:
            expected = im.convert('RGB').crop(src_box)
        if seed.crop(target).tobytes() != expected.tobytes():
            raise ValueError('Seed no longer contains exact neighbor pixels')
    return req


def ingest(r, c, source):
    name = pid(r, c)
    if not source:
        raise ValueError('--source is required for ingest')
    req = validate_request(r, c)
    receipt_path = T / 'receipts' / f'{name}.receipt.json'
    receipt = read(receipt_path)
    if receipt.get('status') != 'returned_image' or receipt.get('tool') != 'image_gen.imagegen':
        raise ValueError('Save an actual successful builtin tool receipt before ingestion')
    src, dest = Path(source).resolve(), T / 'native' / f'{name}.png'
    if dest.exists() or Path(str(dest) + '.generation.json').exists():
        raise ValueError('Refusing to overwrite an existing native output or record')
    with Image.open(src) as im:
        im.load()
        width, height, fmt, mode = *im.size, im.format, im.mode
        if fmt != 'PNG':
            raise ValueError('Host source must be a PNG; no conversion is performed')
        metadata = {k: str(v)[:4000] for k, v in im.info.items()}
        opaque = 'A' not in im.getbands() or im.getchannel('A').getextrema() == (255, 255)
    source_sha = sha(src)
    shutil.copy2(src, dest)
    if sha(dest) != source_sha:
        raise RuntimeError('Copied output differs from source')
    prompt_path = T / 'prompts' / f'{name}.prompt.txt'
    record = {'file': str(dest), 'sha256': source_sha, 'generatedAt': now(),
          'generatedAtEvidence': 'Recorded during ingestion; actual generation timestamp undisclosed',
          'width': width, 'height': height, 'format': fmt, 'mode': mode, 'opaque': opaque,
          'tool': 'image_gen.imagegen', 'route': 'builtin',
          'configSnapshot': read(T / 'batch-evidence.json')['configurationSnapshot'],
          'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False},
          'actualModel': None, 'actualQuality': None,
          'unverifiedReason': '宿主管理；工具未披露实际型号和质量，没有将提示词当作显式参数证据。',
          'evidence': {'toolReceipt': str(receipt_path), 'toolReceiptSha256': sha(receipt_path),
                       'pngMetadata': metadata},
          'prompt': str(prompt_path), 'promptSha256': sha(prompt_path),
          'request': str(T / 'prompts' / f'{name}.request.json'),
          'references': req['references'], 'neighborSources': req['neighborSources'],
          'cornerTreatment': req['cornerTreatment'], 'coordinates': req['coordinates'],
          'sourceOutputPath': str(src), 'sourceOutputSha256': source_sha,
          'nativePixelsPreserved': True, 'resizedAfterGeneration': False,
          'formalAccepted': False, 'sizeMatchesPlan': [width, height] == [N, N],
          'visualStatus': 'pending_QA'}
    write(str(dest) + '.generation.json', record)
    checkpoint('native_output_pending_QA', activePatch=name,
               nextStep='Inspect actual output, size and seam geometry before preparing its neighbor.')
    print(json.dumps({'native': str(dest), 'size': [width, height], 'sha256': source_sha,
                      'sizeMatchesPlan': record['sizeMatchesPlan']}))


def validate(r, c):
    req = validate_request(r, c)
    path = T / 'native' / f'{pid(r, c)}.png.generation.json'
    if path.exists():
        native_source(path, info(r, c))
    print(json.dumps({'valid': True, 'tile': TILE, 'patch': pid(r, c),
                      'nativeExists': path.exists(), 'referenceCount': len(req['references']),
                      'exactNeighborStripsVerified': True, 'readOnly': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'prepare', 'ingest', 'validate'])
    parser.add_argument('--row', type=int, default=1)
    parser.add_argument('--col', type=int, default=1)
    parser.add_argument('--source')
    args = parser.parse_args()
    if args.action == 'init':
        init()
    elif args.action == 'prepare':
        prepare(args.row, args.col)
    elif args.action == 'ingest':
        ingest(args.row, args.col, args.source)
    else:
        validate(args.row, args.col)
