from pathlib import Path
from PIL import Image
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
p=B/'r13_c06/pipeline/guides/approved-geometry-context-20261013-v02.png';assert not p.exists();box=[375,900,500,1080]
Image.open(src).convert('RGB').crop(box).resize((750,1080),Image.Resampling.NEAREST).save(p)
atomic_json(Path(str(p)+'.derivation.json'),{'file':str(p),'sha256':sha(p),'source':str(src),'sourceSha256':sha(src),'sourceCrop':box,'operation':'nearest-neighbor geometry-only enlargement, not native final artwork','guideOnly':True,'gameArt':False})
print(p)
