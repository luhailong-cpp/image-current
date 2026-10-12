from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image

B = Path(__file__).resolve().parents[1]
tile, patch, attempt, source_name, output_hint, observation = sys.argv[1:]
assert tile in {f'r{r:02d}_c05' for r in range(9,17)}
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
source = Path(source_name)
assert source.is_file() and str(source) in output_hint
target = T / 'pipeline/returns' / f'{patch}.{attempt}.png'
receipt = T / 'pipeline/receipts' / f'{patch}.{attempt}.receipt.json'
tool_return = T / 'pipeline/returns' / f'{patch}.{attempt}.tool-return.json'
assert not any(p.exists() for p in (target, receipt, tool_return))
target.parent.mkdir(parents=True, exist_ok=True)
receipt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, target)
assert sha(target) == sha(source)
with Image.open(target) as im:
    im.load()
    size, mode, fmt = list(im.size), im.mode, im.format
    opaque = mode == 'RGB' or (mode == 'RGBA' and im.getchannel('A').getextrema() == (255,255))
now = datetime.now(timezone.utc).isoformat()
raw = {'output_hint': output_hint, 'image_url': {'omittedBase64FromMetadata': True, 'unchangedPNGFile': str(target), 'sha256': sha(target)}, 'tool': 'image_gen.imagegen', 'receivedAtUtc': now}
tool_return.write_text(json.dumps(raw, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
rec = {'tool': 'image_gen.imagegen', 'status': 'returned_image', 'recordedAtUtc': now,
       'sourceOutputPath': str(source), 'sourceOutputSha256': sha(source),
       'native': {'file': str(target), 'sha256': sha(target), 'pixels': size, 'mode': mode, 'format': fmt, 'opaque': opaque},
       'request': {'file': str(request), 'sha256': sha(request)},
       'prompt': {'file': req['promptFile'], 'sha256': req['promptSha256']},
       'references': req['references'], 'actualModel': None, 'actualQuality': None,
       'submittedParameters': {'model': None, 'quality': None, 'transparent_background': False},
       'nativePixelsPreserved': True, 'resizedAfterGeneration': False,
       'visualObservation': observation, 'internalAccepted': False, 'formalAccepted': False,
       'toolOutputMetadata': {'output_hint': output_hint}, 'toolReturn': {'file': str(tool_return), 'sha256': sha(tool_return)}}
receipt.write_text(json.dumps(rec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'receipt': str(receipt), 'nativeReturn': str(target), 'sha256': sha(target), 'pixels': size}, ensure_ascii=False))
