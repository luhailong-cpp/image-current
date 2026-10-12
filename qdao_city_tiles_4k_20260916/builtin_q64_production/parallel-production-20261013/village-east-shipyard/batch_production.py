"""Local geometry, provenance and unscaled core assembly for this reserved batch.

No network, image model, Git, or writes outside this batch directory.
Generation itself is performed only by the built-in image_gen tool.
"""
import argparse
import hashlib
import json
import shutil
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
ROOT = BASE.parent.parent
MAP = BASE / 'fishing-village-game-20261009'
ACK = OUT.parent / 'coordination/village-east-shipyard.owner-ack.json'
TILES = ['r10_c11', 'r10_c12', 'r11_c11', 'r11_c12']
CORE, HALO, NATIVE = 1024, 115, 1254
STATE = OUT / 'current-state.json'


@contextmanager
def batch_writer_lock():
    """Serialize short file transactions if two in-batch producers run together."""
    import msvcrt
    p = OUT / 'batch-writer.lock'
    with p.open('a+b') as fh:
        fh.seek(0, 2)
        if fh.tell() == 0:
            fh.write(b'0')
            fh.flush()
        deadline = time.monotonic() + 50
        while True:
            fh.seek(0)
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise RuntimeError('Batch writer transaction timed out; do not overwrite state')
                time.sleep(0.1)
        try:
            yield
        finally:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def info(path, role=None):
    p = Path(path).resolve()
    d = {'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size,
         'sampledAtUtc': now()}
    if role:
        d['role'] = role
    if p.suffix.lower() in ('.png', '.jpg', '.jpeg'):
        with Image.open(p) as im:
            d.update(dimensions=list(im.size), mode=im.mode)
    return d


def save(path, data, overwrite=False):
    p = Path(path).resolve()
    assert p.is_relative_to(OUT), f'Write outside batch rejected: {p}'
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def state():
    return read(STATE) if STATE.exists() else {
        'schemaVersion': 1, 'batch': 'village-east-shipyard', 'tiles': TILES,
        'selected': {}, 'requests': [], 'receipts': [], 'candidates': {},
        'formalAcceptedCount': 0, 'mapComplete': False,
    }


def checkpoint(s, action):
    s['updatedAtUtc'] = now()
    s['lastAction'] = action
    s['selectedCoreCount'] = len(s['selected'])
    s['requiredCoreCount'] = 64
    s['assembledCandidateCount'] = len(s['candidates'])
    i = 1
    while (OUT / f'checkpoints/state-v{i:04d}.json').exists():
        i += 1
    save(OUT / f'checkpoints/state-v{i:04d}.json', s)
    save(STATE, s, overwrite=True)


def gate(required=False):
    split_path = ROOT / 'docs/MAP_PARALLEL_SPLIT_20261013.json'
    split = read(split_path)
    allocation = next((b for b in split.get('batches', []) if b.get('key') == 'village-east-shipyard'), None)
    formally_reserved = bool(allocation and allocation.get('status') == 'allocated_root_reserved'
        and set(allocation.get('tiles', [])) == set(TILES)
        and allocation.get('worker') == '01a1338b-a299-7163-93e7-055f91a79dde'
        and (ROOT / allocation.get('outputDirectory', '')).resolve() == OUT)
    conflicts = []
    for tile in TILES:
        original = MAP / 'southeast' / tile
        selected = original / 'selected-patches.json'
        if selected.is_file():
            for pos, source in read(selected).get('patches', {}).items():
                if source:
                    conflicts.append({'tile': tile, 'patch': pos, 'kind': 'original_owner_selected_source',
                                      'record': info(selected), 'source': source})
        native = original / 'native'
        if native.is_dir():
            for p in native.glob('p*.png'):
                pos = p.name[:3]
                if len(pos) == 3 and pos[1] in '1234' and pos[2] in '1234':
                    conflicts.append({'tile': tile, 'patch': pos, 'kind': 'actual_original_native_file', 'source': info(p)})
    owner_progress = MAP / 'southeast/progress.json'
    progress = read(owner_progress)
    for item in progress.get('inFlightGenerationRequests', []):
        text = json.dumps(item, ensure_ascii=False)
        for tile in TILES:
            if tile in text:
                pos = item.get('patch') if isinstance(item, dict) else None
                conflicts.append({'tile': tile, 'patch': pos, 'kind': 'original_owner_inflight_request',
                                  'request': item, 'record': info(owner_progress)})
    if formally_reserved:
        d = {'readyToGenerate': True, 'authorizationMode': 'allocated_root_reserved',
             'rootInstructions': info(ROOT / 'AGENTS.md'), 'splitContract': info(split_path),
             'allocation': allocation, 'ownerAcknowledged': False,
             'ownerAckExists': ACK.is_file(), 'actualCoordinateConflicts': conflicts,
             'ownerProgressSnapshot': info(owner_progress),
             'meaning': 'Formal root coordinate allocation supersedes old pending-ack gate; no owner acknowledgement is claimed.'}
    elif ACK.is_file():
        a = read(ACK)
        reserved = a.get('reservedTiles', [])
        good = a.get('ready') is True and a.get('activeConflicts') == [] and set(TILES).issubset(set(reserved))
        d = {'readyToGenerate': good, 'ownerAck': info(ACK), 'ackContents': a}
    else:
        d = {'readyToGenerate': False, 'reason': 'no_current_formal_allocation_or_owner_ack', 'path': str(ACK)}
    if required and not d['readyToGenerate']:
        raise RuntimeError('Owner reservation gate is not satisfied: ' + json.dumps(d))
    return d


