"""Local-only, immutable production helpers for the six reserved island east tiles.

This module never calls an image model or imports an original-zone production tool.
All output paths are confined to this file's batch directory. Every command rereads
root AGENTS.md. Mutating artwork commands require current root allocation or valid acknowledgement.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

BATCH = Path(__file__).resolve().parent
ROOT = next(p for p in BATCH.parents if (p / 'AGENTS.md').is_file())
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
MAP = BASE / 'island-game-20261009'
ACK = BASE / 'parallel-production-20261013/coordination/island-east-residences.owner-ack.json'
TILES = [f'r{r:02d}_c{c:02d}' for r in (1, 2) for c in (10, 11, 12)]
SIZE, CORE, HALO, WORLD = 1254, 1024, 115, 57344
CORE_CROP = [115, 115, 1139, 1139]
RX = re.compile(r'^(r(\d{2})_c(\d{2})_p(\d{2})_(\d{2}))_v(\d{2,})$')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def path_text(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def resolve(path):
    p = Path(path)
    if p.is_absolute():
        if p.exists():
            return p
        # Historical owner metadata stores the old root. Resolve in memory only.
        s = str(p).replace('\\', '/')
        if '/qdao_city_tiles_4k_20260916/' in s:
            return ROOT / ('qdao_city_tiles_4k_20260916/' + s.split('/qdao_city_tiles_4k_20260916/', 1)[1])
        return p
    return ROOT / p


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def writable(path):
    p = Path(path).resolve()
    if not p.is_relative_to(BATCH) or p == BATCH:
        raise ValueError(f'Output outside batch is forbidden: {p}')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path, value):
    p = writable(path)
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    return p


def write_text(path, value):
    p = writable(path)
    with p.open('x', encoding='utf-8') as f:
        f.write(value)
    return p


def save_png(path, image):
    p = writable(path)
    with p.open('xb') as f:
        image.save(f, format='PNG')
    return p


def copy_exact(source, target):
    p = writable(target)
    with Path(source).open('rb') as src, p.open('xb') as dst:
        shutil.copyfileobj(src, dst)
    if sha(source) != sha(p):
        raise ValueError('Exact source copy hash mismatch')
    return p


def version_path(folder, stem, suffix='.json'):
    folder = writable(Path(folder) / 'unused').parent
    for n in range(1, 1000000):
        p = folder / f'{stem}-v{n:03d}{suffix}'
        if not p.exists() and not Path(str(p) + '.derivation.json').exists():
            return p
    raise ValueError('Version range exhausted')


def gate(required=False):
    # Read the complete current instructions for every invocation, not a cached hash.
    rules = (ROOT / 'AGENTS.md').read_text(encoding='utf-8-sig')
    out = {'checkedAtUtc': now(), 'rootAGENTS': path_text(ROOT / 'AGENTS.md'),
           'rootAGENTSSha256': hashlib.sha256((ROOT / 'AGENTS.md').read_bytes()).hexdigest(),
           'rootAGENTSReadCharacters': len(rules), 'ownerAck': path_text(ACK),
           'exists': ACK.is_file(), 'ready': False, 'conflictsEmpty': False,
           'reservedTilesCoverAllSix': False, 'allowed': False}
    if ACK.is_file():
        a = read_json(ACK)
        reserved = a.get('reservedTiles', [])
        out.update({'ownerAckSha256': sha(ACK), 'ready': a.get('ready') is True,
                    'conflictsEmpty': a.get('activeConflicts') == [],
                    'reservedTilesCoverAllSix': isinstance(reserved, list) and set(TILES).issubset(set(reserved)),
                    'reservedTiles': reserved, 'activeConflicts': a.get('activeConflicts')})
        out['allowed'] = out['ready'] and out['conflictsEmpty'] and out['reservedTilesCoverAllSix']
    split_path = ROOT / 'docs/MAP_PARALLEL_SPLIT_20261013.json'
    split = read_json(split_path)
    allocation = next((b for b in split.get('batches', []) if b.get('key') == BATCH.name), {})
    root_reserved = (
        split.get('status') == 'allocated_root_reserved'
        and allocation.get('status') == 'allocated_root_reserved'
        and set(TILES) == set(allocation.get('tiles', []))
        and resolve(allocation.get('outputDirectory', '__missing__')).resolve() == BATCH
        and allocation.get('worker') == '01a1338b-be72-7411-ab4e-834155818bfb'
    )
    out.update(allocationManifest=path_text(split_path), allocationManifestSha256=sha(split_path),
               rootReserved=root_reserved, authorizationBasis='allocated_root_reserved' if root_reserved else 'owner_ack',
               ownerAcknowledged=out['ready'], allowed=root_reserved or out['allowed'])
    if required and not out['allowed']:
        raise ValueError('COORDINATE_ALLOCATION_GATE_FAILED ' + json.dumps(out, ensure_ascii=False))
    return out


def geometry(core_version):
    m = RX.fullmatch(core_version)
    if not m:
        raise ValueError('Expected r02_c12_p04_04_v01 style CORE_VERSION')
    co, r, c, pr, pc, v = m.groups()
    r, c, pr, pc = map(int, (r, c, pr, pc))
    tile = f'r{r:02d}_c{c:02d}'
    if tile not in TILES or not (1 <= pr <= 4 and 1 <= pc <= 4):
        raise ValueError('Core is outside this six-tile batch')
    x, y = (c - 1) * 4096 + (pc - 1) * CORE, (r - 1) * 4096 + (pr - 1) * CORE
    return {'id': core_version, 'coordinate': co, 'tileId': tile, 'version': int(v),
            'coreWorldBox': [x, y, x + CORE, y + CORE],
            'nativeWorldBox': [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            'coreCrop': CORE_CROP, 'tileLocalPaste': [(pc - 1) * CORE, (pr - 1) * CORE]}


def reference(path, role, expected=None):
    p = resolve(path)
    with Image.open(p) as im:
        dims = list(im.size)
    digest = sha(p)
    if expected and digest != expected:
        raise ValueError(f'Reference hash changed: {p}')
    return {'file': path_text(p), 'sha256': digest, 'dimensions': dims, 'role': role}


def references():
    contract = read_json(MAP / 'production-contract.json')
    return [reference(contract['layoutReference'], 'sole approved full-map layout authority; overview is layout only', contract.get('layoutSha256')),
            reference(contract['detailStyleReference'], 'material style only, not a coordinate crop', contract.get('detailSha256')),
            reference(ROOT / 'designs/mail-ui-v1/01-mail-event.png', 'primary Daoist Q hand-painted style; do not copy UI, text, people or night scene'),
            reference(ROOT / 'designs/team-ui-v2/team-ui-v2.png', 'primary Daoist Q hand-painted style; do not copy UI, text or people')]


def latest_selection(tile):
    files = sorted((BATCH / 'selections' / tile).glob('selection-v*.json'))
    return (files[-1], read_json(files[-1])) if files else (None, {'tileId': tile, 'selected': {}})


def checked_source(nid, file, expected, record, authority):
    f = resolve(file)
    gp = resolve(record)
    g = read_json(gp)
    digest = sha(f)
    with Image.open(f) as im:
        dims = list(im.size)
    if dims != [SIZE, SIZE] or digest != expected or g.get('sha256') != digest:
        raise ValueError(f'Native path/hash/dimensions changed: {nid}')
    if g.get('coreCrop') != CORE_CROP or not g.get('coreWorldBox') or not g.get('nativeWorldBox'):
        raise ValueError(f'Native geometry record missing or unsupported: {nid}')
    return {'id': nid, 'file': path_text(f), 'sha256': digest, 'dimensions': dims,
            'generationRecord': path_text(gp), 'generationRecordSha256': sha(gp),
            'coreWorldBox': g['coreWorldBox'], 'nativeWorldBox': g['nativeWorldBox'],
            'coreCrop': CORE_CROP, 'selectionAuthority': path_text(authority),
            'selectionAuthoritySha256': sha(authority)}


def selected_sources():
    """Resolve current owner selections on every call; never glob historical images."""
    out = []
    for tile in TILES:
        sp, s = latest_selection(tile)
        for n in s['selected'].values():
            out.append(checked_source(n['id'], n['file'], n['sha256'], n['generationRecord'], sp))
    # South boundary plus the southeast corner core, which can touch the first guide.
    for c in (10, 11, 12, 13):
        tile = f'r03_c{c:02d}'
        sp = MAP / 'northeast' / f'selection-{tile}.json'
        s = read_json(sp)
        for nid in s['cores'][0]:
            if nid:
                f = MAP / 'northeast/native' / f'{nid}.png'
                gp = Path(str(f) + '.generation.json')
                g = read_json(gp)
                out.append(checked_source(nid, f, g['sha256'], gp, sp))
    sp = MAP / 'accelerated-northeast-coast/current-selection-20261012.json'
    s = read_json(sp)
    for candidate in s['candidates']:
        tile = candidate['tileId']
        if tile not in ('r01_c13', 'r02_c13'):
            continue
        natives = {n['id']: n for n in s['native'][tile]}
        for row in candidate['selectedCores']:
            nid = row[0]
            n = natives[nid]
            gp = str(n['file']) + '.generation.json'
            out.append(checked_source(nid, n['file'], n['sha256'], gp, sp))
    return out


def intersection(a, b):
    v = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return v if v[0] < v[2] and v[1] < v[3] else None


def touches(source, target):
    a, b = source['coreWorldBox'], target['coreWorldBox']
    return source['id'].split('_v')[0] != target['coordinate'] and abs(a[0] - b[0]) <= CORE and abs(a[1] - b[1]) <= CORE


def neighbor_sources(g):
    return sorted([n for n in selected_sources() if touches(n, g)], key=lambda n: (n['coreWorldBox'][1], n['coreWorldBox'][0], n['id']))


def assert_current_neighbors(inputs):
    expected = {(n['id'], n['sha256']) for n in inputs['neighbors']}
    current = {(n['id'], n['sha256']) for n in neighbor_sources(inputs['geometry'])}
    if not expected.issubset(current):
        raise ValueError('A captured selected neighbor/hash changed since prepare; prepare a new CORE_VERSION')
    for ref in inputs['references']:
        if sha(resolve(ref['file'])) != ref['sha256']:
            raise ValueError(f'Prepared reference changed: {ref["file"]}')


def guide_layout(layout_ref, box):
    with Image.open(resolve(layout_ref['file'])) as im:
        im = im.convert('RGB')
        # Replicate the overview edge into its guide-only halo, avoiding black padding.
        pad = 8
        padded = Image.new('RGB', (im.width + pad * 2, im.height + pad * 2))
        padded.paste(im, (pad, pad))
        padded.paste(im.crop((0, 0, im.width, 1)).resize((im.width, pad)), (pad, 0))
        padded.paste(im.crop((0, im.height - 1, im.width, im.height)).resize((im.width, pad)), (pad, pad + im.height))
        padded.paste(im.crop((0, 0, 1, im.height)).resize((pad, im.height)), (0, pad))
        padded.paste(im.crop((im.width - 1, 0, im.width, im.height)).resize((pad, im.height)), (pad + im.width, pad))
        for x, y, sx, sy in [(0, 0, 0, 0), (pad + im.width, 0, im.width - 1, 0),
                              (0, pad + im.height, 0, im.height - 1),
                              (pad + im.width, pad + im.height, im.width - 1, im.height - 1)]:
            padded.paste(im.getpixel((sx, sy)), (x, y, x + pad, y + pad))
        extent = [box[0] * im.width / WORLD + pad, box[1] * im.height / WORLD + pad,
                  box[2] * im.width / WORLD + pad, box[3] * im.height / WORLD + pad]
        return padded.transform((SIZE, SIZE), Image.Transform.EXTENT, extent, Image.Resampling.BILINEAR)


def command_plan(args):
    state = gate()
    refs = references()
    cores = [geometry(f'{tile}_p{r:02d}_{c:02d}_v01') for tile in TILES for r in range(1, 5) for c in range(1, 5)]
    value = {'schemaVersion': 1, 'createdAtUtc': now(), 'batch': BATCH.name, 'tiles': TILES,
             'coreCount': len(cores), 'formalTileSize': 4096, 'nativeSize': SIZE, 'halo': HALO,
             'gate': state, 'references': refs, 'cores': cores,
             'actualModel': None, 'modelMetadataStatus': '未返回',
             'imagePolicy': 'Prefer existing/free 2.5; existing built-in 2.0 allowed if unavailable; no paid API.'}
    p = write_json(version_path(BATCH / 'plans', 'plan'), value)
    return {'plan': path_text(p), 'coreCount': len(cores), 'gate': state, 'references': refs}


def command_prepare(args):
    state = gate(not getattr(args, 'preflight', False))
    g = geometry(args.core_version)
    folder = writable(BATCH / 'prepared' / args.core_version / 'unused').parent
    if any(folder.iterdir()):
        raise FileExistsError(f'Prepared version already exists: {folder}')
    refs, neighbors = references(), neighbor_sources(g)
    base_native = getattr(args, 'base_native', None)
    base_record = None
    if base_native:
        bp = Path(base_native).resolve()
        if not bp.is_relative_to(BATCH / 'native') or bp.stem.split('_v')[0] != g['coordinate']:
            raise ValueError('Repair base must be an existing batch native of this same coordinate')
        with Image.open(bp) as bi:
            if bi.size != (SIZE, SIZE):
                raise ValueError('Repair base must be native1254 square')
            guide = bi.convert('RGB')
        base_record = reference(bp, 'previous native candidate used unchanged at native size before exact neighbor anchoring')
    else:
        guide = guide_layout(refs[0], g['nativeWorldBox'])
    layers, conflicts = [], []
    mask = Image.new('1', guide.size)
    # Native halo context is useful but not independently selected artwork. Record
    # conflicting halo pixels, then adopt disjoint selected core pixels as authority.
    for role in ('native_overlap_context', 'selected_neighbor_core'):
        for n in neighbors:
            world = intersection(g['nativeWorldBox'], n['nativeWorldBox'] if role == 'native_overlap_context' else n['coreWorldBox'])
            if not world:
                continue
            crop = [world[0] - n['nativeWorldBox'][0], world[1] - n['nativeWorldBox'][1],
                    world[2] - n['nativeWorldBox'][0], world[3] - n['nativeWorldBox'][1]]
            paste = [world[0] - g['nativeWorldBox'][0], world[1] - g['nativeWorldBox'][1],
                     world[2] - g['nativeWorldBox'][0], world[3] - g['nativeWorldBox'][1]]
            with Image.open(resolve(n['file'])) as im:
                pixels = im.convert('RGB').crop(crop)
            if role == 'native_overlap_context':
                old = guide.crop(paste)
                diff = ImageChops.difference(old, pixels).convert('RGB')
                changed = diff.convert('L').point(lambda v: 255 if v else 0)
                overlap = mask.crop(paste).convert('L')
                count = sum(v > 0 for v in ImageChops.multiply(changed, overlap).getdata())
                if count:
                    conflicts.append({'sourceId': n['id'], 'worldBox': world, 'conflictingContextPixelCount': count})
                mask.paste(1, paste)
            guide.paste(pixels, paste[:2])
            layers.append({'sourceId': n['id'], 'source': n['file'], 'sha256': n['sha256'],
                           'role': role, 'worldBox': world, 'sourceCrop': crop, 'targetPaste': paste,
                           'operation': 'exact copy; no scaling or blending'})
    guide_path = save_png(folder / 'guide.png', guide)
    guide_ref = reference(guide_path, 'edit target; enlarged overview is layout only; exact native anchors are immutable')
    attached = [guide_ref]
    if neighbors:
        plate = Image.new('RGB', (SIZE * len(neighbors), SIZE))
        for i, n in enumerate(neighbors):
            with Image.open(resolve(n['file'])) as im:
                plate.paste(im.convert('RGB'), (i * SIZE, 0))
        pp = save_png(folder / 'native-neighbors.png', plate)
        attached.append(reference(pp, 'unscaled native neighbors left to right: ' + ', '.join(n['id'] for n in neighbors)))
        # Keep both approved UI references attached separately while honoring the
        # built-in entry's five-reference limit. Layout and material are copied
        # unscaled into one clearly described reference plate.
        with Image.open(resolve(refs[0]['file'])) as li, Image.open(resolve(refs[1]['file'])) as di:
            li, di = li.convert('RGB'), di.convert('RGB')
            lp = Image.new('RGB', (li.width + di.width, max(li.height, di.height)), (245,245,240))
            lp.paste(li, (0,0)); lp.paste(di, (li.width,0))
        lpp = save_png(folder / 'layout-and-material-reference.png', lp)
        combined = reference(lpp, 'left: full 1254-square approved map layout authority; right: material close-up only, not a coordinate crop; both exact unscaled copies')
        combined['sources'] = [refs[0], refs[1]]
        attached.extend([combined, refs[2], refs[3]])
    else:
        attached.extend(refs)
    prompt = f'''EDIT THE FIRST INPUT IMAGE IN PLACE. Produce one native {SIZE}x{SIZE} daylight Daoist Q hand-painted map patch, {args.core_version}.
This is an EXTREME CLOSE-UP COORDINATE CROP, not a composed scene, not an overview, not a new illustration of the whole map. Keep exactly the first image's framing, scale and crop. Do not pull the camera back, shrink the objects, or fit complete buildings into the canvas. The overview reference is context only, never the output composition.
Target core world rectangle: {g['coreWorldBox']}; native rectangle including 115px halo: {g['nativeWorldBox']}.
The sole approved layout is the attached full-map reference. Preserve existing buildings, courtyards, identity props, roads and coastline exactly. Do not add or move residences or expand the coast.
The attached guide's blurry enlarged overview is coordinate layout only: replace blur with genuine native detail at the neighboring pixels' CLOSE-UP scale. Preserve all sharp recorded neighboring selected-core anchors in the guide exactly; native halo strips are geometric/color context and must join continuously. Continue the cut-off object fragments and surfaces, do not complete off-canvas objects. Keep exact overlap geometry; no rectangular color bands, feathering, blur or collage seams.
Only recorded neighbor CORE pixels outside the central square are fixed: left x<115, right x>=1139, top y<115, bottom y>=1139 where present. Sharp old neighboring HALO pixels INSIDE [115,115,1139,1139] are editable context. Redraw them when necessary to make continuous objects, removing rectangular transitions at x230, x1024, y230, y1024. Do not preserve a sharp strip merely because it is sharp.
Match the attached mail and team images' fine Daoist Q hand-painted style: rounded forms, jade/teal accents, warm ivory, restrained fine gold, soft modeled shading. Use natural pale grey/blue-grey stone. Daylight, Spring Festival details on existing architecture, sparse lantern/Mid-Autumn accents; trees near existing buildings/walls. No UI, text, NPCs, grids, watermarks or night scene.
The central [115,115,1139,1139] crop is the new 1024 core. Output exactly 1254 square if supported; never upscale an overview or call it finished art. References in attached order: {', '.join(r['role'] for r in attached)}.
'''
    focus = getattr(args, 'focus', None)
    focus_record = None
    if focus:
        fp = Path(focus).resolve()
        if not fp.is_relative_to(BATCH):
            raise ValueError('Focus specification must be inside the batch')
        prompt += '\nEXACT LOCAL SUBJECT AND INVARIANTS:\n' + fp.read_text(encoding='utf-8-sig')
        focus_record = {'file': path_text(fp), 'sha256': sha(fp)}
    prompt_path = write_text(folder / 'prompt.txt', prompt)
    value = {'schemaVersion': 1, 'createdAtUtc': now(), 'geometry': g, 'gate': state,
             'prompt': path_text(prompt_path), 'promptSha256': sha(prompt_path), 'references': attached,
             'auxiliaryMaterialReference': refs[1], 'neighbors': neighbors,
             'guide': path_text(guide_path), 'guideSha256': sha(guide_path),
             'guideIsFinalArt': False, 'actualModel': None, 'actualQuality': None,
             'submittedModel': None, 'submittedQuality': None, 'modelMetadataStatus': '未返回',
             'focusSpecification': focus_record, 'repairBase': base_record}
    write_json(folder / 'guide.derivation.json', {'geometry': g, 'layoutReference': refs[0],
                'layoutOperation': 'previous native candidate copied unscaled before neighbor anchoring' if base_record else 'overview crop enlarged for layout only; replicated guide-only outer halo',
                'repairBase': base_record,
                'layers': layers, 'contextConflicts': conflicts,
                'overlapResolution': 'context in recorded order; disjoint selected-neighbor core rectangles pasted last, exact unscaled; no feathering',
                'finalArtUpscaled': False, 'guideIsFinalArt': False, 'guideSha256': sha(guide_path)})
    p = write_json(folder / 'inputs.json', value)
    return {'inputs': path_text(p), 'guide': path_text(guide_path), 'prompt': path_text(prompt_path),
            'references': attached, 'neighborCount': len(neighbors), 'contextConflictCount': len(conflicts)}


def prepared(core_version):
    geometry(core_version)
    folder = BATCH / 'prepared' / core_version
    inputs = read_json(folder / 'inputs.json')
    if sha(resolve(inputs['prompt'])) != inputs['promptSha256']:
        raise ValueError('Prepared prompt changed; use a new version')
    assert_current_neighbors(inputs)
    return folder, inputs


def command_ingest(args):
    state = gate(True)
    _, inputs = prepared(args.core_version)
    source = Path(args.source).resolve()
    target = copy_exact(source, BATCH / 'native' / f'{args.core_version}.png')
    with Image.open(target) as im:
        dims, fmt, mode = list(im.size), im.format, im.mode
    receipt = {'receiptProvided': bool(args.receipt), 'originalSourcePath': source.as_posix(),
               'nativeSha256': sha(target), 'actualModel': None, 'actualQuality': None,
               'metadataStatus': '未返回; do not infer actual model from target/config or coordinating model'}
    receipt_path = BATCH / 'receipts' / f'{args.core_version}.receipt.json'
    if args.receipt:
        receipt_path = copy_exact(Path(args.receipt), receipt_path)
    else:
        write_json(receipt_path, receipt)
    value = {**inputs['geometry'], 'file': path_text(target), 'sha256': sha(target),
             'createdAtUtc': now(), 'nativeWidth': dims[0], 'nativeHeight': dims[1], 'format': fmt, 'mode': mode,
             'eligibleForSelection': dims == [SIZE, SIZE] and fmt == 'PNG',
             'status': 'candidate_unreviewed' if dims == [SIZE, SIZE] and fmt == 'PNG' else 'rejected_native_dimensions_or_format',
             'sourceFile': source.as_posix(), 'sourceFileSha256': sha(source),
             'resizedAfterGeneration': False, 'finalArtUpscaled': False, 'native4kGeneration': False,
             'prompt': inputs['prompt'], 'promptSha256': inputs['promptSha256'],
             'references': inputs['references'], 'preparedInputs': path_text(BATCH / 'prepared' / args.core_version / 'inputs.json'),
             'preparedInputsSha256': sha(BATCH / 'prepared' / args.core_version / 'inputs.json'),
             'receipt': path_text(receipt_path), 'receiptSha256': sha(receipt_path), 'gate': state,
             'route': 'existing_builtin; external call performed by main agent',
             'actualModel': None, 'actualQuality': None, 'submittedModel': None,
             'submittedQuality': None, 'modelMetadataStatus': '未返回'}
    p = write_json(Path(str(target) + '.generation.json'), value)
    return {'native': path_text(target), 'record': path_text(p), 'sha256': value['sha256'],
            'dimensions': dims, 'eligibleForSelection': value['eligibleForSelection']}


def ingested(core_version):
    geometry(core_version)
    p = BATCH / 'native' / f'{core_version}.png'
    record = read_json(Path(str(p) + '.generation.json'))
    if not record['eligibleForSelection'] or sha(p) != record['sha256']:
        raise ValueError('Native is not an eligible unchanged 1254-square PNG')
    with Image.open(p) as im:
        if im.size != (SIZE, SIZE):
            raise ValueError('Native dimensions changed')
    return p, record


def command_evidence(args):
    state = gate(True)
    native, rec = ingested(args.core_version)
    g = geometry(args.core_version)
    ns = neighbor_sources(g)
    manifest = version_path(BATCH / 'evidence' / args.core_version, 'evidence')
    folder = manifest.parent / manifest.stem
    folder.mkdir(exist_ok=False)
    with Image.open(native) as im:
        own = im.convert('RGB').crop(CORE_CROP)
    cp = save_png(folder / 'core-100pct.png', own)
    evidence = [{'file': path_text(cp), 'sha256': sha(cp), 'size': [CORE, CORE],
                 'role': 'whole native core', 'status': 'pending_visual_review'}]
    x, y = g['coreWorldBox'][:2]
    for n in ns:
        nx, ny = n['coreWorldBox'][:2]
        with Image.open(resolve(n['file'])) as im:
            neighbor = im.convert('RGB').crop(CORE_CROP)
        side, canvas, crops = None, None, None
        if nx == x and ny == y - CORE:
            side, canvas = 'top', Image.new('RGB', (CORE, 384))
            crops = [(neighbor, [0, 832, 1024, 1024], [0, 0]), (own, [0, 0, 1024, 192], [0, 192])]
        elif nx == x and ny == y + CORE:
            side, canvas = 'bottom', Image.new('RGB', (CORE, 384))
            crops = [(own, [0, 832, 1024, 1024], [0, 0]), (neighbor, [0, 0, 1024, 192], [0, 192])]
        elif nx == x - CORE and ny == y:
            side, canvas = 'left', Image.new('RGB', (384, CORE))
            crops = [(neighbor, [832, 0, 1024, 1024], [0, 0]), (own, [0, 0, 192, 1024], [192, 0])]
        elif nx == x + CORE and ny == y:
            side, canvas = 'right', Image.new('RGB', (384, CORE))
            crops = [(own, [832, 0, 1024, 1024], [0, 0]), (neighbor, [0, 0, 192, 1024], [192, 0])]
        if not side:
            continue
        for image, crop, paste in crops:
            canvas.paste(image.crop(crop), paste)
        ep = save_png(folder / f'{side}-192-each-side-100pct.png', canvas)
        evidence.append({'file': path_text(ep), 'sha256': sha(ep), 'size': list(canvas.size),
                         'side': side, 'neighbor': n, 'operation': 'exact native1024 core crops;192 pixels each side; no resizing/blending',
                         'status': 'pending_visual_review'})
    value = {'id': args.core_version, 'createdAtUtc': now(), 'native': path_text(native),
             'nativeSha256': rec['sha256'], 'inspectionScale': 1, 'resized': False,
             'status': 'pending_visual_review', 'gate': state, 'evidence': evidence,
             'unavailableCardinalSides': [s for s in ('top', 'bottom', 'left', 'right') if s not in [e.get('side') for e in evidence]]}
    write_json(manifest, value)
    return {'evidence': path_text(manifest), 'images': evidence, 'status': 'pending_visual_review'}


def command_select(args):
    state = gate(True)
    native, rec = ingested(args.core_version)
    _, inputs = prepared(args.core_version)
    review_source = Path(args.review_json).resolve()
    review = read_json(review_source)
    if review.get('pass') is not True or review.get('nativeSha256') != rec['sha256']:
        raise ValueError('Review must have pass:true and matching nativeSha256')
    g = geometry(args.core_version)
    previous, selection = latest_selection(g['tileId'])
    if selection['selected'].get(g['coordinate'], {}).get('id') == args.core_version:
        raise ValueError('This exact core version is already selected')
    selection_path = version_path(BATCH / 'selections' / g['tileId'], 'selection')
    review_copy = copy_exact(review_source, BATCH / 'reviews' / f'{args.core_version}-{selection_path.stem}.json')
    chosen = {'id': args.core_version, 'coordinate': g['coordinate'], 'file': path_text(native),
              'sha256': rec['sha256'], 'generationRecord': path_text(str(native) + '.generation.json'),
              'coreWorldBox': g['coreWorldBox'], 'nativeWorldBox': g['nativeWorldBox'],
              'coreCrop': CORE_CROP, 'review': path_text(review_copy), 'reviewSha256': sha(review_copy)}
    selected = dict(selection['selected'])
    selected[g['coordinate']] = chosen
    value = {'schemaVersion': 1, 'tileId': g['tileId'], 'createdAtUtc': now(), 'gate': state,
             'previousSelection': path_text(previous) if previous else None,
             'previousSelectionSha256': sha(previous) if previous else None,
             'selected': selected, 'selectedCoreCount': len(selected),
             'completeNativeCoreCoverage': len(selected) == 16, 'formalAccepted': False}
    write_json(selection_path, value)
    return {'selection': path_text(selection_path), 'selectedCoreCount': len(selected), 'formalAccepted': False}


def command_assemble(args):
    state = gate(True)
    tile = args.tile
    if tile not in TILES:
        raise ValueError('Tile outside owned batch')
    sp, s = latest_selection(tile)
    required = {f'{tile}_p{r:02d}_{c:02d}' for r in range(1, 5) for c in range(1, 5)}
    if set(s['selected']) != required:
        raise ValueError(f'16 selected cores required; missing {sorted(required - set(s["selected"]))}')
    canvas = Image.new('RGB', (4096, 4096))
    sources = []
    for co in sorted(required):
        n = s['selected'][co]
        native, rec = ingested(n['id'])
        if sha(native) != n['sha256']:
            raise ValueError('Selection/native hash mismatch')
        g = geometry(n['id'])
        with Image.open(native) as im:
            canvas.paste(im.convert('RGB').crop(CORE_CROP), g['tileLocalPaste'])
        sources.append({**n, 'tileLocalPaste': g['tileLocalPaste'], 'operation': 'exact1024 native crop; no scale or feather'})
    cp = version_path(BATCH / 'candidates', tile, '.png')
    save_png(cp, canvas)
    r, c = map(int, re.fullmatch(r'r(\d+)_c(\d+)', tile).groups())
    value = {'tileId': tile, 'createdAtUtc': now(), 'file': path_text(cp), 'sha256': sha(cp),
             'size': [4096, 4096], 'worldBox': [(c - 1) * 4096, (r - 1) * 4096, c * 4096, r * 4096],
             'selection': path_text(sp), 'selectionSha256': sha(sp), 'sources': sources, 'gate': state,
             'operation': '16 exact unscaled [115,115,1139,1139] crops pasted into4096 candidate',
             'baseCoverageMin': 1, 'baseCoverageMax': 1, 'uncoveredPixels': 0,
             'finalArtUpscaled': False, 'native4kGeneration': False,
             'status': 'complete_native_coverage_pending_whole_tile_and_external_review', 'formalAccepted': False,
             'actualModel': None, 'actualQuality': None, 'modelMetadataStatus': '未返回'}
    dp = write_json(Path(str(cp) + '.derivation.json'), value)
    return {'candidate': path_text(cp), 'derivation': path_text(dp), 'sha256': value['sha256'], 'formalAccepted': False}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('plan')
    g = sub.add_parser('gate'); g.add_argument('--required', action='store_true')
    for name in ('prepare', 'evidence'):
        p = sub.add_parser(name); p.add_argument('core_version')
        if name == 'prepare':
            p.add_argument('--preflight', action='store_true', help='Mechanical preparation only; does not authorize an image call')
            p.add_argument('--focus', help='Local text file with exact cropped subject constraints')
            p.add_argument('--base-native', help='Existing same-coordinate native candidate for localized repair guide')
    p = sub.add_parser('ingest'); p.add_argument('core_version'); p.add_argument('source'); p.add_argument('--receipt')
    p = sub.add_parser('select'); p.add_argument('core_version'); p.add_argument('review_json')
    p = sub.add_parser('assemble'); p.add_argument('tile')
    args = parser.parse_args()
    try:
        if args.command == 'gate':
            result = gate(args.required)
        else:
            result = globals()['command_' + args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, FileNotFoundError, FileExistsError, KeyError, TypeError, OSError) as e:
        print(json.dumps({'error': str(e), 'command': args.command, 'outputsAreImmutable': True}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
