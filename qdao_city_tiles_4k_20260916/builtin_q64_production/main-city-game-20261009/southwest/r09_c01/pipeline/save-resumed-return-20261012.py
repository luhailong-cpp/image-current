from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, sys
from PIL import Image

patch, attempt, source_name, started, returned = sys.argv[1:]
T = Path(__file__).resolve().parents[1]
source = Path(source_name)
request = T / 'pipeline/prompts' / f'{patch}.{attempt}.request.json'
req = json.loads(request.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert req['tile'] == T.name and req['coordinates']['id'] == patch
assert req['prompt'] == Path(req['promptFile']).read_text(encoding='utf-8-sig')
for ref in req['references']:
    assert sha(ref['file']) == ref['sha256']
output = T / 'pipeline/returned-native' / f'{patch}.{attempt}.png'
receipt = T / 'pipeline/receipts' / f'{patch}.{attempt}.receipt.json'
assert source.is_file() and not output.exists() and not receipt.exists()
output.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, output)
assert sha(output) == sha(source)
with Image.open(output) as im:
    im.load()
    size, mode, fmt = list(im.size), im.mode, im.format
rec = {'tool':'image_gen.imagegen','status':'returned_image','route':'builtin',
       'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),
       'savedUnchangedOutput':str(output),'savedOutputSha256':sha(output),
       'nativePixels':size,'mode':mode,'format':fmt,
       'request':str(request),'requestSha256':sha(request),
       'prompt':req['promptFile'],'promptSha256':req['promptSha256'],
       'actualReferences':req['references'],'transparent_background':False,
       'actualModel':None,'actualQuality':None,'apiUsed':False,
       'startedAtUtc':started,'returnedAtUtc':returned,
       'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
       'outputHintEvidence':'Actual builtin tool output named this source path.',
       'formalAccepted':False,'visualStatus':'candidate_pending_joined_QA'}
receipt.parent.mkdir(parents=True, exist_ok=True)
receipt.write_text(json.dumps(rec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'receipt':str(receipt),'savedOutput':str(output),'size':size,'sha256':sha(output)}))
