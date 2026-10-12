from pathlib import Path
from PIL import Image
import json,hashlib
B=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
r=json.loads((B/'r16_c05/pipeline/prompts/p01_01.restart-20261013-v01.request.json').read_text(encoding='utf-8-sig'))
s=Path(r['referenced_image_paths'][1]);out=B/'r16_c05/pipeline/guides/approved-bottom-wall-context-QA-only.png'
assert not out.exists()
im=Image.open(s);im.crop((280,1120,420,1254)).resize((700,670),Image.Resampling.NEAREST).save(out)
Path(str(out)+'.derivation.json').write_text(json.dumps({'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'crop':[280,1120,420,1254],'resize':'nearest geometry context only','gameArt':False,'formalAccepted':False}),encoding='utf-8')
print(out)

