from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'native/s02_04_orphanfix01.png';p=r/'layout-only/s02_04_orphanfix02.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im);d.line((316,488,230,563),fill=(238,30,35),width=13);im.save(p)
p.with_suffix('.png.derivation.json').write_text(json.dumps(dict(worldBox=[23437,25485,24691,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),redBranchToErase=[[322,482],[230,563]],otherCorrection='Remove residual blue locator tint on gold bevel near (222,368). No new marker added there.'),indent=2),encoding='utf-8')
(r/'qa/s02_04_orphanfix01.partial-review.json').write_text(json.dumps(dict(actuallyViewedFullNative=True,actuallyViewedDetail='s02_04_orphanfix01-upper-joint-diagnostic.png',verdict='unselected-partial-progress',fixed='Pinned connection between (222,368) and (322,482) created; tiny northeast spur removed.',remaining=['Southwest branch (322,482)->(230,563) remains','Blue locator tint at upper fixed gold vertex needs cleanup','Other original lower and upper-corner cuts intentionally untouched'],formalAccepted=False),indent=2),encoding='utf-8')
