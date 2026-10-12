"""Local-only native QA. No generator, API, resizing, repainting or shared state writes."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
SW = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SW))
from native_pipeline import Pipeline, quilt

TAG = 'local-review-20261013-v01'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
MANIFESTS = {
 'r09_c01': SW/'r09_c01/pipeline/output/0310020c9169112c/assembly.json',
 'r09_c02': SW/'r09_c02/pipeline/output/8550093af869f2fe/assembly.json',
 'r09_c03': SW/'r09_c03/pipeline/output/4e586b2c586d8ef0/assembly.json'
}
docs, cores, supplemental = {}, {}, {}

def save_image(q, im, name, source=None, box=None, contributions=None):
    target = q/name
    assert not target.exists()
    im.save(target, format='PNG')
    with Image.open(target) as test:
        test.load()
        assert test.size == im.size and test.mode == im.mode and test.tobytes() == im.tobytes()
    return {'file': str(target), 'sha256': sha(target), 'pixels': list(im.size),
            'source': source, 'sourceBox': box, 'contributions': contributions,
            'QAOnly': True, 'sourceResampling': False, 'formalAccepted': False}

def panels(q, im, stem, record):
    w, h = im.size
    columns, rows = w//1024, h//1024
    if columns > 1 and rows > 1:
        panel = Image.new('RGB', ((columns-1)*524, (rows-1)*536), 'white')
        draw = ImageDraw.Draw(panel)
        contributions = []
        for r in range(1, rows):
            for c in range(1, columns):
                box = [c*1024-256, r*1024-256, c*1024+256, r*1024+256]
                target = [(c-1)*524, (r-1)*536+24]
                panel.paste(im.crop(box), tuple(target))
                draw.text((target[0]+4, target[1]-21), f'x{c*1024} y{r*1024}', fill='black')
                contributions.append({'source': record['file'], 'sourceBox': box, 'panelOrigin': target})
        record['panels'].append(save_image(q, panel, stem+'-intersections.png', contributions=contributions))
    for c in range(1, columns):
        panel = Image.new('RGB', (rows*250, 1048), 'white')
        draw = ImageDraw.Draw(panel)
        contributions = []
        for r in range(rows):
            box = [c*1024-119, r*1024, c*1024+119, (r+1)*1024]
            target = [r*250, 24]
            panel.paste(im.crop(box), tuple(target))
            draw.text((target[0]+3, 3), f'x{c*1024} y{r*1024}..{(r+1)*1024}', fill='black')
            contributions.append({'source': record['file'], 'sourceBox': box, 'panelOrigin': target})
        record['panels'].append(save_image(q, panel, f'{stem}-vertical-x{c*1024}.png', contributions=contributions))
    for r in range(1, rows):
        panel = Image.new('RGB', (1024, columns*262), 'white')
        draw = ImageDraw.Draw(panel)
        contributions = []
        for c in range(columns):
            box = [c*1024, r*1024-119, (c+1)*1024, r*1024+119]
            target = [0, c*262+24]
            panel.paste(im.crop(box), tuple(target))
            draw.text((3, target[1]-21), f'y{r*1024} x{c*1024}..{(c+1)*1024}', fill='black')
            contributions.append({'source': record['file'], 'sourceBox': box, 'panelOrigin': target})
        record['panels'].append(save_image(q, panel, f'{stem}-horizontal-y{r*1024}.png', contributions=contributions))

for tile, mp in MANIFESTS.items():
    m = read(mp)
    p = Pipeline(tile)
    arrays, entries = p.sources()
    p.stable()
    current = {e['id']: e['nativeSha256'] for e in entries}
    old = {e['id']: e['nativeSha256'] for e in m['nativeSources']}
    assert current == old, f'Selected native sources changed: {tile}'
    assert sha(m['output']['file']) == m['output']['sha256']
    q = SW/tile/'pipeline'/TAG
    assert not q.exists()
    q.mkdir(parents=True)
    im = Image.open(m['output']['file']).convert('RGB')
    assert list(im.size) == [m['output']['width'], m['output']['height']]
    doc = {'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(),
           'tile': tile, 'sourceAssembly': str(mp), 'sourceAssemblySha256': sha(mp),
           'sourceOutput': m['output'], 'selectedNativeCount': len(entries),
           'selectedNativeIds': sorted(current),
           'missingPatchIds': [f'p{r:02}_{c:02}' for r in range(1,5) for c in range(1,5)
                               if (r,c) not in arrays],
           'formalAccepted': False, 'actualModel': None, 'actualQuality': None,
           'generatorCallsMadeByThisReview': 0, 'sourceResampling': False,
           'selectedNativeSources': entries, 'assembledRectangles': [], 'qaImages': []}
    core = {'file': m['output']['file'], 'sha256': m['output']['sha256'],
            'pixels': list(im.size), 'rectangleInclusive': m['selectedRectangleInclusive'], 'panels': []}
    panels(q, im, 'main', core)
    doc['assembledRectangles'].append(core)
    cores[tile] = im
    if tile == 'r09_c03':
        rectangle = (1,1,4,2)
        required = {(r,c) for r in range(1,5) for c in range(1,3)}
        assert required <= set(arrays)
        combined, metrics = quilt.assemble_pixels(arrays, rectangle, 2)
        context = Image.fromarray(combined)
        crop = context.crop((115,115,2163,4211))
        assert crop.size == (2048,4096)
        cx = save_image(q, context, 'available-left-4x2.context.png')
        rec = save_image(q, crop, 'available-left-4x2.png')
        rec.update(rectangleInclusive=list(rectangle), panels=[], context=cx,
                   usedNativePatchIds=[f'p{r:02}_{c:02}' for r,c in sorted(required)],
                   maximumFeatherRadiusPixels=2, seamMetrics=metrics,
                   missingPixelsFilled=False, colorAdjustment=False, blur=False,
                   geometryWarping=False, finalArtUpscaled=False)
        panels(q, crop, 'left4x2', rec)
        doc['assembledRectangles'].append(rec)
        supplemental[tile] = crop
        doc['qaImages'].append(save_image(q, crop.crop((0,3072,2048,4096)),
                   'bottom-left-two-available-cores.png', source=rec['file'], box=[0,3072,2048,4096]))
    docs[tile] = (q, doc)

for left, right in [('r09_c01','r09_c02'), ('r09_c02','r09_c03')]:
    li = cores[left]
    ri = cores[right]
    q, doc = docs[right]
    panel = Image.new('RGB', (1040,1048), 'white')
    draw = ImageDraw.Draw(panel)
    contributions=[]
    for k in range(4):
        y = k*1024
        part = Image.new('RGB',(256,1024))
        part.paste(li.crop((3968,y,4096,y+1024)), (0,0))
        rsource = supplemental[right] if right in supplemental and k==3 else ri
        assert rsource.height >= y+1024
        part.paste(rsource.crop((0,y,128,y+1024)), (128,0))
        panel.paste(part,(k*260,24))
        draw.text((k*260+3,3),f'{left}/{right} row{k+1}',fill='black')
        contributions.append({'leftSource': MANIFESTS[left].as_posix(),
             'leftCoreBox':[3968,y,4096,y+1024],
             'rightSource': 'available-left-4x2' if rsource is supplemental.get(right) else MANIFESTS[right].as_posix(),
             'rightCoreBox':[0,y,128,y+1024], 'panelOrigin':[k*260,24],
             'operation':'exact adjacent core edge strips pasted without blending or resampling'})
    rec=save_image(q,panel,f'external-{left}-to-{right}.png',contributions=contributions)
    rec['tileBoundaryReviewed']='pending_actual_visual_inspection'
    doc['qaImages'].append(rec)

for tile, (q,doc) in docs.items():
    file=q/'manifest.json'
    assert not file.exists()
    file.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tile':tile,'manifest':str(file),'sha256':sha(file),
        'selectedNativeCount':doc['selectedNativeCount'],'missing':doc['missingPatchIds'],
        'panels':sum(len(x['panels']) for x in doc['assembledRectangles'])+len(doc['qaImages']),
        'formalAccepted':False},ensure_ascii=False))
