from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1]
p=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png')
box=[160,430,290,560]
out=Z/'qa/r06c03_layout_ONLY_NOT_GAME.png'
assert not out.exists()
Image.open(p).crop(box).resize((780,780),Image.Resampling.NEAREST).save(out)
(out.with_suffix('.json')).write_text(json.dumps({'source':p.as_posix(),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cropBox':box,'operation':'nearest enlarged overview for semantic layout inspection only','finalGameArt':False},indent=2),encoding='utf-8')
