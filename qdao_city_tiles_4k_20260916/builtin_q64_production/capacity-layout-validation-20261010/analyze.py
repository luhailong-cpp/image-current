"""Static layout experiment. Reads artwork; never edits it or a client asset.

Polygons are human estimates of visible ground. Raster connectivity cannot infer
an occluded doorway. Slot counts are design experiments, not MMO load tests.
"""
from pathlib import Path
from collections import deque
import base64
import hashlib
import json
import math
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
LABELS = {'main': '主城', 'village': '渔村', 'island': '八仙岛'}
SIDES = [600, 700, 800, 900, 1000, 1100]
ACTORS = [
    ('道童', 'QdaoOriginalRosterV13/00_reference_topright_boy/idle/S.png', 52),
    ('冰剑少女', 'QdaoOriginalRosterV13/01_ice_sword_girl/idle/S.png', 52),
    ('雷法少年', 'QdaoOriginalRosterV14/06_thunder_caster_boy/idle/S.png', 104),
    ('星阵少女', 'QdaoOriginalRosterV14/20_star_formation_master_girl/idle/S.png', 104),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_url(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def raster(annotation):
    # Analysis-only binary geometry; no source artwork is resampled or painted.
    im = Image.new('1', (annotation['annotationWidth'], annotation['annotationHeight']))
    draw = ImageDraw.Draw(im)
    for poly in annotation['walkablePolygons']:
        draw.polygon([tuple(p) for p in poly['points']], fill=1)
    for poly in annotation['obstaclePolygons']:
        draw.polygon([tuple(p) for p in poly['points']], fill=0)
    return np.asarray(im, dtype=bool).copy()


def components(mask):
    # Four-neighbour connectivity: diagonal corner contacts do not make a road.
    h, w = mask.shape
    padded = np.pad(mask, 1).ravel()
    pw = w + 2
    labels = np.zeros(padded.size, dtype=np.int32)
    sizes = []
    for seed in np.flatnonzero(padded):
        if labels[seed]:
            continue
        label = len(sizes) + 1
        labels[seed] = label
        queue = deque([int(seed)])
        size = 0
        while queue:
            index = queue.popleft()
            size += 1
            for nxt in (index - 1, index + 1, index - pw, index + pw):
                if padded[nxt] and labels[nxt] == 0:
                    labels[nxt] = label
                    queue.append(nxt)
        sizes.append(size)
    labels = labels.reshape((h + 2, w + 2))[1:-1, 1:-1]
    return labels, sizes


def grid_slots(mask, world_side, spacing):
    """Square grid of feet centres, with a 1.45-unit shadow-radius clearance.

    Twenty angular perimeter samples are an approximation on a manually annotated
    raster. This is intentionally not named a collision or navigation test.
    """
    h, w = mask.shape
    step = spacing * w / world_side
    radius = 1.45 * w / world_side
    best = np.empty((0, 2), dtype=float)
    for ox, oy in ((0.5, 0.5), (0.25, 0.25), (0.25, 0.75), (0.75, 0.25)):
        xs = np.arange(step * ox, w, step)
        ys = np.arange(step * oy, h, step)
        xx, yy = np.meshgrid(xs, ys)
        pts = np.column_stack((xx.ravel(), yy.ravel()))
        keep = np.ones(len(pts), dtype=bool)
        offsets = [(0, 0)] + [(math.cos(a) * radius, math.sin(a) * radius)
                                for a in np.linspace(0, math.tau, 20, endpoint=False)]
        for dx, dy in offsets:
            xi = np.floor(pts[:, 0] + dx).astype(int)
            yi = np.floor(pts[:, 1] + dy).astype(int)
            valid = (xi >= 0) & (yi >= 0) & (xi < w) & (yi < h)
            values = np.zeros(len(pts), dtype=bool)
            values[valid] = mask[yi[valid], xi[valid]]
            keep &= values
        selected = pts[keep]
        if len(selected) > len(best):
            best = selected
    return best


def analyze(annotation):
    path = Path(annotation['imagePath'])
    assert sha(path) == annotation['imageSha256'], 'Artwork changed after annotation'
    with Image.open(path) as image:
        assert image.size == (annotation['annotationWidth'], annotation['annotationHeight'])
    mask = raster(annotation)
    labels, sizes = components(mask)
    largest_id = int(np.argmax(sizes)) + 1
    largest = labels == largest_id
    anchors = []
    for point in annotation['anchors']:
        x, y = map(int, point['point'])
        anchors.append({**point, 'component': int(labels[y, x]),
                        'inLargestComponent': bool(largest[y, x])})
    scenarios = []
    for main_side in SIDES:
        side = main_side * (1 if annotation['map'] == 'main' else math.sqrt(0.75))
        for spacing in (5, 6):
            slots = grid_slots(largest, side, spacing)
            # 20% unoccupied slots are equivalent to 25% extra capacity over people.
            limit = math.floor(len(slots) * 0.8)
            count = min(5000, limit)
            rng = np.random.default_rng(5000)
            selected = slots[rng.permutation(len(slots))[:count]]
            selected = selected[np.argsort(selected[:, 1])]
            ix = np.floor(selected[:, 0]).astype(int)
            iy = np.floor(selected[:, 1]).astype(int)
            assert np.all(largest[iy, ix])
            assert len(selected) == len(set(map(tuple, selected)))
            scenarios.append({
                'mainWorldSide': main_side, 'worldSide': side, 'spacing': spacing,
                'slotCount': len(slots), 'largestComponentSlots': len(slots),
                'reservedFraction': 0.2, 'usableAfterReserve': limit,
                'placedCount': count, 'all5000Placed': count == 5000,
                'areaWorld': int(mask.sum()) / mask.size * side**2,
                'largestComponentAreaWorld': int(largest.sum()) / mask.size * side**2,
                'positions': np.round(selected, 3).tolist(),
                'continuousReservedCorridorValidated': False,
                'runtimePerformanceValidated': False,
                'method': 'Square feet grid, largest visible component only; sampled shadow clearance. Distributed empty slots do not prove uninterrupted circulation.',
            })
    return {
        'walkablePixels': int(mask.sum()), 'walkableFraction': int(mask.sum()) / mask.size,
        'componentCount': len(sizes), 'componentSizesPixels': sorted(sizes, reverse=True),
        'largestComponentFraction': int(largest.sum()) / mask.size,
        'largestShareOfAnnotatedGround': int(largest.sum()) / int(mask.sum()),
        'anchors': anchors, 'scenarios': scenarios,
        'allAnchorsInLargestVisibleComponent': all(a['inLargestComponent'] for a in anchors),
    }


def main():
    result = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'method': '人工保守可见地面＋真实角色原世界尺度＋最大连通片静态站位。非真实导航、通行或5000人运行验收。',
        'capacity5000Validated': False, 'worldSizeApproved': False,
        'reserveMeaning': '20%站位空置（等价于比人数多25%的位置），不代表预留通道已验证连续。',
        'actorFootClearanceRadiusWorld': 1.45,
        'actors': [], 'maps': [],
    }
    for label, relative, ppu in ACTORS:
        path = Path('D:/work/mmorpg-client/Assets/Resources/World/Characters') / relative
        with Image.open(path) as im:
            frame = im.height / ppu
        result['actors'].append({'label': label, 'path': str(path), 'sha256': sha(path),
                                 'frameWorldHeight': frame, 'pivot': [0.5, 0.92]})
    for mid, label in LABELS.items():
        p = ROOT / 'maps' / f'{mid}.json'
        annotation = json.loads(p.read_text(encoding='utf-8-sig'))
        analysis = analyze(annotation)
        result['maps'].append({'id': mid, 'label': label, 'annotation': annotation,
                               'annotationSha256': sha(p), 'analysis': analysis})
    (ROOT / 'results.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    summary = {**result, 'actors': result['actors'], 'maps': []}
    for m in result['maps']:
        data = {**m['analysis'], 'scenarios': [{k: v for k, v in s.items() if k != 'positions'} for s in m['analysis']['scenarios']]}
        summary['maps'].append({'id': m['id'], 'label': m['label'], 'annotationSha256': m['annotationSha256'], 'analysis': data})
    (ROOT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    for actor in result['actors']:
        actor['imageUrl'] = image_url(Path(actor['path']))
    for m in result['maps']:
        m['annotation']['imageUrl'] = image_url(Path(m['annotation']['imagePath']))
    (ROOT / 'results.js').write_text('window.CAPACITY_REVIEW=' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print(json.dumps([{'map': m['id'], 'visibleFraction': m['analysis']['walkableFraction'],
                       'largestFraction': m['analysis']['largestComponentFraction'],
                       'first5000at5': next((s['mainWorldSide'] for s in m['analysis']['scenarios'] if s['spacing'] == 5 and s['all5000Placed']), None),
                       'first5000at6': next((s['mainWorldSide'] for s in m['analysis']['scenarios'] if s['spacing'] == 6 and s['all5000Placed']), None)} for m in result['maps']], ensure_ascii=False))


if __name__ == '__main__':
    main()
