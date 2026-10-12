from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image

B = Path(__file__).resolve().parents[2]
data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
tile, patch, attempt = data['tile'], data['patch'], data['attempt']
assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9, 17) for c in (7, 8)}
T = B / tile
request = T / 'pipeline/prompts' / f'{patch}.{attempt}.request.json'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
req = read(request)
assert req['tile'] == tile and req['coordinates']['id'] == patch
assert Path(req['promptFile']).read_text(encoding='utf-8-sig') == req['prompt']
assert sha(Path(req['promptFile'])) == req['promptSha256']
for ref in req['references']:
    assert sha(Path(ref['file'])) == ref['sha256']
source = Path(data['sourceOutputPath'])
assert source.is_file()
target = T / 'pipeline/returned-originals' / f'{patch}.{attempt}.png'
receipt = T / 'pipeline/receipts' / f'{patch}.{attempt}.receipt.json'
assert not target.exists() and not receipt.exists()
target.parent.mkdir(parents=True, exist_ok=True)
receipt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, target)
assert sha(target) == sha(source)
with Image.open(target) as im:
    im.load()
    size, mode, fmt = list(im.size), im.mode, im.format
    opaque = mode == 'RGB' or (mode == 'RGBA' and im.getchannel('A').getextrema() == (255, 255))
rec = dict(data, tool='image_gen.imagegen', status='returned_image',
           recordedAtUtc=datetime.now(timezone.utc).isoformat(),
           sourceOutputSha256=sha(source), savedUnmodifiedOriginal=str(target),
           savedUnmodifiedOriginalSha256=sha(target), nativePixels=size,
           format=fmt, mode=mode, opaque=opaque, request=str(request),
           requestSha256=sha(request), actualModel=None, actualQuality=None,
           paidApiUsed=False, resizedAfterGeneration=False,
           internalAccepted=False, formalAccepted=False)
receipt.write_text(json.dumps(rec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'receipt':str(receipt), 'original':str(target), 'sha256':sha(target), 'pixels':size}, ensure_ascii=False))
