"""Tile-only orchestration. No network requests; original images remain untouched."""
from pathlib import Path
import sys, json, hashlib, datetime, importlib.util
from PIL import Image
T = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('production_workflow', T.parent / 'production_workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
def dump(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
if not w.CONFIG.exists():
    p = T / 'records/p01_01_v20261012T135016_73f165cf.preparation.json'
    prior = json.loads(p.read_text(encoding='utf-8'))
    snapshot = T / 'records/config-carried-snapshot-20261012.json'
    if not snapshot.exists():
        dump(snapshot, prior['configSnapshot'])
        dump(T / 'records/config-snapshot-origin-20261012.json', {
            'status': 'historical_preference_snapshot_carried_forward_not_actual_backend_claim',
            'missingPath': str(w.CONFIG), 'sourcePreparation': str(p),
            'sourcePreparationSha256': w.sha(p), 'historicalConfigSha256': prior['configSha256'],
            'snapshot': str(snapshot), 'snapshotSha256': w.sha(snapshot),
            'actualModel': None, 'actualQuality': None, 'recordedAt': now()})
    w.CONFIG = snapshot
command = sys.argv[1]
if command == 'prepare':
    result = w.prepare('r15_c14', sys.argv[2])
elif command == 'ingest':
    version, source = sys.argv[2], Path(sys.argv[3]).resolve()
    assert Image.open(source).size == (1254,1254), 'Native must be exactly 1254; never resize'
    h = w.sha(source)
    receipt = T / 'records' / (version + '.receipt.json')
    assert not receipt.exists(), 'Receipt immutable'
    dump(receipt, {'tool':'image_gen.imagegen', 'route':'builtin',
        'status':'succeeded_pending_visual_qa', 'generatedAt':now(),
        'originalOutputPath':str(source), 'sourceSha256':h, 'actualSize':[1254,1254],
        'actualModel':None, 'actualQuality':None, 'resizedAfterGeneration':False,
        'finalArtUpscaled':False})
    result = w.ingest('r15_c14', version, str(source), str(receipt))
    resume = T / 'production-resume-20261012.json'
    j=json.loads(resume.read_text(encoding='utf-8'))
    j.update({'nativeGenerationCalls':len(list((T/'records').glob('*.receipt.json'))),
              'activeNativeCount':len(json.loads((T/'active-native-map.json').read_text(encoding='utf-8'))),
              'status':'native_generation_in_progress', 'lastNativeIngestedAt':now(),
              'inFlightImageGenCount':0})
    dump(resume,j)
elif command == 'assemble':
    result = w.assemble('r15_c14')
else:
    raise ValueError(command)
print(json.dumps(result, ensure_ascii=False, indent=2))
