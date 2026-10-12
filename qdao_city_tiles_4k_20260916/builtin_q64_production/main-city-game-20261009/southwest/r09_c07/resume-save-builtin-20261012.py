from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image

base = Path(__file__).resolve().parent.parent
tile, patch, attempt, source_name, *started = sys.argv[1:]
assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
target = base / tile
source = Path(source_name)
request = target / 'pipeline' / 'prompts' / f'{patch}.{attempt}.request.json'
assert source.is_file() and request.is_file()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw = target / 'pipeline' / 'returned-originals' / f'{patch}.{attempt}.png'
receipt = target / 'pipeline' / 'receipts' / f'{patch}.{attempt}.receipt.json'
assert not raw.exists() and not receipt.exists()
raw.parent.mkdir(parents=True, exist_ok=True)
receipt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, raw)
assert sha(raw) == sha(source)
with Image.open(raw) as im:
    pixels, mode, fmt = list(im.size), im.mode, im.format
data = {'tool':'image_gen.imagegen','status':'returned_image',
        'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),
        'savedUnmodifiedOriginal':str(raw),'savedUnmodifiedOriginalSha256':sha(raw),
        'nativePixels':pixels,'format':fmt,'mode':mode,
        'request':str(request),'requestSha256':sha(request),
        'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
        'startedAtUtc':started[0] if started else None,
        'apiUsed':False,'visualDisposition':'pending_visual_inspection',
        'actualModel':None,'actualQuality':None,
        'outputHint':f'Generated images are saved to {source.parent} as {source} by default.'}
receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(receipt),'original':str(raw),'pixels':pixels,'sha256':sha(raw)}))
