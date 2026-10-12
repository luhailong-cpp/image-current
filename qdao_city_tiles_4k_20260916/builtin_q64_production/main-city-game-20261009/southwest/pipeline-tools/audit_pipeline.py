"""Audit pipeline mechanics using real read-only inputs and isolated test outputs.

No image generator is called. This does not assert visual quality or produce
selected native artwork. All test writes stay below pipeline-tools/audit-runs.
"""
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import importlib.util
import json
import sys
import uuid

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location('pipeline_under_audit', ROOT / 'native_pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
out = HERE / 'audit-runs' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6])
out.mkdir(parents=True)


def isolated(pipeline, name):
    pipeline.work = out / name

    def boundary(path):
        path = Path(path).resolve()
        mod.require(path.is_relative_to(out.resolve()), 'Audit write outside isolated output folder')
        return path

    pipeline.write_target = boundary
    return pipeline


def args(**changes):
    result = dict(row=2, col=1, attempt='audit-only', content_prefix='AUDIT ONLY: this request is not submitted.',
                  content_prefix_file=None, anchor_top=None, anchor_left=None,
                  source=None, receipt=None, request=None)
    result.update(changes)
    return SimpleNamespace(**result)


# Preserve a before/after inventory of all existing production evidence.
protected = [p for name in ('r10_c05', 'r11_c05') for p in (ROOT / name).rglob('*') if p.is_file()]
protected += [p for p in (ROOT / 'progress.json', ROOT / 'resume-ack-20261010.json') if p.is_file()]
before = {str(p): mod.sha(p) for p in protected}

preflight = mod.Pipeline('r11_c05').assemble(True, 2)
mod.require(preflight['verifiedNativeCount'] == 4, 'Audit requires the existing four-patch first row')
p = isolated(mod.Pipeline('r11_c05'), 'prepare')
current_refs = p.current_refs()
mod.require(Path(current_refs[-1]['file']).suffix.lower() == '.jpg', 'Current primary style must be the replacement JPG')
prepared = p.prepare(args())
request = mod.read(prepared['request'])
mod.require([r['file'] for r in request['references']] == request['referenced_image_paths'], 'Request reference order mismatch')
with Image.open(prepared['seed']) as im:
    seed = np.asarray(im.convert('RGB'))
with Image.open(ROOT / 'r11_c05/native/p01_01.png') as im:
    upper = np.asarray(im.convert('RGB'))[1024:1254]
mod.require(np.array_equal(seed[:230], upper), 'Prepared upper native strip was not copied exactly')

assembled = isolated(mod.Pipeline('r11_c05'), 'assemble').assemble(False, 2)
with Image.open(assembled['output']['file']) as im:
    actual = np.asarray(im.convert('RGB'))
with Image.open(ROOT / 'r11_c05/output/r11_c05.partial-p01_01-p01_04.png') as im:
    existing = np.asarray(im.convert('RGB'))
mod.require(np.array_equal(actual, existing), 'Assembly differs from current first-row pixels')

rejections = []
for name, image, expected_text in (
    ('wrong-size', Image.new('RGB', (32, 32), (0, 0, 0)), 'expected 1254x1254'),
    ('transparent', Image.new('RGBA', (1254, 1254), (0, 0, 0, 0)), 'transparent pixels'),
):
    source = out / (name + '.fixture-not-art.png')
    image.save(source)
    receiver = isolated(mod.Pipeline('r11_c05'), 'ingest-' + name)
    receiver.t = out / ('ingest-' + name)
    try:
        receiver.ingest(args(request=prepared['request'], source=str(source),
                             receipt=str(ROOT / 'r11_c05/receipts/p01_04.receipt.json')))
    except ValueError as exc:
        mod.require(expected_text in str(exc), f'Unexpected rejection: {exc}')
        mod.require(not list(receiver.t.rglob('*.generation.json')), 'Rejected output occupied a native record')
        mod.require(not (receiver.t / 'native/p02_01.png').exists(), 'Rejected output occupied native pixels')
        rejections.append({'fixture': name, 'result': str(exc), 'nativeSlotCreated': False})
    else:
        raise AssertionError(f'{name} fixture was incorrectly accepted')

after = {str(p): mod.sha(p) for p in protected}
mod.require(before == after, 'Existing production file changed during audit')
report = {'status': 'passed', 'generatedImageCount': 0, 'selectedNativeCountAdded': 0,
          'auditOnly': True, 'outputDirectory': str(out), 'preflight': preflight,
          'currentRequiredReferences': current_refs, 'preparedRequest': prepared,
          'upper230PixelsExact': True, 'assembledOutput': assembled,
          'existingFirstRowPixelDifferences': int(np.count_nonzero(actual != existing)),
          'invalidIngestRejections': rejections,
          'existingProductionFilesCheckedUnchanged': len(before),
          'limits': ['No tool call was made.', 'Valid native ingest was inspected but not simulated.',
                     'Visual quality and formal acceptance are not established by these checks.']}
(out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'passed', 'report': str(out / 'audit.json'),
                  'existingFirstRowPixelDifferences': report['existingFirstRowPixelDifferences'],
                  'existingProductionFilesCheckedUnchanged': len(before),
                  'context': assembled['context']['file'], 'generatedImages': 0}, ensure_ascii=False, indent=2))
