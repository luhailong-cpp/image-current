"""QA-only native hard seam candidate. No blending, resampling or image synthesis.

Every candidate pixel copies a selected input pixel at exactly the same global
coordinate. Only the 1254-pixel QA preview is resized. This cannot repair geometry.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import argparse
import re
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
QA = ROOT / 'qa'
STEP = 1024
NATIVE = 1254
HALO = 115
OVERLAP = 230
PREFIX = 'hardseam'
PARAMS = {'rgbDifferenceWeight': 1.0, 'gradientDifferenceWeight': 0.4,
          'gradientStrengthWeight': 0.08, 'lateralStepPenalty': 0.75,
          'centerBiasPerPixel': 0.0002, 'maxStepPerPixel': 1,
          'edgeMarginPixels': 3}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def save(name, array):
    path = QA / (PREFIX + '-' + name + '.png')
    Image.fromarray(array).save(path)
    return {'path': path.as_posix(), 'dimensions': list(Image.open(path).size), 'sha256': sha(path)}

def gradients(a):
    a = a.astype(np.float32)
    gy, gx = np.gradient(a, axis=(0, 1))
    return gx, gy

def seam(a, b, label):
    """Both images H x 230. Path is first B column; left side uses A."""
    af = a.astype(np.float32)
    bf = b.astype(np.float32)
    diff = np.abs(af-bf).mean(axis=2)
    agx, agy = gradients(a)
    bgx, bgy = gradients(b)
    gd = (np.abs(agx-bgx)+np.abs(agy-bgy)).mean(axis=2)
    gs = np.maximum(np.hypot(agx, agy).mean(axis=2), np.hypot(bgx, bgy).mean(axis=2))
    cost = diff + PARAMS['gradientDifferenceWeight']*gd + PARAMS['gradientStrengthWeight']*gs
    cost += np.abs(np.arange(OVERLAP)-HALO)[None, :]*PARAMS['centerBiasPerPixel']
    margin = PARAMS['edgeMarginPixels']
    cost[:, :margin] = np.inf
    cost[:, -margin:] = np.inf
    previous = cost[0].copy()
    back = np.zeros(cost.shape, np.int8)
    penalty = PARAMS['lateralStepPenalty']
    for y in range(1, cost.shape[0]):
        left = np.r_[np.inf, previous[:-1]+penalty]
        right = np.r_[previous[1:]+penalty, np.inf]
        options = np.stack((left, previous, right))
        choice = options.argmin(axis=0)
        back[y] = choice.astype(np.int8)-1
        previous = options[choice, np.arange(OVERLAP)]+cost[y]
    path = np.empty(cost.shape[0], np.int16)
    path[-1] = previous.argmin()
    for y in range(len(path)-1, 0, -1):
        path[y-1] = path[y]+back[y, path[y]]
    assert np.max(np.abs(np.diff(path))) <= 1
    rr = np.arange(len(path))
    def stats(values):
        return {'mean': float(values.mean()), 'p95': float(np.percentile(values, 95)), 'max': float(values.max())}
    record = {'label': label, 'axis': 'first-B-column-per-row',
              'path': path.tolist(), 'pathMin': int(path.min()), 'pathMax': int(path.max()),
              'rgbDifferenceChosen': stats(diff[rr, path]),
              'rgbDifferenceMidpoint': stats(diff[:, HALO]),
              'weightedChosen': stats(cost[rr, path]),
              'weightedMidpoint': stats(cost[:, HALO])}
    return path, record

def join(a, aid, b, bid, offset, label):
    overlap_a = a[:, offset:offset+OVERLAP]
    overlap_b = b[:, :OVERLAP]
    path, rec = seam(overlap_a, overlap_b, label)
    take_b = np.arange(OVERLAP)[None, :] >= path[:, None]
    out = np.empty((a.shape[0], offset+b.shape[1], 3), np.uint8)
    ids = np.empty(out.shape[:2], np.uint8)
    out[:, :a.shape[1]] = a
    ids[:, :a.shape[1]] = aid
    out[:, offset+OVERLAP:] = b[:, OVERLAP:]
    ids[:, offset+OVERLAP:] = bid[:, OVERLAP:]
    out[:, offset:offset+OVERLAP] = np.where(take_b[..., None], overlap_b, overlap_a)
    ids[:, offset:offset+OVERLAP] = np.where(take_b, bid[:, :OVERLAP], aid[:, offset:offset+OVERLAP])
    rec['overlapOffset'] = offset
    return out, ids, rec

def main(prefix='hardseam'):
    global PREFIX
    if not re.fullmatch(r'hardseam(?:-[a-zA-Z0-9]+)*', prefix):
        raise ValueError('Output prefix must remain within qa/hardseam-*')
    PREFIX = prefix
    index = json.loads((ROOT/'current-native-map.json').read_text(encoding='utf-8-sig'))
    selected = index['r09_c03']
    assert len(selected) == 4 and all(len(row) == 4 for row in selected)
    inputs = []
    data = []
    for r, row in enumerate(selected):
        for c, stem in enumerate(row):
            path = ROOT/'native'/(stem+'.png')
            recpath = Path(str(path)+'.generation.json')
            rec = json.loads(recpath.read_text(encoding='utf-8-sig'))
            box = rec['coordinates']['nativeGlobalBox']
            assert box == [8077+c*STEP, 32653+r*STEP, 9331+c*STEP, 33907+r*STEP], (stem, box)
            im = Image.open(path)
            assert im.mode == 'RGB' and im.size == (NATIVE, NATIVE), (stem, im.mode, im.size)
            data.append(np.array(im))
            inputs.append({'sourceId': 1+r*4+c, 'row': r+1, 'column': c+1, 'stem': stem,
                           'path': path.as_posix(), 'sha256': sha(path), 'nativeGlobalBox': box,
                           'record': recpath.as_posix(), 'recordSha256': sha(recpath)})
    rows = []
    row_ids = []
    seams = []
    for r in range(4):
        canvas = data[r*4]
        ids = np.full((NATIVE, NATIVE), 1+r*4, np.uint8)
        for c in range(1, 4):
            right = data[r*4+c]
            rid = np.full((NATIVE, NATIVE), 1+r*4+c, np.uint8)
            canvas, ids, rec = join(canvas, ids, right, rid, c*STEP, f'row-{r+1}-columns-{c}-{c+1}')
            rec['assemblyFrameOriginGlobal'] = [8077, 32653+r*STEP]
            rec['orientation'] = 'vertical-path'
            seams.append(rec)
        rows.append(canvas)
        row_ids.append(ids)
    canvas, ids = rows[0], row_ids[0]
    for r in range(1, 4):
        trans, tids, rec = join(canvas.transpose(1, 0, 2), ids.T, rows[r].transpose(1, 0, 2), row_ids[r].T, r*STEP, f'rows-{r}-{r+1}')
        canvas, ids = trans.transpose(1, 0, 2), tids.T
        rec['orientation'] = 'horizontal-path; path entries are first-B-row-per-column'
        rec['assemblyFrameOriginGlobal'] = [8077, 32653]
        seams.append(rec)
    assert canvas.shape == (4326, 4326, 3)
    candidate = canvas[HALO:HALO+4096, HALO:HALO+4096].copy()
    source_mask = ids[HALO:HALO+4096, HALO:HALO+4096].copy()
    del canvas, ids, rows, row_ids
    validated = 0
    counts = {}
    for inp, arr in zip(inputs, data):
        sid = inp['sourceId']
        yy, xx = np.where(source_mask == sid)
        nx = xx + 8192-inp['nativeGlobalBox'][0]
        ny = yy + 32768-inp['nativeGlobalBox'][1]
        assert nx.min() >= 0 and nx.max() < NATIVE and ny.min() >= 0 and ny.max() < NATIVE
        bad = np.any(candidate[yy, xx] != arr[ny, nx], axis=1)
        assert not bad.any(), (sid, int(bad.sum()))
        validated += len(xx)
        counts[str(sid)] = len(xx)
    assert validated == 4096**2
    straight = np.concatenate([np.concatenate([data[r*4+c][HALO:HALO+STEP, HALO:HALO+STEP] for c in range(4)], axis=1) for r in range(4)], axis=0)
    outputs = [save('candidate-4096', candidate), save('source-id-mask', source_mask), save('straight-4096', straight)]
    preview_path = QA/(PREFIX+'-preview-1254-QA-only.png')
    Image.fromarray(candidate).resize((1254, 1254), Image.Resampling.LANCZOS).save(preview_path)
    outputs.append({'path': preview_path.as_posix(), 'dimensions': [1254, 1254], 'sha256': sha(preview_path), 'resampledQAPreviewOnly': True})
    crops = []
    for y in (1024, 2048, 3072):
        for x in (1024, 2048, 3072):
            box = [x-300, y-300, x+300, y+300]
            a = straight[box[1]:box[3], box[0]:box[2]]
            b = candidate[box[1]:box[3], box[0]:box[2]]
            out = save(f'cross-{x}-{y}-straight-left-candidate-right-100pct', np.concatenate((a, b), axis=1))
            out.update({'sourceCrop': box, 'left': 'straight native core', 'right': 'hard seam candidate', 'scale': '1:1'})
            crops.append(out)
    # Extra visible wall and door runs, away from crossings.
    for label, box in [('wall-row34', [0, 2922, 4096, 3222]), ('central-vertical', [1898, 2048, 2198, 4096])]:
        a = straight[box[1]:box[3], box[0]:box[2]]
        b = candidate[box[1]:box[3], box[0]:box[2]]
        axis = 0 if label == 'wall-row34' else 1
        out = save(label+'-straight-first-candidate-second-100pct', np.concatenate((a, b), axis=axis))
        out.update({'sourceCrop': box, 'first': 'straight native core', 'second': 'hard seam candidate', 'scale': '1:1'})
        crops.append(out)
    # Verify disk roundtrip and unchanged source inputs.
    reread = np.array(Image.open(QA/(PREFIX+'-candidate-4096.png')))
    assert np.array_equal(candidate, reread)
    assert all(sha(inp['path']) == inp['sha256'] for inp in inputs)
    report = {'createdAtUtc': datetime.now(timezone.utc).isoformat(), 'tile': 'r09_c03',
              'status': 'QA candidate; not production acceptance; does not repair geometry',
              'algorithm': 'Sequential continuous DP hard seams: each row left-to-right, then rows top-to-bottom; RGB and gradient difference with gradient strength and path step penalties',
              'parameters': PARAMS, 'selectedMapSha256': sha(ROOT/'current-native-map.json'),
              'scriptPath': Path(__file__).as_posix(), 'scriptSha256': sha(__file__),
              'candidateGlobalBox': [8192,32768,12288,36864], 'assemblyCrop': [115,115,4211,4211],
              'inputs': inputs, 'outputs': outputs, 'comparisonCrops': crops, 'seams': seams,
              'validation': {'pixelCount': validated, 'exactSameGlobalCoordinateSourcePixels': True,
                             'sourceIdPixelCounts': counts, 'diskRoundtripExact': True, 'sourceInputsUnchanged': True,
                             'interpolation': False, 'feathering': False, 'colorAdjustment': False, 'displacement': False,
                             'candidateDiffersFromStraightPixelCount': int(np.any(candidate != straight, axis=2).sum())},
              'limitations': ['Native overlapping images can disagree in geometry and lighting; this operation chooses existing pixels only.',
                              'Sequential row assembly gives later horizontal seams priority at crossings.',
                              'Mask identifies selected native sources; derived sources retain their prior generation provenance.']}
    dump(QA/(PREFIX+'-report.json'), report)
    print(json.dumps({'candidate': outputs[0], 'report': (QA/(PREFIX+'-report.json')).as_posix(), 'validatedPixels': validated, 'seams': len(seams)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', default='hardseam')
    args = parser.parse_args()
    main(args.prefix)
