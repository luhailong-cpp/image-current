from pathlib import Path
import hashlib,json
from PIL import Image

tile=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
out=Path(__file__).parent
batch=tile/'repair-batches/c3c4-upper-gap-02'
trial=json.loads((batch/'trial.json').read_text(encoding='utf-8'))
box=(2940,450,3210,750)
paths=[]
for name,path,crop in [('base-context-native.png',trial['baseCandidate']['file'],box),('source-context-native.png',trial['source']['file'],(495,450,765,750))]:
    target=out/name
    assert not target.exists()
    with Image.open(path) as im: im.crop(crop).save(target)
    paths.append({'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'input':path,'inputSHA256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'cropLTRB':crop,'nativePixelScale':1})
(out/'review-input-crops.json').write_text(json.dumps(paths,indent=2),encoding='utf-8')
print(json.dumps(paths,indent=2))
