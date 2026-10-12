"""QA-only native local repair across one or more adjacent 4096 tiles.

Example:
  python native_multi_tile_repair.py --base-prefix hardseam-v04 \
    --base-prefix c04-hardseam-v01 --repair r09_c04_s03_01_v01 \
    --prefix multi-test-v01 --band 50 --repair-roi 30 200 330 650 \
    --mandatory-target 80 300 200 500

Every ROI and mandatory target is in the original 1254 repair image coordinates.
An explicit base is also accepted as --base CANDIDATE MASK REPORT. Only qa/ is
written. Existing prefix outputs are never overwritten. No interpolation,
feathering, colour adjustment, displacement, or automatic acceptance is used.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
QA = ROOT / 'qa'
SIZE, REPAIR_SIZE = 4096, 1254
PARAMS = {'rgbDifferenceWeight': 1.0, 'gradientDifferenceWeight': 0.4,
          'gradientStrengthWeight': 0.08, 'lateralStepPenalty': 0.75,
          'centerBiasPerPixel': 0.0002, 'maxStepPerPixel': 1, 'edgeMarginPixels': 3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def safe_prefix(prefix):
    require(isinstance(prefix, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,100}', prefix),
            'Prefix must be a safe filename of at most 101 characters.')
    return prefix


def within_root(path):
    p = Path(path).resolve()
    require(p.is_relative_to(ROOT.resolve()), f'Input must stay within southwest: {p}')
    return p


def box4(value, label):
    require(isinstance(value, (list, tuple)) and len(value) == 4 and
            all(isinstance(x, int) and not isinstance(x, bool) for x in value),
            f'{label}: expected four integer coordinates.')
    x0, y0, x1, y1 = value
    require(x0 < x1 and y0 < y1, f'{label}: rectangle must have positive area.')
    return list(value)


def intersection(a, b):
    c = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return c if c[0] < c[2] and c[1] < c[3] else None


def slices(box, origin_box):
    return (slice(box[1]-origin_box[1], box[3]-origin_box[1]),
            slice(box[0]-origin_box[0], box[2]-origin_box[0]))


def read_image(path, shape, mode):
    with Image.open(path) as image:
        require(image.mode == mode, f'{path}: expected {mode}, got {image.mode}.')
        result = np.array(image)
    require(result.shape == shape, f'{path}: expected shape {shape}, got {result.shape}.')
    return result


def cost_path(old, new, side):
    a, b = old.astype(np.float32), new.astype(np.float32)
    diff = np.abs(a-b).mean(2)
    ay, ax = np.gradient(a, axis=(0, 1))
    by, bx = np.gradient(b, axis=(0, 1))
    gd = (np.abs(ax-bx)+np.abs(ay-by)).mean(2)
    gs = np.maximum(np.hypot(ax, ay).mean(2), np.hypot(bx, by).mean(2))
    h, w = diff.shape
    cost = PARAMS['rgbDifferenceWeight']*diff + PARAMS['gradientDifferenceWeight']*gd + PARAMS['gradientStrengthWeight']*gs
    cost += np.abs(np.arange(w)-w//2)[None, :]*PARAMS['centerBiasPerPixel']
    margin = PARAMS['edgeMarginPixels']
    cost[:, :margin] = np.inf
    cost[:, -margin:] = np.inf
    prev, back = cost[0].copy(), np.zeros((h, w), np.int8)
    for y in range(1, h):
        choices = np.stack((np.r_[np.inf, prev[:-1]+PARAMS['lateralStepPenalty']], prev,
                            np.r_[prev[1:]+PARAMS['lateralStepPenalty'], np.inf]))
        choice = choices.argmin(0)
        back[y] = choice.astype(np.int8)-1
        prev = choices[choice, np.arange(w)]+cost[y]
    require(np.isfinite(prev).any(), 'No finite DP edge path.')
    path = np.empty(h, np.int16)
    path[-1] = prev.argmin()
    for y in range(h-1, 0, -1):
        path[y-1] = path[y]+back[y, path[y]]
    require(np.max(np.abs(np.diff(path))) <= 1, 'Discontinuous DP path.')
    values = diff[np.arange(h), path]
    return path, {'side': side, 'path': path.tolist(), 'pathMin': int(path.min()),
                  'pathMax': int(path.max()), 'rgbDifferenceMean': float(values.mean()),
                  'rgbDifferenceP95': float(np.percentile(values, 95)),
                  'rgbDifferenceMax': float(values.max()),
                  'pathInterpretation': 'Distance from ROI edge to first AI pixel; rows for left/right, columns for top/bottom.'}


def validate_pixels(candidate, ids, inputs, global_box):
    """Check all source hashes/records, coordinate extents, and all 16M pixels."""
    require(candidate.shape == (SIZE, SIZE, 3) and ids.shape == (SIZE, SIZE), 'Tile/mask shape mismatch.')
    source_ids = [s.get('sourceId') for s in inputs]
    require(all(isinstance(s, int) and 1 <= s <= 255 for s in source_ids), 'Source IDs must be integers 1..255.')
    require(len(set(source_ids)) == len(source_ids), 'Duplicate source IDs in report.')
    require(set(map(int, np.unique(ids))) <= set(source_ids), 'Mask contains unknown source IDs.')
    counts, total = {}, 0
    for source in inputs:
        sid = source['sourceId']
        path, record_path = within_root(source['path']), within_root(source['record'])
        require(sha(path) == source['sha256'], f'Source hash changed: {path}')
        require(sha(record_path) == source['recordSha256'], f'Source record hash changed: {record_path}')
        record = load(record_path)
        box = box4(source['nativeGlobalBox'], 'source nativeGlobalBox')
        require(record.get('coordinates', {}).get('nativeGlobalBox') == box, f'Source coordinates disagree: {path}')
        require(record.get('sha256') == source['sha256'], f'Source generation hash disagrees: {path}')
        arr = read_image(path, (box[3]-box[1], box[2]-box[0], 3), 'RGB')
        yy, xx = np.where(ids == sid)
        counts[str(sid)] = int(len(xx))
        if len(xx):
            nx, ny = xx+global_box[0]-box[0], yy+global_box[1]-box[1]
            require(nx.min() >= 0 and ny.min() >= 0 and nx.max() < arr.shape[1] and ny.max() < arr.shape[0], f'Source coordinate out of bounds: {sid}')
            require(np.array_equal(candidate[yy, xx], arr[ny, nx]), f'Pixel mismatch for source {sid}.')
            total += len(xx)
    require(total == SIZE**2, 'Not every tile pixel has a verified source.')
    return {'pixelCount': int(total), 'mismatchedPixels': 0, 'sameGlobalCoordinateExact': True,
            'sourceIdPixelCounts': counts, 'sourceInputsAndRecordsUnchanged': True,
            'interpolation': False, 'feathering': False, 'colorAdjustment': False, 'displacement': False}


def read_base(spec):
    candidate_path, mask_path, report_path = [within_root(p) for p in spec]
    report = load(report_path)
    box = box4(report.get('candidateGlobalBox'), 'candidateGlobalBox')
    require(box[2]-box[0] == SIZE and box[3]-box[1] == SIZE, 'Base footprint must be 4096 square.')
    tile = report.get('tile')
    match = re.fullmatch(r'r([0-9]{2})_c([0-9]{2})', str(tile))
    require(match is not None, 'Base report needs an rNN_cNN tile name.')
    row, col = map(int, match.groups())
    require(row > 0 and col > 0 and box == [(col-1)*SIZE, (row-1)*SIZE, col*SIZE, row*SIZE], 'Tile name does not match global box.')
    hashes = {str(candidate_path): sha(candidate_path), str(mask_path): sha(mask_path)}
    reported_hashes = {x.get('sha256') for x in report.get('outputs', [])}
    require(all(h in reported_hashes for h in hashes.values()), 'Base candidate/mask hash is absent from report outputs.')
    validation = report.get('validation', {})
    require(validation.get('mismatchedPixels') == 0 and validation.get('pixelCount') == SIZE**2, 'Base report is not fully validated.')
    base = read_image(candidate_path, (SIZE, SIZE, 3), 'RGB')
    ids = read_image(mask_path, (SIZE, SIZE), 'L')
    inputs = report.get('inputs', [])
    validation = validate_pixels(base, ids, inputs, box)
    return {'tile': tile, 'box': box, 'base': base, 'ids': ids, 'inputs': inputs,
            'paths': [candidate_path, mask_path, report_path], 'hashes': [sha(p) for p in (candidate_path, mask_path, report_path)],
            'baseValidation': validation}


def canvas_crop(bases, crop_box, field='base'):
    """Read same-coordinate regions; unprovided area remains transparent QA only."""
    out = np.zeros((crop_box[3]-crop_box[1], crop_box[2]-crop_box[0], 4), np.uint8)
    for base in bases:
        clip = intersection(crop_box, base['box'])
        if clip:
            dst, src = slices(clip, crop_box), slices(clip, base['box'])
            out[dst][:, :, :3] = base[field][src]
            out[dst][:, :, 3] = 255
    return out


def apply_repair(base_specs, repair, prefix, band=100, repair_rois=None, mandatory_targets=None, check_only=False, flush_edges=None):
    """Write independent verified art/mask/report for every intersecting tile."""
    safe_prefix(prefix)
    require(7 <= band <= 150, 'Band must be in 7..150.')
    require(base_specs, 'At least one base candidate/mask/report is required.')
    require(not list(QA.glob(prefix+'-*')), f'Output prefix exists: {prefix}. Choose a new prefix.')
    repair_path = within_root(repair if str(repair).lower().endswith('.png') else ROOT/'native'/(str(repair)+'.png'))
    repair_record_path = Path(str(repair_path)+'.generation.json')
    repair_record = load(repair_record_path)
    repair_box = box4(repair_record.get('coordinates', {}).get('nativeGlobalBox'), 'repair nativeGlobalBox')
    require(repair_box[2]-repair_box[0] == REPAIR_SIZE and repair_box[3]-repair_box[1] == REPAIR_SIZE, 'Repair footprint must be 1254 square.')
    repair_hash = sha(repair_path)
    require(repair_hash == repair_record.get('sha256'), 'Repair hash does not match generation record.')
    new = read_image(repair_path, (REPAIR_SIZE, REPAIR_SIZE, 3), 'RGB')
    bases = [read_base(spec) for spec in base_specs]
    flush_edges = list(dict.fromkeys(flush_edges or []))
    require(set(flush_edges) <= {'left', 'right', 'top', 'bottom'}, 'Unknown flush edge.')
    extent = [min(b['box'][0] for b in bases), min(b['box'][1] for b in bases),
              max(b['box'][2] for b in bases), max(b['box'][3] for b in bases)]
    require(len({b['tile'] for b in bases}) == len(bases), 'Duplicate base tile.')
    for i, base in enumerate(bases):
        for other in bases[i+1:]:
            require(intersection(base['box'], other['box']) is None, 'Base tile footprints overlap.')
    old_rgba = canvas_crop(bases, repair_box)
    old, coverage = old_rgba[:, :, :3], old_rgba[:, :, 3] == 255
    selected = np.zeros((REPAIR_SIZE, REPAIR_SIZE), bool)
    rois, paths, cores = repair_rois or [[0, 0, REPAIR_SIZE, REPAIR_SIZE]], [], []
    for i, raw_roi in enumerate(rois, 1):
        roi = box4(raw_roi, 'repair ROI')
        x0, y0, x1, y1 = roi
        require(0 <= x0 < x1 <= REPAIR_SIZE and 0 <= y0 < y1 <= REPAIR_SIZE, 'ROI must stay inside repair image.')
        h, w = y1-y0, x1-x0
        require(min(h, w) > 2*band, 'Each ROI dimension must exceed twice the band width.')
        require(coverage[y0:y1, x0:x1].all(), 'ROI includes pixels outside supplied base tiles.')
        a, b = old[y0:y1, x0:x1], new[y0:y1, x0:x1]
        edges = {'left': (a[:, :band], b[:, :band]),
                 'right': (a[:, ::-1][:, :band], b[:, ::-1][:, :band]),
                 'top': (a[:band].transpose(1, 0, 2), b[:band].transpose(1, 0, 2)),
                 'bottom': (a[::-1][:band].transpose(1, 0, 2), b[::-1][:band].transpose(1, 0, 2))}
        cuts = {}
        for side, (before, after) in edges.items():
            if side in flush_edges:
                axis = {'left': 0, 'top': 1, 'right': 2, 'bottom': 3}[side]
                roi_edge = roi[axis]+repair_box[axis % 2]
                require(roi_edge == extent[axis], 'Flush edge must coincide with the supplied tile group outer boundary.')
                cuts[side] = np.zeros(before.shape[0], np.int16)
                record = {'side': side, 'path': cuts[side].tolist(), 'pathMin': 0, 'pathMax': 0,
                          'selectionMode': 'Explicit native repair to supplied tile group outer boundary; no interior feather or pixel alteration.'}
            else:
                cuts[side], record = cost_path(before, after, side)
            paths.append({**record, 'roiIndex': i, 'repairPatchRoi': roi})
        yy, xx = np.indices((h, w))
        use = ((xx >= cuts['left'][:, None]) & (xx < w-cuts['right'][:, None]) &
               (yy >= cuts['top'][None, :]) & (yy < h-cuts['bottom'][None, :]))
        require(use[band:h-band, band:w-band].all(), 'ROI core was not fully selected.')
        selected[y0:y1, x0:x1] |= use
        cores.append([x0+band, y0+band, x1-band, y1-band])
    targets = mandatory_targets or []
    for target in targets:
        x0, y0, x1, y1 = box4(target, 'mandatory target')
        require(0 <= x0 < x1 <= REPAIR_SIZE and 0 <= y0 < y1 <= REPAIR_SIZE, 'Target must stay inside repair image.')
        require(selected[y0:y1, x0:x1].all(), f'Mandatory target not fully selected: {target}. Enlarge ROI or reduce band.')
    require(selected.any() and not (selected & ~coverage).any(), 'Selected repair pixels must be covered by base art.')
    changed_bases = []
    for base in bases:
        clip = intersection(base['box'], repair_box)
        base['candidate'] = base['base'].copy()
        if not clip:
            continue
        bs, rs = slices(clip, base['box']), slices(clip, repair_box)
        used = {x['sourceId'] for x in base['inputs']}
        available = [x for x in range(1, 256) if x not in used]
        require(available, f'No unused source ID for {base["tile"]}.')
        sid = available[0]
        use = selected[rs]
        base['candidate'][bs][use] = new[rs][use]
        out_ids = base['ids'].copy()
        out_ids[bs][use] = sid
        selection = np.zeros((SIZE, SIZE), bool)
        selection[bs] = use
        require(np.array_equal(base['candidate'][~selection], base['base'][~selection]), 'Art outside selection changed.')
        source = {'sourceId': sid, 'stem': repair_path.stem, 'path': repair_path.as_posix(),
                  'sha256': repair_hash, 'nativeGlobalBox': repair_box,
                  'record': repair_record_path.as_posix(), 'recordSha256': sha(repair_record_path),
                  'role': 'Native AI repair selected by globally shared binary edge mask; DP except explicitly recorded flush outer edges.'}
        base.update({'outputIds': out_ids, 'selection': selection, 'repairSourceId': sid,
                     'newInputs': base['inputs']+[source], 'repairIntersectionGlobalBox': clip})
        base['validation'] = validate_pixels(base['candidate'], out_ids, base['newInputs'], base['box'])
        base['validation'].update({'unchangedOutsideRepairSelection': True, 'mandatoryCoreUsesRepairOnly': True,
                                   'mandatoryTargetsUseRepairOnly': True, 'repairPixelCount': int(selection.sum())})
        changed_bases.append(base)
    require(sum(int(b['selection'].sum()) for b in changed_bases) == int(selected.sum()), 'Distributed selection pixel count mismatch.')
    if check_only:
        return {'status': 'check_only_passed', 'artworkWritten': False, 'repairGlobalBox': repair_box,
                'selectedPixels': int(selected.sum()), 'tiles': [{'tile': b['tile'], 'validation': b['validation']} for b in changed_bases]}
    artifacts = []
    def save(label, arr, extra=None):
        path = QA/(prefix+'-'+label+'.png')
        require(not path.exists(), f'Refusing to overwrite {path}.')
        with path.open('xb') as handle:
            Image.fromarray(arr).save(handle, format='PNG')
        item = {'path': path.as_posix(), 'sha256': sha(path), 'dimensions': [arr.shape[1], arr.shape[0]]}
        if extra:
            item.update(extra)
        artifacts.append(item)
        return item
    def save_json(label, value):
        path = QA/(prefix+'-'+label+'.json')
        with path.open('x', encoding='utf-8') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        return {'path': path.as_posix(), 'sha256': sha(path)}
    local_mask = save('repair-local-selection-mask', selected.astype(np.uint8)*255,
                      {'binaryValues': [0, 255], 'nativeGlobalBox': repair_box, 'scale': '1:1'})
    old_new = old_rgba.copy()
    old_new[:, :, :3][selected] = new[selected]
    save('repair-area-base-left-candidate-right-100pct', np.concatenate((old_rgba, old_new), 1),
         {'nativeGlobalBox': repair_box, 'scale': '1:1', 'transparentPixels': 'Outside supplied base tiles only.'})
    boundary_artifacts = []
    for i, roi in enumerate(rois, 1):
        x0, y0, x1, y1 = [roi[j]+repair_box[j % 2] for j in range(4)]
        boxes = {'top': [x0-100, y0-100, x1+100, y0+band+100],
                 'bottom': [x0-100, y1-band-100, x1+100, y1+100],
                 'left': [x0-100, y0-100, x0+band+100, y1+100],
                 'right': [x1-band-100, y0-100, x1+100, y1+100]}
        for side, crop in boxes.items():
            a, b = canvas_crop(bases, crop), canvas_crop(bases, crop, 'candidate')
            boundary_artifacts.append(save(f'roi{i}-{side}-base-first-candidate-second-100pct',
                 np.concatenate((a, b), 0 if side in ('top', 'bottom') else 1),
                 {'nativeGlobalBox': crop, 'scale': '1:1', 'outsideRoiPaddingPixels': 100,
                  'transparentPixels': 'Outside supplied base tiles only.'}))
    results = []
    for base in changed_bases:
        tile = base['tile']
        art = save(tile+'-candidate-4096', base['candidate'])
        ids = save(tile+'-source-id-mask', base['outputIds'])
        selection = save(tile+'-repair-selection-mask', base['selection'].astype(np.uint8)*255, {'binaryValues': [0, 255]})
        disk = read_image(art['path'], (SIZE, SIZE, 3), 'RGB')
        disk_ids = read_image(ids['path'], (SIZE, SIZE), 'L')
        validation = validate_pixels(disk, disk_ids, base['newInputs'], base['box'])
        require(np.array_equal(disk, base['candidate']) and np.array_equal(disk_ids, base['outputIds']), 'Disk art/mask roundtrip mismatch.')
        disk_selection = read_image(selection['path'], (SIZE, SIZE), 'L')
        require(np.array_equal(disk_selection, base['selection'].astype(np.uint8)*255), 'Disk selection roundtrip mismatch.')
        validation.update(base['validation'])
        validation['diskRoundtripExact'] = True
        validation['mandatoryCorePatchBoxes'] = cores
        validation['mandatoryTargetPatchBoxes'] = targets
        report = {'createdAtUtc': datetime.now(timezone.utc).isoformat(), 'tile': tile,
                  'status': 'QA native repair candidate; pending visual review; not formal acceptance',
                  'algorithm': 'Shared repair-space selection from four continuous edge paths per ROI; DP except explicitly recorded flush outer edges; binary same-global-coordinate pixel selection.',
                  'candidateGlobalBox': base['box'], 'repairGlobalBox': repair_box,
                  'repairIntersectionGlobalBox': base['repairIntersectionGlobalBox'],
                  'parameters': {**PARAMS, 'bandPixels': band, 'repairRois': rois, 'flushOuterEdges': flush_edges},
                  'paths': paths, 'repairSourceId': base['repairSourceId'], 'inputs': base['newInputs'],
                  'outputs': [art, ids, selection, local_mask]+boundary_artifacts,
                  'baseCandidate': {'path': base['paths'][0].as_posix(), 'sha256': base['hashes'][0]},
                  'baseSourceIdMask': {'path': base['paths'][1].as_posix(), 'sha256': base['hashes'][1]},
                  'baseReport': {'path': base['paths'][2].as_posix(), 'sha256': base['hashes'][2]},
                  'baseValidation': base['baseValidation'], 'validation': validation,
                  'sourceIdPixelFormula': '(tile-local x + candidateGlobalBox.x0 - source.nativeGlobalBox.x0, tile-local y + candidateGlobalBox.y0 - source.nativeGlobalBox.y0)',
                  'script': {'path': Path(__file__).as_posix(), 'sha256': sha(__file__)},
                  'limitations': ['Hard selection cannot fix incorrect AI geometry or guarantee invisible edges.',
                                 '100-percent QA views must be inspected before accepting art.',
                                 'Only supplied base tiles are present; QA transparency marks unavailable context.']}
        report_file = save_json(tile+'-report', report)
        results.append({'tile': tile, 'candidate': art, 'sourceIdMask': ids, 'report': report_file,
                        'repairSourceId': base['repairSourceId'], 'validation': validation})
    for base in bases:
        require([sha(p) for p in base['paths']] == base['hashes'], 'Base changed while repair was running.')
    require(sha(repair_path) == repair_hash and sha(repair_record_path) == changed_bases[0]['newInputs'][-1]['recordSha256'], 'Repair source changed during operation.')
    result = {'status': 'qa_candidates_written', 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
              'artworkWritten': True, 'repairGlobalBox': repair_box, 'selectedPixels': int(selected.sum()),
              'repairRois': rois, 'mandatoryTargets': targets, 'flushOuterEdges': flush_edges, 'sharedSelectionMask': local_mask,
              'allInputsUnchanged': True, 'distributedSelectedPixelsExact': True,
              'tiles': results, 'outputs': artifacts}
    result['manifest'] = save_json('manifest', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base-prefix', action='append', default=[], help='Repeat for qa/PREFIX-candidate-4096.png, -source-id-mask.png and -report.json.')
    parser.add_argument('--base', nargs=3, action='append', default=[], metavar=('CANDIDATE', 'MASK', 'REPORT'), help='Explicit base paths; repeat for adjacent tiles.')
    parser.add_argument('--repair', required=True, help='Native source stem, or full PNG path inside southwest; .generation.json must exist.')
    parser.add_argument('--prefix', required=True, help='Fresh safe QA output prefix, e.g. multi-boundary-v01.')
    parser.add_argument('--band', type=int, default=100)
    parser.add_argument('--repair-roi', type=int, nargs=4, action='append', help='Repeat for repair-image-local rectangles.')
    parser.add_argument('--mandatory-target', type=int, nargs=4, action='append', help='Entire rectangle must select AI pixels; fails without writing if unmet.')
    parser.add_argument('--check-only', action='store_true', help='Validate and compute everything in memory without writing outputs.')
    parser.add_argument('--flush-edge', choices=['left', 'right', 'top', 'bottom'], action='append', help='Select repair through an outer edge of the supplied tile group; forbidden on interior edges.')
    args = parser.parse_args()
    try:
        bases = list(args.base)
        for prefix in args.base_prefix:
            safe_prefix(prefix)
            bases.append([QA/(prefix+'-candidate-4096.png'), QA/(prefix+'-source-id-mask.png'), QA/(prefix+'-report.json')])
        result = apply_repair(bases, args.repair, args.prefix, args.band, args.repair_roi, args.mandatory_target, args.check_only, args.flush_edge)
        print(json.dumps({k: v for k, v in result.items() if k != 'outputs'}, ensure_ascii=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'invalid_input', 'message': str(exc)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    sys.exit(main())
