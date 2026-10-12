from pathlib import Path
import json, re, shutil, hashlib, sys
from PIL import Image

BASE = Path(__file__).resolve().parent
FRAME = sys.argv[1]
receipt = json.loads((BASE / 'receipts' / f'{FRAME}.json').read_text(encoding='utf-8'))
hint = receipt['result']['output_hint']
source = Path(re.search(r' as (.+?\.png) by default', hint, flags=re.S).group(1))
target = BASE / f'{FRAME}.png'
if target.exists():
    raise RuntimeError('Candidate already exists; do not overwrite')
shutil.copy2(source, target)
with Image.open(target) as im:
    info = {'width': im.width, 'height': im.height, 'format': im.format, 'mode': im.mode, 'alphaExtrema': list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None}
hashfile = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs = receipt['request']['referenced_image_paths']
record = {
    'file': target.name,
    'sha256': hashfile(target),
    'startedAt': receipt['startedAt']['current_time'],
    'generatedAt': receipt['completedAt']['current_time'],
    **info,
    'tool': 'image_gen.imagegen', 'route': 'builtin',
    'configSnapshot': json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),
    'submittedParameters': {**receipt['request'], 'model': None, 'quality': None},
    'actualModel': None, 'actualQuality': None,
    'unverifiedReason': 'Host managed: tool exposes no model or quality selectors and returned neither as verifiable metadata.',
    'prompt': f'prompts/{FRAME}.txt',
    'references': [{'path': p, 'sha256AtGeneration': hashfile(p)} for p in refs],
    'evidence': {'receipt': f'receipts/{FRAME}.json', 'outputHintField': 'result.output_hint', 'hostSourcePath': str(source)},
    'action': 'cast', 'direction': 'W', 'frame': int(FRAME), 'durationMs': 45,
    'status': 'candidate-for-owner-review',
    'operation': 'byte-for-byte copy of native image_gen output; no scaling, alignment or pose synthesis',
    'visualReview': {'status': 'static-output-viewed; final sequence review by owner pending', 'clientIntegration': 'not-performed'}
}
(BASE / f'{FRAME}.png.generation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'file': str(target), 'sha256': record['sha256'], **info}, ensure_ascii=False))
