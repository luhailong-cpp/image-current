from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parents[1];src=p/'native/p34-v20261013-r2fix1.png';south=p/'native/p44-v20261013-r2.png';east=p.parent/'r08_c12/native/p31-v20261012.png';out=p/'layout-only/p34-repair2-target.png';assert not out.exists()
im=Image.open(src).convert('RGB');im.paste(Image.open(east).convert('RGB').crop((0,0,230,1254)),(1024,0));im.paste(Image.open(south).convert('RGB').crop((0,0,1254,230)),(0,1024));im.save(out)
Path(str(out)+'.generation.json').write_text(json.dumps({'operation':'native integer crop/paste of actual neighbor strips onto saved native candidate; no resizing or drawn pixels','derivedFrom':[{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in [src,south,east]]},indent=2),encoding='utf-8');print(str(out))
