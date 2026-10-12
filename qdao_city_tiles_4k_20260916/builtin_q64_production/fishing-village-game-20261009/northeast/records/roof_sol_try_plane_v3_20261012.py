from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
qa=Z/'qa/r05_c12-loweredge-v3-plane-trial';qa.mkdir(exist_ok=False)
tp=Z/'qa/r05_c12-roofbridge-v1/context.native-1to1.png';sp=Z/'native/r05_c12_p11-p21-loweredge-v3.png'
target=Image.open(tp).convert('RGB');source=Image.open(sp).convert('RGB')
box=(0,627,900,1100)
out=target.copy();out.paste(source.crop(box),box[:2]);out.save(qa/'context.native-1to1.png')
specs=[('top',(0,547,1024,707)),('bottom',(0,1020,1024,1180)),('right',(820,547,980,1180)),('interior-blue-tiles',(0,620,900,970)),('left-halo',(0,547,160,1180))]
for label,crop in specs:out.crop(crop).save(qa/f'{label}.native-1to1.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
(qa/'construction.json').write_text(json.dumps(dict(schemaVersion=1,operation='Trial exact integer crop and opaque paste from existing v3 raw native; no new generation and no resize',source=dict(path=str(sp),sha256=sha(sp)),base=dict(path=str(tp),sha256=sha(tp)),contributionLocalBox=list(box),contributionWorldBox=[44941,17408,45841,17881],formalAccepted=False,visualReview='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