def geometry(tile, patch):
    assert tile in TILES
    assert len(patch) == 3 and patch[0] == 'p' and patch[1] in '1234' and patch[2] in '1234'
    r, c = int(tile[1:3]), int(tile[5:7])
    sr, sc = int(patch[1]), int(patch[2])
    x, y = (c - 1) * 4096 + (sc - 1) * CORE, (r - 1) * 4096 + (sr - 1) * CORE
    return {'tile': tile, 'patch': patch, 'coreGlobalBox': [x, y, x + CORE, y + CORE],
            'nativeGlobalBox': [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            'coreCrop': [HALO, HALO, HALO + CORE, HALO + CORE],
            'tilePasteAt': [(sc - 1) * CORE, (sr - 1) * CORE],
            'expectedNativeDimensions': [NATIVE, NATIVE]}


def locate_neighbor(s, x, y):
    if x < 0 or y < 0:
        return None
    tile = f'r{y // 4096 + 1:02d}_c{x // 4096 + 1:02d}'
    patch = f'p{y % 4096 // CORE + 1}{x % 4096 // CORE + 1}'
    key = tile + '_' + patch
    if tile in TILES:
        v = s['selected'].get(key)
        if not v:
            return None
        anchor = info(v['path'], f'current selected {key}')
        anchor['continuationAllowed'] = v.get('continuationAllowed', {})
        anchor['reviewStatus'] = v.get('reviewStatus')
        return anchor
    # Only the two specifically authorized western anchors are consumed here.
    if tile not in ('r10_c10', 'r11_c10'):
        return None
    p = MAP / 'southeast' / tile / 'selected-patches.json'
    if not p.is_file():
        return None
    d = read(p)
    v = d.get('patches', {}).get(patch)
    if not isinstance(v, str):
        raise RuntimeError(f'Unsupported current selection schema: {p} / {patch}')
    q = Path(v)
    if not q.is_absolute():
        q = p.parent / q
    a = info(q, f'western existing selected {key}')
    a['selectionRecord'] = info(p)
    return a


def init():
    contract = read(MAP / 'production-contract.json')
    layout = Path(contract['layoutReference'])
    style = ROOT / 'designs/mail-ui-v1/01-mail-event.png'
    team = ROOT / 'designs/team-ui-v2/team-ui-v2.png'
    detail = Path(contract['detailStyleReference'])
    assert sha(layout) == contract['layoutSha256']
    assert sha(detail) == contract['detailSha256']
    assert contract['formalTilePixels'] == [4096, 4096]
    refs = [info(layout, 'approved layout only'), info(detail, 'independent detail/material style only'),
            info(style, 'primary approved Daoist Q hand-painted style'),
            info(team, 'second primary approved style reference; no UI copied')]
    order = []
    for c in (11, 12):
        for pc in range(1, 5):
            for r in (10, 11):
                for pr in range(1, 5):
                    order.append(geometry(f'r{r:02d}_c{c:02d}', f'p{pr}{pc}'))
    plan = {'schemaVersion': 1, 'preparedAtUtc': now(), 'batch': 'village-east-shipyard',
            'tiles': TILES, 'globalCoreBox': [40960, 36864, 49152, 45056],
            'tileCount': 4, 'coreCount': 64, 'formalTileDimensions': [4096, 4096],
            'nativeCorePixels': CORE, 'haloPixels': HALO, 'expectedNativeDimensions': [NATIVE, NATIVE],
            'coreCrop': [HALO, HALO, HALO + CORE, HALO + CORE],
            'contract': info(MAP / 'production-contract.json'),
            'splitContract': info(ROOT / 'docs/MAP_PARALLEL_SPLIT_20261013.json'),
            'rootInstructions': info(ROOT / 'AGENTS.md'), 'references': refs,
            'ownerGate': gate(), 'generationOrder': order,
            'artRules': 'Daylight Daoist Q painterly; retain original deck, coast, boats and net geometry. No people, UI, new buildings, route closure or low-resolution pixels in final art.',
            'actualModel': None, 'modelPreference': 'Existing free 2.5 preferred, existing built-in 2.0 permitted; no paid API.',
            'writeScope': str(OUT), 'originalZoneAndSharedRecordsReadOnly': True,
            'formalAcceptedCount': 0, 'mapComplete': False}
    i = 1
    while (OUT / f'production-plan-v{i}.json').exists():
        i += 1
    p = OUT / f'production-plan-v{i}.json'
    save(p, plan)
    if not STATE.exists():
        checkpoint(state(), 'prepared production plan; no generation')
    print(json.dumps({'plan': str(p), 'ownerGate': plan['ownerGate'], 'coreCount': len(order)}))


def prepare(tile, patch, description, retry=False):
    g = gate(required=True)
    coordinate_conflicts = [c for c in g.get('actualCoordinateConflicts', [])
                           if c['tile'] == tile and c.get('patch') in (None, patch)]
    if coordinate_conflicts:
        conflict_path = OUT / f'conflicts/{tile}-{patch}-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}.json'
        save(conflict_path, {'coordinate': tile + '/' + patch, 'conflicts': coordinate_conflicts,
                             'action': 'Pause only this conflict coordinate; other unconflicted allocated coordinates may continue.'})
        raise RuntimeError('Real source/in-flight conflict for this coordinate: ' + str(conflict_path))
    s = state()
    key = tile + '_' + patch
    if key in s['selected'] and not retry:
        raise RuntimeError('Already selected; use an explicit new repair version: ' + key)
    geom = geometry(tile, patch)
    x, y = geom['coreGlobalBox'][:2]
    left, top = locate_neighbor(s, x - CORE, y), locate_neighbor(s, x, y - CORE)
    for anchor, direction in ((left, 'east'), (top, 'south')):
        if anchor and anchor.get('continuationAllowed', {}).get(direction) is False:
            raise RuntimeError('Known failed adjacent edge must be repaired before continuation: '
                               + anchor['path'] + ' / ' + direction)
    if not left and not top:
        raise RuntimeError('No stable native adjacent anchor for ' + key)
    if tile.startswith('r11_') and patch[1] == '1' and top is None:
        raise RuntimeError('Wait for the same-column r10 bottom core before starting this r11 column')
    contract = read(MAP / 'production-contract.json')
    layout = Path(contract['layoutReference'])
    detail = Path(contract['detailStyleReference'])
    style = ROOT / 'designs/mail-ui-v1/01-mail-event.png'
    folder = OUT / tile
    folder.mkdir(parents=True, exist_ok=True)
    version = 1
    while (folder / f'requests/{patch}-v{version}.request.json').exists():
        version += 1
    with Image.open(layout) as im:
        scale = im.width / 57344
        extent = [a * scale for a in geom['nativeGlobalBox']]
        guide = im.convert('RGB').transform((NATIVE, NATIVE), Image.Transform.EXTENT,
                    tuple(extent), resample=Image.Resampling.BICUBIC)
    guide_path = folder / f'layout-only/{patch}-v{version}-layout-only.png'
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide.save(guide_path)
    conditioned = guide.copy()
    pasted = []
    for direction, item, crop, dest in [
            ('left', left, [1024, 0, 1254, 1254], [0, 0]),
            ('top', top, [0, 1024, 1254, 1254], [0, 0])]:
        if not item:
            continue
        with Image.open(item['path']) as im:
            assert im.size == (NATIVE, NATIVE)
            conditioned.paste(im.convert('RGB').crop(tuple(crop)), tuple(dest))
        pasted.append({'direction': direction, 'source': item, 'sourceCrop': crop, 'pasteAt': dest,
                       'operation': 'unscaled adjacent native overlap pasted onto layout-only guide'})
    conditioned_path = folder / f'layout-only/{patch}-v{version}-conditioned-target.png'
    conditioned.save(conditioned_path)
    refs = [info(conditioned_path, 'edit target; blurry region is layout guidance only')]
    refs += [left] if left else [top]
    if left and top:
        refs += [top, info(layout, 'authoritative full-map layout only')]
    else:
        refs += [info(layout, 'authoritative full-map layout only'), info(detail, 'independent daylight material/style, not coordinate crop')]
    refs += [info(style, 'primary approved Q Daoist hand-painted style; never copy UI, people or night')]
    assert len(refs) == 5
    anchors = 'left 230 pixels' if left else ''
    if top:
        anchors += (' and ' if anchors else '') + 'top 230 pixels'
    prompt = f'''Use case: precise-object-edit / native game-map continuation.
Asset: one opaque 1254x1254 native map patch, {tile}/{patch}; 1024x1024 final core at [115,115,1139,1139].
Image1 is the edit target: {anchors} contain existing native art. The blurry remainder is ONLY the approved layout guide, never final pixels. Preserve the finished native strips and reconstruct the remainder as sharp original detail. Continue every plank, rope, contour, shadow and waterline seamlessly across the strip boundaries without a pasted band, duplicate object or change of scale. At a top/left overlap corner, the top native strip was pasted last.
Image2 is the immediate adjacent native anchor controlling actual scale, painterly material and exact continuation. '''
    prompt += ('Image3 is the immediate TOP native anchor. Image4 is the authoritative whole-village layout only. ' if left and top else 'Image3 is the authoritative whole-village layout only. Image4 is independent daytime material/detail style, NOT a coordinate crop. ')
    prompt += f'''Image5 is the primary approved rounded Q Daoist hand-painted style; do not copy its UI, night, people or text.
Target native world box: {geom['nativeGlobalBox']}; final core world box: {geom['coreGlobalBox']}. Keep the tight cropped view and the approved object's exact footprint, perspective and placement. No zoom-out, rotation or reframing.
Scene: {description}
Style: refined high-definition rounded Daoist Q hand-painted game environment. Warm natural wooden deck and ropes, blue-green sea, restrained clean grain and net weave, soft daytime shading, crisp coherent contours. Natural pale grey/blue-grey stone only where already present. Existing Spring Festival architecture and occasional Lantern/Mid-Autumn details only, no added decorations in open routes.
Constraints: preserve approved shipyard/deck/coast/boat geometry; no new or moved building, whole ship, lighthouse, pole, furniture, tree island, planter, people, NPC, animal, text, UI, icon, watermark or frame. Keep roads, deck paths and exits open. Replace the blurry guide with new sharp native detail; do not merely sharpen or enlarge its pixels. Exactly one 1254-square opaque patch.'''
    request = {'schemaVersion': 1, 'submittedAtUtc': now(), 'key': key, 'version': version,
               'tool': 'image_gen__imagegen', 'generationMode': 'builtin', 'prompt': prompt,
               'referenced_image_paths': [x['path'] for x in refs], 'referenceRolesAndHashes': refs,
               'transparent_background': False, 'geometry': geom, 'conditionedGuide': {
                   'file': info(conditioned_path), 'layoutOnlySource': info(layout),
                   'overviewExtent': extent, 'pastedNativeReferences': pasted,
                   'classification': 'Reference/edit input only, never final or accepted artwork'},
               'ownerGate': g, 'rootInstructionsReadBeforeCall': info(ROOT / 'AGENTS.md'),
               'requestedModelPreference': 'Free/existing 2.5 preferred; built-in 2.0 permitted',
               'submittedModelSelector': None, 'submittedQualitySelector': None,
               'actualModel': None, 'actualQuality': None, 'paidApiUsed': False,
               'status': 'prepared_not_yet_submitted'}
    p = folder / f'requests/{patch}-v{version}.request.json'
    save(p, request)
    prompt_path = folder / f'requests/{patch}-v{version}.prompt.txt'
    prompt_path.write_text(prompt + '\n', encoding='utf-8')
    s['requests'].append(str(p))
    checkpoint(s, 'prepared builtin request ' + key + f'-v{version}')
    print(json.dumps({'request': str(p), 'conditionedTarget': str(conditioned_path),
                      'geometry': geom, 'references': [x['path'] for x in refs]}))


def ingest(request_path, source_path, metadata_path):
    p = Path(request_path).resolve()
    assert p.is_relative_to(OUT)
    req = read(p)
    src = Path(source_path).resolve()
    meta = read(metadata_path)
    tile, patch, version = req['geometry']['tile'], req['geometry']['patch'], req['version']
    dst = OUT / tile / f'native/{patch}-v{version}.png'
    assert not dst.exists()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    original, stored = info(src), info(dst)
    assert original['sha256'] == stored['sha256']
    valid = stored['dimensions'] == [NATIVE, NATIVE]
    receipt = {'schemaVersion': 1, 'receivedAtUtc': now(), 'request': info(p),
               'tool': 'image_gen__imagegen', 'toolMetadataWithoutImageData': meta,
               'originalToolOutput': original, 'savedNative': stored,
               'actualModel': meta.get('actualModel'), 'actualQuality': meta.get('actualQuality'),
               'geometry': req['geometry'], 'dimensionsSatisfyContract': valid,
               'resized': False, 'layoutPixelsDeclaredFinal': False, 'formalAccepted': False,
               'selectionStatus': 'provisional_pending_native_visual_QA' if valid else 'dimension_contract_failed'}
    receipt_path = OUT / tile / f'requests/{patch}-v{version}.receipt.json'
    save(receipt_path, receipt)
    generation = dict(receipt)
    generation['prompt'] = req['prompt']
    generation['referenceRolesAndHashes'] = req['referenceRolesAndHashes']
    save(dst.with_suffix('.png.generation.json'), generation)
    s = state()
    s['receipts'].append(str(receipt_path))
    if valid:
        selected = dict(stored)
        selected.update(geometry=req['geometry'], version=version, receipt=str(receipt_path),
                        reviewStatus='provisional_pending_native_visual_QA')
        s['selected'][req['key']] = selected
        tile_selected = {k.split('_p')[1]: v for k, v in s['selected'].items() if k.startswith(tile + '_p')}
        selection = {'tile': tile, 'updatedAtUtc': now(), 'patches': {'p' + k: v for k, v in tile_selected.items()},
                     'selectedCount': len(tile_selected), 'requiredCount': 16, 'internalReady': False,
                     'formalAccepted': False, 'candidate': s['candidates'].get(tile)}
        n = 1
        while (OUT / tile / f'selections/selected-patches-v{n:04d}.json').exists():
            n += 1
        save(OUT / tile / f'selections/selected-patches-v{n:04d}.json', selection)
    checkpoint(s, 'saved native output ' + req['key'] + f'-v{version}')
    print(json.dumps({'savedNative': stored, 'receipt': str(receipt_path),
                      'validNativeDimensions': valid, 'selectedCoreCount': len(s['selected'])}))


def assemble(tile):
    assert tile in TILES
    s = state()
    sources = []
    canvas = Image.new('RGB', (4096, 4096))
    for r in range(1, 5):
        for c in range(1, 5):
            patch = f'p{r}{c}'
            rec = s['selected'].get(tile + '_' + patch)
            if not rec:
                raise RuntimeError('Missing selected native: ' + tile + '_' + patch)
            assert sha(rec['path']) == rec['sha256']
            with Image.open(rec['path']) as im:
                assert im.size == (NATIVE, NATIVE)
                canvas.paste(im.convert('RGB').crop((115, 115, 1139, 1139)), ((c - 1) * CORE, (r - 1) * CORE))
            sources.append({'patch': patch, 'source': rec, 'sourceCrop': [115, 115, 1139, 1139],
                            'pasteAt': [(c - 1) * CORE, (r - 1) * CORE]})
    version = 1
    while (OUT / tile / f'candidate/{tile}-4096-candidate-v{version}.png').exists():
        version += 1
    dst = OUT / tile / f'candidate/{tile}-4096-candidate-v{version}.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst)
    manifest = {'tile': tile, 'createdAtUtc': now(), 'candidate': info(dst), 'sources': sources,
                'operation': '16 unscaled 1024 core crops from measured native 1254 outputs, exact integer paste',
                'resamplingApplied': False, 'layoutPixelsUsed': False, 'formalAccepted': False,
                'internalReady': False, 'visualQA': 'pending', 'externalQA': 'pending'}
    save(dst.with_suffix('.png.derivation.json'), manifest)
    s['candidates'][tile] = info(dst)
    checkpoint(s, 'assembled native candidate ' + tile)
    print(json.dumps({'candidate': info(dst), 'manifest': str(dst.with_suffix('.png.derivation.json'))}))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    sub.add_parser('gate')
    a = sub.add_parser('prepare')
    a.add_argument('tile'); a.add_argument('patch'); a.add_argument('--description', required=True)
    a.add_argument('--retry', action='store_true')
    a = sub.add_parser('ingest')
    a.add_argument('request'); a.add_argument('source'); a.add_argument('metadata')
    a = sub.add_parser('assemble'); a.add_argument('tile')
    a = p.parse_args()
    if a.command == 'gate':
        print(json.dumps(gate()))
    else:
        with batch_writer_lock():
            if a.command == 'init': init()
            elif a.command == 'prepare': prepare(a.tile, a.patch, a.description, a.retry)
            elif a.command == 'ingest': ingest(a.request, a.source, a.metadata)
            elif a.command == 'assemble': assemble(a.tile)


if __name__ == '__main__':
    main()
