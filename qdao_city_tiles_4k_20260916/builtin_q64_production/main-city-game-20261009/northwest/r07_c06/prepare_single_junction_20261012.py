from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
root=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    if p.exists(): raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
write(root/'qa/west-seam-r3-fix01-quilt01/rejection.json',dict(recordedAt=now,actuallyViewedFullOverview=True,individualPerimeterCropsClaimedViewed=False,verdict='rejected-unselected',reason='Full native proposal exposes a doubled/notched left vertex, lower-left cut grout, and clipped bottom grout. No pixels adopted.',candidateUnchanged=True))
write(root/'qa/west-seam-r3-fix01-quilt02/failure.json',dict(recordedAt=now,verdict='construction-failed-unselected',reason='No continuous source-selection path avoids all mismatched grout in the left perimeter band. No image or proof output created.',candidateUnchanged=True))
src=root/'layout-only/west-seam-r3-fix01.actual-1254.png'
guide=root/'layout-only/west-seam-r3-fix02.locator-guide.png'
im=Image.open(src).convert('RGB')
draw=ImageDraw.Draw(im)
# Supplemental ink is only a locator in a reference, never final game art.
draw.rectangle((617,555,795,716),outline=(224,0,190),width=3)
draw.ellipse((618,619,636,637),outline=(0,120,220),width=3)
draw.ellipse((743,573,761,591),outline=(0,120,220),width=3)
draw.ellipse((617,681,637,701),outline=(235,40,30),width=3)
im.save(guide)
der=json.loads(src.with_suffix('.png.derivation.json').read_text(encoding='utf-8'))
write(guide.with_suffix('.png.derivation.json'),dict(schemaVersion=1,worldBox=der['worldBox'],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=sha(src)),pixels='Original actual candidate pixels plus visible locator ink only',locator=dict(rectangle=[617,555,795,716],blueFixedAnchors=[[627,628],[752,582]],redOrphan=[627,691])))
