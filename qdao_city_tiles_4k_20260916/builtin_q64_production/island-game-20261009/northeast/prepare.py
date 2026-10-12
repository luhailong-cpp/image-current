"""Mechanical layout guides and provenance only; no game artwork is drawn here."""
from pathlib import Path
from PIL import Image
import hashlib, json
from datetime import datetime, timezone

ZONE = Path(__file__).resolve().parent
ROOT = ZONE.parents[3]
CONTRACT = json.loads((ZONE.parent / 'production-contract.json').read_text(encoding='utf-8-sig'))

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    for folder in ['guides', 'prompts', 'native', 'receipts', 'qa', 'tiles']:
        (ZONE / folder).mkdir(exist_ok=True)
    refs = []
    for key, role in [('layoutReference', 'sole full-map layout authority'), ('detailStyleReference', 'material and Spring Festival architecture style only; NOT coordinate crop'), ('primaryStyleReference', 'primary approved rounded Daoist hand-painted style only; no UI or night lighting')]:
        p = Path(CONTRACT[key])
        im = Image.open(p)
        refs.append({'file': p.as_posix(), 'sha256': digest(p), 'size': list(im.size), 'role': role})
    assert refs[0]['sha256'] == CONTRACT['layoutSha256']
    assert refs[1]['sha256'] == CONTRACT['detailSha256']
    write_json(ZONE / 'reference-audit.json', {'checkedAtUtc': now(), 'references': refs, 'batchPolicy': 'Continue already verified batch; shared config read-only.'})
    tiles = []
    for r in range(1, 8):
        for c in range(8, 15):
            box = [(c-1)*4096, (r-1)*4096, c*4096, r*4096]
            tiles.append({'id': f'r{r:02}_c{c:02}', 'worldBox': box, 'layoutBox': [v*1254/57344 for v in box], 'status': 'not_started'})
    write_json(ZONE / 'tile-plan.json', {'zone': 'northeast', 'totalTiles': 49, 'firstTile': 'r03_c12', 'tiles': tiles})
    layout = Image.open(CONTRACT['layoutReference']).convert('RGB')
    patches = []
    for r in range(4):
        for c in range(4):
            ident = f'r03_c12_p{r+1:02}_{c+1:02}'
            x, y = 45056+c*1024, 8192+r*1024
            core = [x,y,x+1024,y+1024]
            box = [x-115,y-115,x+1139,y+1139]
            source_box = [v*1254/57344 for v in box]
            guide = ZONE/'guides'/f'{ident}.layout-only.png'
            layout.transform((1254,1254), Image.Transform.EXTENT, source_box, Image.Resampling.BICUBIC).save(guide)
            rec = {'id': ident, 'coreWorldBox': core, 'nativeWorldBox': box, 'expectedNativeSize': [1254,1254], 'coreCrop': [115,115,1139,1139], 'layoutBox': source_box, 'guide': guide.as_posix(), 'guideSha256': digest(guide), 'guideRole': 'layout-only enlarged coordinate crop, forbidden as final artwork pixels', 'operation': 'Pillow EXTENT BICUBIC of exact floating box, layout-only', 'derivedFrom': refs[0], 'status': 'not_started'}
            write_json(guide.with_suffix('.png.derivation.json'), rec)
            patches.append(rec)
    write_json(ZONE/'patch-plan-r03_c12.json', {'patches':patches,'adjacentNativeOverlapPixels':230,'noFinalArtScaling':True})
    write_json(ZONE/'progress.json', {'zone':'northeast','status':'preparing_first_native','updatedAtUtc':now(),'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'target4kCount':49,'currentTile':'r03_c12','currentPatch':'r03_c12_p01_01','nextStep':'Generate first exact-coordinate native patch using built-in image_gen, then measure dimensions and inspect geometry.','errors':[{'stage':'python_discovery','error':'python command points to Windows Store alias; bundled Python selected as recovery','resolved':True}], 'clientMappingValidated':False,'navigationValidated':False,'capacity5000Validated':False})
    print(json.dumps({'references':refs,'firstPatch':patches[0]},ensure_ascii=False))

if __name__ == '__main__':
    main()
