from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, sys, re
from PIL import Image

B = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(B))
from checkpoint_resume import atomic_json

tile, patch, attempt, request_name, receipt_name = sys.argv[1:]
assert re.fullmatch(r'r(?:09|1[0-6])_c0[1-8]', tile)
assert re.fullmatch(r'p0[1-4]_0[1-4]', patch)
assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', attempt)
T = B / tile
request, receipt = Path(request_name), Path(receipt_name)
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
req, rr = read(request), read(receipt)
assert rr['tool'] == 'image_gen.imagegen' and rr['status'] == 'returned_image'
assert not rr.get('explicitlyRejected', False)
assert req['tile'] == tile and req['coordinates']['id'] == patch
assert Path(req['promptFile']).read_text(encoding='utf-8') == req['prompt']
assert sha(Path(req['promptFile'])) == req['promptSha256']
for ref in req['references']:
    assert sha(Path(ref['file'])) == ref['sha256']
source = Path(rr['sourceOutputPath'])
with Image.open(source) as im:
    assert im.size == (1254, 1254) and im.format == 'PNG'
    assert im.mode in ('RGB', 'RGBA')
    if im.mode == 'RGBA':
        assert im.getchannel('A').getextrema() == (255, 255)
target = T / 'refinement' / 'versions' / attempt / (patch + '.png')
record = Path(str(target) + '.generation.json')
assert not target.exists() and not record.exists()
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, target)
base_record = T / 'native' / (patch + '.png.generation.json')
rec = read(base_record)
rec.update(file=str(target), sha256=sha(target), sourceOutputPath=str(source),
           sourceOutputSha256=sha(source), generatedAt=datetime.now(timezone.utc).isoformat(),
           prompt=req['promptFile'], promptSha256=req['promptSha256'], request=str(request),
           requestSha256=sha(request), references=req['references'],
           neighborSources=req.get('neighborSources', []), cornerTreatment=req.get('cornerTreatment'),
           coordinates=req['coordinates'], formalAccepted=False, visualStatus='candidate_pending_joined_QA',
           refinementOf=str(base_record), nativePixelsPreserved=True, resizedAfterGeneration=False)
rec['evidence'] = {'toolReceipt': str(receipt), 'toolReceiptSha256': sha(receipt), 'pngMetadata': {}}
atomic_json(record, rec)
selection = T / 'refinement' / 'selection.json'
sel = read(selection) if selection.exists() else {}
previous = sel.get(patch, 'native/' + patch + '.png.generation.json')
sel[patch] = record.relative_to(T).as_posix()
atomic_json(selection, sel)
atomic_json(target.parent / (patch + '.selection-evidence.json'), {
    'previousRecord': previous, 'newRecord': sel[patch], 'recordSha256': sha(record),
    'selectedAtUtc': datetime.now(timezone.utc).isoformat(), 'formalAccepted': False})
print(json.dumps({'native': str(target), 'sha256': sha(target), 'selected': patch, 'formalAccepted': False}))
