from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
p=r/'layout-only/s02_01_anchorfix01.locator-guide.png'
src=r/'native/s02_01_resume01.png'
im=Image.open(src).convert('RGB')
d=ImageDraw.Draw(im)
d.line((131,230,279,230),fill=(0,175,220),width=4)
d.ellipse((122,221,140,239),outline=(220,0,180),width=3)
d.ellipse((270,221,288,239),outline=(220,0,180),width=3)
im.save(p)
def sha(x): return hashlib.sha256(x.read_bytes()).hexdigest()
meta=json.loads(src.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
out=p.with_suffix('.png.derivation.json')
assert not out.exists()
out.write_text(json.dumps(dict(guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=sha(src)),worldBox=meta.get('worldBoxWithHalo',meta.get('worldBox')),pixels='Original native image with cyan desired joining edge and two magenta endpoint locators only',fixedEndpoints=[[131,230],[279,230]],layoutChange='One thin horizontal edge closes the existing triangular inset. All diagonal branches and vertices stay fixed.'),indent=2),encoding='utf-8')
rej=r/'qa/west-seam-r3-fix02.review.json'
assert not rej.exists()
rej.write_text(json.dumps(dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),actuallyViewedFullNative=True,verdict='rejected-unselected',reason='Requested central connection was not created: actual vertical seam retains the incoming and lower orphan grout at separate heights. No supplemental pixels adopted.',candidateUnchanged=True),indent=2),encoding='utf-8')
