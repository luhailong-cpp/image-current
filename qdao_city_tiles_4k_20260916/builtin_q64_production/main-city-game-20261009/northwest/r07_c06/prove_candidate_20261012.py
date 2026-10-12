"""Prove this candidate is a translation of unchanged native source pixels."""
from pathlib import Path
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v2', HERE.parent / 'production_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
MANIFEST = HERE / 'candidate/r07_c06-candidate-hard-2e59491c741a.assembly.json'
QA = HERE / 'qa/final-candidate-20261012'
OUTPUT = QA / 'candidate-pixel-proof.json'
if OUTPUT.exists():
    raise FileExistsError(OUTPUT)

cache = {}
def file_sha(path):
    p = Path(path)
    if p not in cache:
        cache[p] = hashlib.sha256(p.read_bytes()).hexdigest()
    return cache[p]

def pixels(im):
    return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()

manifest = v2.read(MANIFEST)
candidate_path = Path(manifest['output']['file'])
candidate = Image.open(candidate_path).convert('RGB')
assert candidate.size == (4096, 4096)
assert file_sha(candidate_path) == manifest['output']['sha256']
selected = v2.read(HERE / 'selection.json')
sources = []
for source in manifest['nativeSources']:
    pid = source['id']
    native = Path(source['file'])
    assert v2.selected_path(HERE, pid, selected).resolve() == native.resolve()
    v2.validate_native(native, HERE, pid)
    assert file_sha(native) == source['sha256']
    generation = v2.read(source['generationRecord']['file'])
    request_path = generation['evidence']['request']
    receipt_path = generation['evidence']['receipt']
    prompt_path = generation['prompt']
    assert file_sha(request_path) == generation['evidence']['requestSha256']
    assert file_sha(receipt_path) == generation['evidence']['receiptSha256']
    assert file_sha(prompt_path) == generation['evidence']['promptSha256']
    request = v2.read(request_path)
    submitted = dict(generation['submittedParameters'])
    submitted.pop('model', None)
    submitted.pop('quality', None)
    assert submitted == request['parameters']
    assert Path(prompt_path).read_text(encoding='utf-8').strip() == submitted['prompt'].strip()
    assert generation['route'] == 'builtin'
    assert generation['actualModel'] is None and generation['actualQuality'] is None
    assert datetime.fromisoformat(request['recordedAt']) < datetime.fromisoformat(generation['generatedAt'])
    refs = []
    for ref in generation['references']:
        assert file_sha(ref['file']) == ref['sha256']
        refs.append(dict(file=ref['file'], sha256=ref['sha256'], verified=True))
    host = Path(generation['evidence']['hostOutputPath'])
    assert host.is_file() and file_sha(host) == file_sha(native)
    with Image.open(native) as im:
        assert im.size == (1254, 1254) and im.format == 'PNG'
        assert im.convert('RGBA').getchannel('A').getextrema() == (255, 255)
        crop = im.convert('RGB').crop(tuple(source['coreCropLTRB']))
    x, y = source['tileCorePasteXY']
    placed = candidate.crop((x, y, x+1024, y+1024))
    assert crop.tobytes() == placed.tobytes()
    sources.append(dict(id=pid, file=str(native), sha256=file_sha(native), hostFile=str(host), hostByteIdentical=True,
                        coreCrop=source['coreCropLTRB'], candidateBox=[x,y,x+1024,y+1024],
                        sourceCorePixelSha256=pixels(crop), candidateCorePixelSha256=pixels(placed),
                        corePixelsExactlyEqual=True, prompt=prompt_path, request=request_path, receipt=receipt_path,
                        generationRecord=source['generationRecord'], references=refs))

qa = v2.read(QA / 'crops.json')
art = Image.open(qa['art']['file']).convert('RGB')
assert candidate.tobytes() == art.tobytes()
neighbors = {side: Image.open(value['file']).convert('RGB') for side, value in qa['neighbors'].items()}
for side, value in qa['neighbors'].items():
    assert file_sha(value['file']) == value['sha256']
entries = []
for e in qa['entries']:
    x, y = e['coordinate']
    category = e['category']
    if category == 'internal-vertical':
        expected = candidate.crop((x-128,y,x+128,y+1024))
    elif category == 'internal-horizontal':
        expected = candidate.crop((x,y-128,x+1024,y+128))
    elif category == 'internal-junction':
        expected = candidate.crop((x-192,y-192,x+192,y+192))
    elif category == 'external-north':
        expected = Image.new('RGB',(1024,256))
        expected.paste(neighbors['north'].crop((x,3968,x+1024,4096)),(0,0))
        expected.paste(candidate.crop((x,0,x+1024,128)),(0,128))
    elif category == 'external-west':
        expected = Image.new('RGB',(256,1024))
        expected.paste(neighbors['west'].crop((3968,y,4096,y+1024)),(0,0))
        expected.paste(candidate.crop((0,y,128,y+1024)),(128,0))
    else:
        raise ValueError(category)
    actual = Image.open(e['file']).convert('RGB')
    assert file_sha(e['file']) == e['sha256']
    assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
    entries.append(dict(name=e['name'],file=e['file'],sha256=e['sha256'],category=category,
                        candidateAndNeighborPixelsExactlyEqual=True,pixelSha256=pixels(actual)))
assert len(sources) == 16 and len(entries) == 41
record = dict(tile=HERE.name,createdAt=datetime.now(timezone.utc).isoformat(),status='pixel-proof-passed-visual-review-separate',
              candidate=dict(file=str(candidate_path),sha256=file_sha(candidate_path),size=list(candidate.size),pixelSha256=pixels(candidate)),
              assemblyManifest=dict(file=str(MANIFEST),sha256=file_sha(MANIFEST)),
              qaArt=dict(file=qa['art']['file'],sha256=file_sha(qa['art']['file']),candidateRawPixelsIdentical=True),
              selectedSources=sources,sourceCount=16,candidateCoveredPixels=4096*4096,originalHostCopiesByteIdentical=True,
              sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,
              corePixelsUnchanged=True,sourceCrop=[115,115,1139,1139],nativeSize=[1254,1254],
              cropCount=41,crops=entries,neighbors=qa['neighbors'],formalAccepted=False,
              actualModel=None,actualQuality=None,scope='Only r07_c06 files written; proof does not grant visual acceptance')
v2.write_json(OUTPUT,record)
print(json.dumps(dict(proof=str(OUTPUT),sha256=file_sha(OUTPUT),sourceCount=len(sources),cropCount=len(entries),
                      originalHostCopiesByteIdentical=True,candidateRawPixelsIdenticalToQaArt=True,formalAccepted=False),indent=2))
