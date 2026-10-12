"""Export three inspected builtin whisker repairs; no pose synthesis."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'records/cast/E/edge-root-20261008'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ('05', '07', '08'):
    runtime = ROOT / f'runtime/cast/E/{n}.png'
    request = json.loads((REC / f'{n}.request.json').read_text(encoding='utf-8'))
    receipt = json.loads((REC / f'{n}.receipt.json').read_text(encoding='utf-8'))
    previous = json.loads((REC / f'{n}.previous.generation.json').read_text(encoding='utf-8'))
    assert sha(runtime) == previous['sha256'], 'Unexpected runtime replacement: ' + n
    native = Path(re.search(r'as (C:.*?\.png) by default', receipt['output_hint']).group(1))
    im = Image.open(native)
    assert im.mode == 'RGBA' and im.size == (1254, 1254), (im.mode, im.size)
    references = []
    for i, p in enumerate(request['referenced_image_paths']):
        ref = {'path':p, 'sha256':sha(Path(p)), 'purpose':('edit target','E identity','W identity','approved painted material style')[i]}
        if i == 0:
            ref.update(supersededAtPath=True, historicalGenerationRecord=f'records/cast/E/edge-root-20261008/{n}.previous.generation.json')
        references.append(ref)
    im.resize((1024,1024), Image.Resampling.LANCZOS).save(runtime)
    result = Image.open(runtime)
    record = {'file':runtime.relative_to(ROOT).as_posix(), 'sha256':sha(runtime),
              'generatedAt':receipt['endedAt'], 'width':1024, 'height':1024, 'format':'PNG',
              'tool':'image_gen.imagegen', 'route':'builtin',
              'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),
              'submittedParameters':{'model':None, 'quality':None, **{k:v for k,v in request.items() if k!='prompt'}},
              'actualModel':None, 'actualQuality':None, 'unverifiedReason':'宿主管理，工具未暴露model/quality参数，实际返回未披露型号或质量。',
              'prompt':f'prompts/cast/E/edge-root-20261008/{n}.txt', 'references':references,
              'evidence':{'receipt':f'records/cast/E/edge-root-20261008/{n}.receipt.json'},
              'native':{'width':im.width, 'height':im.height, 'mode':im.mode, 'sha256':sha(native)},
              'derivedFrom':{'path':native.as_posix(), 'sha256':sha(native), 'retained':True,
                             'retentionReason':'Host-generated cache is outside this pet-only write scope; no workspace source copy was made.'},
              'editHistory':{'previousRecord':f'records/cast/E/edge-root-20261008/{n}.previous.generation.json','previousRuntimeSha256':previous['sha256']},
              'operation':'Uniform whole-canvas Lanczos resize 1254 to 1024; no translation, crop, mirror, interpolation or foot alignment.',
              'action':'cast', 'direction':'E', 'frame':int(n), 'durationMs':45, 'pivot':[.5,.08], 'event':None,
              'visualStatus':'Root inspected actual generated full frame: right whiskers now terminate inside canvas, four limbs and original pose/accessories retained. Current sequence review recorded separately.'}
    (REC/f'{n}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/f'records/cast/E/{n}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frame':n,'sha256':record['sha256'],'nativeSize':im.size,'alphaExtrema':result.getchannel('A').getextrema()}))
