"""Native-only Southwest production tooling. No image-generation API is called.

CLI: native_pipeline.py TILE {init,prepare,ingest,assemble,preflight} [options]
Only explicit init creates coordinates/layout guides. Existing coordinates are
reused. Requests live in TILE/pipeline; no old prompt/native output is overwritten.
The delivered r10_c05 is read-only, including its selected local repairs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT.parent / 'production-contract.json'
CONFIG = ROOT.parents[3] / 'config' / 'image-generation.json'
PRESERVED_CONFIG = ROOT / 'pipeline-tools' / 'image-generation.last-request-snapshot-20261012.json'
GRID, CORE, HALO, PATCH, OVERLAP, FINAL = 4, 1024, 115, 1254, 230, 4096
EXPECTED = {(r, c) for r in range(1, 5) for c in range(1, 5)}
PROTECTED = {'r10_c05'}
QUILT_PATH = ROOT / 'pipeline-tools' / 'quilt.py'
spec = importlib.util.spec_from_file_location('southwest_native_quilt', QUILT_PATH)
quilt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quilt)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def pid(row, col):
    require((row, col) in EXPECTED, 'Patch row/column must be 1..4')
    return f'p{row:02d}_{col:02d}'


def tile_numbers(tile):
    match = re.fullmatch(r'r(\d{2})_c(\d{2})', tile)
    require(match is not None, 'Tile must use rNN_cNN')
    row, col = map(int, match.groups())
    require(1 <= row <= 16 and 1 <= col <= 16, 'Tile outside the existing 16x16 artwork grid')
    return row, col


def origin(tile):
    r, c = tile_numbers(tile)
    return (c - 1) * FINAL, (r - 1) * FINAL


def coords(tile, row, col):
    name = pid(row, col)
    ox, oy = origin(tile)
    x, y = ox + (col - 1) * CORE, oy + (row - 1) * CORE
    return {'id': name, 'row': row, 'column': col,
            'coreWorldBox': [x, y, x + CORE, y + CORE],
            'contextWorldBox': [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            'nativeCoreBox': [HALO, HALO, HALO + CORE, HALO + CORE]}


def absolute(value):
    p = Path(value)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()


def supported_selected_record(directory, key, relative):
    """Permit immutable refinement versions without relaxing tile/source identity."""
    p = Path(relative)
    if p.is_absolute() or p.drive or '..' in p.parts:
        return False
    directory = Path(directory).resolve()
    target = (directory / p).resolve()
    if not target.is_relative_to(directory):
        return False
    name = f'{key}.png.generation.json'
    legacy = {(directory / 'native' / name).resolve(),
              (directory / 'refinement' / 'native' / name).resolve()}
    if target in legacy:
        return True
    return (len(p.parts) == 4 and p.parts[:2] == ('refinement', 'versions')
            and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', p.parts[2]) is not None
            and p.parts[3] == name
            and target.parent.parent == (directory / 'refinement' / 'versions').resolve())


class Pipeline:
    def __init__(self, tile):
        row, col = tile_numbers(tile)
        require(9 <= row <= 16 and 1 <= col <= 8, 'Writes are restricted to the assigned Southwest 64 tiles')
        self.tile, self.row, self.col = tile, row, col
        self.t = ROOT / tile
        self.work = self.t / 'pipeline'
        self.contract = read(CONTRACT)
        plan = self.contract['nativePatchPlan']
        require(self.contract['artCanvasPixels'] == [65536, 65536]
                and self.contract['formalTilePixels'] == [FINAL, FINAL]
                and (plan['subrows'], plan['subcolumns'], plan['corePixels'],
                     plan['haloPixels'], plan['expectedNativePixels']) == (4, 4, CORE, HALO, PATCH)
                and plan['resizeFinalArtAllowed'] is False, 'Artwork/native contract changed')
        require(self.contract['builtinOnly'] and not self.contract['paidApiAllowed'], 'Expected builtin-only batch')
        self.checked, self.warnings, self.missing_historical = {}, [], set()
        self.check(CONTRACT)
        self.check(Path(__file__))
        self.check(QUILT_PATH)
        self.record_cache = {}

    def warn(self, kind, **data):
        item = {'kind': kind, **data}
        if item not in self.warnings:
            self.warnings.append(item)

    def check(self, path, expected=None, historical_primary=False):
        path = absolute(path)
        old = self.contract.get('previousPrimaryStyleReference')
        if not path.is_file():
            if historical_primary and old and path == absolute(old) and expected:
                self.warn('missing_historical_primary_reference', file=str(path), recordedSha256=expected,
                          currentReplacement=self.contract['primaryStyleReference'],
                          note='Historical hash is preserved; replacement is not asserted byte-identical.')
                self.missing_historical.add(str(path))
                return expected
            raise ValueError(f'Missing required source/provenance: {path}')
        digest = self.checked.get(str(path))
        if digest is None:
            digest = sha(path)
            self.checked[str(path)] = digest
        if expected:
            require(digest == expected.lower(), f'SHA-256 mismatch: {path}')
        return digest

    def ref(self, path, role, **extra):
        path = absolute(path)
        return {'file': str(path), 'sha256': self.check(path), 'role': role, **extra}

    def stable(self):
        for path, digest in self.checked.items():
            require(Path(path).is_file() and sha(path) == digest, f'Input changed while running: {path}')
        for path in self.missing_historical:
            require(not Path(path).exists(), f'Historical reference appeared while running; rerun: {path}')

    def write_target(self, path):
        require(self.tile not in PROTECTED, f'{self.tile} is delivered with local repairs; this tool cannot rewrite it')
        path = Path(path).resolve()
        require(path.is_relative_to(self.t.resolve()), 'Write outside requested Southwest tile')
        return path

    def save_json(self, path, data):
        path = self.write_target(path)
        require(not path.exists(), f'Refusing to overwrite existing evidence: {path}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def save_image(self, path, image):
        path = self.write_target(path)
        require(not path.exists(), f'Refusing to overwrite existing pixels: {path}')
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format='PNG')
        with Image.open(path) as actual:
            actual.load()
            require(actual.size == image.size and actual.mode == image.mode
                    and actual.tobytes() == image.tobytes(), 'Saved PNG pixels differ')
        return {'file': str(path), 'sha256': sha(path), 'width': image.width, 'height': image.height,
                'mode': image.mode, 'format': 'PNG', 'sourceResampling': False}

    def resume(self):
        require(self.contract.get('newArtworkGenerationAllowed') is True, 'Production is not released')
        resume_path = absolute(self.contract['productionResumeControl'])
        resume = read(resume_path)
        self.check(resume_path)
        require(resume.get('newArtworkGenerationAllowed') is True
                and resume.get('preserveArtCoordinatesAndApprovedLayout') is True,
                'Resume control does not authorize existing-grid production')
        return {'file': str(resume_path), 'sha256': self.check(resume_path)}

    def current_refs(self):
        result = []
        for key, hashkey, role in [
            ('layoutReference', 'layoutSha256', 'approved whole-city geometry only; no full scene output'),
            ('detailStyleReference', 'detailSha256', 'approved clean grey stone, daylight and material finish'),
            ('primaryStyleReference', 'primaryStyleSha256', 'current primary Daoist chibi style; copy no UI')]:
            path = absolute(self.contract[key])
            self.check(path, self.contract.get(hashkey))
            result.append(self.ref(path, role))
        return result

    def tile_dir(self, tile):
        row, col = tile_numbers(tile)
        for zone in self.contract['zones']:
            if zone['rows'][0] <= row <= zone['rows'][1] and zone['columns'][0] <= col <= zone['columns'][1]:
                return ROOT.parent / zone['id'] / tile
        raise ValueError(f'No zone owner for {tile}')

    def coordinate_file(self, tile=None):
        tile = tile or self.tile
        path = self.tile_dir(tile) / 'coordinates.json'
        require(path.exists(), f'No coordinates; explicitly run {tile} init before prepare/ingest')
        doc = read(path)
        self.check(path)
        ox, oy = origin(tile)
        require(doc['tile'] == tile and doc['tileCoreWorldBox'] == [ox, oy, ox + FINAL, oy + FINAL],
                f'Existing tile coordinates differ: {path}')
        require((doc['nativePixels'], doc['corePixels'], doc['haloPixels']) == (PATCH, CORE, HALO),
                'Existing native geometry differs')
        require(len(doc['patches']) == 16, 'Coordinate file does not contain 16 patches')
        seen = set()
        for item in doc['patches']:
            expected = coords(tile, item['row'], item['column'])
            require(all(item.get(k) == v for k, v in expected.items()), f'Coordinate mismatch: {item.get("id")}')
            require(item['id'] not in seen, 'Duplicate patch in coordinate file')
            seen.add(item['id'])
        return doc

    def selected_record(self, tile, row, col, optional=False):
        name = pid(row, col)
        directory = self.tile_dir(tile)
        selection = directory / 'refinement' / 'selection.json'
        selected, selection_evidence = directory / 'native' / f'{name}.png.generation.json', None
        if selection.exists():
            data = read(selection)
            require(isinstance(data, dict), 'Refinement selection must be a mapping')
            selection_evidence = {'file': str(selection), 'sha256': self.check(selection)}
            for key, value in data.items():
                require(key in {pid(r, c) for r, c in EXPECTED}, 'Unknown selected patch')
                p = Path(value)
                require(not p.is_absolute() and not p.drive, 'Selected record must be tile-relative')
                require(supported_selected_record(directory, key, p),
                        'Selected record is outside supported native directories')
            if name in data:
                selected = directory / data[name]
                selection_evidence['selectedRecord'] = data[name]
        if not selected.exists():
            # A present image without its record must not silently become a missing neighbor.
            require(not selected.with_name(f'{name}.png').exists(), f'Unrecorded neighbor: {selected}')
            if optional:
                return None
            raise ValueError(f'Missing required selected native neighbor: {selected}')
        return selected.resolve(), selection_evidence

    def native_record(self, tile, row, col, selection):
        record_path, selection_evidence = selection
        key = str(record_path)
        if key in self.record_cache:
            return self.record_cache[key]
        digest = self.check(record_path)
        record = read(record_path)
        require(record['coordinates'] == coords(tile, row, col), f'Native record coordinates differ: {record_path}')
        native = absolute(record['file'])
        require(record_path == native.with_name(native.name + '.generation.json'), 'Record/native name differs')
        require(native.name == f'{pid(row, col)}.png' and native.is_relative_to(self.tile_dir(tile).resolve()),
                'Selected native identity differs')
        require(record.get('route') == 'builtin' and record.get('tool') == 'image_gen.imagegen', 'Not a builtin source')
        require(record.get('nativePixelsPreserved') is True and record.get('resizedAfterGeneration') is False,
                'Native preservation evidence missing')
        require([record['width'], record['height']] == [PATCH, PATCH], 'Native dimensions differ; never resize to fix')
        require('actualModel' in record and 'actualQuality' in record, 'Actual model/quality evidence fields missing')
        native_hash = self.check(native, record['sha256'])
        require(record['sourceOutputSha256'] == native_hash, 'Saved native is not byte-identical to recorded tool output')
        original = absolute(record['sourceOutputPath'])
        if original.exists():
            self.check(original, native_hash)
        else:
            self.warn('host_temporary_output_absent', file=str(original),
                      verifiedNativeCopy=str(native), sha256=native_hash)
        prompt = absolute(record['prompt'])
        self.check(prompt, record['promptSha256'])
        require(bool(prompt.read_text(encoding='utf-8-sig').strip()), 'Empty prompt')
        receipt = absolute(record['evidence']['toolReceipt'])
        receipt_hash = self.check(receipt, record['evidence'].get('toolReceiptSha256'))
        actual_receipt = read(receipt)
        require(actual_receipt.get('status') == 'returned_image'
                and actual_receipt.get('tool') == 'image_gen.imagegen', 'Receipt is not a successful builtin image')
        references = record.get('references', [])
        require(bool(references), 'Missing actual reference list')
        paths = {absolute(ref['file']) for ref in references}
        primary_paths = {absolute(self.contract['primaryStyleReference'])}
        if self.contract.get('previousPrimaryStyleReference'):
            primary_paths.add(absolute(self.contract['previousPrimaryStyleReference']))
        require(absolute(self.contract['layoutReference']) in paths
                and absolute(self.contract['detailStyleReference']) in paths
                and bool(primary_paths & paths), 'Required style/layout reference evidence missing')
        for ref in references:
            self.check(ref['file'], ref['sha256'], historical_primary=True)
        for neighbor in record.get('neighborSources', []):
            self.check(neighbor['file'], neighbor['sha256'])
            if neighbor.get('generationRecord'):
                self.check(neighbor['generationRecord'], neighbor['generationRecordSha256'])
        request_evidence = None
        if record.get('request'):
            request_path = absolute(record['request'])
            request_hash = self.check(request_path, record.get('requestSha256'))
            request = read(request_path)
            require(request['prompt'] == prompt.read_text(encoding='utf-8-sig')
                    and request['references'] == references and request['coordinates'] == record['coordinates'],
                    'Saved request differs from recorded prompt/reference/coordinates')
            request_evidence = {'file': str(request_path), 'sha256': request_hash}
        with Image.open(native) as im:
            im.load()
            require(im.format == 'PNG' and im.size == (PATCH, PATCH) and im.mode in ('RGB', 'RGBA'),
                    'Actual native PNG format/dimensions differ')
            require(im.mode == record['mode'] and im.format == record['format'], 'Actual native mode differs')
            require(im.mode != 'RGBA' or im.getextrema()[3] == (255, 255), 'Native ground contains transparent pixels')
            image = im.convert('RGB')
        entry = {'id': pid(row, col), 'row': row, 'column': col, 'sourceTile': tile,
                 'nativeFile': str(native), 'nativeSha256': native_hash, 'actualNativePixels': [PATCH, PATCH],
                 'recordFile': str(record_path), 'recordSha256': digest, 'selectionEvidence': selection_evidence,
                 'promptFile': str(prompt), 'promptSha256': record['promptSha256'],
                 'receiptFile': str(receipt), 'receiptSha256': receipt_hash, 'requestEvidence': request_evidence,
                 'references': references, 'neighborSources': record.get('neighborSources', []),
                 'cornerTreatment': record.get('cornerTreatment'), 'coordinates': record['coordinates'],
                 'configSnapshot': record.get('configSnapshot'), 'submittedParameters': record.get('submittedParameters'),
                 'actualModel': record['actualModel'], 'actualQuality': record['actualQuality'],
                 'unverifiedReason': record.get('unverifiedReason'), 'formalAccepted': False,
                 'sourceResampling': False, 'generatedAt': record.get('generatedAt')}
        self.record_cache[key] = image, entry
        return image, entry

    def repair_intersection_check(self, tile, world_box):
        # Local repairs are not whole-patch replacements. Refuse stale raw borders
        # where any delivered local repair overlaps the requested neighbor strip.
        directory = self.tile_dir(tile)
        ox, oy = origin(tile)
        for manifest in (directory / 'repairs' / 'output').glob('*.repair-assembly.json'):
            self.check(manifest)
            data = read(manifest)
            for step in data.get('steps', []):
                box = step.get('candidateBox')
                if box:
                    other = [box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy]
                    intersects = max(other[0], world_box[0]) < min(other[2], world_box[2]) and max(other[1], world_box[1]) < min(other[3], world_box[3])
                    require(not intersects, f'Neighbor strip intersects a delivered local repair in {tile}; supply a native unified border anchor')

    def neighbor(self, row, col, side):
        tile, rr, cc = self.tile, row, col
        if side == 'left':
            cc -= 1
            if cc == 0:
                if self.col == 1:
                    return None
                tile, cc = f'r{self.row:02d}_c{self.col - 1:02d}', 4
        else:
            rr -= 1
            if rr == 0:
                if self.row == 1:
                    return None
                tile, rr = f'r{self.row - 1:02d}_c{self.col:02d}', 4
        selection = self.selected_record(tile, rr, cc, optional=tile != self.tile)
        if selection is None:
            self.warn('cross_tile_neighbor_unavailable', sourceTile=tile, patch=pid(rr, cc), side=side)
            return None
        self.coordinate_file(tile)
        image, entry = self.native_record(tile, rr, cc, selection)
        crop = [CORE, 0, PATCH, PATCH] if side == 'left' else [0, CORE, PATCH, PATCH]
        context = entry['coordinates']['contextWorldBox']
        world_box = [context[0] + crop[0], context[1] + crop[1], context[0] + crop[2], context[1] + crop[3]]
        self.repair_intersection_check(tile, world_box)
        ref = {'file': entry['nativeFile'], 'sha256': entry['nativeSha256'], 'role': f'exact selected {side} native strip',
               'generationRecord': entry['recordFile'], 'generationRecordSha256': entry['recordSha256'],
               'sourceTile': tile, 'sourcePatch': entry['id'], 'selectionEvidence': entry['selectionEvidence'],
               'sourceCrop': crop, 'sourceWorldBox': world_box, 'sourceResampling': False}
        return image.crop(crop), ref

    def anchor(self, path, row, col, side):
        require((side == 'top' and row == 1) or (side == 'left' and col == 1), 'Unified anchor is only for the tile outer first row/column')
        path = absolute(path)
        expected = (FINAL + OVERLAP, OVERLAP) if side == 'top' else (OVERLAP, FINAL + OVERLAP)
        with Image.open(path) as im:
            im.load()
            require(im.format == 'PNG' and im.size == expected and im.mode in ('RGB', 'RGBA'), f'{side} anchor must be opaque PNG {expected}')
            require(im.mode != 'RGBA' or im.getextrema()[3] == (255, 255), 'Anchor has transparent pixels')
            im = im.convert('RGB')
        crop = [(col - 1) * CORE, 0, (col - 1) * CORE + PATCH, OVERLAP] if side == 'top' else [0, (row - 1) * CORE, OVERLAP, (row - 1) * CORE + PATCH]
        ref = self.ref(path, f'caller-supplied unified {side} native border anchor', sourceCrop=crop,
                       fullAnchorPixels=list(expected), sourceResampling=False)
        derivation = Path(str(path) + '.derivation.json')
        if derivation.exists():
            ref['derivationEvidence'] = {'file': str(derivation), 'sha256': self.check(derivation)}
        else:
            self.warn('anchor_upstream_derivation_not_supplied', file=str(path),
                      note='Input path, dimensions and hash recorded; this tool only certifies exact crop/paste, not how the supplied border was made.')
        return im.crop(crop), ref

    def init(self):
        self.resume()
        self.write_target(self.t / 'coordinates.json')
        if (self.t / 'coordinates.json').exists():
            self.coordinate_file()
            return {'status': 'existing_coordinates_reused', 'tile': self.tile, 'writes': False}
        refs = self.current_refs()
        require(not list((self.t / 'native').glob('*')), 'Cannot initialize coordinates around preexisting native files')
        with Image.open(refs[0]['file']) as im:
            overview = im.convert('RGB')
        entries = []
        # All coordinate/layout writes happen only inside explicit init.
        for row, col in sorted(EXPECTED):
            item = coords(self.tile, row, col)
            wb = item['contextWorldBox']
            box = [wb[0] * overview.width / 65536, wb[1] * overview.height / 65536,
                   wb[2] * overview.width / 65536, wb[3] * overview.height / 65536]
            guide = self.t / 'guides' / f'{pid(row, col)}.layout-only.png'
            image = overview.transform((PATCH, PATCH), Image.Transform.EXTENT, box, Image.Resampling.NEAREST)
            out = self.save_image(guide, image)
            item.update({'guide': str(guide), 'guideSha256': out['sha256'], 'layoutSourceBox': box,
                         'guideOnly': True, 'gameArt': False, 'derivedFrom': [refs[0]],
                         'operation': 'nearest-neighbor layout-only sampling; never native final game art'})
            self.save_json(str(guide) + '.derivation.json', item)
            entries.append(item)
        ox, oy = origin(self.tile)
        self.save_json(self.t / 'coordinates.json', {'tile': self.tile,
                       'tileCoreWorldBox': [ox, oy, ox + FINAL, oy + FINAL],
                       'tileContextWorldBox': [ox - HALO, oy - HALO, ox + FINAL + HALO, oy + FINAL + HALO],
                       'nativePixels': PATCH, 'corePixels': CORE, 'haloPixels': HALO,
                       'adjacentOverlapPixels': OVERLAP, 'halfOpenCoordinates': True, 'patches': entries})
        return {'status': 'initialized_layout_guides_only', 'tile': self.tile, 'guideCount': 16, 'nativeCreated': 0}

    def request_path(self, row, col, attempt):
        require(re.fullmatch(r'[A-Za-z0-9_-]{1,40}', attempt) is not None, 'Attempt must be a short filename-safe identifier')
        return self.work / 'prompts' / f'{pid(row, col)}.{attempt}.request.json'

    def prepare(self, args):
        row, col = args.row, args.col
        name = pid(row, col)
        resume_evidence = self.resume()
        self.write_target(self.work)
        doc = self.coordinate_file()
        require(self.selected_record(self.tile, row, col, optional=True) is None,
                'Existing selected native art cannot be overwritten; use a separate explicit refinement workflow')
        request_path = self.request_path(row, col, args.attempt)
        require(not request_path.exists(), 'Request attempt exists; choose a new --attempt')
        item = next(q for q in doc['patches'] if q['id'] == name)
        guide = absolute(item['guide'])
        self.check(guide, item['guideSha256'])
        if Path(str(guide) + '.derivation.json').exists():
            self.check(Path(str(guide) + '.derivation.json'))
        with Image.open(guide) as im:
            require(im.size == (PATCH, PATCH), 'Existing guide dimensions differ')
            seed = im.convert('RGB')
        left = self.anchor(args.anchor_left, row, col, 'left') if args.anchor_left else self.neighbor(row, col, 'left')
        upper = self.anchor(args.anchor_top, row, col, 'top') if args.anchor_top else self.neighbor(row, col, 'top')
        neighbors = []
        if left:
            seed.paste(left[0], (0, 0))
            left[1].update({'targetBox': [0, 0, OVERLAP, PATCH],
                            'effectiveTargetBox': [0, OVERLAP if upper else 0, OVERLAP, PATCH]})
            neighbors.append(left[1])
        corner = {'priority': 'upper', 'pasteOrder': ['left when available', 'upper when available'],
                  'bothSourcesPresent': bool(left and upper), 'blendingOrResampling': False}
        if left and upper:
            delta = np.abs(np.asarray(left[0])[:OVERLAP].astype(np.int16) - np.asarray(upper[0])[:, :OVERLAP].astype(np.int16))
            corner.update({'inputCornerMaxAbsDifference': int(delta.max()), 'inputCornerMeanAbsDifference': float(delta.mean()),
                           'visualReviewRequired': True})
        if upper:
            seed.paste(upper[0], (0, 0))
            upper[1].update({'targetBox': [0, 0, PATCH, OVERLAP], 'effectiveTargetBox': [0, 0, PATCH, OVERLAP]})
            neighbors.append(upper[1])
        seed_path = self.work / 'guides' / f'{name}.{args.attempt}.continuity-seed.png'
        required_refs = self.current_refs()
        content = args.content_prefix or ''
        if args.content_prefix_file:
            prefix_file = absolute(args.content_prefix_file)
            self.check(prefix_file)
            content = prefix_file.read_text(encoding='utf-8-sig') + '\n' + content
        prompt = (content.strip() + '\n\n' if content.strip() else '') + f'''Use case: precise-object-edit. Asset: one native game-map detail patch for 五行奇谈 Southwest. Output one opaque PNG, requested native canvas 1254x1254.
EDIT IMAGE 1 ONLY. This is patch {name} in tile {self.tile}, exact art-world context {coords(self.tile, row, col)['contextWorldBox']}. Central 1024x1024 core is [115,115,1139,1139]. Preserve this extremely close framing and clipped objects. Do not zoom out, recenter, widen the crop, or invent a complete scene/building from a small fragment.
Image 2 is the approved whole-city geometry reference only; never render the entire city. Image 3 defines daylight, clean natural pale grey/blue-grey stone and finished materials. Image 4 is the current primary Daoist chibi style: rounded full forms, polished hand painting, soft volume, crisp readable edges. Do not copy UI, text, people, moon or reference framing.
Repaint coarse guide areas into genuinely new native detail at the exact projected geometry. Keep the established overhead oblique camera, object intersections, paving directions, stair tread/riser heights, rails, door openings and shadows. Where a guide shows only one surface, output only that close surface. Follow the mandatory content prefix above when provided.
Stone: broad quiet grey faces with sparse very faint brush strokes and smooth restrained tonal variation; no dense cellular patterns, marble veins, branching cracks, noisy fragments, stippling or red paving. Crisp rounded bevels and seams; no blur as a material shortcut. Keep existing wood warm and clean with subtle grain. Keep only the existing partial decorative marks, never invent a full emblem.
Continuity: any sharp top/left strips in Image 1 are exact native neighboring artwork, not low-resolution guide. Preserve their scale, line positions, lighting and material tone. Extend every intersecting line into the new native interior with no artificial strip divider, new vertical grout joint or rearranged object. Upper strip owns the shared top-left corner.
Preserve all existing functional buildings and open connected ground. Keep festival accents sparse; no added tree islands, pots, people, props, night lighting, distant panorama, watermarks, labels or grids. Only approved existing trees beside buildings/walls. Output only this exact cropped fragment; an enlarged guide is never final art.
'''
        config_path = CONFIG if CONFIG.is_file() else PRESERVED_CONFIG
        config = read(config_path)
        self.check(config_path)
        if config_path == PRESERVED_CONFIG:
            self.warn('global_config_absent_using_previous_request_metadata', file=str(config_path),
                      sha256=self.check(config_path), actualModel=None, actualQuality=None,
                      note='Exact historical request metadata only; builtin actual model/quality remain undisclosed, no parameters or global configuration changed.')
        self.stable()
        self.save_image(seed_path, seed)
        refs = [self.ref(seed_path, 'edit target: coarse layout with exact native overlap strips; not final art')] + required_refs
        prompt_path = request_path.with_name(request_path.name.replace('.request.json', '.prompt.txt'))
        require(not prompt_path.exists(), 'Prompt path already exists')
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding='utf-8')
        request = {'prompt': prompt, 'promptFile': str(prompt_path), 'promptSha256': sha(prompt_path),
                   'referenced_image_paths': [r['file'] for r in refs], 'transparent_background': False,
                   'references': refs, 'neighborSources': neighbors, 'cornerTreatment': corner,
                   'coordinates': coords(self.tile, row, col), 'tile': self.tile,
                   'requestedNativePixels': [PATCH, PATCH], 'submittedParameters': {'model': None, 'quality': None},
                   'configSnapshot': config, 'actualModel': None, 'actualQuality': None,
                   'preparedAtUtc': now(), 'productionResumeEvidence': resume_evidence,
                   'warnings': self.warnings, 'requiresActualVisualInspectionBeforeToolCall': True}
        self.save_json(request_path, request)
        self.save_json(str(seed_path) + '.derivation.json', {'file': str(seed_path), 'sha256': sha(seed_path),
                       'guide': str(guide), 'guideSha256': item['guideSha256'], 'neighbors': neighbors,
                       'cornerTreatment': corner, 'operation': 'native strips pasted without resampling onto layout guide',
                       'gameArt': False, 'sourceResampling': False})
        return {'status': 'prepared_not_generated', 'request': str(request_path), 'seed': str(seed_path),
                'receiptSuggestedPath': str(self.work / 'receipts' / f'{name}.{args.attempt}.receipt.json'),
                'warnings': self.warnings}

    def ingest(self, args):
        require(args.source and args.receipt, 'ingest requires --source and --receipt from the actual builtin result')
        self.write_target(self.work)
        self.coordinate_file()
        request_path = absolute(args.request) if args.request else self.request_path(args.row, args.col, args.attempt)
        req = read(request_path)
        self.check(request_path)
        expected = coords(self.tile, args.row, args.col)
        require(req.get('tile') == self.tile and req.get('requestedNativePixels') == [PATCH, PATCH],
                'Request tile/native dimensions do not match ingestion target')
        require(req['coordinates'] == expected, 'Request coordinates do not match ingestion target')
        for ref in req['references'] + req.get('neighborSources', []):
            self.check(ref['file'], ref['sha256'])
        for ref in req.get('neighborSources', []):
            if ref.get('generationRecord'):
                self.check(ref['generationRecord'], ref['generationRecordSha256'])
        prompt = absolute(req['promptFile'])
        self.check(prompt, req['promptSha256'])
        require(prompt.read_text(encoding='utf-8-sig') == req['prompt'], 'Prompt differs from request')
        receipt = absolute(args.receipt)
        receipt_hash = self.check(receipt)
        evidence = read(receipt)
        require(evidence.get('status') == 'returned_image' and evidence.get('tool') == 'image_gen.imagegen',
                'Receipt must describe an actual successful builtin result')
        src = absolute(args.source)
        source_hash = self.check(src)
        with Image.open(src) as im:
            im.load()
            width, height = im.size
            fmt, mode = im.format, im.mode
            require(fmt == 'PNG' and mode in ('RGB', 'RGBA'), 'Source must be the unchanged native PNG')
            opaque = mode != 'RGBA' or im.getextrema()[3] == (255, 255)
            require((width, height) == (PATCH, PATCH),
                    f'Native output is {width}x{height}, expected {PATCH}x{PATCH}; preserve the tool output separately and never resize it or occupy the selected native slot')
            require(opaque, 'Native ground contains transparent pixels; preserve the tool output separately and do not occupy the selected native slot')
            metadata = {key: str(value)[:4000] for key, value in im.info.items()}
        dest = self.write_target(self.t / 'native' / f'{pid(args.row, args.col)}.png')
        record_path = Path(str(dest) + '.generation.json')
        require(not dest.exists() and not record_path.exists(), 'Cannot overwrite native output/evidence')
        require(self.selected_record(self.tile, args.row, args.col, optional=True) is None, 'Selected native already exists')
        self.stable()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        require(sha(dest) == source_hash, 'Native copy is not byte-identical')
        record = {'file': str(dest), 'sha256': source_hash, 'generatedAt': now(),
                  'generatedAtEvidence': 'Ingestion timestamp; actual host generation time undisclosed',
                  'width': width, 'height': height, 'format': fmt, 'mode': mode, 'opaque': opaque,
                  'tool': 'image_gen.imagegen', 'route': 'builtin', 'configSnapshot': req['configSnapshot'],
                  'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False},
                  'actualModel': None, 'actualQuality': None,
                  'unverifiedReason': 'Host-managed builtin exposes no actual model/quality values; configuration is a target only.',
                  'evidence': {'toolReceipt': str(receipt), 'toolReceiptSha256': receipt_hash, 'pngMetadata': metadata},
                  'prompt': str(prompt), 'promptSha256': sha(prompt), 'request': str(request_path), 'requestSha256': sha(request_path),
                  'references': req['references'], 'neighborSources': req.get('neighborSources', []),
                  'cornerTreatment': req.get('cornerTreatment'), 'coordinates': expected,
                  'sourceOutputPath': str(src), 'sourceOutputSha256': source_hash,
                  'nativePixelsPreserved': True, 'resizedAfterGeneration': False,
                  'formalAccepted': False, 'sizeMatchesPlan': [width, height] == [PATCH, PATCH],
                  'visualStatus': 'pending_QA'}
        self.save_json(record_path, record)
        return {'status': 'native_saved_pending_QA', 'native': str(dest), 'size': [width, height],
                'sizeMatchesPlan': record['sizeMatchesPlan'], 'sha256': source_hash, 'formalAccepted': False}

    def sources(self):
        self.coordinate_file()
        arrays, entries = {}, []
        for row, col in sorted(EXPECTED):
            selection = self.selected_record(self.tile, row, col, optional=True)
            if selection:
                image, entry = self.native_record(self.tile, row, col, selection)
                arrays[(row, col)] = np.asarray(image, dtype=np.uint8)
                entries.append(entry)
        return arrays, entries

    def assemble(self, preflight, feather):
        arrays, entries = self.sources()
        rectangle = quilt.choose_rectangle(set(arrays))
        missing = [pid(r, c) for r, c in sorted(EXPECTED - set(arrays))]
        summary = {'tile': self.tile, 'verifiedNativeCount': len(arrays), 'missingPatchIds': missing,
                   'selectedRectangleInclusive': list(rectangle) if rectangle else None,
                   'formalAccepted': False, 'actualModel': None, 'actualQuality': None,
                   'warnings': self.warnings, 'sourceResampling': False,
                   'protectedExistingDelivery': self.tile in PROTECTED}
        if rectangle:
            top, left, bottom, right = rectangle
            width, height = (right - left + 1) * CORE, (bottom - top + 1) * CORE
            summary.update({'plannedContextPixels': [width + OVERLAP, height + OVERLAP],
                            'plannedCorePixels': [width, height]})
        self.stable()
        if preflight:
            return {**summary, 'status': 'preflight_passed', 'writes': False}
        self.write_target(self.work)
        require(rectangle is not None, 'No verified native pixels; no assembly created')
        selected = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
        complete = set(arrays) == EXPECTED
        combined, seams = quilt.assemble_pixels(arrays, rectangle, feather)
        cropped = combined[HALO:HALO + height, HALO:HALO + width].copy()
        require(cropped.shape == (height, width, 3), 'Core crop dimensions differ')
        require(not complete or (width, height) == (FINAL, FINAL), 'Full candidate must be 4096 square')
        self.stable()
        signature = hashlib.sha256(json.dumps({'sources': [(e['id'], e['nativeSha256']) for e in entries],
                                               'feather': feather, 'script': sha(Path(__file__)),
                                               'quilt': sha(QUILT_PATH)}, sort_keys=True).encode()).hexdigest()[:16]
        output_dir = self.work / 'output' / signature
        require(not output_dir.exists(), f'Assembly already exists: {output_dir}; preserving it')
        tag = 'candidate' if complete else f'partial-{pid(top, left)}-{pid(bottom, right)}'
        context_out = self.save_image(output_dir / f'{self.tile}.{tag}.context.png', Image.fromarray(combined))
        core_out = self.save_image(output_dir / f'{self.tile}.{tag}.png', Image.fromarray(cropped))
        qa = []
        for region in quilt.qa_regions(width, height, bottom - top + 1, right - left + 1, 0):
            out = self.save_image(self.work / 'qa' / signature / f'{region["name"]}.png',
                                  Image.fromarray(cropped).crop(region['box']))
            qa.append({**out, 'kind': region['kind'], 'cropBoxInOutput': region['box'], 'visualQa': 'pending'})
        ox, oy = origin(self.tile)
        box = [ox + (left - 1) * CORE, oy + (top - 1) * CORE, ox + right * CORE, oy + bottom * CORE]
        manifest = {'schemaVersion': 1, 'createdAtUtc': now(), **summary,
                    'status': 'candidate_pending_visual_and_external_QA' if complete else 'partial_native_coverage',
                    'complete4kCandidate': complete, 'formalAcceptedCount': 0,
                    'clientMappingValidated': False, 'capacity5000Validated': False,
                    'productionContract': {'file': str(CONTRACT), 'sha256': self.checked[str(CONTRACT.resolve())]},
                    'script': {'file': str(Path(__file__)), 'sha256': sha(Path(__file__))},
                    'quiltImplementation': {'file': str(QUILT_PATH), 'sha256': sha(QUILT_PATH)},
                    'coordinateConvention': 'existing artwork pixel grid; half-open; not client/world units',
                    'selectedCoreWorldBox': box, 'assembledContextWorldBox': [box[0] - HALO, box[1] - HALO, box[2] + HALO, box[3] + HALO],
                    'contextOutput': context_out, 'output': core_out, 'outputWorldBox': box,
                    'outerCropPixelsPerSide': HALO, 'assembledNativeCount': len(selected),
                    'usedPatchIds': [pid(r, c) for r, c in sorted(selected)], 'nativeSources': entries,
                    'verifiedSourceHashes': self.checked, 'seamMetrics': seams, 'qa': qa,
                    'composition': {'method': 'native minimum-error quilting; rows then row joins',
                                    'maximumFeatherRadiusPixels': feather, 'sourceResampling': False,
                                    'finalArtUpscaled': False, 'guidePixelsCompositedIntoFinal': False,
                                    'missingPixelsFilled': False, 'colorAdjustment': False, 'blur': False,
                                    'geometryWarping': False, 'externalBordersAutomaticallyRepaired': False},
                    'visualQa': {'status': 'pending', 'internalGeometryReviewed': False,
                                 'externalTileSeamsReviewed': False,
                                 'note': 'Previous r11 stone/leaf tone-seam findings remain open; numeric costs do not establish continuity.'}}
        self.save_json(output_dir / 'assembly.json', manifest)
        return {**summary, 'status': manifest['status'], 'context': context_out, 'output': core_out,
                'assembly': str(output_dir / 'assembly.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tile')
    parser.add_argument('action', choices=['init', 'prepare', 'ingest', 'assemble', 'preflight'])
    parser.add_argument('--row', type=int, default=1)
    parser.add_argument('--col', type=int, default=1)
    parser.add_argument('--attempt', default='v01')
    parser.add_argument('--content-prefix')
    parser.add_argument('--content-prefix-file')
    parser.add_argument('--anchor-top', help='4326x230 native PNG covering the entire tile top context')
    parser.add_argument('--anchor-left', help='230x4326 native PNG covering the entire tile left context')
    parser.add_argument('--source')
    parser.add_argument('--receipt')
    parser.add_argument('--request')
    parser.add_argument('--feather', type=int, choices=[0, 1, 2], default=2)
    args = parser.parse_args()
    try:
        pipeline = Pipeline(args.tile)
        if args.action == 'init':
            result = pipeline.init()
        elif args.action == 'prepare':
            result = pipeline.prepare(args)
        elif args.action == 'ingest':
            result = pipeline.ingest(args)
        else:
            result = pipeline.assemble(args.action == 'preflight', args.feather)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f'Native pipeline stopped: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
